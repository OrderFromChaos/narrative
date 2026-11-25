"""Check the page checks of core/tools/wording.py against expected files.

Each fixture is a page in core/tests/pages/, and each expected file has the name of the page and another suffix:
- `<page>.findings`: the NAR028 findings of wording.checkPage(), one `line: code detail` per line.
- `<page>.sections`: the section list of wording.listSections(), with the name of the page in place of the path.

Give each page a `.findings` file, a `.sections` file, or both. --update writes the expected files from the current
output, for a fixture whose output you have read and checked.

Usage:
    $ python3 core/tests/run_pages.py
    $ python3 core/tests/run_pages.py --update

Exit codes:
    0  every check passed
    1  at least one check failed, or a page has no expected file
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = TESTS_DIR / 'pages'
sys.path.insert(0, str(TESTS_DIR.parent / 'tools'))

import wording  # noqa: E402


# the codes of the page checks that the fixtures cover. The other wording codes have Java fixtures
CODES = frozenset({'NAR028'})
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--update', action='store_true', help='write the expected files from the current output')
    args = parser.parse_args()

    failures = 0
    pages = sorted(path for path in FIXTURES_DIR.iterdir() if wording.isPage(path))
    for page in pages:
        outputs = {
            '.findings': [
                f'{finding.line}: {finding.code} {finding.detail}'
                for finding in wording.checkPage(page)
                if finding.code in CODES
            ],
            '.sections': [
                entry.replace(str(page), page.name, 1) for entry in wording.listSections(page, changed_lines=None)
            ],
        }
        expected_paths = [page.with_name(page.name + suffix) for suffix in outputs]
        if args.update:
            for suffix, lines in outputs.items():
                page.with_name(page.name + suffix).write_text(''.join(f'{line}\n' for line in lines), encoding='utf-8')
            continue
        if not any(path.is_file() for path in expected_paths):
            print(f'FAIL {page.name}: no .findings or .sections file')
            failures += 1
            continue
        for suffix, lines in outputs.items():
            expected_path = page.with_name(page.name + suffix)
            if not expected_path.is_file():
                continue
            expected = expected_path.read_text(encoding='utf-8').splitlines()
            if lines == expected:
                print(f'ok   {expected_path.name}')
                continue
            failures += 1
            print(f'FAIL {expected_path.name}')
            diff = difflib.unified_diff(expected, lines, 'expected', 'actual', lineterm='')
            print('\n'.join(f'     {line}' for line in diff))

    if args.update:
        print(f'wrote the expected files of {len(pages)} pages')
        return EXIT_SUCCESS
    print(f'\n{failures} failed' if failures else f'\nall {len(pages)} pages passed')
    return EXIT_FAILURE if failures else EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
