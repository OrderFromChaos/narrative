"""Run javachecks.py --prose on each case file and compare the subject-verb pairs with the expected file.

For tests/review/<Name>.java the expected pairs are in tests/review/<Name>.pairs, one `File.java:line: 'subject verb'`
per line.

Run the script with the interpreter of the lint venv, because javachecks.py imports spaCy from that venv:
    $ ~/.local/share/narrative/lintenv/bin/python tests/run_review.py

Exit codes:
    0  every case gave its expected pairs
    1  at least one case did not
"""

from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
JAVACHECKS_PATH = TESTS_DIR.parents[2] / 'skills' / 'gtnh' / 'javachecks.py'
PAIRS_HEADER = '--- every subject that cannot act'
EXIT_SUCCESS = 0
EXIT_MISMATCH = 1


def main() -> int:
    """Print each case whose pairs differ from the expected file."""
    cases = sorted((TESTS_DIR / 'review').glob('*.java'))
    failures: list[str] = []
    for case_path in cases:
        expected = case_path.with_suffix('.pairs').read_text(encoding='utf-8').splitlines()
        result = reviewPairs(case_path)
        if result != expected:
            diff = difflib.unified_diff(expected, result, 'expected', 'result', lineterm='')
            failures.append(f'{case_path.name}: the pairs differ from the expected file\n' + '\n'.join(diff))
    for failure in failures:
        print(failure)
    print(f'{len(failures)} of {len(cases)} cases wrong')
    return EXIT_MISMATCH if failures else EXIT_SUCCESS


def reviewPairs(java_path: Path) -> list[str]:
    """Run javachecks.py --prose on one file, and read the list of pairs, with the path cut to the file name.

    Returns:
        The lines of the pair list, or an empty list for `(none)`.
    """
    completed = subprocess.run(
        [sys.executable, str(JAVACHECKS_PATH), '--prose', '--all-sentences', str(java_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    lines = completed.stdout.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(PAIRS_HEADER)) + 1
    end = next(index for index in range(start, len(lines)) if lines[index].startswith('---'))
    return [line.replace(f'{java_path.parent}/', '') for line in lines[start:end] if line != '(none)']


if __name__ == '__main__':
    sys.exit(main())
