"""Write the units of one agent session as files, and read the agent's edits back as one verdict per unit.

In the edit mode of the agent predictor, the session gets files, not a list of units, and applies the
skill to the files in place, like a normal session. A unit with file context goes back into the unit's
file: the real file when the repository still has that file, and otherwise a file built from the
context of every unit of that file, with each context at the line of the unit and the excerpts one
blank line apart. A unit with no context becomes a comment block of a notes file. After the session,
the verdict of each unit comes from the diff of the unit's file:

    the unit's lines unchanged          keep
    no comment left where the unit was  cut
    other comment text                  rewrite, with the new text

The rules of a change come from a grader, a separate session that reads the git diff and lists
each changed comment with the rules of the change. The list is matched to the units by file and text.
The same match is a check of the diff reader. A unit that is changed by the diff reader's verdict and
missing from the grader's list, or the reverse, is counted in the `Agreement` of the session.

Usage, from run.py:
    workspace = buildWorkspace(session_dir, units, pyproject_path)
    listed = readChangeList(grader_reply)
    predictions, agreement = readEdits(workspace, units, run_index, listed)
"""

from __future__ import annotations

import difflib
import io
import json
import shutil
import textwrap
import tokenize
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from matrix import Prediction
from schema import REPO_ROOT, Kind, Language, Unit, UnitId, Verdict


# the comment width of a unit with no context, in a notes file
NOTES_WIDTH = 100
# the least similarity of two runs of lines for one to count as the edit of the other
SAME_RUN = 0.5
# the least similarity of a listed comment to a unit's text for the entry to match that unit
SAME_COMMENT = 0.6
PAGE_KINDS = frozenset({Kind.PAGE, Kind.PR_BODY, Kind.CHAT})
COMMENT_PREFIX = {Language.PYTHON: '#', Language.JAVA: '//', Language.MARKDOWN: ''}
SUFFIX = {Language.PYTHON: '.py', Language.JAVA: '.java', Language.MARKDOWN: '.md'}


def buildWorkspace(session_dir: Path, units: list[Unit], pyproject_path: Path) -> Workspace:
    """Write the files of one session to a fresh directory, with the skill's config as pyproject.toml.

    Returns:
        The directory, the place of each unit, and the text of each file as written.
    """
    if session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True)
    shutil.copyfile(pyproject_path, session_dir / 'pyproject.toml')
    workspace = planWorkspace(session_dir, units)
    for relative, text in workspace.written.items():
        target = session_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    return workspace


def planWorkspace(session_dir: Path, units: list[Unit]) -> Workspace:
    """Lay out the files of one session without writing them, so a session's edits can be read again later.

    Returns:
        The directory, the place of each unit, and the text of each file.
    """
    by_file: dict[str, list[Unit]] = defaultdict(list)
    loose: dict[str, list[Unit]] = defaultdict(list)
    for unit in units:
        if unit.context and unit.focus_line and unit.origin.file and unit.origin.line:
            by_file[unit.origin.file].append(unit)
        else:
            loose[unit.group].append(unit)

    projects: dict[str, int] = {}
    placements: dict[UnitId, Placement] = {}
    written: dict[str, str] = {}
    for origin_file, file_units in sorted(by_file.items()):
        origin = PurePosixPath(origin_file)
        project = projects.setdefault(str(origin.parent.parent), len(projects) + 1)
        relative = f'p{project}/{origin.parent.name}/{origin.name}'
        text, line_of_unit = sourceOf(origin_file, file_units)
        written[relative] = text
        for unit in file_units:
            first = line_of_unit[unit.id]
            placements[unit.id] = Placement(relative, first, unitSpan(text.splitlines(), first, unit))
    for index, (_group, group_units) in enumerate(sorted(loose.items()), start=1):
        language = group_units[0].language
        page = group_units[0].kind in PAGE_KINDS
        relative = f'notes/notes_{index}{".md" if page else SUFFIX[language]}'
        text, placed = notesOf(group_units, relative, prefix='' if page else COMMENT_PREFIX[language])
        written[relative] = text
        placements.update(placed)
    return Workspace(session_dir, placements, written)


