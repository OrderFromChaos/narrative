"""Run verify.py on the three fixture projects and compare each fixture file with the file's expected code.

Each project is one Java level of GTNHGradle: this directory for Java 25, java8/ for Java 8 and jabel/ for jabel. The
fixtures of a project are the files of its fixtures/ directory, and in java8/ and jabel/ also the directories and files
of ./fixtures that the project's shared-fixtures.txt names, one per line.

For a file under fixtures/<code>/ whose name starts with Flagged, the expected codes are that code
alone. For a file whose name starts with Clean, no code is expected. A warning counts as its code.

Usage:
    $ python3 tests/run_fixtures.py --gradle ~/.gradle/wrapper/dists/gradle-9.4.0-bin/<hash>/gradle-9.4.0/bin/gradle
    $ python3 tests/run_fixtures.py --gradle /usr/bin/gradle --venv ~/.local/share/narrative/lintenv

Exit codes:
    0  every fixture file of every project gave its expected codes
    1  at least one fixture file did not
    2  verify.py did not run the checks on a project
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
VERIFY_PATH = TESTS_DIR.parents[2] / 'skills' / 'gtnh' / 'verify.py'
# the fixture project of each Java level, in the order of the runs
PROJECT_DIRS = (TESTS_DIR, TESTS_DIR / 'java8', TESTS_DIR / 'jabel')
SHARED_LIST = 'shared-fixtures.txt'
EXIT_SUCCESS = 0
EXIT_MISMATCH = 1
EXIT_NOT_RUN = 2


def main() -> int:
    """Run verify.py from each fixture project, then print each fixture file that has the wrong codes."""
    parser = argparse.ArgumentParser(description='Check every fixture file against its expected code.')
    parser.add_argument('--gradle', required=True, help='the Gradle command, as verify.py --gradle takes it')
    parser.add_argument('--venv', type=Path, help='the lint venv, as verify.py --venv takes it')
    args = parser.parse_args()

    exit_codes = [checkProject(project_dir, args.gradle, args.venv) for project_dir in PROJECT_DIRS]
    if EXIT_NOT_RUN in exit_codes:
        return EXIT_NOT_RUN
    return EXIT_MISMATCH if EXIT_MISMATCH in exit_codes else EXIT_SUCCESS


def checkProject(project_dir: Path, gradle: str, venv: Path | None) -> int:
    """Run verify.py from one fixture project, and print each of its fixture files that has the wrong codes.

    Returns:
        0 when every fixture file has its expected codes, 1 when one does not, 2 when verify.py did not run the checks.
    """
    targets = fixtureTargets(project_dir)
    venv_arguments = ['--venv', str(venv)] if venv else []
    target_arguments = [os.path.relpath(target, project_dir) for target in targets]
    # with --no-fix there is no re-wrap, and the NAR125 fixtures stay ragged
    command = [sys.executable, str(VERIFY_PATH), '--gradle', gradle, *venv_arguments, '--no-fix', *target_arguments]
    result = subprocess.run(command, cwd=project_dir, capture_output=True, text=True, check=False)
    name = project_dir.relative_to(TESTS_DIR).as_posix() if project_dir != TESTS_DIR else 'tests'
    if result.returncode not in {EXIT_SUCCESS, EXIT_MISMATCH}:
        print(f'{name}: verify.py exited {result.returncode}')
        print(result.stdout + result.stderr)
        return EXIT_NOT_RUN

    reported = readReportedCodes(result.stdout)
    fixture_paths = sorted(
        path for target in targets for path in ([target] if target.is_file() else target.rglob('*.java'))
    )
    mismatches = []
    for fixture_path in fixture_paths:
        expected = {fixture_path.parent.name} if fixture_path.stem.startswith('Flagged') else set()
        relative = Path(os.path.relpath(fixture_path, project_dir)).as_posix()
        found = reported.get(relative, set())
        if found != expected:
            mismatches.append(f'{name}: {relative}: expected {sorted(expected)}, found {sorted(found)}')
    for mismatch in mismatches:
        print(mismatch)
    print(f'{name}: {len(mismatches)} of {len(fixture_paths)} fixture files with the wrong codes')
    return EXIT_MISMATCH if mismatches else EXIT_SUCCESS


def fixtureTargets(project_dir: Path) -> list[Path]:
    """List the fixture directories and files of a project: its fixtures/, then the entries of its shared list."""
    shared_path = project_dir / SHARED_LIST
    if not shared_path.is_file():
        return [project_dir / 'fixtures']

    lines = shared_path.read_text(encoding='utf-8').splitlines()
    entries = [line for line in lines if line and not line.startswith('#')]
    return [project_dir / 'fixtures', *(TESTS_DIR / 'fixtures' / entry for entry in entries)]


def readReportedCodes(verify_output: str) -> dict[str, set[str]]:
    """Collect the codes of each file from the finding lines of verify.py.

    Returns:
        The codes by file path, relative to the fixture project. verify.py prints the paths in that form.
    """
    # matches:
    # `fixtures/NAR101/Flagged.java:6: NAR101 method above its first caller in this class`
    # `fixtures/NAR119/Flagged.java:7: warning NAR119 FIXME in a comment`  # noqa: NAR010
    FINDING = re.compile(r'^(?P<path>\S+\.java):\d+: (?:warning )?(?P<code>NAR\d{3}(?:-[a-z]+)?) ')
    reported: dict[str, set[str]] = defaultdict(set)
    for line in verify_output.splitlines():
        if finding := FINDING.match(line):
            reported[finding['path']].add(finding['code'])
    return reported


if __name__ == '__main__':
    sys.exit(main())
