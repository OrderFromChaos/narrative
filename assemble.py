"""Print the SKILL.md of an entry skill of Narrative, or the skills to load for a repository.

For a skill with `modules` in skills.toml, the output is a whole SKILL.md: the frontmatter, then
each module in the order of skills.toml. build_skills.py writes that output to skills/<name>/.

For a skill with `combines`, such as `code`, the output is one short paragraph: the languages of
the current directory, with the most files first, and the skills to load with the Skill tool. The
SKILL.md of `code` runs this script when the skill loads. Claude Code shows an agent at most 2 KB of
such output, and saves longer output to a file, so the paragraph names skills and has no rules.

With --requires, the output is the skills that a skill requires, one per line, for install.sh.

Usage:
    $ python3 assemble.py python
    $ python3 assemble.py code
    $ python3 assemble.py python --requires

Exit codes:
    0  the text was printed
    2  the skill name is not in skills.toml, or skills.toml names a file that is missing
"""

from __future__ import annotations

import argparse
import collections
import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / 'skills.toml'
# the plugin's name, before the colon of a skill command such as /nar:python
PLUGIN_NAME = 'nar'
# the directories left out of a walk of a directory with no git repository
SKIPPED_DIRECTORIES = frozenset({'.git', '.gradle', 'build', 'node_modules', '.venv', '__pycache__'})
# the largest number of files in a walk, so the load time of a skill on a large directory with no git
# repository has a bound
MAX_WALKED_FILES = 200_000
EXIT_SUCCESS = 0
EXIT_BAD_REQUEST = 2