def sourceOf(origin_file: str, units: list[Unit]) -> tuple[str, dict[UnitId, int]]:
    """Give the text of the file of these units: the real file when the repository has that file, else the excerpts.

    A real file is used only when each unit's context is at the unit's line in that file, so a file
    changed since the rating is not used.

    Returns:
        The text, and the line of each unit in the text.
    """
    real_path = REPO_ROOT / origin_file
    if real_path.is_file():
        real = real_path.read_text(encoding='utf-8')
        real_lines = real.splitlines()
        if all(contextAt(real_lines, unit) for unit in units):
            return real, {unit.id: unitLine(unit) for unit in units}

    excerpts: list[Excerpt] = []
    for unit in sorted(units, key=contextStart):
        start, context = contextStart(unit), unit.context.splitlines()
        if excerpts and start <= excerpts[-1].start + len(excerpts[-1].lines):
            previous = excerpts[-1]
            overlap = previous.start + len(previous.lines) - start
            if previous.lines[len(previous.lines) - overlap :] == context[:overlap]:
                excerpts[-1] = Excerpt(previous.start, previous.lines + context[overlap:], (*previous.units, unit))
                continue
        excerpts.append(Excerpt(start, context, (unit,)))

    out: list[str] = []
    line_of_unit: dict[UnitId, int] = {}
    for excerpt in excerpts:
        if out:
            out.append('')
        line_of_unit.update({unit.id: len(out) + unitLine(unit) - excerpt.start + 1 for unit in excerpt.units})
        out.extend(excerpt.lines)
    return '\n'.join(out) + '\n', line_of_unit


def contextAt(lines: list[str], unit: Unit) -> bool:
    start = contextStart(unit) - 1
    context = unit.context.splitlines()
    return start >= 0 and lines[start : start + len(context)] == context


def contextStart(unit: Unit) -> int:
    """Return the line of the original file where the unit's context starts."""
    return unitLine(unit) - (unit.focus_line or 1) + 1


def unitLine(unit: Unit) -> int:
    return unit.origin.line or 1


def notesOf(units: list[Unit], relative: str, *, prefix: str) -> tuple[str, dict[UnitId, Placement]]:
    """Write units with no context as blocks of a notes file, one blank line apart.

    Returns:
        The text, and the place of each unit in the text.
    """
    out: list[str] = []
    placed: dict[UnitId, Placement] = {}
    for unit in units:
        if out:
            out.append('')
        lines = textwrap.wrap(unit.text, NOTES_WIDTH) or ['']
        placed[unit.id] = Placement(relative, len(out) + 1, len(lines))
        out.extend(f'{prefix} {line}' if prefix else line for line in lines)
    return '\n'.join(out) + '\n', placed


def unitSpan(lines: list[str], first: int, unit: Unit) -> int:
    """Count the lines of a unit from its first line: the comment lines whose text, joined, is the unit's text.

    A trailing comment, after code on the same line, is one line.
    """
    wanted = ' '.join(unit.text.split())
    joined = ''
    for count, line in enumerate(lines[first - 1 :], start=1):
        text = commentText(line, unit.language)
        if text is None:
            return max(count - 1, 1)
        joined = f'{joined} {text}'.strip()
        if len(joined) >= len(wanted) or not lineIsComment(line, unit.language):
            return count
    return 1


def readEdits(
    workspace: Workspace,
    units: list[Unit],
    run_index: int,
    listed: list[ListedChange],
) -> tuple[dict[UnitId, Prediction], Agreement]:
    """Turn the session's edits into one prediction per unit, from the diff of each file.

    A changed unit gets the rules of its entry in the grader's list of changes, and no rules when the
    list has no entry for the unit.

    Returns:
        A prediction for each unit of the workspace, and how the diff and the list agree.
    """
    by_id = {unit.id: unit for unit in units}
    citations = matchListed(workspace, by_id, listed)
    cited = citations.rules
    predictions: dict[UnitId, Prediction] = {}
    for relative, before_text in workspace.written.items():
        after_path = workspace.root / relative
        after_text = after_path.read_text(encoding='utf-8', errors='replace') if after_path.is_file() else ''
        before, after = before_text.splitlines(), after_text.splitlines()
        before_blocks, after_blocks = paragraphs(before), paragraphs(after)
        block_opcodes = difflib.SequenceMatcher(
            None,
            ['\n'.join(before[start:end]) for start, end in before_blocks],
            ['\n'.join(after[start:end]) for start, end in after_blocks],
            autojunk=False,
        ).get_opcodes()
        for unit_id, placement in workspace.placements.items():
            if placement.path != relative:
                continue
            unit = by_id[unit_id]
            old_lines, new_lines = partnerLines(placement, before, after, before_blocks, after_blocks, block_opcodes)
            verdict, new_text = judgeEdit(unit, old_lines, new_lines)
            predictions[unit_id] = Prediction(
                unit=unit_id,
                run=run_index,
                action=verdict,
                rules=cited.get(unit_id, ()) if verdict is not Verdict.KEEP else (),
                new_text=new_text,
            )
    changed = {unit_id for unit_id, prediction in predictions.items() if prediction.action is not Verdict.KEEP}
    agreement = Agreement(
        both=len(changed & cited.keys()),
        diff_only=len(changed - cited.keys()),
        list_only=len(cited.keys() - changed),
        unmatched_entries=citations.unmatched,
    )
    return predictions, agreement


