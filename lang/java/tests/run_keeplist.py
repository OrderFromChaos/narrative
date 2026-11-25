"""Check the keep-list of javachecks.py on a copy of the NAR120 fixture, with no Gradle run.

The copy is in a temporary directory outside git, so the keep-list is given with --keep-list. The steps:
1. With no entry, the NAR120 finding is printed.
2. --keep writes the entry and the reason.
3. With the entry, the finding is not printed, and the count line counts the finding as kept.
4. After a blank line above the method, the entry still matches.
5. After a change to the text of the line, the finding is printed again.

Run the script with the interpreter of the lint venv, because javachecks.py imports spaCy from that venv:
    $ ~/.local/share/narrative/lintenv/bin/python tests/run_keeplist.py

Exit codes:
    0  every step gave its expected output
    1  at least one step did not
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
JAVACHECKS_PATH = TESTS_DIR.parents[2] / 'skills' / 'gtnh' / 'javachecks.py'
FIXTURE_PATH = TESTS_DIR / 'fixtures' / 'NAR120' / 'Flagged.java'
# the line of the fixture with the return contract
CONTRACT_LINE = 9
CONTRACT_TEXT = '// returns 0 for an empty list'
# the count line of a run with the NAR120 finding printed, and of a run with the finding kept
PRINTED = '1 findings, 0 warnings, 0 kept over 1 files'
KEPT = '0 findings, 0 warnings, 1 kept over 1 files'
EXIT_SUCCESS = 0
EXIT_MISMATCH = 1


def main() -> int:
    """Run each step on a copy of the fixture, then print each step whose output differs from the expectation."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as work_name:
        work_dir = Path(work_name)
        java_path = work_dir / 'Flagged.java'
        keep_path = work_dir / 'narrative-keep'
        shutil.copyfile(FIXTURE_PATH, java_path)
        check = ['Flagged.java', '--keep-list', str(keep_path)]

        output = runJavachecks(work_dir, check)
        expect(failures, 'no entry', output, code='NAR120', count_line=PRINTED)

        keep = ['--keep', f'Flagged.java:{CONTRACT_LINE}:NAR120', '--reason', 'kept by the test', '--keep-list']
        runJavachecks(work_dir, [*keep, str(keep_path)])
        entries = keep_path.read_text(encoding='utf-8') if keep_path.is_file() else ''
        if entries != f'# kept by the test\nFlagged.java\tNAR120\t{CONTRACT_TEXT}\n':
            failures.append(f'--keep wrote {entries!r}')

        output = runJavachecks(work_dir, check)
        expect(failures, 'with the entry', output, code=None, count_line=KEPT)

        source = java_path.read_text(encoding='utf-8')
        java_path.write_text(source.replace('\n\n    public', '\n\n\n    public', 1), encoding='utf-8')
        output = runJavachecks(work_dir, check)
        expect(failures, 'after the line moved', output, code=None, count_line=KEPT)

        source = java_path.read_text(encoding='utf-8')
        java_path.write_text(source.replace(CONTRACT_TEXT, '// returns 0 when the list is empty'), encoding='utf-8')
        output = runJavachecks(work_dir, check)
        expect(failures, 'after the line changed', output, code='NAR120', count_line=PRINTED)

    for failure in failures:
        print(failure)
    print(f'{len(failures)} failed steps')
    return EXIT_MISMATCH if failures else EXIT_SUCCESS


def runJavachecks(work_dir: Path, arguments: list[str]) -> str:
    command = [sys.executable, str(JAVACHECKS_PATH), *arguments]
    return subprocess.run(command, cwd=work_dir, capture_output=True, text=True, check=False).stdout


def expect(failures: list[str], step: str, output: str, *, code: str | None, count_line: str) -> None:
    """Add a failure when the NAR120 finding is printed against `code`, or when the count line differs."""
    if (' NAR120 ' in output) != (code is not None):
        failures.append(f'{step}: expected {code or "no finding"}, output:\n{output}')
    if count_line not in output.splitlines():
        failures.append(f'{step}: expected the count line {count_line!r}, output:\n{output}')


if __name__ == '__main__':
    sys.exit(main())
