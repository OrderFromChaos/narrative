"""Run javachecks.py --rewrap on each case file and compare the result with the expected file.

For tests/rewrap/<Name>.java the expected result is tests/rewrap/<Name>.expected.java. The re-wrap
runs on a copy in a temporary directory, twice. After the second run, the file must be the same as
after the first.

Usage, with the interpreter of the lint venv. javachecks.py imports spaCy from that venv:
    $ ~/.local/share/narrative/lintenv/bin/python tests/run_rewrap.py

Exit codes:
    0  every case gave its expected file
    1  at least one case did not
"""

from __future__ import annotations

import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
JAVACHECKS_PATH = TESTS_DIR.parents[2] / 'skills' / 'java' / 'javachecks.py'
EXIT_SUCCESS = 0
EXIT_MISMATCH = 1


def main() -> int:
    """Re-wrap a copy of each case twice, then print each case whose result differs from the expected file."""
    cases = sorted(path for path in (TESTS_DIR / 'rewrap').glob('*.java') if not path.name.endswith('.expected.java'))
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as work_dir:
        for case_path in cases:
            copy_path = Path(work_dir) / case_path.name
            shutil.copyfile(case_path, copy_path)
            rewrapFile(copy_path)
            once = copy_path.read_text(encoding='utf-8')
            rewrapFile(copy_path)
            expected = case_path.with_name(f'{case_path.stem}.expected.java').read_text(encoding='utf-8')
            if once != expected:
                diff = difflib.unified_diff(expected.splitlines(), once.splitlines(), 'expected', 'result', lineterm='')
                failures.append(f'{case_path.name}: the result differs from the expected file\n' + '\n'.join(diff))
            elif copy_path.read_text(encoding='utf-8') != once:
                failures.append(f'{case_path.name}: a second re-wrap changed the file')
    for failure in failures:
        print(failure)
    print(f'{len(failures)} of {len(cases)} cases wrong')
    return EXIT_MISMATCH if failures else EXIT_SUCCESS


def rewrapFile(java_path: Path) -> None:
    subprocess.run([sys.executable, str(JAVACHECKS_PATH), '--rewrap', str(java_path)], check=True, capture_output=True)


if __name__ == '__main__':
    sys.exit(main())
