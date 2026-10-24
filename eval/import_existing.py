"""Read the round 10 label files into the unit set, and report every unit whose gold labels disagree.

Sources:
    gold    benchmark/round10/rating*.md with rating*_key.md and eval/sources/round10_ratings.tsv
    gold    benchmark/round10/seeds.md, the user's rewrites of Claude's text
    gold    benchmark/round10/agentverb/gold.tsv, sentence labels for NAR017 alone
    silver  benchmark/round10/classes.jsonl, joined to corpus.jsonl for the text

The context of a rated comment is the snippet that the user rated, at level snippet. A seed has no
context unless the seed's text is a rated comment, and a gold.tsv sentence has none: level none. The
context of a silver comment comes from the comment's file. A window of the file at the last commit
of corpus.jsonl, or at the commit of a history record, is level window. The hunks of an edit run's
diff are level snippet.

A gold.tsv `agent` line is a NAR017 rewrite, and an `ok` line a keep. A rating or seed label has the date of the label's
decision in decisions.jsonl. A gold.tsv or classes.jsonl label has the author date of the label's
line in `git blame`.

The split group of a gold.tsv sentence is the block of 10 lines around the sentence. gold.tsv has no
column for the source file of a sentence.

Usage:
    $ uv run eval/import_existing.py
    $ uv run eval/import_existing.py --out /tmp/units.jsonl --conflicts /tmp/conflicts.md

Exit codes:
    0  the units and the conflict report were written
    2  a source file is missing or malformed
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path

from schema import (
    REPO_ROOT,
    REPORTS_DIR,
    UNITS_DIR,
    ContextLevel,
    Kind,
    Label,
    Language,
    Origin,
    Tier,
    Unit,
    Verdict,
    failing,
    makeUnitId,
    mergeUnits,
    splitOf,
    writeUnits,
)


ROUND10_DIR = REPO_ROOT / 'benchmark' / 'round10'
DECISIONS_PATH = REPO_ROOT / 'benchmark' / 'decisions.jsonl'
RATING_VERDICTS_PATH = Path(__file__).resolve().parent / 'sources' / 'round10_ratings.tsv'
SEEDS_PATH = ROUND10_DIR / 'seeds.md'
AGENTVERB_GOLD_PATH = ROUND10_DIR / 'agentverb' / 'gold.tsv'
CLASSES_PATH = ROUND10_DIR / 'classes.jsonl'
CORPUS_PATH = ROUND10_DIR / 'corpus.jsonl'
EDITS_DIR = ROUND10_DIR / 'edits'
RATING_FILES = ('rating', 'rating2', 'rating3', 'rating4', 'rating5')
CONTEXT_LINES = 15
GOLD_TSV_BLOCK = 10
EXIT_SUCCESS = 0
EXIT_UNUSABLE = 2


def main() -> int:
    """Import every source, merge units by id, write the unit file and the conflict report.

    Returns:
        0 when both files were written, 2 when a source could not be read.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=UNITS_DIR / 'round10.jsonl')
    parser.add_argument('--conflicts', type=Path, default=REPORTS_DIR / 'conflicts.md')
    arguments = parser.parse_args()

    try:
        decision_dates = readDecisionDates(DECISIONS_PATH)
        ratings = importRatings(decision_dates)
        seeds, repeated_seeds = importSeeds(decision_dates, ratings)
        gold_tsv = importAgentVerbGold()
        classes, context_misses = importClasses()
    except (OSError, KeyError, ValueError, ImportSourceError) as exc:
        print(f'import_existing.py: {exc}', file=sys.stderr)
        return EXIT_UNUSABLE

    units = mergeUnits([*ratings, *seeds, *gold_tsv, *classes])
    writeUnits(arguments.out, units)
    conflicts = findConflicts(units)
    arguments.conflicts.parent.mkdir(parents=True, exist_ok=True)
    arguments.conflicts.write_text(renderConflicts(conflicts), encoding='utf-8')

    gold_tsv_lines = AGENTVERB_GOLD_PATH.read_text(encoding='utf-8').splitlines()
    gold_tsv_verdicts = Counter(line.split('\t', 1)[0] for line in gold_tsv_lines)
    print(f'ratings: {len(ratings)} gold labels from {len(RATING_FILES)} rating files, {countIds(ratings)} units')
    print(f'seeds: {len(seeds) + repeated_seeds} rows, {len(seeds)} gold labels, {repeated_seeds} repeat a rating')
    print(
        f'gold.tsv: {len(gold_tsv_lines)} lines ({gold_tsv_verdicts["agent"]} agent, {gold_tsv_verdicts["ok"]} ok), '
        f'{countIds(gold_tsv)} units after {len(gold_tsv_lines) - countIds(gold_tsv)} duplicate lines collapsed',
    )
    print(
        f'classes.jsonl: {len(classes)} silver labels on {countIds(classes)} units, '
        f'{context_misses} with no context found',
    )
    splits = Counter(unit.split.value for unit in units)
    print(f'total: {len(units)} units, {splits["dev"]} dev, {splits["test"]} test, written to {arguments.out}')
    print(f'conflicts: {len(conflicts)} units with disagreeing gold labels, written to {arguments.conflicts}')
    for conflict in conflicts:
        rulings = ', '.join(f'{label.date} {label.verdict.value}' for label in conflict.labels)
        print(f'  {conflict.unit.id} {conflict.unit.origin.dataset}: {shorten(conflict.unit.text)} <- {rulings}')
    return EXIT_SUCCESS


