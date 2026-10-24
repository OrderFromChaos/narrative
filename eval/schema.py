"""Read and write the units of the eval set, one JSONL record per unit.

A unit is one comment, one docstring, or one sentence of prose, with up to 15 lines of the unit's
file on each side. A record, indented:

    {
        "id": "7bfae996c5f7f009",
        "text": "in the order they were read",
        "context": "",
        "focus_line": null,
        "context_level": "none",
        "language": "python",
        "kind": "comment",
        "group": "seeds.md:9",
        "origin": {
            "dataset": "round10-seeds",
            "file": null,
            "line": null,
            "arm": null,
            "ref": "benchmark/round10/seeds.md:9"
        },
        "split": "dev",
        "confidential": false,
        "labels": [
            {
                "verdict": "rewrite",
                "rules": [],
                "rewrite": "in read order",
                "labeller": "user",
                "tier": "gold",
                "date": "2026-10-01",
                "judged": [],
                "partial": false,
                "audit": false,
                "note": null
            }
        ]
    }

`id` is a hash of the normalised text and the context file, so two copies of one comment in one
file are one unit. `split` comes from a hash of `group`, so the units of one file, PR or session
are all in dev or all in test.

Label fields:
    judged   the rule codes the label rules on. A code in `judged` and absent from `rules` is a
             negative for that code.
    partial  the verdict covers only the codes in `judged`, so the label is left out of every
             matrix that is not for one of those codes
    audit    the label is a blind re-label of a unit that already had a gold label

`context_level` is how much of the unit's surroundings the predictor and the labeller see:
    none     the unit alone
    snippet  a few lines chosen for display, such as a rated snippet or the hunks of a diff
    window   up to 15 lines on each side of the unit, from the whole file
    repo     the repository at the unit's commit

A unit passes under a keep label, and fails under a cut or a rewrite. In one tier, the current
label of a unit is the unit's latest label in that tier. When the unit passes under one label of the
latest date and fails under another, the unit has a conflict and is left out of the matrix.

Public units are under eval/units/. The private store has the same layout. The `runs/` and
`reports/` directories of the private store contain no units. Every unit of a file under `work/`
in the private store is confidential, even where a record has `confidential: false`.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import NewType


EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
UNITS_DIR = EVAL_DIR / 'units'
REPORTS_DIR = EVAL_DIR / 'reports'
PRIVATE_DIR = Path.home() / '.local' / 'share' / 'narrative' / 'eval-private'
PRIVATE_SKIPPED_DIRS = frozenset({'runs', 'reports'})
CONFIDENTIAL_DIR = 'work'
DEV_SHARE = 0.6


def loadUnits(units_dir: Path, private_dir: Path | None) -> list[Unit]:
    """Read every public unit file, then the private store when the store exists, and merge by id.

    Raises:
        UnitFileError: A record lacks a field, or has a value of the wrong type.
    """
    units = [unit for path in sorted(units_dir.glob('*.jsonl')) for unit in readUnitFile(path)]
    if private_dir is not None and private_dir.is_dir():
        for path in sorted(private_dir.rglob('*.jsonl')):
            parts = path.relative_to(private_dir).parts
            if PRIVATE_SKIPPED_DIRS.intersection(parts):
                continue
            units.extend(readUnitFile(path, confidential=parts[0] == CONFIDENTIAL_DIR))
    return mergeUnits(units)


def readUnitFile(unit_path: Path, *, confidential: bool = False) -> list[Unit]:
    """Parse one unit file. With `confidential`, every unit of the file is marked confidential.

    Raises:
        UnitFileError: A line is not JSON, or a record is malformed.
    """
    units = []
    for number, line in enumerate(unit_path.read_text(encoding='utf-8').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            unit = parseUnit(json.loads(line))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise UnitFileError(f'{unit_path}:{number}: {exc!r}') from exc
        units.append(replace(unit, confidential=True) if confidential else unit)
    return units


def mergeUnits(units: Iterable[Unit]) -> list[Unit]:
    """Collapse units with one id into one unit with the labels of all of them, in first-seen order.

    A label that appears in two records is kept once. A unit is confidential when any record of the
    unit is.
    """
    merged: dict[UnitId, Unit] = {}
    for unit in units:
        if (seen := merged.get(unit.id)) is None:
            merged[unit.id] = replace(unit, labels=tuple(dict.fromkeys(unit.labels)))
            continue
        labels = tuple(dict.fromkeys([*seen.labels, *unit.labels]))
        merged[unit.id] = replace(seen, labels=labels, confidential=seen.confidential or unit.confidential)
    return list(merged.values())


def writeUnits(unit_path: Path, units: Iterable[Unit]) -> None:
    unit_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(unitRecord(unit), ensure_ascii=False) + '\n' for unit in units]
    unit_path.write_text(''.join(lines), encoding='utf-8')


def appendUnits(unit_path: Path, units: Iterable[Unit]) -> None:
    unit_path.parent.mkdir(parents=True, exist_ok=True)
    with unit_path.open('a', encoding='utf-8') as unit_file:
        for unit in units:
            unit_file.write(json.dumps(unitRecord(unit), ensure_ascii=False) + '\n')


def makeUnitId(text: str, context_file: str) -> UnitId:
    normalised = ' '.join(text.split())
    digest = hashlib.sha256(f'{normalised}\0{context_file}'.encode()).hexdigest()
    return UnitId(digest[:16])


def splitOf(group: str) -> Split:
    share = int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) / 0x1_0000_0000
    return Split.DEV if share < DEV_SHARE else Split.TEST


def currentLabel(unit: Unit, tier: Tier, *, rule: str | None) -> Label | Conflict | None:
    """Pick the current label of the unit in one tier, for the overall matrix or for one rule.

    Without `rule`, only labels that are not partial count. With `rule`, only labels with the rule
    in `judged` count.

    Returns:
        The latest such label, a Conflict when the unit passes under one label of the latest date
        and fails under another, or None when the unit has no such label.
    """
    labels = [
        label
        for label in unit.labels
        if label.tier is tier and (not label.partial if rule is None else rule in label.judged)
    ]
    if not labels:
        return None
    latest = max(label.date for label in labels)
    newest = [label for label in labels if label.date == latest]
    rulings = {failing(label, rule=rule) for label in newest}
    return newest[0] if len(rulings) == 1 else Conflict(tuple(newest))


def failing(label: Label, *, rule: str | None) -> bool:
    """Whether the unit fails under the label: a cut or a rewrite, or, with `rule`, the rule in `rules`."""
    return label.verdict is not Verdict.KEEP if rule is None else rule in label.rules


def unitRecord(unit: Unit) -> dict[str, object]:
    return {
        'id': unit.id,
        'text': unit.text,
        'context': unit.context,
        'focus_line': unit.focus_line,
        'context_level': unit.context_level.value,
        'language': unit.language.value,
        'kind': unit.kind.value,
        'group': unit.group,
        'origin': {
            'dataset': unit.origin.dataset,
            'file': unit.origin.file,
            'line': unit.origin.line,
            'arm': unit.origin.arm,
            'ref': unit.origin.ref,
        },
        'split': unit.split.value,
        'confidential': unit.confidential,
        'labels': [labelRecord(label) for label in unit.labels],
    }


def labelRecord(label: Label) -> dict[str, object]:
    return {
        'verdict': label.verdict.value,
        'rules': list(label.rules),
        'rewrite': label.rewrite,
        'labeller': label.labeller,
        'tier': label.tier.value,
        'date': label.date,
        'judged': list(label.judged),
        'partial': label.partial,
        'audit': label.audit,
        'note': label.note,
    }


def parseUnit(record: Mapping[str, object]) -> Unit:
    """Build a Unit from one decoded record.

    Raises:
        KeyError: A required field is absent.
        TypeError: A field has the wrong JSON type.
        ValueError: An enum field has a value outside the enum, or a label is malformed.
    """
    origin = asMapping(record['origin'])
    raw_labels = record['labels']
    if not isinstance(raw_labels, list):
        raise TypeError(f'labels is {type(raw_labels).__name__}, not a list')
    return Unit(
        id=UnitId(asText(record['id'])),
        text=asText(record['text']),
        context=asText(record['context']),
        focus_line=asOptionalNumber(record.get('focus_line')),
        context_level=ContextLevel(record['context_level']),
        language=Language(record['language']),
        kind=Kind(record['kind']),
        group=asText(record['group']),
        origin=Origin(
            dataset=asText(origin['dataset']),
            file=asOptionalText(origin.get('file')),
            line=asOptionalNumber(origin.get('line')),
            arm=asOptionalText(origin.get('arm')),
            ref=asOptionalText(origin.get('ref')),
        ),
        split=Split(record['split']),
        confidential=record.get('confidential', False) is True,
        labels=tuple(parseLabel(asMapping(raw_label)) for raw_label in raw_labels),
    )


def parseLabel(record: Mapping[str, object]) -> Label:
    """Build a Label from one decoded label record.

    Raises:
        KeyError: A required field is absent.
        TypeError: A field has the wrong JSON type.
        ValueError: An enum value is unknown, or the date is not YYYY-MM-DD.
    """
    verdict = Verdict(record['verdict'])
    date = asText(record['date'])
    if not DATE.fullmatch(date):
        raise ValueError(f'date {date!r} (expected "2026-10-01")')
    return Label(
        verdict=verdict,
        rules=asCodes(record.get('rules', [])),
        rewrite=asOptionalText(record.get('rewrite')),
        labeller=asText(record['labeller']),
        tier=Tier(record['tier']),
        date=date,
        judged=asCodes(record.get('judged', [])),
        partial=record.get('partial', False) is True,
        audit=record.get('audit', False) is True,
        note=asOptionalText(record.get('note')),
    )


def asMapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f'{type(value).__name__}, not an object')
    return value


def asText(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f'{type(value).__name__}, not a string')
    return value


def asOptionalText(value: object) -> str | None:
    return None if value is None else asText(value)


def asOptionalNumber(value: object) -> int | None:
    # bool subclasses Python int. Reject it too
    if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
        raise TypeError(f'{type(value).__name__}, not an integer')
    return value


def asCodes(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise TypeError(f'{type(value).__name__}, not a list')
    return tuple(asText(code) for code in value)


### vocabulary #########################################################################

UnitId = NewType('UnitId', str)
# matches:
# `2026-10-01`
DATE = re.compile(r'\d{4}-\d{2}-\d{2}')


class Verdict(Enum):
    KEEP = 'keep'
    CUT = 'cut'
    REWRITE = 'rewrite'


class Tier(Enum):
    GOLD = 'gold'
    SILVER = 'silver'
    BRONZE = 'bronze'


class Split(Enum):
    DEV = 'dev'
    TEST = 'test'


class ContextLevel(Enum):
    NONE = 'none'
    SNIPPET = 'snippet'
    WINDOW = 'window'
    REPO = 'repo'


class Language(Enum):
    PYTHON = 'python'
    JAVA = 'java'
    MARKDOWN = 'markdown'


class Kind(Enum):
    COMMENT = 'comment'
    DOCSTRING = 'docstring'
    JAVADOC = 'javadoc'
    PAGE = 'page'
    PR_BODY = 'pr-body'
    CHAT = 'chat'
    # a sentence of a comment or of a docstring, of unknown kind
    PROSE = 'prose'


@dataclass(frozen=True)
class Label:
    verdict: Verdict
    rules: tuple[str, ...]
    rewrite: str | None
    labeller: str
    tier: Tier
    # YYYY-MM-DD
    date: str
    judged: tuple[str, ...] = ()
    partial: bool = False
    audit: bool = False
    note: str | None = None


@dataclass(frozen=True)
class Conflict:
    labels: tuple[Label, ...]


@dataclass(frozen=True)
class Origin:
    dataset: str
    file: str | None
    line: int | None
    arm: str | None
    # a commit, a PR URL, a transcript path, or a path and anchor in this repository
    ref: str | None


@dataclass(frozen=True)
class Unit:
    id: UnitId
    text: str
    context: str
    # the line of `context` where the unit starts, counting from 1, or None when context is empty
    focus_line: int | None
    context_level: ContextLevel
    language: Language
    kind: Kind
    group: str
    origin: Origin
    split: Split
    labels: tuple[Label, ...]
    confidential: bool = False


class UnitFileError(RuntimeError):
    pass