def readChangeList(reply: str) -> list[ListedChange]:
    """Read the grader's JSON array of changes.

    Returns:
        The entries with a file and the comment before the change, or an empty list for a reply with no such array.
    """
    end = reply.rfind(']')
    for start in (index for index in range(end, -1, -1) if reply[index] == '['):
        try:
            entries = json.loads(reply[start : end + 1])
        except json.JSONDecodeError:
            continue
        if isinstance(entries, list) and all(isinstance(entry, dict) for entry in entries):
            return [
                ListedChange(
                    file=str(entry.get('file', '')).removeprefix('./'),
                    old=str(entry.get('old', '')),
                    rules=tuple(str(rule) for rule in entry.get('rules') or [] if isinstance(rule, str)),
                )
                for entry in entries
            ]
    return []


def matchListed(
    workspace: Workspace,
    by_id: dict[UnitId, Unit],
    listed: list[ListedChange],
) -> Citations:
    """Match each listed change to the unit, in the same file, whose text is most like the listed comment.

    Returns:
        The rules of each matched unit, and the number of entries that match no unit.
    """
    cited: dict[UnitId, tuple[str, ...]] = {}
    unmatched = 0
    for change in listed:
        old = ' '.join(change.old.replace('#', ' ').split())
        scored = [
            (difflib.SequenceMatcher(None, old, ' '.join(by_id[unit_id].text.split())).ratio(), unit_id)
            for unit_id, placement in workspace.placements.items()
            if placement.path == change.file
        ]
        best_ratio, best = max(scored, default=(0.0, None))
        if best is None or best_ratio < SAME_COMMENT:
            unmatched += 1
            continue
        cited[best] = tuple(sorted({*cited.get(best, ()), *change.rules}))
    return Citations(cited, unmatched)


def paragraphs(lines: list[str]) -> list[tuple[int, int]]:
    """Split lines into runs of lines with text, at the blank lines.

    Returns:
        The start and end index of each run, end exclusive.
    """
    runs: list[tuple[int, int]] = []
    start = None
    for index, line in enumerate([*lines, '']):
        if line.strip() and start is None:
            start = index
        elif not line.strip() and start is not None:
            runs.append((start, index))
            start = None
    return runs


def partnerLines(
    placement: Placement,
    before: list[str],
    after: list[str],
    before_blocks: list[tuple[int, int]],
    after_blocks: list[tuple[int, int]],
    block_opcodes: Sequence[Opcode],
) -> tuple[list[str], list[str]]:
    """Find the lines that replaced a unit's lines: first the partner of the unit's run, then the unit's lines there.

    Runs are matched first, so the edits to two neighbouring units are told apart even when the
    session changes the line count of each unit. Where the session deleted or added runs, each old run
    is paired in order with the most similar later run, and a run with no similar run was deleted.

    Returns:
        The unit's lines before the session, and the lines that took their place, empty after a cut.
    """
    first, last = placement.first_line - 1, placement.first_line - 1 + placement.line_count
    old_lines = before[first:last]
    home = next((index for index, (start, end) in enumerate(before_blocks) if start <= first < end), None)
    if home is None:
        return old_lines, old_lines
    for tag, i1, i2, j1, j2 in block_opcodes:
        if not i1 <= home < i2:
            continue
        if tag == 'equal':
            return old_lines, old_lines
        if tag == 'delete':
            return old_lines, []
        texts = ['\n'.join(before[start:end]) for start, end in before_blocks[i1:i2]]
        candidates = ['\n'.join(after[start:end]) for start, end in after_blocks[j1:j2]]
        partner = pairRuns(texts, candidates)[home - i1]
        if partner is None:
            return old_lines, []
        break
    else:
        return old_lines, old_lines
    block_start, block_end = before_blocks[home]
    block = before[block_start:block_end]
    replaced = after[after_blocks[j1 + partner][0] : after_blocks[j1 + partner][1]]
    line_opcodes = difflib.SequenceMatcher(None, block, replaced, autojunk=False).get_opcodes()
    local_first, local_last = first - block_start, last - block_start
    touched = [op for op in line_opcodes if op[0] != 'equal' and op[1] < local_last and op[2] > local_first]
    if not touched:
        return old_lines, old_lines
    return old_lines, [line for op in touched for line in replaced[op[3] : op[4]]]