def readDecisionDates(decisions_path: Path) -> dict[str, str]:
    dates = {}
    for line in decisions_path.read_text(encoding='utf-8').splitlines():
        decision = json.loads(line)
        dates[decision['id']] = decision['date']
    return dates


def importRatings(decision_dates: dict[str, str]) -> list[Unit]:
    """Make one gold unit per rated comment, with the rated snippet as the unit's context.

    The labels of each rating file have the date of the decision named after the file.

    Raises:
        ImportSourceError: An item in round10_ratings.tsv is absent from the rating files, or a
            snippet has fewer comment blocks than the item needs.
    """
    verdicts = readRatingVerdicts(RATING_VERDICTS_PATH)
    units = []
    for name in RATING_FILES:
        snippets = readRatingSnippets(ROUND10_DIR / f'{name}.md')
        key = readRatingKey(ROUND10_DIR / f'{name}_key.md')
        date = decision_dates[f'R10-{name}']
        for item, verdict in verdicts.items():
            section = item.rstrip('b')
            if section not in snippets:
                continue
            snippet = snippets[section]
            blocks = commentBlocks(snippet)
            block_index = 1 if item.endswith('b') else 0
            if len(blocks) <= block_index:
                raise ImportSourceError(f'{name}.md {section} has {len(blocks)} comment blocks')
            start, end = blocks[block_index]
            text = ' '.join(commentOf(line) for line in snippet[start:end])
            key_row = key[section]
            label = Label(
                verdict=verdict.verdict,
                rules=(),
                rewrite=verdict.rewrite,
                labeller='user',
                tier=Tier.GOLD,
                date=date,
            )
            units.append(
                Unit(
                    id=makeUnitId(text, key_row.file),
                    text=text,
                    context='\n'.join(snippet),
                    focus_line=start + 1,
                    context_level=ContextLevel.SNIPPET,
                    language=Language.PYTHON,
                    kind=Kind.COMMENT,
                    group=key_row.file,
                    origin=Origin(
                        dataset=f'round10-{name}',
                        file=key_row.file,
                        line=key_row.line,
                        arm=key_row.arm,
                        ref=f'benchmark/round10/{name}.md#{item}',
                    ),
                    split=splitOf(key_row.file),
                    labels=(label,),
                ),
            )
    found = {unit.origin.ref.rpartition('#')[2] for unit in units if unit.origin.ref}
    if missing := sorted(set(verdicts) - found):
        raise ImportSourceError(f'rated items absent from the rating files: {", ".join(missing)}')
    return units


def readRatingVerdicts(verdicts_path: Path) -> dict[str, RatingVerdict]:
    """Parse round10_ratings.tsv: item, verdict, and the rewrite text for a rewrite with one.

    Raises:
        ValueError: A verdict is not keep, cut or rewrite.
    """
    verdicts = {}
    for line in verdicts_path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        item, raw_verdict, *rest = line.split('\t')
        verdicts[item] = RatingVerdict(verdict=Verdict(raw_verdict), rewrite=rest[0] if rest and rest[0] else None)
    return verdicts


