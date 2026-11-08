"""Run the narrative-gtnh toolchain over a GTNH mod, or the prose checks over pages.

Use this instead of calling the tools by hand. A missing tool, report or JDK is exit 2, so a pass means every check ran.

The project is the current directory, a Gradle build with GTNHGradle. The Java level of the project comes from
enableModernJavaSyntax in gradle.properties: Java 25 for jvmDowngrader or modern, Java 17 syntax with the Java 8 library
for jabel or true, and Java 8 for false or no value. First, javachecks.py --rewrap fills each paragraph of the javadoc
and the whole-line // comments again up to column 120, unless --no-fix is given. Under --since, only a paragraph with a
changed line is re-wrapped. Then, in one Gradle run, the code is formatted (spotlessApply, or spotlessCheck with
--no-fix), compiled with the raw-type and unchecked warnings of javac, and checked with Checkstyle and PMD and the
configs beside this script. javac comes from the JDK of the project's toolchain, and Checkstyle and PMD run on a JDK 25
at every level. Those tasks come from the init script narrative.init.gradle, so no project file changes. javachecks.py
then reads the comments, runs the prose checks, and merges the three reports into one list of findings.

A Markdown, HTML or plain text file named on the command line gets the prose checks of javachecks.py, in the same list
of findings as the Java sources. A Gradle project is required only when Java sources are checked. When only pages are
named, no Java source is checked. In a Gradle project, verify.py then prints a warning. A path of `-` is a page read
from stdin, Markdown, or the suffix given with --stdin-suffix. The page is saved in the cache directory as `stdin` with
that suffix, and each finding is reported at the path of the saved page.

With --prose-only, Gradle does not run: no spotless, javac, Checkstyle or PMD. After a re-wrap, javachecks.py checks the
comments and the pages, and verify.py writes the review lists. A run after an edit of comments only takes seconds
instead of a Gradle run. The checks of Gradle still have to pass in a run without --prose-only before the change is
done.

With --project DIR, DIR is the project in place of the current directory. Each named path is read from the current
directory.

After the checks, verify.py writes three review lists over the Java sources and the pages to review-lists.txt in the
cache directory, .narrative_cache or the directory given with --cache-dir: every sentence, every subject that cannot act
paired with the subject's verb, and every sentence with a pronoun. The path of the file and the number of entries in
each list are on the last line of the output, so `tail -1` shows them. verify.py writes no lists on exit 2, or after a
Gradle failure. Without --since, each list stops after 1000 entries, with the command for the next 1000. Under --since,
a passage of a source file or a page is checked and listed when a line of the passage changed.

Usage:
    $ python3 verify.py                          # every src/*/java of the mod in the current directory
    $ python3 verify.py --since origin/dev       # only lines changed since merge-base(HEAD, origin/dev)
    $ python3 verify.py --no-fix                 # no re-wrap, and spotlessCheck in place of spotlessApply
    $ python3 verify.py src/main/java/com/example/gui
    $ python3 verify.py README.md docs/page.html
    $ python3 verify.py --prose-only --since origin/dev     # comments and pages only, with no Gradle run
    $ python3 verify.py --project ../MyMod --cache-dir /tmp/narrative     # a mod in another directory
    $ printf '%s\n' "$DRAFT" | python3 verify.py - --cache-dir /tmp/narrative      # a page from stdin

Exit codes:
    0  every check passed. Warnings may be printed
    1  at least one finding, or the code does not compile or is not formatted
    2  the toolchain, gradle.properties, gradlew or a report is missing, enableModernJavaSyntax or
       forceToolchainVersion has a value with no level in Scope of SKILL.md, nothing was checked, javachecks.py
       stopped before its count line, or javachecks.py --prose failed and wrote no review list
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from wording import countEntries


SKILL_DIR = Path(__file__).resolve().parent
PROSE_SUFFIXES = frozenset({'.md', '.markdown', '.html', '.htm', '.txt'})
# agentverbs.py imports these, so the venv's interpreter must import them
PARSER_MODULES = ('spacy', 'en_core_web_md')
# %LOCALAPPDATA% on Windows. $XDG_DATA_HOME, or ~/.local/share, on Linux and macOS
DATA_HOME = Path(os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
# the lint venv of every language skill, one per machine
SHARED_VENV = DATA_HOME / 'narrative' / 'lintenv'
VENV_PYTHON = Path('Scripts/python.exe') if sys.platform == 'win32' else Path('bin/python')
GRADLEW = 'gradlew.bat' if sys.platform == 'win32' else 'gradlew'
REPORT_DIR = Path('build/narrative')
CHECK_TASKS = ('narrativeCheckstyle', 'narrativePmd')
PASS_NOTE = 'These lint checks cover only some of the rules. Check the other rules by hand.'
# the default cache directory: the spaCy results of a run without Gradle, a page read from stdin, and the three review
# lists of the last run, for Prose review
CACHE_DIR = Path('.narrative_cache')
LISTS_NAME = 'review-lists.txt'
# the command-line path of a page read from stdin
STDIN_PATH = Path('-')
# the units of the three lists of javachecks.py --prose, in the order javachecks.py prints them
LIST_UNITS = ('sentences', 'pairs', 'pronoun sentences')
EXIT_SUCCESS = 0
EXIT_FINDINGS = 1
EXIT_NO_TOOLCHAIN = 2


def main() -> int:
    """Check the prerequisites, run Gradle with the init script, and run javachecks.py on Gradle's reports."""
    parser = argparse.ArgumentParser(description='Run the narrative-gtnh toolchain.')
    parser.add_argument(
        'paths',
        nargs='*',
        type=Path,
        help='Java source dirs or files (default: every src/*/java), or pages for the prose checks',
    )
    parser.add_argument('--since', help='report only lines changed since merge-base(HEAD, SINCE)')
    parser.add_argument('--no-fix', action='store_true', help='no re-wrap, and spotlessCheck in place of spotlessApply')
    parser.add_argument('--venv', type=Path, default=SHARED_VENV, help=f'the lint venv (default: {SHARED_VENV})')
    parser.add_argument('--gradle', help='the Gradle command, in place of ./gradlew')
    parser.add_argument('--max-workers', type=int, default=2, help='the Gradle worker limit (default: 2)')
    parser.add_argument(
        '--all-sentences',
        action='store_true',
        help='list every entry of the review lists, not the first 1000 of each',
    )
    parser.add_argument('--prose-only', action='store_true', help='check comments and pages only, with no Gradle run')
    parser.add_argument('--project', type=Path, help='the mod directory (default: the current directory)')
    parser.add_argument('--cache-dir', type=Path, default=CACHE_DIR, help=f'the cache directory (default: {CACHE_DIR})')
    parser.add_argument('--stdin-suffix', default='.md', help='the suffix of a page read from stdin (default: .md)')
    args = parser.parse_args()
    print(f'narrative-gtnh skill: {readInstalledVersion()}', flush=True)

    venv_python = (args.venv / VENV_PYTHON).absolute()
    if missing := missingVenvModules(venv_python):
        print(f'verify.py: {", ".join(missing)} missing from {args.venv}. Set the venv up with:', file=sys.stderr)
        print(setupCommands(args.venv), file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    cache_dir = prepareCache(args.cache_dir.absolute())
    paths = [readStdinPage(cache_dir, args.stdin_suffix) if path == STDIN_PATH else path for path in args.paths]
    if args.project is not None:
        # the named paths are relative to the directory of the command, and the project is the directory of the run
        paths = [path.absolute() for path in paths]
        os.chdir(args.project)
    pages = [path for path in paths if path.suffix.lower() in PROSE_SUFFIXES]
    java_sources = [path for path in paths if path.suffix.lower() not in PROSE_SUFFIXES]
    since = ['--since', args.since] if args.since else []
    if pages and not java_sources:
        if Path('gradle.properties').is_file():
            print('verify.py: only pages are named, so no Java source is checked. Name src/main/java too', flush=True)
        page_arguments = [*map(str, pages), *since, '--cache', str(cache_dir / 'prose-cache.json')]
        return reportFindings(venv_python, page_arguments, page_arguments, cache_dir, all_sentences=args.all_sentences)

    project_dir = Path.cwd()
    sources = java_sources or sorted((project_dir / 'src').glob('*/java')) or [project_dir / 'src' / 'main' / 'java']
    if args.prose_only:
        if not args.no_fix:
            print(f'rewrap         {rewrapComments(venv_python, sources, args.since)}', flush=True)
        print('gradle         not run: --prose-only. Run verify.py without --prose-only before the change is done')
        prose_arguments = [*map(str, [*sources, *pages]), *since, '--cache', str(cache_dir / 'prose-cache.json')]
        return reportFindings(
            venv_python,
            prose_arguments,
            prose_arguments,
            cache_dir,
            all_sentences=args.all_sentences,
        )

    try:
        settings = readGradleProperties(project_dir / 'gradle.properties')
        gradle_command = args.gradle.split() if args.gradle else findGradlew(project_dir)
    except PrerequisiteError as exc:
        print(f'verify.py: {exc}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    print(f'level          {settings.level.summary}', flush=True)
    report_dir = project_dir / REPORT_DIR
    try:
        changed_files = readChangedFiles(args.since, project_dir) if args.since else None
    except PrerequisiteError as exc:
        print(f'verify.py: {exc}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    if changed_files is not None and not changed_files:
        print(f'verify.py: no line changed since {args.since}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    # before Gradle, because splitting a // comment moves every later line of the file, and Gradle must see the final
    # lines
    if not args.no_fix:
        print(f'rewrap         {rewrapComments(venv_python, sources, args.since)}', flush=True)

    ruleset_path = writeRuleset(sources, report_dir, settings.level)
    gradle_run = runGradle(
        gradle_command,
        settings,
        report_dir,
        ruleset_path,
        changed_files,
        fix=not args.no_fix,
        max_workers=args.max_workers,
    )
    print(gradle_run.summary(), flush=True)
    if gradle_run.missing_jdk:
        print(f'verify.py: Gradle found no JDK for the build: {gradle_run.missing_jdk}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    # verify.py prints no review lists here. javachecks.py has not read the comments yet, so the comments can still have
    # prose findings, and the sentences of the lists change with each fix of a prose finding
    if gradle_run.failed_tasks:
        print(gradle_run.output_tail)
        return EXIT_FINDINGS

    if gradle_run.missing_tasks:
        print(f'verify.py: Gradle did not run {", ".join(gradle_run.missing_tasks)}', file=sys.stderr)
        print(gradle_run.output_tail, file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    reports = [report_dir / 'pmd.xml', report_dir / 'checkstyle.xml', report_dir / 'javac.log']
    if missing_reports := [str(report) for report in reports if not report.is_file()]:
        print(f'verify.py: Gradle wrote no {", ".join(missing_reports)}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    targets = [str(path) for path in [*sources, *pages]]
    since.extend(['--cache', str(report_dir / 'prose-cache.json')])
    report_arguments = ['--pmd', str(reports[0]), '--checkstyle', str(reports[1]), '--javac', str(reports[2])]
    return reportFindings(
        venv_python,
        [*targets, *report_arguments, *since],
        [*targets, *since],
        cache_dir,
        all_sentences=args.all_sentences,
    )


def readStdinPage(cache_dir: Path, suffix: str) -> Path:
    """Save the page on stdin in the cache directory, so the checks can read the page as a file.

    Returns:
        The path of the saved page.
    """
    page_path = cache_dir / f'stdin{suffix}'
    page_path.write_text(sys.stdin.read(), encoding='utf-8')
    return page_path


def reportFindings(
    venv_python: Path,
    check_arguments: list[str],
    list_arguments: list[str],
    cache_dir: Path,
    *,
    all_sentences: bool,
) -> int:
    """Print the findings of javachecks.py, then write the three review lists to LISTS_NAME in the cache directory.

    The path of the lists and the number of entries in each list are on the last line. On a run with findings, the count
    line of javachecks.py comes before the last line.

    Returns:
        The exit code of javachecks.py, or 2 when javachecks.py printed no count line, as after a Python exception.
    """
    checked = subprocess.run(
        [str(venv_python), str(SKILL_DIR / 'javachecks.py'), *check_arguments],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    print(checked.stdout, end='')
    if checked.returncode not in {EXIT_SUCCESS, EXIT_FINDINGS}:
        return checked.returncode

    # javachecks.py prints the count line last in every run that checked. A Python exception is also exit 1, but
    # with no count line
    # matches:
    # `4 findings, 0 warnings over 226 files`
    if not re.search(r'^\d+ findings, \d+ warnings over \d+ files$', checked.stdout, re.MULTILINE):
        print('verify.py: javachecks.py stopped before the count line of its findings', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    if checked.returncode == EXIT_SUCCESS:
        print(PASS_NOTE, flush=True)
    lists_path = cache_dir / LISTS_NAME
    counts = writeReviewLists(venv_python, list_arguments, lists_path, all_sentences=all_sentences)
    if counts is None:
        print('verify.py: javachecks.py --prose failed, so no review list was written', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN
    if checked.returncode == EXIT_SUCCESS:
        print(f'Prose review: read the {counts} in {lists_path}')
        return EXIT_SUCCESS

    # the lists are the same with or without findings. After the fix of a finding, the sentences and the lists differ
    print(f'Review lists of this failing run: {counts} in {lists_path}. Take Prose review from the next run.')
    return EXIT_FINDINGS


def writeReviewLists(venv_python: Path, arguments: list[str], lists_path: Path, *, all_sentences: bool) -> str | None:
    """Write the three lists for Prose review in SKILL.md to `lists_path`, with javachecks.py --prose.

    Args:
        venv_python: The interpreter of the lint venv, with spaCy.
        arguments: The Java sources and pages, then the --since and --cache arguments of this run.
        lists_path: The file for the lists, in the cache directory.
        all_sentences: List every entry, not only the first 1000 of each list.

    Returns:
        The number of entries in each list, such as `12 sentences, 3 pairs and 1 pronoun sentences`. None when
        javachecks.py --prose fails or prints fewer lists than LIST_UNITS.
    """
    every = ['--all-sentences'] if all_sentences else []
    listed = subprocess.run(
        [str(venv_python), str(SKILL_DIR / 'javachecks.py'), *arguments, '--prose', *every],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    # each list starts at a heading line such as `--- every sentence of every comment ... ---`
    sections: list[list[str]] = []
    for line in listed.stdout.splitlines():
        if line.startswith('--- ') and line.endswith(' ---'):
            sections.append([])
        elif sections:
            sections[-1].append(line)
    if listed.returncode != EXIT_SUCCESS or len(sections) != len(LIST_UNITS):
        return None

    lists_path.write_text(listed.stdout, encoding='utf-8')
    counts = [f'{countEntries(entries)} {unit}' for entries, unit in zip(sections, LIST_UNITS, strict=True)]
    return f'{counts[0]}, {counts[1]} and {counts[2]}'


def prepareCache(cache_dir: Path) -> Path:
    """Create the cache directory with a .gitignore of `*`, so git leaves the cache out.

    Returns:
        The cache directory.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    ignore_path = cache_dir / '.gitignore'
    if not ignore_path.exists():
        ignore_path.write_text('*\n', encoding='utf-8')
    return cache_dir


def rewrapComments(venv_python: Path, sources: list[Path], since: str | None) -> str:
    """Fill the javadoc and // comments again up to column 120 in place, with javachecks.py --rewrap.

    Returns:
        A summary: the number of files re-wrapped, or the error of javachecks.py.
    """
    since_arguments = ['--since', since] if since else []
    command = [str(venv_python), str(SKILL_DIR / 'javachecks.py'), '--rewrap', *map(str, sources), *since_arguments]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != EXIT_SUCCESS:
        return f'not run: {result.stderr.strip()}'
    return f'{len(result.stdout.splitlines())} files re-wrapped'


def readInstalledVersion() -> str:
    """Name the installed version: the plugin and the plugin commit, the stamp of install.sh, or the directory.

    Each version in the plugin cache is at `<cache>/<marketplace>/<plugin>/<commit>/skills/<skill>/`.
    """
    in_cache = len(SKILL_DIR.parents) > 4 and SKILL_DIR.parents[4].name == 'cache' and SKILL_DIR.parent.name == 'skills'
    if in_cache:
        plugin_root = SKILL_DIR.parents[1]
        return f'plugin {plugin_root.parent.name}@{plugin_root.parents[1].name} at {plugin_root.name}'
    try:
        return (SKILL_DIR / 'INSTALLED').read_text(encoding='utf-8').strip()
    except FileNotFoundError:
        return f'running from {SKILL_DIR}'


def missingVenvModules(venv_python: Path) -> list[str]:
    if not venv_python.is_file():
        return [str(venv_python)]

    missing: list[str] = []
    for module in PARSER_MODULES:
        probe = subprocess.run([str(venv_python), '-c', f'import {module}'], capture_output=True, check=False)
        if probe.returncode != 0:
            missing.append(module)
    return missing


def setupCommands(venv: Path) -> str:
    lock_path = SKILL_DIR / 'requirements-lock.txt'
    return f'    uv venv --python 3.11 {venv}\n    uv pip install --python {venv / VENV_PYTHON} -r {lock_path}'


def readGradleProperties(properties_path: Path) -> GradleSettings:
    """Read the GTNHGradle settings for the Java level and the formatter.

    GTNHGradle reads `true` and `false` with any case, and the other values of enableModernJavaSyntax exactly.

    Raises:
        PrerequisiteError: the file does not exist, enableModernJavaSyntax has an unknown value, or
            forceToolchainVersion names a JDK other than the toolchain of the level.
    """
    if not properties_path.is_file():
        raise PrerequisiteError(f'no {properties_path}. Run verify.py from the root of a GTNHGradle project')

    values: dict[str, str] = {}
    for raw_line in properties_path.read_text(encoding='utf-8').splitlines():
        if (line := raw_line.strip()) and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()

    syntax = values.get('enableModernJavaSyntax', '')
    # GTNHGradle ModernJavaSyntaxMode.fromString: an empty value is false, and true and false match with any case
    named = syntax.lower() if syntax.lower() in {'true', 'false'} else syntax
    level = next((level for level in JavaLevel if named in level.syntax_values), None)
    if level is None:
        raise PrerequisiteError(
            f'enableModernJavaSyntax = {syntax} in {properties_path} (expected jvmDowngrader, modern, jabel, true, '
            'false or no value)',
        )

    forced = values.get('forceToolchainVersion', '-1')
    if forced not in {'-1', str(level.toolchain)}:
        raise PrerequisiteError(
            f'forceToolchainVersion = {forced} in {properties_path} (expected -1 or {level.toolchain}, the toolchain '
            f'of enableModernJavaSyntax = {syntax}). The rules are tested on that toolchain only',
        )
    return GradleSettings(spotless=values.get('disableSpotless', 'false') != 'true', level=level)


def findGradlew(project_dir: Path) -> list[str]:
    """Return the command that runs the Gradle wrapper of the project.

    A wrapper with no executable bit, as in a checkout of a repository that stores gradlew with mode 644, runs through
    sh on Linux and macOS.

    Raises:
        PrerequisiteError: the project has no wrapper.
    """
    wrapper = project_dir / GRADLEW
    if not wrapper.is_file():
        raise PrerequisiteError(f'no {wrapper}. Pass --gradle to name another Gradle command')
    if sys.platform != 'win32' and not os.access(wrapper, os.X_OK):
        return ['sh', str(wrapper.absolute())]
    return [str(wrapper.absolute())]


def writeRuleset(source_paths: list[Path], report_dir: Path, level: JavaLevel) -> Path:
    """Write the PMD ruleset for NAR107: one typeIs test per sealed type of the project, and the message of the level.

    A typeIs() test is by qualified name. The name of a nested sealed type is taken as the name of the file, a dot and
    the simple name of the type, so a sealed type nested two levels deep is not tested.
    """
    # matches:
    # `public sealed interface Settlement permits Solved, Stalled {`
    # `    sealed interface Line permits Line.Text, Line.Rule {`
    # rejects:
    # `non-sealed class Stalled implements Settlement {`
    SEALED = re.compile(
        r'^(?P<indent>\s*)(?:\w+\s+)*(?<!non-)sealed\s+(?:\w+\s+)*(?:interface|class)\s+(?P<name>\w+)',
        re.MULTILINE,
    )
    PACKAGE = re.compile(r'^package\s+([\w.]+);', re.MULTILINE)
    names: list[str] = []
    java_paths = (sorted(path.rglob('*.java')) if path.is_dir() else [path] for path in source_paths)
    for java_path in (found for group in java_paths for found in group):
        source = java_path.read_text(encoding='utf-8', errors='replace')
        package = PACKAGE.search(source)
        prefix = f'{package[1]}.' if package else ''
        for declaration in SEALED.finditer(source):
            nested = bool(declaration['indent'])
            names.append(
                f'{prefix}{java_path.stem}.{declaration["name"]}' if nested else f'{prefix}{declaration["name"]}',
            )

    tests = ''.join(f" or pmd-java:typeIs('{name}')" for name in names)
    ruleset = (
        (SKILL_DIR / 'pmd-ruleset.xml')
        .read_text(encoding='utf-8')
        .replace('(: SEALED_TYPES :)', tests)
        .replace('NAR107_MESSAGE', level.nar107_message)
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    ruleset_path = report_dir / 'pmd-ruleset.xml'
    ruleset_path.write_text(ruleset, encoding='utf-8')
    return ruleset_path


def readChangedFiles(since: str, project_dir: Path) -> list[Path]:
    """List the Java source files with lines added or changed since merge-base(HEAD, since), and the untracked ones.

    Raises:
        PrerequisiteError: git fails, or there is no commit `since`.
    """
    root = Path(runGit(['rev-parse', '--show-toplevel'], project_dir).strip())
    base = runGit(['merge-base', 'HEAD', since], root).strip()
    names = [
        *runGit(['diff', '-M', '--name-only', '--diff-filter=d', base, '--', '*.java'], root).splitlines(),
        *runGit(['ls-files', '--others', '--exclude-standard', '--', '*.java'], root).splitlines(),
    ]
    return sorted({(root / name).resolve() for name in names})


def runGit(arguments: list[str], repo_path: Path) -> str:
    """Run one git command in the repository.

    Raises:
        PrerequisiteError: git exits nonzero.
    """
    result = subprocess.run(['git', '-C', str(repo_path), *arguments], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise PrerequisiteError(f'git {" ".join(arguments)} failed: {result.stderr.strip()}')
    return result.stdout


def runGradle(
    gradle_command: list[str],
    settings: GradleSettings,
    report_dir: Path,
    ruleset_path: Path,
    changed_files: list[Path] | None,
    *,
    fix: bool,
    max_workers: int,
) -> GradleRun:
    """Run spotless, compileJava and narrativeCheck in one Gradle invocation, and keep the invocation's output.

    The reports and caches of earlier runs stay, so a task whose inputs did not change is up to date. Incremental
    compilation is off in the init script, so compileJava compiles every file or none. Its output is written to
    javac.log only in a run where compileJava compiled. Under --since, Checkstyle and PMD read only the files of
    changed-files.txt.
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    files_property: list[str] = []
    if changed_files is not None:
        files_path = report_dir / 'changed-files.txt'
        files_path.write_text(''.join(f'{path}\n' for path in changed_files), encoding='utf-8')
        files_property = [f'-Pnarrative.files={files_path}']

    spotless = (['spotlessApply'] if fix else ['spotlessCheck']) if settings.spotless else []
    base_command = [
        *gradle_command,
        '--init-script',
        str(SKILL_DIR / 'narrative.init.gradle'),
        '--console=plain',
        '--continue',
        '--no-configuration-cache',
        f'--max-workers={max_workers}',
        f'-Pnarrative.skillDir={SKILL_DIR}',
        f'-Pnarrative.reportDir={report_dir}',
        f'-Pnarrative.pmdRuleset={ruleset_path}',
        *files_property,
    ]
    result = subprocess.run(
        [*base_command, *spotless, 'compileJava', 'narrativeCheck'],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    (report_dir / 'gradle.log').write_text(output, encoding='utf-8')
    # matches:
    # `> Task :compileJava`
    # rejects:
    # `> Task :compileJava UP-TO-DATE`
    if re.search(r'^> Task \S*:compileJava$', output, re.MULTILINE):
        (report_dir / 'javac.log').write_text(output, encoding='utf-8')
    elif not (report_dir / 'javac.log').is_file():
        # up to date, with no log of the run that compiled. Compile once more for the warnings
        rerun = subprocess.run([*base_command, 'compileJava', '--rerun'], capture_output=True, text=True, check=False)
        (report_dir / 'javac.log').write_text(rerun.stdout + rerun.stderr, encoding='utf-8')

    failed = sorted(
        set(re.findall(r"Execution failed for task '([^']+)'", output))
        | set(re.findall(r'^> Task (\S+) FAILED$', output, re.MULTILINE)),
    )
    ran = {task for task in CHECK_TASKS if re.search(rf'^> Task \S*:{task}(?: UP-TO-DATE)?$', output, re.MULTILINE)}
    # matches:
    # `> Cannot find a Java installation on your machine (Linux amd64) matching: {languageVersion=8, ...}`
    missing_jdk = re.search(r'Cannot find a Java installation on your machine.*', output)
    tail = '\n'.join(output.splitlines()[-40:])
    return GradleRun(
        result.returncode,
        failed,
        sorted(set(CHECK_TASKS) - ran),
        tail,
        missing_jdk[0] if missing_jdk else '',
    )


### vocabulary #########################################################################################


class PrerequisiteError(RuntimeError):
    pass


class JavaLevel(Enum):
    """A Java level of GTNHGradle: the enableModernJavaSyntax values, the toolchain, and the level's NAR107 message.

    The values and toolchains are those of ToolchainModule.computeToolchainVersion in GTNHGradle 2.0.34. A jabel build
    compiles with --release 8, so the library is that of Java 8.
    """

    JAVA_25 = (
        frozenset({'jvmDowngrader', 'modern'}),
        25,
        'Java 25',
        'default arm in a switch over an enum or sealed type. List every constant, so a missing one is a compile error',
    )
    JABEL = (
        frozenset({'jabel', 'true'}),
        17,
        'jabel: Java 17 syntax, Java 8 library',
        'default arm in a switch over an enum. List every constant, so a missing one is a compile error',
    )
    JAVA_8 = (
        frozenset({'false', ''}),
        8,
        'Java 8',
        'default arm in a switch over an enum. List every constant, and throw after the switch',
    )

    def __init__(self, syntax_values: frozenset[str], toolchain: int, summary: str, nar107_message: str) -> None:
        self.syntax_values = syntax_values
        self.toolchain = toolchain
        self.summary = summary
        self.nar107_message = nar107_message


@dataclass(frozen=True)
class GradleSettings:
    spotless: bool
    level: JavaLevel


@dataclass(frozen=True)
class GradleRun:
    exit_code: int
    failed_tasks: list[str]
    missing_tasks: list[str]
    output_tail: str
    missing_jdk: str

    def summary(self) -> str:
        if self.failed_tasks:
            return f'gradle         failed: {", ".join(self.failed_tasks)}'
        return 'gradle         spotless, compileJava, narrativeCheckstyle and narrativePmd ran'


if __name__ == '__main__':
    sys.exit(main())