def main() -> int:
    """Print the SKILL.md of a skill with modules, or the skills to load for a skill with `combines`.

    Returns:
        0 when the text was printed, 2 for an unknown skill or a missing module.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('name', help='a skill of skills.toml, such as python or code')
    parser.add_argument('--requires', action='store_true', help='print the skills this skill requires')
    arguments = parser.parse_args()

    try:
        manifest = readManifest(MANIFEST_PATH)
        if arguments.requires:
            skill = manifest.modular.get(arguments.name)
            sys.stdout.write(''.join(f'{name}\n' for name in skill.requires) if skill else '')
            return EXIT_SUCCESS
        sys.stdout.write(skillText(manifest, arguments.name))
    except ManifestError as exc:
        print(f'assemble.py: {exc}', file=sys.stderr)
        return EXIT_BAD_REQUEST
    return EXIT_SUCCESS


def skillText(manifest: Manifest, name: str) -> str:
    """Pick the text of one skill: a whole SKILL.md, or the skills to load for the current directory.

    Raises:
        ManifestError: the name is unknown, or a module is missing.
    """
    if combined := manifest.combined.get(name):
        return loadList(manifest, combined, Path.cwd())
    skill = manifest.modular.get(name)
    if skill is None:
        known = ', '.join([*manifest.modular, *manifest.combined])
        raise ManifestError(f'no skill named {name!r}. The skills are {known}')
    return staticSkill(skill)


def readManifest(manifest_path: Path) -> Manifest:
    """Read skills.toml: a table with `modules` has rules, and a table with `combines` names other skills.

    Raises:
        ManifestError: a table has neither `modules` nor `combines`, has no description, or names an
            unknown skill.
    """
    with manifest_path.open('rb') as manifest:
        tables = tomllib.load(manifest)
    modular: dict[str, ModularSkill] = {}
    combined: dict[str, CombinedSkill] = {}
    try:
        for name, table in tables.items():
            if 'modules' in table:
                marker = table.get('marker')
                modular[name] = ModularSkill(
                    name,
                    table['description'],
                    tuple(table['modules']),
                    tuple(table.get('files', ())),
                    tuple(table.get('suffixes', ())),
                    tuple(table.get('requires', ())),
                    BuildMarker(tuple(marker['files']), marker['contains']) if marker else None,
                )
            elif 'combines' in table:
                combined[name] = CombinedSkill(name, table['description'], tuple(table['combines']))
            else:
                raise ManifestError(f'[{name}] in skills.toml has neither modules nor combines')
    except KeyError as exc:
        raise ManifestError(f'a table in skills.toml has no {exc.args[0]}') from exc
    named = [(skill.name, skill.combines) for skill in combined.values()]
    named += [(skill.name, skill.requires) for skill in modular.values()]
    for name, others in named:
        unknown = [other for other in others if other not in modular]
        if unknown:
            raise ManifestError(f'[{name}] names {", ".join(unknown)}, which skills.toml has no table for')
    return Manifest(modular, combined)


def staticSkill(skill: ModularSkill) -> str:
    """Write the whole SKILL.md of one skill: the frontmatter, then each module.

    Raises:
        ManifestError: a module is missing.
    """
    frontmatter = f'---\nname: {skill.name}\ndescription: {skill.description}\n---\n'
    return frontmatter + ''.join(readModule(module) for module in skill.modules)


def loadList(manifest: Manifest, combined: CombinedSkill, directory: Path) -> str:
    """Name the skills to load for the combined languages with source files in the directory.

    Returns:
        One paragraph: the languages with their file counts, most files first, and every skill to load,
        each skill that a language skill requires first. A language skill whose build marker is missing
        is left out, with one line on why, and the skills it requires still load. Without a source file
        of a combined language, one line about the missing files.
    """
    counts = collections.Counter(Path(name).suffix.lower() for name in sourceFiles(directory))
    skills = [manifest.modular[name] for name in combined.combines]
    counted = [(sum(counts[suffix] for suffix in skill.suffixes), skill) for skill in skills]
    found = sorted(((count, skill) for count, skill in counted if count), key=lambda pair: -pair[0])
    if not found:
        return f'No source file of {" or ".join(combined.combines)} is below {directory}.\n'

    to_load: list[str] = []
    for _count, skill in found:
        for name in [*skill.requires, skill.name] if hasMarker(skill, directory) else skill.requires:
            if name not in to_load:
                to_load.append(name)
    fitting = [(count, skill) for count, skill in found if hasMarker(skill, directory)]
    listed = ', '.join(f'{skill.name} ({count} files)' for count, skill in fitting)
    paragraph = f'This repository has source files of {listed}. ' if fitting else ''
    for count, skill in found:
        if (marker := skill.marker) and not hasMarker(skill, directory):
            paragraph += (
                f'The repository has {count} {" or ".join(skill.suffixes)} files, but no'
                f' {" or ".join(marker.files)} in the current directory contains `{marker.contains}`, so'
                f' `{PLUGIN_NAME}:{skill.name}` does not fit those files. Do not load `{PLUGIN_NAME}:{skill.name}`. '
            )
    commands = ', '.join(f'`{PLUGIN_NAME}:{name}`' for name in to_load)
    return (
        f'{paragraph}Before you write or review anything, load each of these skills with the Skill tool,'
        f' in this order: {commands}.\n'
    )


def hasMarker(skill: ModularSkill, directory: Path) -> bool:
    """Tell whether the directory has the build of the skill: a marker file that contains the marker text.

    A skill with no marker, such as python, fits any directory with its source files.
    """
    if skill.marker is None:
        return True
    marker_paths = (directory / name for name in skill.marker.files)
    return any(path.is_file() and skill.marker.contains in path.read_text(errors='replace') for path in marker_paths)


def sourceFiles(directory: Path) -> list[str]:
    """List the files below a directory: the files of git, less the ignored files, or a walk with no git repository.

    Returns:
        Paths relative to the directory.
    """
    command = ['git', '-C', str(directory), 'ls-files', '--cached', '--others', '--exclude-standard']
    listed = subprocess.run(command, capture_output=True, text=True, check=False)
    if listed.returncode == 0:
        return listed.stdout.splitlines()

    walked: list[str] = []
    for current, directories, files in os.walk(directory):
        # a directory with a .git entry is another checkout, such as a worktree of another branch
        directories[:] = [
            name for name in directories
            if name not in SKIPPED_DIRECTORIES and not (Path(current) / name / '.git').exists()
        ]
        walked.extend(files)
        if len(walked) >= MAX_WALKED_FILES:
            break
    return walked


def readModule(relative: str) -> str:
    """Read one module of skills.toml, relative to the repository root.

    Raises:
        ManifestError: the file is missing.
    """
    try:
        return (ROOT / relative).read_text(encoding='utf-8')
    except OSError as exc:
        raise ManifestError(f'{relative} in skills.toml cannot be read: {exc.strerror}') from exc


### vocabulary #########################################################################


@dataclass(frozen=True)
class ModularSkill:
    """A table of skills.toml with modules: rules, and the tools beside the rules."""

    name: str
    description: str
    modules: tuple[str, ...]
    files: tuple[str, ...]
    # the suffixes of the language's source files, for a combined skill. Empty for a skill of no language
    suffixes: tuple[str, ...]
    # the skills to load before this one, such as core
    requires: tuple[str, ...]
    # the build that a combined skill needs before it loads this skill, such as a GTNH Gradle build
    marker: BuildMarker | None


@dataclass(frozen=True)
class BuildMarker:
    """Build files at the root of a repository, one of which must contain a text."""

    files: tuple[str, ...]
    contains: str


@dataclass(frozen=True)
class CombinedSkill:
    """A table of skills.toml with `combines`: the skills to load for each combined language of the repository."""

    name: str
    description: str
    combines: tuple[str, ...]


@dataclass(frozen=True)
class Manifest:
    modular: dict[str, ModularSkill]
    combined: dict[str, CombinedSkill]


class ManifestError(ValueError):
    pass


if __name__ == '__main__':
    sys.exit(main())