def readRatingSnippets(rating_path: Path) -> dict[str, list[str]]:
    # matches:
    # "## item\n\n```python\n# a comment\nx = 1\n```"
    SNIPPET = re.compile(r'^## (\S+)\n+```python\n(.*?)^```', re.MULTILINE | re.DOTALL)
    return {match[1]: match[2].splitlines() for match in SNIPPET.finditer(rating_path.read_text(encoding='utf-8'))}


def readRatingKey(key_path: Path) -> dict[str, KeyRow]:
    """Parse the item table of a rating key: item, source or variant, and `file:line` in backticks.

    Raises:
        ImportSourceError: A table row has no `file:line`.
    """
    rows = {}
    for line in key_path.read_text(encoding='utf-8').splitlines():
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if not cells[0].startswith('R10-'):
            continue
        location = re.fullmatch(r'`(.+):(\d+)`', cells[2])
        if location is None:
            raise ImportSourceError(f'{key_path.name}: {cells[0]} names no file:line')
        rows[cells[0]] = KeyRow(file=location[1], line=int(location[2]), arm=cells[1])
    return rows


def commentBlocks(snippet: list[str]) -> list[tuple[int, int]]:
    """Find each run of whole-line comments, and each end-of-line comment.

    Dividers such as `### vocabulary ###` and pragmas such as `# noqa: NAR005` are left out.

    Returns:
        The start and end index of each block, end exclusive, in snippet order.
    """
    blocks: list[tuple[int, int]] = []
    for index, line in enumerate(snippet):
        stripped = line.strip()
        whole_line = stripped.startswith('#')
        if whole_line and stripped.startswith('###'):
            continue
        if not whole_line and (END_OF_LINE.search(line) is None or PRAGMA.match(commentOf(line))):
            continue
        if whole_line and blocks and blocks[-1][1] == index and snippet[index - 1].strip().startswith('#'):
            blocks[-1] = (blocks[-1][0], index + 1)
        else:
            blocks.append((index, index + 1))
    return blocks


