"""Run verify.py on the fixture project and compare each fixture file with the file's expected code.

For a file under fixtures/<code>/ whose name starts with Flagged, the expected codes are that code
alone. For a file whose name starts with Clean, no code is expected. A warning counts as its code.

Usage:
    $ python3 tests/run_fixtures.py --gradle ~/.gradle/wrapper/dists/gradle-9.4.0-bin/<hash>/gradle-9.4.0/bin/gradle
    $ python3 tests/run_fixtures.py --gradle /usr/bin/gradle --venv ~/.local/share/narrative/lintenv

Exit codes:
    0  every fixture file gave its expected codes
    1  at least one fixture file did not
    2  verify.py did not run the checks
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
VERIFY_PATH = TESTS_DIR.parents[2] / 'skills' / 'java' / 'verify.py'
EXIT_SUCCESS = 0
EXIT_MISMATCH = 1
EXIT_NOT_RUN = 2


def main() -> int:
    """Run verify.py from the fixture project, then print each fixture file that has the wrong codes."""
    parser = argparse.ArgumentParser(description='Check every fixture file against its expected code.')
    parser.add_argument('--gradle', required=True, help='the Gradle command, as verify.py --gradle takes it')
    parser.add_argument('--venv', type=Path, help='the lint venv, as verify.py --venv takes it')
    args = parser.parse_args()

    venv = ['--venv', str(args.venv)] if args.venv else []
    # with --no-fix there is no re-wrap, and the NAR125 fixtures stay ragged
    command = [sys.executable, str(VERIFY_PATH), '--gradle', args.gradle, *venv, '--no-fix', 'fixtures']
    result = subprocess.run(command, cwd=TESTS_DIR, capture_output=True, text=True, check=False)
    if result.returncode not in {EXIT_SUCCESS, EXIT_MISMATCH}:
        print(result.stdout + result.stderr)
        return EXIT_NOT_RUN

    reported = readReportedCodes(result.stdout)
    mismatches = []
    for fixture_path in sorted((TESTS_DIR / 'fixtures').glob('*/*.java')):
        expected = {fixture_path.parent.name} if fixture_path.stem.startswith('Flagged') else set()
        found = reported.get(fixture_path.relative_to(TESTS_DIR).as_posix(), set())
        if found != expected:
            mismatches.append(
                f'{fixture_path.relative_to(TESTS_DIR)}: expected {sorted(expected)}, found {sorted(found)}',
            )
    for mismatch in mismatches:
        print(mismatch)
    fixture_count = len(list((TESTS_DIR / 'fixtures').glob('*/*.java')))
    print(f'{len(mismatches)} of {fixture_count} fixture files with the wrong codes')
    return EXIT_MISMATCH if mismatches else EXIT_SUCCESS


def readReportedCodes(verify_output: str) -> dict[str, set[str]]:
    """Collect the codes of each file from the finding lines of verify.py.

    Returns:
        The codes by file path, relative to the fixture project. verify.py prints the paths in that form.
    """
    # matches:
    # `fixtures/NAR101/Flagged.java:6: NAR101 method above its first caller in this class`
    # `fixtures/NAR119/Flagged.java:7: warning NAR119 FIXME in a comment`  # noqa: NAR010
    FINDING = re.compile(r'^(?P<path>\S+\.java):\d+: (?:warning )?(?P<code>NAR\d{3}) ')
    reported: dict[str, set[str]] = defaultdict(set)
    for line in verify_output.splitlines():
        if finding := FINDING.match(line):
            reported[finding['path']].add(finding['code'])
    return reported


if __name__ == '__main__':
    sys.exit(main())
