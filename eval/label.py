"""Label units in the terminal with one keypress per verdict, or re-label old gold units blind.

Each unit is shown in the unit's file context, with no label and no prediction. Keys:

    k  keep        c  cut        r  rewrite        s  skip        q  quit

A unit passes under a keep, and fails under a cut or a rewrite. After a rewrite, type the rewrite,
or press Enter. In an audit, each unit is one keypress: the audit compares pass and fail only.

The queue has the units of the split with no gold label for the whole unit, then each unit whose
gold label is older than the latest date in eval/standards.toml, newest label first.

With --audit, label.py prints a seeded random sample of gold units labelled before today, blind,
then the agreement with the earlier labels on pass or fail: Cohen's kappa and percent
agreement, per month of the earlier label, and the counts of changes from pass to fail and from
fail to pass. That
agreement is the human ceiling. Each re-label is saved as an audit label, so a changed
verdict becomes the current label.

A label of a public unit is appended to eval/units/labels.jsonl, and of a private unit to
labels.jsonl in the private store. With --dry-run, no label is saved.

When stdin is not a terminal, each answer is one line of stdin:

    $ printf 'k\\nc\\nk\\nq\\n' | uv run eval/label.py --audit --size 5 --dry-run

Usage:
    $ uv run eval/label.py
    $ uv run eval/label.py --split test --source round10-classes --limit 30
    $ uv run eval/label.py --audit
    $ uv run eval/label.py --audit --size 5 --seed trial --dry-run

Exit codes:
    0  the queue or the sample ended, or the labeller quit
    2  the units or eval/standards.toml were unusable
"""

from __future__ import annotations

import argparse
import random
import sys
import time
import tomllib
from dataclasses import replace
from pathlib import Path

from matrix import ceilingLine, summariseAgreement
from schema import (
    DATE,
    EVAL_DIR,
    PRIVATE_DIR,
    UNITS_DIR,
    Label,
    Tier,
    Unit,
    UnitFileError,
    Verdict,
    appendUnits,
    currentLabel,
    failing,
    loadUnits,
    readUnitFile,
)


if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty


STANDARDS_PATH = EVAL_DIR / 'standards.toml'
LABELS_FILE = 'labels.jsonl'
AUDIT_SEED = 'narrative-audit'
AUDIT_SIZE = 50
CONTEXT_SHOWN = 12
EXIT_SUCCESS = 0
EXIT_UNUSABLE = 2


