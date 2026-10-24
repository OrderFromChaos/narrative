"""Write each entry skill of skills.toml to skills/<name>/: a SKILL.md that loads the rules, and the tools.

An install copies one skill directory and nothing else, so every tool of a skill is in the skill's
directory. The rules and the tools are written once in core/ and lang/, and each entry skill gets a
copy of the tools of the skill.

The SKILL.md of a skill with modules is the output of assemble.py: the frontmatter, then the rules.
The SKILL.md of a skill with `combines`, such as `code`, has the frontmatter and one line. When the
skill loads, Claude Code runs assemble.py and puts the output, the skills to load, in place of that
line. With `allowed-tools` in the frontmatter, the line runs with no permission prompt.

With --check, nothing is written, and a file of skills/ that differs from the build, is missing, or
is not part of the build is an error. verify_docs.py runs the check.

Usage:
    $ python3 build_skills.py
    $ python3 build_skills.py --check

Exit codes:
    0  every skill was written, or every file of skills/ matches the build
    1  --check found a difference
    2  skills.toml names a file that is missing, or two files of one skill have one name
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assemble import MANIFEST_PATH, ManifestError, readManifest, staticSkill


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / 'skills'
# the command in SKILL.md that runs assemble.py. allowed-tools names the same command, so the command
# runs with no permission prompt
LOAD_COMMAND = 'python3 ${CLAUDE_PLUGIN_ROOT}/assemble.py'
EXIT_SUCCESS = 0
EXIT_DIFFERS = 1
EXIT_BAD_MANIFEST = 2


def main() -> int:
    """Build every entry skill, or compare skills/ with the build.

    Returns:
        0 when skills/ matches the build after the run, 1 for a difference under --check, 2 when
        skills.toml is wrong.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='compare skills/ with the build and write nothing')
    arguments = parser.parse_args()

    try:
        built = buildAll()
    except ManifestError as exc:
        print(f'build_skills.py: {exc}', file=sys.stderr)
        return EXIT_BAD_MANIFEST

    differences = compareWithDisk(built)
    if arguments.check:
        for difference in differences:
            print(f'skills/ differs from the build: {difference}')
        if differences:
            print('run python3 build_skills.py to rebuild skills/')
        return EXIT_DIFFERS if differences else EXIT_SUCCESS

    writeAll(built)
    for difference in differences:
        print(f'rebuilt: {difference}')
    print(f'{len(built)} files in skills/, {len(differences)} changed')
    return EXIT_SUCCESS


def buildAll() -> dict[Path, bytes]:
    """Render the SKILL.md of every entry skill, and copy the tools of every skill with modules.

    Raises:
        ManifestError: skills.toml is wrong, a file is missing, or two files of one skill have one name.

    Returns:
        The content of each file, by the file's path under skills/.
    """
    manifest = readManifest(MANIFEST_PATH)
    built: dict[Path, bytes] = {}
    for combined in manifest.combined.values():
        loader = loaderSkill(combined.name, combined.description)
        built[OUTPUT_DIR / combined.name / 'SKILL.md'] = loader.encode('utf-8')
    for skill in manifest.modular.values():
        built[OUTPUT_DIR / skill.name / 'SKILL.md'] = staticSkill(skill).encode('utf-8')
        for source in skill.files:
            target = OUTPUT_DIR / skill.name / Path(source).name
            if target in built:
                raise ManifestError(f'[{skill.name}] has two files named {target.name}')
            built[target] = readSource(source)
    return built


def loaderSkill(name: str, description: str) -> str:
    """Write a SKILL.md whose text comes from assemble.py when the skill loads."""
    return (
        f'---\nname: {name}\ndescription: {description}\nallowed-tools: Bash({LOAD_COMMAND} *)\n---\n\n'
        f'!`{LOAD_COMMAND} {name}`\n'
    )


def readSource(relative: str) -> bytes:
    """Read one file of skills.toml, relative to the repository root.

    Raises:
        ManifestError: the file is missing.
    """
    try:
        return (ROOT / relative).read_bytes()
    except OSError as exc:
        raise ManifestError(f'{relative} in skills.toml cannot be read: {exc.strerror}') from exc


def compareWithDisk(built: dict[Path, bytes]) -> list[str]:
    """List each file of skills/ that differs from the build, is missing, or is not part of the build.

    Returns:
        One line per file, as a path relative to the repository root.
    """
    differences: list[str] = []
    for path, content in built.items():
        if not path.is_file():
            differences.append(f'{path.relative_to(ROOT)} is missing')
        elif path.read_bytes() != content:
            differences.append(f'{path.relative_to(ROOT)} is out of date')
    differences.extend(f'{path.relative_to(ROOT)} is not part of the build' for path in strayFiles(built))
    return differences


def strayFiles(built: dict[Path, bytes]) -> list[Path]:
    """List the files below skills/ that are not part of the build, leaving out the bytecode of a run.

    Returns:
        The paths, sorted.
    """
    if not OUTPUT_DIR.is_dir():
        return []
    files = (path for path in OUTPUT_DIR.rglob('*') if path.is_file() and '__pycache__' not in path.parts)
    return sorted(path for path in files if path not in built)


def writeAll(built: dict[Path, bytes]) -> None:
    """Write every built file, and delete each file of skills/ that is not part of the build.

    A stray file is deleted, because a file from an earlier build can be the text of a withdrawn rule.
    Each delete is of one named file, and directories are left in place.
    """
    for path in strayFiles(built):
        path.unlink()
    for path, content in built.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != content:
            path.write_bytes(content)


if __name__ == '__main__':
    sys.exit(main())