def pairRuns(old: list[str], new: list[str]) -> list[int | None]:
    """Pair each old run with a new run, in order, by similarity.

    Returns:
        For each old run, the index of the paired new run, or None for a run with no similar new run.
    """
    if len(old) == len(new):
        return list(range(len(old)))
    paired: list[int | None] = []
    next_new = 0
    for text in old:
        ratios = [
            (difflib.SequenceMatcher(None, text, new[index]).ratio(), index) for index in range(next_new, len(new))
        ]
        best_ratio, best = max(ratios, default=(0.0, -1))
        if best_ratio < SAME_RUN:
            paired.append(None)
            continue
        paired.append(best)
        next_new = best + 1
    return paired


def judgeEdit(unit: Unit, old_lines: list[str], new_lines: list[str]) -> tuple[Verdict, str | None]:
    """Decide keep, cut or rewrite for one unit from the unit's lines before and after the session.

    Returns:
        The verdict, and the new comment text for a rewrite.
    """
    new = ' '.join(text for line in new_lines if (text := commentText(line, unit.language)))
    old = ' '.join(text for line in old_lines if (text := commentText(line, unit.language)))
    if not new:
        return Verdict.CUT, None
    if ' '.join(new.split()) == ' '.join(old.split()):
        return Verdict.KEEP, None
    return Verdict.REWRITE, new


def commentText(line: str, language: Language) -> str | None:
    """Return the comment text of one line, without the comment marker, or None for a line with no comment.

    A Markdown line is all text.
    """
    if language is Language.MARKDOWN:
        return line.strip() or None
    if language is Language.JAVA:
        marker = line.find('//')
        return (line[marker + 2 :].strip() or None) if marker >= 0 else None
    try:
        for token in tokenize.generate_tokens(io.StringIO(line).readline):
            if token.type == tokenize.COMMENT:
                return token.string.lstrip('#').strip() or None
    except (tokenize.TokenError, SyntaxError):
        # the tokens end early on a line that opens a bracket or a string. A comment before that point is
        # returned in the loop
        pass
    return None


def lineIsComment(line: str, language: Language) -> bool:
    prefix = COMMENT_PREFIX[language]
    return bool(prefix) and line.lstrip().startswith(prefix)


### vocabulary #########################################################################


@dataclass(frozen=True)
class Placement:
    """The place of one unit in the files of a session."""

    # relative to the session's directory
    path: str
    first_line: int
    line_count: int


# a hunk of difflib.SequenceMatcher.get_opcodes(): the tag, then the line ranges before and after
Opcode = tuple[str, int, int, int, int]


@dataclass(frozen=True)
class Excerpt:
    """A run of lines of an original file, from the contexts of the units placed in the excerpt."""

    # the line of the original file where the excerpt starts
    start: int
    lines: list[str]
    units: tuple[Unit, ...]


@dataclass(frozen=True)
class ListedChange:
    """One entry of the grader's list of changes."""

    file: str
    old: str
    rules: tuple[str, ...]


@dataclass(frozen=True)
class Citations:
    """The rules of each unit, from the grader's list of changes."""

    rules: dict[UnitId, tuple[str, ...]]
    # entries of the list with no matching unit
    unmatched: int


@dataclass(frozen=True)
class Agreement:
    """The units changed by the diff reader's verdicts, compared with the units of the grader's list."""

    both: int
    diff_only: int
    list_only: int
    # entries of the list with no matching unit, such as a comment that is not a rated unit
    unmatched_entries: int

    def plus(self, other: Agreement) -> Agreement:
        return Agreement(
            self.both + other.both,
            self.diff_only + other.diff_only,
            self.list_only + other.list_only,
            self.unmatched_entries + other.unmatched_entries,
        )

    def asRecord(self) -> dict[str, int]:
        return {
            'both': self.both,
            'diff_only': self.diff_only,
            'list_only': self.list_only,
            'unmatched_entries': self.unmatched_entries,
        }


@dataclass(frozen=True)
class Workspace:
    root: Path
    placements: dict[UnitId, Placement]
    # the text of each file as written, by path relative to root
    written: dict[str, str]