def main() -> int:
    """Build the queue or the audit sample, label each unit, and print the agreement after an audit.

    Returns:
        0 when labelling ended, 2 when an input was unusable.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--units', type=Path, default=UNITS_DIR, help='the public unit directory')
    parser.add_argument('--private', type=Path, default=PRIVATE_DIR, help='the private store, merged when present')
    parser.add_argument('--split', choices=('dev', 'test', 'all'), default='dev')
    parser.add_argument('--source', help='only units of this origin dataset, such as round10-classes')
    parser.add_argument('--limit', type=int, help='stop after this many units')
    parser.add_argument('--audit', action='store_true', help='re-label a seeded sample of old gold units blind')
    parser.add_argument('--size', type=int, default=AUDIT_SIZE, help='the audit sample size')
    parser.add_argument('--seed', default=AUDIT_SEED, help='the audit sample seed')
    parser.add_argument('--dry-run', action='store_true', help='save no label')
    arguments = parser.parse_args()

    try:
        units = loadUnits(arguments.units, arguments.private)
        public_ids = {unit.id for path in arguments.units.glob('*.jsonl') for unit in readUnitFile(path)}
        latest_standard = readLatestStandard(STANDARDS_PATH)
    except (OSError, UnitFileError, tomllib.TOMLDecodeError, ValueError) as exc:
        print(f'label.py: {exc}', file=sys.stderr)
        return EXIT_UNUSABLE

    today = time.strftime('%Y-%m-%d')
    chosen = [
        unit
        for unit in units
        if arguments.split in ('all', unit.split.value) and arguments.source in (None, unit.origin.dataset)
    ]
    if arguments.audit:
        queue = sampleAudit(chosen, today, size=arguments.size, seed=arguments.seed)
    else:
        queue = buildQueue(chosen, latest_standard)
    queue = queue[: arguments.limit]
    print(f'{len(queue)} units to label. Keys: k keep, c cut, r rewrite, s skip, q quit')

    pairs: list[tuple[str, bool, bool]] = []
    for position, unit in enumerate(queue, start=1):
        showUnit(unit, position, len(queue))
        try:
            key = readChoice('verdict [k/c/r/s/q]:', 'kcrsq')
            if key == 'q':
                break
            if key == 's':
                continue
            label = askLabel(key, today, audit=arguments.audit)
        except EOFError:
            break
        if arguments.audit:
            earlier = currentLabel(unit, Tier.GOLD, rule=None)
            if isinstance(earlier, Label):
                pairs.append((earlier.date[:7], failing(earlier, rule=None), failing(label, rule=None)))
        if not arguments.dry_run:
            target = arguments.units if unit.id in public_ids else arguments.private
            appendUnits(target / LABELS_FILE, [replace(unit, labels=(label,))])

    if arguments.audit:
        print()
        print(f'audit of {len(pairs)} units' + (', not saved' if arguments.dry_run else ''))
        if pairs:
            print(ceilingLine(summariseAgreement(pairs)))
    return EXIT_SUCCESS


def readLatestStandard(standards_path: Path) -> str | None:
    """Read the latest date on which the labelling standard changed.

    Returns:
        The latest YYYY-MM-DD of `changes`, or None when the list is empty or the file is absent.

    Raises:
        ValueError: `changes` is not a list of YYYY-MM-DD strings.
    """
    if not standards_path.exists():
        return None
    changes = tomllib.loads(standards_path.read_text(encoding='utf-8')).get('changes', [])
    if not isinstance(changes, list) or not all(isinstance(day, str) and DATE.fullmatch(day) for day in changes):
        raise ValueError(f'{standards_path}: changes must be a list of dates (expected ["2026-10-01"])')
    return max(changes, default=None)


def buildQueue(units: list[Unit], latest_standard: str | None) -> list[Unit]:
    """Put the units without a gold label for the whole unit first, then the units with a gold label
    from before the latest standard change, newest label first.
    """
    unlabelled = []
    stale = []
    for unit in units:
        label = currentLabel(unit, Tier.GOLD, rule=None)
        if label is None:
            unlabelled.append(unit)
        elif isinstance(label, Label) and latest_standard is not None and label.date < latest_standard:
            stale.append((label.date, unit))
    unlabelled.sort(key=lambda unit: (unit.group, unit.origin.line or 0))
    stale.sort(key=lambda entry: entry[0], reverse=True)
    return [*unlabelled, *(unit for _, unit in stale)]


def sampleAudit(units: list[Unit], today: str, *, size: int, seed: str) -> list[Unit]:
    """Draw a seeded random sample of the units with a gold label for the whole unit from before today.

    A unit whose gold labels conflict has no earlier label to compare with, and is left out.

    Raises:
        Nothing.
    """
    candidates = sorted(
        (
            unit
            for unit in units
            if isinstance(label := currentLabel(unit, Tier.GOLD, rule=None), Label) and label.date < today
        ),
        key=lambda unit: unit.id,
    )
    return random.Random(seed).sample(candidates, min(size, len(candidates)))


def showUnit(unit: Unit, position: int, total: int) -> None:
    where = f'{unit.origin.file}:{unit.origin.line}' if unit.origin.file else unit.group
    shape = f'{unit.language.value} {unit.kind.value}'
    print(f'\n--- {position} of {total} · {shape} · {where} · context {unit.context_level.value}')
    if unit.context and unit.focus_line is not None:
        lines = unit.context.splitlines()
        start = max(unit.focus_line - 1 - CONTEXT_SHOWN, 0)
        for number, line in enumerate(lines[start : unit.focus_line - 1 + CONTEXT_SHOWN], start=start + 1):
            print(('>>> ' if number == unit.focus_line else '    ') + line)
    print(f'\nunit: {unit.text}')


def askLabel(key: str, today: str, *, audit: bool) -> Label:
    """Make the label for a verdict key. For a rewrite outside an audit, ask for the rewritten text.

    Raises:
        EOFError: stdin ended.
    """
    if key == 'k':
        return Label(
            verdict=Verdict.KEEP,
            rules=(),
            rewrite=None,
            labeller='user',
            tier=Tier.GOLD,
            date=today,
            audit=audit,
        )
    verdict = Verdict.CUT if key == 'c' else Verdict.REWRITE
    rewrite = readLine('rewrite (Enter to skip): ') if verdict is Verdict.REWRITE and not audit else ''
    return Label(
        verdict=verdict,
        rules=(),
        rewrite=rewrite or None,
        labeller='user',
        tier=Tier.GOLD,
        date=today,
        audit=audit,
    )


def readChoice(prompt: str, allowed: str) -> str:
    """Read one allowed key: a keypress at a terminal, or the first letter of a line otherwise.

    Raises:
        EOFError: stdin ended.
    """
    print(prompt, end=' ', flush=True)
    while True:
        key = readKey().strip().lower()[:1]
        if key and key in allowed:
            print(key)
            return key


def readKey() -> str:
    """Read one keypress at a terminal, or one line when stdin is not a terminal.

    Raises:
        EOFError: stdin ended.
    """
    if not sys.stdin.isatty():
        line = sys.stdin.readline()
        if not line:
            raise EOFError
        return line
    if sys.platform == 'win32':
        return msvcrt.getwch()
    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    try:
        tty.setcbreak(descriptor)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, saved)


def readLine(prompt: str) -> str:
    if sys.stdin.isatty():
        return input(prompt).strip()
    print(prompt, end='', flush=True)
    line = sys.stdin.readline()
    if not line:
        raise EOFError
    print(line.strip())
    return line.strip()


if __name__ == '__main__':
    sys.exit(main())
