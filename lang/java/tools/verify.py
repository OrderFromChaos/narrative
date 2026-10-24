"""Run the narrative-gtnh toolchain over a GTNH mod, or the prose checks over pages.

Use this instead of calling the tools by hand. A missing tool, report or JDK is exit 2, so a pass
means every check ran.

The project is the current directory, a Gradle build with GTNHGradle. First, javachecks.py --rewrap
re-wraps ragged javadoc and whole-line // comments over 120 columns, unless --no-fix is given. Under
--since, only changed lines are re-wrapped. Then, in one Gradle run, the code
is formatted (spotlessApply, or spotlessCheck with --no-fix), compiled with the raw-type and
unchecked warnings of javac, and checked with Checkstyle and PMD and the configs beside this script.
Those tasks come from the init script narrative.init.gradle, so no project file changes. javachecks.py then reads the
comments, runs the prose checks, and merges the three reports into one list of findings.

A Markdown, HTML or plain text file named on the command line gets the prose checks of
javachecks.py, in the same list of findings as the Java sources. A Gradle project is required only
when Java sources are checked.

After the checks, the output ends with three review lists over the Java sources and the pages: every
sentence, every subject that cannot act paired with the subject's verb, and every sentence with a
pronoun. On a run with findings, the lists come after the findings, and the count of findings is the
last line. verify.py prints no lists on exit 2, or after a Gradle failure. Without --since, each
list stops after 1000 entries, with the command for the next 1000.

Usage:
    $ python3 verify.py                          # every src/*/java of the mod in the current directory
    $ python3 verify.py --since origin/dev       # only lines changed since merge-base(HEAD, origin/dev)
    $ python3 verify.py --no-fix                 # no re-wrap, and spotlessCheck in place of spotlessApply
    $ python3 verify.py src/main/java/com/example/gui
    $ python3 verify.py README.md docs/page.html

Exit codes:
    0  every check passed. Warnings may be printed
    1  at least one finding, or the code does not compile or is not formatted
    2  the toolchain, gradle.properties, gradlew or a report is missing, the project is not Java 25,
       or nothing was checked
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


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
# the GTNHGradle enableModernJavaSyntax values for Java 25 with the modern library
JAVA_25_SYNTAX = frozenset({'jvmDowngrader', 'modern'})
REPORT_DIR = Path('build/narrative')
CHECK_TASKS = ('narrativeCheckstyle', 'narrativePmd')
PASS_NOTE = 'A pass is no evidence about the rules that no check implements. Read the lists below.'
FAILING_RUN_HEADING = (
    '\n=== review lists from a failing run. Fix the findings above, then read the lists of the next run ==='
)
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
    args = parser.parse_args()
    print(f'narrative-gtnh skill: {readInstalledVersion()}', flush=True)

    venv_python = (args.venv / VENV_PYTHON).absolute()
    if missing := missingVenvModules(venv_python):
        print(f'verify.py: {", ".join(missing)} missing from {args.venv}. Set the venv up with:', file=sys.stderr)
        print(setupCommands(args.venv), file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    pages = [path for path in args.paths if path.suffix.lower() in PROSE_SUFFIXES]
    java_sources = [path for path in args.paths if path.suffix.lower() not in PROSE_SUFFIXES]
    if pages and not java_sources:
        page_targets = [str(page) for page in pages]
        return reportFindings(venv_python, page_targets, page_targets, all_sentences=args.all_sentences)

    project_dir = Path.cwd()
    try:
        settings = readGradleProperties(project_dir / 'gradle.properties')
        gradle_command = args.gradle.split() if args.gradle else [str(findGradlew(project_dir))]
    except PrerequisiteError as exc:
        print(f'verify.py: {exc}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    report_dir = project_dir / REPORT_DIR
    sources = java_sources or sorted((project_dir / 'src').glob('*/java')) or [project_dir / 'src' / 'main' / 'java']
    try:
        changed_files = readChangedFiles(args.since, project_dir) if args.since else None
    except PrerequisiteError as exc:
        print(f'verify.py: {exc}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    if changed_files is not None and not changed_files:
        print(f'verify.py: no line changed since {args.since}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    # before Gradle, because splitting a // comment moves every later line of the file, and Gradle must see
    # the final lines
    if not args.no_fix:
        print(f'rewrap         {rewrapComments(venv_python, sources, args.since)}', flush=True)

    ruleset_path = writeRuleset(sources, report_dir)
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

    # verify.py prints no review lists here. javachecks.py has not read the comments yet, so the comments can
    # still have prose findings, and the sentences of the lists change with each fix of a prose finding
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
    since = ['--since', args.since] if args.since else []
    since.extend(['--cache', str(report_dir / 'prose-cache.json')])
    report_arguments = ['--pmd', str(reports[0]), '--checkstyle', str(reports[1]), '--javac', str(reports[2])]
    return reportFindings(
        venv_python,
        [*targets, *report_arguments, *since],
        [*targets, *since],
        all_sentences=args.all_sentences,
    )


def reportFindings(
    venv_python: Path,
    check_arguments: list[str],
    list_arguments: list[str],
    *,
    all_sentences: bool,
) -> int:
    """Print the findings of javachecks.py, then the three review lists.

    On a run with findings, the lists come under FAILING_RUN_HEADING, and the count line of javachecks.py
    comes last.

    Returns:
        The exit code of javachecks.py.
    """
    checked = subprocess.run(
        [str(venv_python), str(SKILL_DIR / 'javachecks.py'), *check_arguments],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    if checked.returncode == EXIT_SUCCESS:
        print(checked.stdout, end='')
        print(PASS_NOTE, flush=True)
        printReviewLists(venv_python, list_arguments, all_sentences=all_sentences)
        return EXIT_SUCCESS

    if checked.returncode != EXIT_FINDINGS:
        print(checked.stdout, end='')
        return checked.returncode

    # the last line of javachecks.py has the count of findings. verify.py prints that line last, after the lists
    *finding_lines, count_line = checked.stdout.splitlines() or ['']
    print('\n'.join(finding_lines))
    print(FAILING_RUN_HEADING, flush=True)
    printReviewLists(venv_python, list_arguments, all_sentences=all_sentences)
    print(f'\n{count_line}')
    return EXIT_FINDINGS


def printReviewLists(venv_python: Path, arguments: list[str], *, all_sentences: bool) -> None:
    """Print the three lists for Prose review in SKILL.md, with javachecks.py --prose.

    Args:
        venv_python: The interpreter of the lint venv, with spaCy.
        arguments: The Java sources and pages, then the --since and --cache arguments of this run.
        all_sentences: List every entry, not only the first 1000 of each list.
    """
    every = ['--all-sentences'] if all_sentences else []
    subprocess.run([str(venv_python), str(SKILL_DIR / 'javachecks.py'), *arguments, '--prose', *every], check=False)


def rewrapComments(venv_python: Path, sources: list[Path], since: str | None) -> str:
    """Re-wrap ragged javadoc and long // comments in place, with javachecks.py --rewrap.

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
    """Return the commit and date that install.sh wrote to INSTALLED beside this script."""
    stamp = SKILL_DIR / 'INSTALLED'
    try:
        return stamp.read_text(encoding='utf-8').strip()
    except FileNotFoundError:
        return f'not installed by install.sh, running from {SKILL_DIR}'


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
    """Read the GTNHGradle settings for the language level and the formatter.

    Raises:
        PrerequisiteError: the file does not exist, or the project is not set to Java 25.
    """
    if not properties_path.is_file():
        raise PrerequisiteError(f'no {properties_path}. Run verify.py from the root of a GTNHGradle project')

    values: dict[str, str] = {}
    for raw_line in properties_path.read_text(encoding='utf-8').splitlines():
        if (line := raw_line.strip()) and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            values[key.strip()] = value.strip()

    syntax = values.get('enableModernJavaSyntax', 'false')
    if syntax not in JAVA_25_SYNTAX:
        raise PrerequisiteError(
            f'enableModernJavaSyntax = {syntax} in {properties_path} (expected jvmDowngrader or modern). '
            'narrative-gtnh checks Java 25 projects only',
        )
    forced = values.get('forceToolchainVersion', '-1')
    if forced not in {'-1', '25'}:
        raise PrerequisiteError(f'forceToolchainVersion = {forced} in {properties_path} (expected -1 or 25)')
    return GradleSettings(spotless=values.get('disableSpotless', 'false') != 'true')


def findGradlew(project_dir: Path) -> Path:
    """Return the Gradle wrapper of the project.

    Raises:
        PrerequisiteError: the project has no wrapper.
    """
    wrapper = project_dir / GRADLEW
    if not wrapper.is_file():
        raise PrerequisiteError(f'no {wrapper}. Pass --gradle to name another Gradle command')
    return wrapper.absolute()


def writeRuleset(source_paths: list[Path], report_dir: Path) -> Path:
    """Write the PMD ruleset with one typeIs test per sealed type of the project for NAR107.

    A typeIs() test is by qualified name. The name of a nested sealed type is taken as the name of
    the file, a dot and the simple name of the type, so a sealed type nested two levels deep is not tested.
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
    ruleset = (SKILL_DIR / 'pmd-ruleset.xml').read_text(encoding='utf-8').replace('(: SEALED_TYPES :)', tests)
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

    The reports and caches of earlier runs stay, so a task whose inputs did not change is up to date.
    Incremental compilation is off in the init script, so compileJava compiles every file or none. Its
    output is written to javac.log only in a run where compileJava compiled. Under --since, Checkstyle
    and PMD read only the files of changed-files.txt.
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


@dataclass(frozen=True)
class GradleSettings:
    spotless: bool


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
