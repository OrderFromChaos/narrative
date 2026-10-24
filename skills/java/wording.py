"""The wording checks and the --since helpers, shared by the checkers of every language of Narrative.

NAR012 to NAR016 and NAR018 flag wording that no comment, docstring or published page needs. The
checks read lines of prose. A language's checker passes in the lines of the language's comments and
doc comments, and checkPage() reads a Markdown, HTML or plain text page through prose.py.

readChangedLines() lists the lines that the diff against a base branch adds or changes, for --since.
findFiles() lists the files of a directory, and does not enter another checkout below the directory.

Usage, from a script in this directory:
    import wording
    findings = wording.wordingFindings(prose_lines, list_items, checked_file)
    findings = wording.checkPage(Path('README.md'))
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import prose


### standard library only. The checkers of each language import this, and they run wherever python3 does

RULES = {
    'NAR012': 'decision id in a comment or docstring. Unresolvable outside the repository where it was recorded',
    'NAR013': 'dash or semicolon joining clauses in a comment or docstring. Write two sentences',
    'NAR014': 'deliberately / on purpose / by design in a comment or docstring. Reassurance, no information',
    'NAR015': 'changelog wording in a comment or docstring. State the current code or data plainly',
    'NAR016': 'container verb in a comment or docstring. State the fact without making the subject hold or carry it',
    'NAR018': 'possessive "own" in a comment or docstring. Drop "own", or name the owner',
    'NAR000': 'file could not be read or parsed',
}

# the number of entries of each review list without --since and --all-sentences: the sentences of --prose,
# and the pairs and the pronoun sentences of agentverbs.py
LIST_PAGE = 1000


def checkPage(checked_file: Path) -> list[Finding]:
    """Run the wording checks over the passages of a Markdown, HTML or plain text file.

    Returns:
        Every finding not silenced by a `<!-- noqa -->` comment, or a single NAR000 if the file
        could not be read.
    """
    try:
        source = checked_file.read_text(encoding='utf-8')
    except OSError as exc:
        return [Finding(checked_file, 0, 'NAR000', f'unreadable: {exc.strerror}')]
    except UnicodeDecodeError as exc:
        return [Finding(checked_file, 0, 'NAR000', f'not UTF-8: {exc.reason}')]

    passages = prose.readPassages(checked_file)
    prose_lines = [line for passage in passages for line in zip(passage.lines, passage.texts, strict=True)]
    list_items = {passage.lines[0] for passage in passages if passage.list_item}
    suppressed = prose.suppressedCodes(source)
    findings = wordingFindings(prose_lines, list_items, checked_file)
    return [f for f in findings if not (suppressed.get(f.line, set()) & {f.code, 'ALL'})]


def wordingFindings(prose_lines: list[tuple[int, str]], list_items: set[int], checked_file: Path) -> list[Finding]:
    """Flag six kinds of wording that no comment, docstring or published page needs.

    - NAR012: a decision id, unresolvable outside the repository where the id was recorded
    - NAR013: a dash or a semicolon joining clauses, outside backticked code
    - NAR014: reassurance words, listed in WORDING
    - NAR015: changelog wording about code that is gone
    - NAR016: a container verb on a subject that is not a container, listed in WORDING
    - NAR018: a possessive followed by `own`, listed in WORDING

    `used to` counts as changelog only after a pronoun subject. In `the key used to sort`, it means
    employed for. A bare `now` is not flagged. `now that X` and `until now` are common in correct
    prose. A dash after a list-item term is a separator, not a clause join. Pragmas, section dividers
    and pasted usage lines (`$`, `>>>`) are skipped.

    Args:
        prose_lines: line number and text of each line of prose
        list_items: the lines that open a list item. A dash after the term is allowed on these lines
        checked_file: the file the lines come from

    Returns:
        One finding per rule and line.
    """
    WORDING = {
        # matches:
        # `Q08`  # noqa: NAR012
        # `R10-fence-form`  # noqa: NAR012
        # `R2b-B5`  # noqa: NAR012
        # `V-03`  # noqa: NAR012
        # rejects:
        # `Q8`
        'NAR012': re.compile(r'\b(?:Q\d{2}|R\d{1,2}[a-z]?-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*|V-\d\d)\b'),
        # matches:
        # `a -- b`  # noqa: NAR013
        # an em dash
        # rejects:
        # `a-b`
        # `--flag`
        'NAR013': re.compile(r'\s--\s|\u2014'),
        'NAR014': re.compile(r'\b(?:deliberately|on purpose|by design|intentionally)\b', re.IGNORECASE),
        'NAR015': re.compile(
            r'\b(?:no longer|any ?more|previously|this change|the old)\b'
            r'|\b(?:it|this|that|which|they|there)\s+used to\b',
            re.IGNORECASE,
        ),
        'NAR016': re.compile(r'\b(?:carr(?:y|ies|ied|ying)|hold(?:s|ing)?|held)\b', re.IGNORECASE),
        'NAR018': re.compile(r"\b(?:its|their|his|her|our|your|\w+'s) own\b", re.IGNORECASE),
    }

    # matches:
    # `a; b`
    # rejects:
    # `a;b`
    SEMICOLON = re.compile(r';(?:\s|$)')
    findings: list[Finding] = []
    for number, text in prose_lines:
        for code, pattern in WORDING.items():
            if code == 'NAR013' and number in list_items:
                continue
            if found := pattern.search(text):
                findings.append(Finding(checked_file, number, code, repr(found.group(0).strip())))
        # a semicolon in backticked code is code. A list item gets no semicolon exemption
        if SEMICOLON.search(re.sub(r'`[^`]*`', '', text)):
            findings.append(Finding(checked_file, number, 'NAR013', repr(';')))

    return findings


def listPage(
    listed: list[str],
    first: int,
    *,
    unit: str,
    option: list[str],
    arguments: Sequence[Path | str],
) -> list[str]:
    """Cut a review list to LIST_PAGE entries from entry `first`, counted from 1.

    Args:
        listed: Every entry of the list.
        first: The first entry to keep.
        unit: The entries in the plural, such as `sentences`, for the line on the entries left out.
        option: The program and the options of the command for the next entries, up to the number.
        arguments: The paths and options of the command for the next entries, after the number.

    Returns:
        The entries, then a line with the number left out and the command for the next entries.
    """
    end = first - 1 + LIST_PAGE
    page = listed[first - 1 : end]
    if end < len(listed):
        command = ' '.join([*option, str(end + 1), *(str(argument) for argument in arguments)])
        page.append(f'... {len(listed) - end} left out of {len(listed)} {unit}. For the next {LIST_PAGE}: {command}')
    return page


def readChangedLines(since: str, any_repo_path: Path, pattern: str) -> ChangedLines:
    """List the lines that the diff against merge-base(HEAD, since) adds or changes, per file that matches `pattern`.

    For a hunk that only deletes lines, the line below the deleted lines is listed, so a finding on that
    line is reported under --since. Every line of an untracked file is listed.

    Raises:
        GitError: git fails, or `since` names no commit.
    """
    # matches:
    # `@@ -10,2 +12,3 @@ def readPlan(path):`
    # `@@ -4 +4 @@`
    HUNK = re.compile(r'^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@')
    repo_root = Path(runGit(['rev-parse', '--show-toplevel'], any_repo_path).strip())
    base = runGit(['merge-base', 'HEAD', since], repo_root).strip()
    changed: ChangedLines = {}
    current: Path | None = None
    for diff_line in runGit(['diff', '-M', '--unified=0', base, '--', pattern], repo_root).splitlines():
        if diff_line.startswith('+++ '):
            new_name = diff_line.removeprefix('+++ ')
            current = None if new_name == '/dev/null' else (repo_root / new_name.removeprefix('b/')).resolve()
        elif current is not None and (hunk := HUNK.match(diff_line)):
            start, count = int(hunk['start']), int(hunk['count'] or '1')
            changed.setdefault(current, set()).update(range(start, start + count) if count else {start + 1})

    for untracked in runGit(['ls-files', '--others', '--exclude-standard', '--', pattern], repo_root).splitlines():
        untracked_path = (repo_root / untracked).resolve()
        line_count = len(untracked_path.read_text(encoding='utf-8', errors='replace').splitlines())
        changed.setdefault(untracked_path, set()).update(range(1, line_count + 1))
    return changed


def findFiles(directory: Path, pattern: str) -> list[Path]:
    """Find the files below a directory whose names match a glob.

    A directory below with its own `.git` entry is another checkout, such as the worktree of another
    branch in .claude/worktrees/, or a submodule. The files of another checkout are not the files of
    this one, so the walk does not enter it.

    Returns:
        The matching files, sorted.
    """
    found: list[Path] = []
    for current, subdirectories, names in os.walk(directory):
        subdirectories[:] = [name for name in subdirectories if not (Path(current) / name / '.git').exists()]
        found.extend(Path(current) / name for name in fnmatch.filter(names, pattern))
    return sorted(found)


def runGit(arguments: list[str], repo_path: Path) -> str:
    """Run one git command in the repository.

    Raises:
        GitError: git exits nonzero.
    """
    result = subprocess.run(['git', '-C', str(repo_path), *arguments], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise GitError(f'git {" ".join(arguments)} failed: {result.stderr.strip()}')
    return result.stdout


def inChange(changed_lines: set[int], spans: Spans, line: int) -> bool:
    return bool(spans.get(line, frozenset({line})) & changed_lines)


def changedLinesOf(changed: ChangedLines | None, checked_file: Path) -> set[int] | None:
    """Return the changed lines of a source file under --since, or None for a file that is checked whole.

    With no --since, and for a page, every line is checked.
    """
    if changed is None or isPage(checked_file):
        return None
    return changed.get(checked_file.resolve(), set())


def isPage(checked_file: Path) -> bool:
    return checked_file.suffix.lower() in prose.PROSE_SUFFIXES


### vocabulary #########################################################################


@dataclass(frozen=True)
class Finding:
    checked_file: Path
    line: int
    code: str
    detail: str

    def __str__(self) -> str:
        return f'{self.checked_file}:{self.line}: {self.code} {self.detail}'


class GitError(RuntimeError):
    pass


# the changed lines of each file, by resolved path
ChangedLines = dict[Path, set[int]]
# the lines that count for --since when a finding is on a line, by line
Spans = dict[int, frozenset[int]]
