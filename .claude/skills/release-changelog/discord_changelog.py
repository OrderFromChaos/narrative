"""Write a Discord changelog of Narrative from a JSON spec: messages with plain-text tables in code blocks.

Discord doesn't render Markdown tables, and a message has at most 2,000 characters. Each message of the spec has a lead,
an optional table, and an optional tail. A table has a header of three cells and rows of three cells. A cell is wrapped
to the width of the cell column, and a newline in a cell starts a new line, such as the lines of a bulleted list. The
messages are joined with a `=== next message ===` line, so the user can post them one at a time.

Usage:
    python3 discord_changelog.py SPEC.json OUT.md [--prose PROSE.md]

    $ python3 discord_changelog.py examples/2b7637d.json /tmp/changelog.md --prose /tmp/changelog_prose.md
    message 1: 1477 characters
    message 2: 1574 characters
    message 3: 1444 characters
    message 4: 1735 characters

--prose writes the text outside the code blocks to PROSE.md. Step 6 of SKILL.md checks PROSE.md.

Exit codes:
    0  each message has at most 2,000 characters
    1  a message has more than 2,000 characters
    2  the spec can't be read
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any


COLUMN_WIDTHS = (16, 27, 27)
MESSAGE_LIMIT = 2000
MESSAGE_BREAK = '\n\n\n=== next message ===\n\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Write a Discord changelog from a JSON spec.')
    parser.add_argument('spec', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--prose', type=Path, help='write the text outside the code blocks to this file')
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        print(f'discord_changelog.py: {args.spec}: {exc}', file=sys.stderr)
        return 2

    messages = [renderMessage(message) for message in spec['messages']]
    args.out.write_text(MESSAGE_BREAK.join(messages), encoding='utf-8')
    if args.prose is not None:
        prose = re.sub(r'```.*?```', '', '\n\n'.join(messages), flags=re.DOTALL)
        args.prose.write_text(prose, encoding='utf-8')

    too_long = 0
    for number, message in enumerate(messages, start=1):
        print(f'message {number}: {len(message)} characters')
        too_long += len(message) > MESSAGE_LIMIT
    return 1 if too_long else 0


def renderMessage(message: dict[str, Any]) -> str:
    parts = [message['lead']]
    if 'table' in message:
        parts.append(renderTable(message['table']['header'], message['table']['rows']))
    if 'tail' in message:
        parts.append(message['tail'])
    return '\n'.join(parts)


def renderTable(header: list[str], rows: list[list[str]]) -> str:
    """Render a table of three columns as plain text in a code block. A rule line separates two rows."""
    top = '=+='.join('=' * width for width in COLUMN_WIDTHS)
    rule = '-+-'.join('-' * width for width in COLUMN_WIDTHS)
    lines = [joinCells([[cell] for cell in header])[0], top]
    for index, row in enumerate(rows):
        if index:
            lines.append(rule)
        lines.extend(joinCells([wrapCell(cell, width) for cell, width in zip(row, COLUMN_WIDTHS, strict=True)]))
    return '```\n' + '\n'.join(lines) + '\n```'


def wrapCell(cell: str, width: int) -> list[str]:
    wrapped: list[str] = []
    for part in cell.split('\n'):
        wrapped.extend(textwrap.wrap(part, width) or [''])
    return wrapped


def joinCells(cells: list[list[str]]) -> list[str]:
    """Join the wrapped lines of three cells into the lines of one table row."""
    height = max(len(lines) for lines in cells)
    return [
        ' | '.join(
            (lines[index] if index < len(lines) else '').ljust(width)
            for lines, width in zip(cells, COLUMN_WIDTHS, strict=True)
        ).rstrip()
        for index in range(height)
    ]


if __name__ == '__main__':
    sys.exit(main())