def commentOf(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith('#'):
        return stripped.removeprefix('#').strip()
    return END_OF_LINE.split(line, maxsplit=1)[1].strip()


def importSeeds(decision_dates: dict[str, str], ratings: list[Unit]) -> tuple[list[Unit], int]:
    """Make one gold unit per seed pair: Claude's text, labelled with the user's rewrite.

    A user answer that is a name, such as `total_cents`, is a cut: the comment becomes the name.
    In an answer with several backticked forms, the `# comment` form is the rewrite. A seed whose
    text is a rated comment gets the rated comment's id. When the user gave the same rewrite in the
    rating, no second label is added. Each row has the date of the seed decision with the row's
    number, or the date of the row before when no seed decision has that number.

    Returns:
        The seed units, and the number of seed rows with the same label as a rating.
    """
    rated = {' '.join(unit.text.split()): unit for unit in ratings}
    units = []
    repeated = 0
    date = decision_dates['R10-rating']
    for number, (claude_cell, user_cell) in enumerate(readSeedRows(SEEDS_PATH), start=1):
        date = decision_dates.get(f'R10-seed-{number}', date)
        text = seedText(backtickSpans(claude_cell)[0])
        answers = backtickSpans(user_cell)
        comment_answers = [answer.removeprefix('# ') for answer in answers if answer.startswith('# ')]
        if len(answers) == 1 and RENAME.fullmatch(answers[0]):
            verdict, rewrite, note = Verdict.CUT, None, f'renamed: {answers[0]}'
        else:
            verdict, rewrite, note = Verdict.REWRITE, (comment_answers or ['\n'.join(answers)])[0], None
        label = Label(
            verdict=verdict,
            rules=(),
            rewrite=rewrite,
            labeller='user',
            tier=Tier.GOLD,
            date=date,
            note=note,
        )
        if (rating := rated.get(' '.join(text.split()))) is not None:
            if any(sameRewrite(seen, label) for seen in rating.labels):
                repeated += 1
                continue
            units.append(replace(rating, labels=(label,)))
            continue

        kind = Kind.CHAT if 'chat' in claude_cell else Kind.PAGE if 'header' in claude_cell else Kind.COMMENT
        group = f'seeds.md:{number}'
        units.append(
            Unit(
                id=makeUnitId(text, ''),
                text=text,
                context='',
                focus_line=None,
                context_level=ContextLevel.NONE,
                language=Language.PYTHON if kind is Kind.COMMENT else Language.MARKDOWN,
                kind=kind,
                group=group,
                origin=Origin(
                    dataset='round10-seeds',
                    file=None,
                    line=None,
                    arm=None,
                    ref=f'benchmark/round10/{group}',
                ),
                split=splitOf(group),
                labels=(label,),
            ),
        )
    return units, repeated


def readSeedRows(seeds_path: Path) -> list[tuple[str, str]]:
    # the pair table: from the `| Claude | user |` header to the first blank line
    lines = seeds_path.read_text(encoding='utf-8').splitlines()
    start = lines.index('| Claude | user |') + 2
    end = lines.index('', start)
    rows = []
    for line in lines[start:end]:
        claude_cell, user_cell = line.strip().strip('|').split(' | ')
        rows.append((claude_cell.strip(), user_cell.strip()))
    return rows


def backtickSpans(cell: str) -> list[str]:
    # matches:
    # `` `executemany` takes one sequence per row ``
    # `in read order`
    SPAN = re.compile(r'``\s(.+?)\s``|`([^`]+)`')
    return [double or single for double, single in SPAN.findall(cell)]


def seedText(claude_text: str) -> str:
    # `over: ByteCount  # the bytes above the quota` is a field with an end-of-line comment
    if '  # ' in claude_text:
        return claude_text.split('  # ', 1)[1]
    return claude_text.lstrip('#').strip()


def sameRewrite(seen: Label, label: Label) -> bool:
    return seen.verdict is label.verdict and ' '.join((seen.rewrite or '').split()) == ' '.join(
        (label.rewrite or '').split(),
    )


def importAgentVerbGold() -> list[Unit]:
    """Make one gold unit per gold.tsv line, labelled for NAR017 alone. Duplicate lines share an id.

    Raises:
        ValueError: A line is not `agent` or `ok`, a tab, then the sentence.
    """
    lines = AGENTVERB_GOLD_PATH.read_text(encoding='utf-8').splitlines()
    dates = blameDates(AGENTVERB_GOLD_PATH)
    relative = AGENTVERB_GOLD_PATH.relative_to(REPO_ROOT)
    units = []
    for index, line in enumerate(lines):
        raw_verdict, text = line.split('\t', 1)
        match raw_verdict:
            case 'agent':
                rules: tuple[str, ...]
                verdict, rules = Verdict.REWRITE, ('NAR017',)
            case 'ok':
                verdict, rules = Verdict.KEEP, ()
            case _:
                raise ValueError(f'{relative}:{index + 1}: label {raw_verdict!r} (expected "agent" or "ok")')
        first = index - index % GOLD_TSV_BLOCK + 1
        group = f'{relative}:{first}-{first + GOLD_TSV_BLOCK - 1}'
        label = Label(
            verdict=verdict,
            rules=rules,
            rewrite=None,
            labeller='user',
            tier=Tier.GOLD,
            date=dates[index],
            judged=('NAR017',),
            partial=True,
        )
        units.append(
            Unit(
                id=makeUnitId(text, ''),
                text=text,
                context='',
                focus_line=None,
                context_level=ContextLevel.NONE,
                language=Language.PYTHON,
                kind=Kind.PROSE,
                group=group,
                origin=Origin(dataset='agentverb-gold', file=None, line=None, arm=None, ref=f'{relative}:{index + 1}'),
                split=splitOf(group),
                labels=(label,),
            ),
        )
    return units


def importClasses() -> tuple[list[Unit], int]:
    """Make one silver unit per classes.jsonl record, with the text of the matching corpus.jsonl record.

    A trim is a rewrite to the trimmed text. Every F code of the file was judged on every record,
    so an F code absent from a record is a negative for that record. A K code is the kind
    of a kept comment, and goes in the note.

    Returns:
        The units, and the number of them whose context could not be found.

    Raises:
        KeyError: No corpus record has the file, line and arm of a classes record.
    """
    corpus = {}
    for line in CORPUS_PATH.read_text(encoding='utf-8').splitlines():
        record = json.loads(line)
        corpus[record['file'], record['line'], record['arm']] = record
    corpus_commit = runGit('log', '-1', '--format=%h', '--', str(CORPUS_PATH.relative_to(REPO_ROOT)))
    classes = [json.loads(line) for line in CLASSES_PATH.read_text(encoding='utf-8').splitlines()]
    dates = blameDates(CLASSES_PATH)
    fault_codes = tuple(sorted({code for record in classes for code in record['codes'] if code.startswith('F')}))
    sources = ContextSources(corpus_commit=corpus_commit)
    units = []
    misses = 0
    for index, record in enumerate(classes):
        harvested = corpus[record['file'], record['line'], record['arm']]
        context, focus_line = sources.contextOf(record, harvested['raw'])
        misses += context == ''
        kinds = [code for code in record['codes'] if not code.startswith('F')]
        notes = [f'kinds: {" ".join(kinds)}' if kinds else '', record['note'] or '']
        verdict = {'keep': Verdict.KEEP, 'trim': Verdict.REWRITE, 'cut': Verdict.CUT}[record['verdict']]
        label = Label(
            verdict=verdict,
            rules=tuple(code for code in record['codes'] if code.startswith('F')),
            rewrite=record['trimmed'],
            labeller='agent',
            tier=Tier.SILVER,
            date=dates[index],
            judged=fault_codes,
            note='. '.join(note for note in notes if note) or None,
        )
        group = f'{record["arm"]}:{record["file"]}'
        units.append(
            Unit(
                id=makeUnitId(harvested['text'], record['file']),
                text=harvested['text'],
                context=context,
                focus_line=focus_line,
                context_level=contextLevelOf(record['source'], context),
                language=Language.PYTHON,
                kind=Kind.DOCSTRING if harvested['kind'] == 'docstring' else Kind.COMMENT,
                group=group,
                origin=Origin(
                    dataset='round10-classes',
                    file=record['file'],
                    line=record['line'],
                    arm=record['arm'],
                    ref=sources.refOf(record),
                ),
                split=splitOf(group),
                labels=(label,),
            ),
        )
    return units, misses


def contextLevelOf(source: str, context: str) -> ContextLevel:
    # the diff of an edit run has hunks, not whole files, so the context is a snippet
    if not context:
        return ContextLevel.NONE
    return ContextLevel.SNIPPET if source == 'edit' else ContextLevel.WINDOW


def blameDates(blamed_path: Path) -> list[str]:
    """Date each line of a tracked file by the author date of the line's last commit.

    Returns:
        One YYYY-MM-DD date per line, in the author's timezone.
    """
    porcelain = runGit('blame', '--line-porcelain', '--', str(blamed_path.relative_to(REPO_ROOT)))
    dates = []
    author_time = 0
    for line in porcelain.splitlines():
        if line.startswith('author-time '):
            author_time = int(line.split()[1])
        elif line.startswith('author-tz '):
            raw_offset = line.split()[1]
            offset_s = (-1 if raw_offset[0] == '-' else 1) * (int(raw_offset[1:3]) * 3600 + int(raw_offset[3:5]) * 60)
            dates.append(time.strftime('%Y-%m-%d', time.gmtime(author_time + offset_s)))
    return dates


def runGit(*arguments: str) -> str:
    """Run git in the repository and return git's stdout.

    Raises:
        ImportSourceError: git exited nonzero.
    """
    completed = subprocess.run(
        ['git', '-C', str(REPO_ROOT), *arguments],
        capture_output=True,
        text=True,
        errors='replace',
        check=False,
    )
    if completed.returncode != 0:
        raise ImportSourceError(f'git {" ".join(arguments[:2])}: {completed.stderr.strip()}')
    return completed.stdout


def findConflicts(units: list[Unit]) -> list[ConflictedUnit]:
    """Find every unit that passes under one gold label and fails under another of the same scope.

    Two labels have one scope when both are partial on the same codes, or neither is partial.

    Returns:
        Each such unit with the labels of the disagreeing scope, in date order.
    """
    conflicts = []
    for unit in units:
        scopes: dict[str, list[Label]] = {}
        for label in unit.labels:
            if label.tier is Tier.GOLD:
                scope = f'partial {" ".join(label.judged)}' if label.partial else 'whole'
                scopes.setdefault(scope, []).append(label)
        for labels in scopes.values():
            if not agreeing(labels):
                conflicts.append(ConflictedUnit(unit, tuple(sorted(labels, key=lambda label: label.date))))
    return conflicts


def agreeing(labels: list[Label]) -> bool:
    return len({failing(label, rule=None) for label in labels}) == 1


def renderConflicts(conflicts: list[ConflictedUnit]) -> str:
    """Write the conflict report as Markdown: one section per unit, one line per label.

    A conflict whose labels have different dates is decided by the latest label. When the labels of
    the latest date conflict, the unit is left out of every matrix until a new label is added.
    """
    lines = [
        '# Gold label conflicts',
        '',
        'Generated by `eval/import_existing.py`. Each unit below has gold labels that disagree.',
        'Where the dates differ, the latest label is the current label. Where the latest date has',
        'two labels, the unit is left out of every matrix until a new label is added.',
        '',
    ]
    if not conflicts:
        lines.append('No conflicts.')
    for unit, labels in ((conflict.unit, conflict.labels) for conflict in conflicts):
        latest = [label for label in labels if label.date == labels[-1].date]
        status = 'decided by the latest label' if agreeing(latest) else 'unresolved, left out of the matrix'
        lines += [f'## `{unit.id}` ({unit.origin.dataset}, {status})', '', f'> {unit.text}', '']
        if unit.origin.ref:
            lines += [f'Source: `{unit.origin.ref}`', '']
        for label in labels:
            rewrite = f': `{label.rewrite}`' if label.rewrite else ''
            lines.append(f'- {label.date} {label.verdict.value}{rewrite}')
        lines.append('')
    return '\n'.join(lines)


def countIds(units: list[Unit]) -> int:
    return len({unit.id for unit in units})


def shorten(text: str) -> str:
    return text if len(text) <= 80 else text[:77] + '...'


### vocabulary #########################################################################

# matches:
# `total_cents`
# `over_quota: ByteCount`
# rejects:
# `signed error`
RENAME = re.compile(r'[A-Za-z_]\w*(?:: [A-Za-z_]\w*)?')
# matches:
# `location: str  # 'line 4' in a billing file`
END_OF_LINE = re.compile(r'(?<=\S)\s+# ')
# matches:
# `noqa: NAR005`
# `type: ignore`
PRAGMA = re.compile(r'(?:noqa|type:|pragma|fmt:)')


@dataclass(frozen=True)
class RatingVerdict:
    verdict: Verdict
    rewrite: str | None


@dataclass(frozen=True)
class ConflictedUnit:
    unit: Unit
    # the disagreeing labels of one scope, in date order
    labels: tuple[Label, ...]


@dataclass(frozen=True)
class KeyRow:
    file: str
    line: int
    # the key's column for the skill version or variant behind the comment
    arm: str


class ContextSources:
    """Find the file lines around a classes.jsonl comment, from git or from an edit run's diff.

    A fresh record's file is read at the last commit of corpus.jsonl, so the file's line numbers
    are those of the harvest. The arm of a history record is a commit. The arm of an edit record is
    the name of a diff in benchmark/round10/edits/, and only the new-side lines of the diff's hunks
    are known.
    """

    def __init__(self, *, corpus_commit: str) -> None:
        self.corpus_commit = corpus_commit.strip()
        self.files: dict[str, dict[int, str]] = {}
        self.file_commits: dict[str, list[str]] = {}
        # new-side lines by `<arm>:<file>`, for each arm in parsed_arms
        self.edit_lines: dict[str, dict[int, str]] = {}
        self.parsed_arms: set[str] = set()

    def contextOf(self, record: dict[str, str], raw: str) -> tuple[str, int | None]:
        """Cut up to CONTEXT_LINES lines on each side of the comment from the comment's file.

        The comment is at the known line that contains the first line of `raw` and is nearest the
        recorded line. An edit diff may lack the first line of a docstring, so a later line of
        `raw` is tried next. A gap between two hunks of a diff becomes a `...` line.

        Returns:
            The context and the line of the comment in the context, or `('', None)` when the file
            or the comment could not be found.
        """
        needles = [line.strip() for line in raw.splitlines() if len(line.strip()) > 3]
        recorded = int(record['line'])
        match record['source']:
            case 'edit':
                known = self.readEditLines(record['arm'], record['file'])
            case 'history':
                known = self.readFile(record['arm'], record['file'])
            case 'fresh':
                known = self.readHarvestedFile(record['file'], recorded, needles[0] if needles else '')
            case _:
                known = {}
        focus = None
        for needle in needles:
            found = [number for number, text in known.items() if needle in text]
            if found:
                focus = min(found, key=lambda number: abs(number - recorded))
                break
        if focus is None:
            return '', None

        numbers = [number for number in range(focus - CONTEXT_LINES, focus + CONTEXT_LINES + 1) if number in known]
        context: list[str] = []
        focus_line = None
        for previous, number in zip([None, *numbers], numbers, strict=False):
            if previous is not None and number != previous + 1:
                context.append('...')
            if number == focus:
                focus_line = len(context) + 1
            context.append(known[number])
        return '\n'.join(context), focus_line

    def refOf(self, record: dict[str, str]) -> str:
        match record['source']:
            case 'edit':
                return f'benchmark/round10/edits/{record["arm"]}.diff'
            case 'history':
                return f'{record["arm"]}:{record["file"]}'
            case _:
                return f'{self.corpus_commit}:{record["file"]}'

    def readHarvestedFile(self, file_name: str, recorded: int, needle: str) -> dict[int, str]:
        """Read a fresh record's file as harvested: at the corpus commit, or at a later commit of the file.

        harvest.py read a working tree that was ahead of the corpus commit for some tooling files.
        The first version with `needle` on the recorded line is taken. When no version has `needle`
        on that line, the version at the corpus commit is taken.
        """
        at_corpus = self.readFile(self.corpus_commit, file_name)
        if needle in at_corpus.get(recorded, ''):
            return at_corpus
        if file_name not in self.file_commits:
            self.file_commits[file_name] = runGit('log', '--format=%h', '--', file_name).split()
        for commit in reversed(self.file_commits[file_name]):
            version = self.readFile(commit, file_name)
            if needle in version.get(recorded, ''):
                return version
        return at_corpus

    def readFile(self, commit: str, file_name: str) -> dict[int, str]:
        # a file absent at the commit has no lines
        key = f'{commit}:{file_name}'
        if key not in self.files:
            try:
                self.files[key] = dict(enumerate(runGit('show', key).splitlines(), start=1))
            except ImportSourceError:
                self.files[key] = {}
        return self.files[key]

    def readEditLines(self, arm: str, file_name: str) -> dict[int, str]:
        """Read the new-side lines of one file from an edit run's diff, by line number.

        A path in the diff is `b/<arm>/<path>`, which is also the corpus file name with `b/` cut.
        The whole diff is parsed on the first call for the arm.
        """
        if arm not in self.parsed_arms:
            self.parsed_arms.add(arm)
            diff_path = EDITS_DIR / f'{arm}.diff'
            current: dict[int, str] = {}
            number = 0
            diff_text = diff_path.read_text(encoding='utf-8', errors='replace') if diff_path.exists() else ''
            for line in diff_text.splitlines():
                if line.startswith('+++ b/'):
                    current = self.edit_lines.setdefault(f'{arm}:{line.removeprefix("+++ b/")}', {})
                elif hunk := re.match(r'@@ -\S+ \+(\d+)', line):
                    number = int(hunk[1])
                elif line.startswith(('+', ' ')) and not line.startswith('+++'):
                    current[number] = line[1:]
                    number += 1
        return self.edit_lines.get(f'{arm}:{file_name}', {})


class ImportSourceError(RuntimeError):
    pass


if __name__ == '__main__':
    sys.exit(main())
