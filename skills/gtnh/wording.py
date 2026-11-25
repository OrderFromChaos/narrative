"""`wording.py` has the wording checks and the --since helpers. The checkers of every language of Narrative import the
module.

NAR012 to NAR016, NAR018, and NAR024 flag wording that a comment, docstring or published page doesn't need. The checks
read lines of prose. A language's checker passes in the lines of the language's comments and doc comments, and
checkPage() reads a Markdown, HTML or plain text page through prose.py. checkPage() also reports NAR028 on a page: a
release named by the release's place in the history, such as `older bundles`, in a sentence without a version number or
a date.

listSections() lists each section of a page with the section's size, for the section list of verify.py. pageSize()
compares the words of a page with the words of the page at a commit, for verify.py --cleanup.

readChangedLines() lists the lines that the diff against a base branch adds or changes, for --since. pageSpans() maps
each line of a page to the lines of the line's passage, for --since. countEntries() counts the entries of a review list,
for the last line of verify.py. findFiles() lists the files of a directory, and does not enter another checkout below
the directory.

Usage, from a script in this directory:
    import wording
    findings = wording.wordingFindings(prose_lines, list_items, checked_file)
    findings = wording.checkPage(Path('README.md'))
"""

from __future__ import annotations

import fnmatch
import itertools
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
    'NAR024': 'contrast with ", not" or "not merely". State the fact, and a fact about the other thing separately',
    'NAR028': 'release named by its place in the history, on a page. Write the version number or the date',
    'NAR000': 'file could not be read or parsed',
}

# the number of entries of each review list without --since and --all-sentences: the sentences of --prose, and the pairs
# and the pronoun sentences of agentverbs.py
LIST_PAGE = 1000
# matches the last line of a list cut by listPage():
# `... 412 left out of 1412 sentences. For the next 1000: checks.py --prose --from-sentence 1001 src/`
LEFT_OUT = re.compile(r'^\.\.\. \d+ left out of (?P<total>\d+) ')
# the heading of the section list of verify.py
SECTIONS_HEADING = (
    '--- each section of each page, with the words and the lines: what does the reader of the page do with the'
    ' section? Label the section keep, move or cut ---'
)
# the git pathspecs of a page
PAGE_PATTERNS = tuple(sorted(f'*{suffix}' for suffix in prose.PROSE_SUFFIXES))


def checkPage(checked_file: Path) -> list[Finding]:
    """Run the wording checks over the passages of a Markdown, HTML or plain text file.

    Returns:
        Every finding not silenced by a `<!-- noqa -->` comment, or a single NAR000 if the file could not be read.
    """
    try:
        source = checked_file.read_text(encoding='utf-8')
    except OSError as exc:
        return [Finding(checked_file, 0, 'NAR000', f'unreadable: {exc.strerror}')]
    except UnicodeDecodeError as exc:
        return [Finding(checked_file, 0, 'NAR000', f'not UTF-8: {exc.reason}')]

    passages = prose.textPassages(source, checked_file.suffix)
    prose_lines = [line for passage in passages for line in zip(passage.lines, passage.texts, strict=True)]
    list_items = {passage.lines[0] for passage in passages if passage.list_item}
    suppressed = prose.suppressedCodes(source)
    findings = [*wordingFindings(prose_lines, list_items, checked_file), *undatedReleases(passages, checked_file)]
    return [f for f in findings if not (suppressed.get(f.line, set()) & {f.code, 'ALL'})]


def undatedReleases(passages: list[prose.Passage], checked_file: Path) -> list[Finding]:
    """Flag NAR028: a release named by the release's place in the history, in a sentence without a version or a date.

    A reader of `bundles before this version` can't tell which release the sentence means, and the meaning changes with
    each release. A version number or a date anywhere in the sentence counts, so
    `bundles from earlier versions of pack 2.9.0` isn't flagged. A phrase in backticks is a quoted example, and isn't
    flagged either.

    Returns:
        One finding per phrase, on the line where the phrase starts.
    """
    # matches:
    # `before this version`
    # `the current release`
    # `older bundles`
    # `earlier versions`
    # rejects:
    # `the version field`
    RELATIVE = re.compile(
        r'\b(?:this|the current|the latest|the new)\s+(?:version|release|build)\b'
        r'|\b(?:earlier|older|previous|prior|newer|recent|later)\s+(?:versions?|releases?|builds?|bundles?)\b',
        re.IGNORECASE,
    )
    # matches:
    # `v1.0.0`, `2.9.1`, `v0.6`
    # `2026-04-13`, `2026-04`, `in 2024`, `March 2025`
    DATED = re.compile(
        r'\bv?\d+\.\d+\.\d+\b|\bv\d+(?:\.\d+)?\b|\b\d{4}-\d{2}\b|\b(?:19|20)\d{2}\b',
        re.IGNORECASE,
    )
    findings: list[Finding] = []
    for passage in passages:
        cursor = 0
        for sentence in prose.SENTENCE_BREAK.split(passage.text.strip()):
            if not sentence:
                continue
            cursor = max(passage.text.find(sentence, cursor), 0)
            # a phrase in backticks is a quoted example, such as a rule's example of the phrase. Each span becomes
            # spaces of the same length, so an offset in `masked` is an offset in the sentence
            masked = re.sub(r'`[^`]*`', lambda span: ' ' * len(span.group(0)), sentence)
            if not DATED.search(sentence):
                for found in RELATIVE.finditer(masked):
                    phrase = ' '.join(found.group(0).split())
                    findings.append(
                        Finding(checked_file, passage.lineAt(cursor + found.start()), 'NAR028', repr(phrase)),
                    )
            cursor += len(sentence)
    return findings


def listSections(page: Path, changed_lines: set[int] | None) -> list[str]:
    """List each section of a page with the section's size, for the section list of verify.py.

    A section runs from a heading to the next heading of any level, so each subsection is a separate entry. The words
    are the words of the prose, without the headings and the code blocks. A page without a heading is one entry.

    Args:
        page: A Markdown, HTML or plain text page.
        changed_lines: Under --since, the changed lines of the page, and only a section with a changed line is listed.
            None without --since.

    Returns:
        One entry per section, such as `README.md:20: ### Server install: 78 words, 7 lines (6% of the page)`.
    """
    passages = prose.readPassages(page)
    line_count = len(page.read_text(encoding='utf-8').splitlines())
    # the words of the headings count for no section, so the shares of the sections add up to 100%
    total = sum(len(passage.text.split()) for passage in passages if not passage.heading) or 1
    starts = [passage for passage in passages if passage.heading]
    if not starts or passages[0].lines[0] < starts[0].lines[0]:
        starts.insert(0, prose.Passage((1,), ('(the text before the first heading)',)))
    listed: list[str] = []
    for start, after in itertools.zip_longest(starts, starts[1:]):
        first = start.lines[0]
        end = after.lines[0] if after else line_count + 1
        if changed_lines is not None and not changed_lines & set(range(first, end)):
            continue
        words = sum(
            len(passage.text.split()) for passage in passages if first <= passage.lines[0] < end and not passage.heading
        )
        title = f'{"#" * start.heading} {start.text}' if start.heading else start.text
        size = f'{plural(words, "word")}, {plural(end - first, "line")} ({round(100 * words / total)}% of the page)'
        listed.append(f'{page}:{first}: {title}: {size}')
    return listed


def pageSize(page: Path, since: str | None) -> str:
    """Compare the words of a page with the words of the page at HEAD, or at merge-base(HEAD, since), for verify.py
    --cleanup.

    Returns:
        A line such as `README.md: 1,210 words, 2,950 at HEAD (-59%)`. When the page isn't in that commit, the line has
        the reason.
    """
    now = countWords(page.read_text(encoding='utf-8'), page.suffix)
    try:
        repo_root = Path(runGit(['rev-parse', '--show-toplevel'], page.resolve().parent).strip())
        base, name = (
            ('HEAD', 'HEAD') if since is None else (runGit(['merge-base', 'HEAD', since], repo_root).strip(), since)
        )
        relative = page.resolve().relative_to(repo_root).as_posix()
        before = countWords(runGit(['show', f'{base}:{relative}'], repo_root), page.suffix)
    except GitError:
        return f'{page}: {now:,} words. The page is not in HEAD of a git repository, so the page has no size to compare'
    if not before:
        return f'{page}: {now:,} words, 0 at {name}'
    return f'{page}: {now:,} words, {before:,} at {name} ({round(100 * (now - before) / before):+d}%)'


def plural(count: int, noun: str) -> str:
    return f'{count} {noun}' if count == 1 else f'{count} {noun}s'


def countWords(text: str, suffix: str) -> int:
    return sum(len(passage.text.split()) for passage in prose.textPassages(text, suffix))


def wordingFindings(prose_lines: list[tuple[int, str]], list_items: set[int], checked_file: Path) -> list[Finding]:
    """Flag seven kinds of wording that no comment, docstring, or published page needs.

    - NAR012: a decision id, unresolvable outside the repository where the id was recorded
    - NAR013: a dash or a semicolon joining clauses, outside backticked code
    - NAR014: reassurance words, listed in WORDING
    - NAR015: changelog wording about code that is gone
    - NAR016: a container verb on a subject that is not a container, listed in WORDING
    - NAR018: a possessive followed by `own`, listed in WORDING
    - NAR024: a contrast with `, not` or `not merely`, outside backticked code: `amounts are in cents, not dollars`.
      `, not only`, `, not yet`, `, not even`, `, not necessarily` and `, not always` are left out

    `used to` counts as changelog only after a pronoun subject. In `the key used to sort`, it means employed for. A bare
    `now` is not flagged. `now that X` and `until now` are common in correct prose. A dash after a list-item term is a
    separator, and doesn't join clauses. Pragmas, section dividers, and pasted usage lines (`$`, `>>>`) are skipped.

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
    # matches:
    # `amounts are in cents, not dollars`
    # `where the contract is complex, not merely where the body is long`
    # rejects:
    # `not only the first file, not yet the second`
    CONTRAST = re.compile(r',\s+not\s+(?!only\b|yet\b|even\b|necessarily\b|always\b)|\bnot merely\b', re.IGNORECASE)
    findings: list[Finding] = []
    following = {number: text for number, text in prose_lines}
    for number, text in prose_lines:
        # A phrase such as `, not` can wrap onto the next line, so each pattern reads the line and the next line. A
        # match counts for the line where the match starts.
        joined = f'{text} {following.get(number + 1, "")}'
        for code, pattern in WORDING.items():
            if code == 'NAR013' and number in list_items:
                continue
            if (found := pattern.search(joined)) and found.start() < len(text):
                findings.append(Finding(checked_file, number, code, repr(' '.join(found.group(0).split()))))
        # a semicolon in backticked code is code. A list item doesn't get a semicolon exemption. Each backtick span
        # becomes spaces of the same length, so an offset in `masked` is an offset in `joined`
        masked = re.sub(r'`[^`]*`', lambda span: ' ' * len(span.group(0)), joined)
        if SEMICOLON.search(masked[: len(text)]):
            findings.append(Finding(checked_file, number, 'NAR013', repr(';')))
        if (found := CONTRAST.search(masked)) and found.start() < len(text):
            findings.append(Finding(checked_file, number, 'NAR024', repr(' '.join(found.group(0).split()))))

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


def readChangedLines(since: str, any_repo_path: Path, *patterns: str) -> ChangedLines:
    """List the lines that the diff against merge-base(HEAD, since) adds or changes in each page and in each file that
    `patterns` matches.

    For a hunk that only deletes lines, the line below the deleted lines is listed, so a finding on that line is
    reported under --since. Every line of an untracked file is listed.

    Raises:
        GitError: git fails, or `since` isn't a commit.
    """
    # matches:
    # `@@ -10,2 +12,3 @@ def readPlan(path):`
    # `@@ -4 +4 @@`
    HUNK = re.compile(r'^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@')
    repo_root = Path(runGit(['rev-parse', '--show-toplevel'], any_repo_path).strip())
    base = runGit(['merge-base', 'HEAD', since], repo_root).strip()
    patterns = (*patterns, *PAGE_PATTERNS)
    changed: ChangedLines = {}
    current: Path | None = None
    for diff_line in runGit(['diff', '-M', '--unified=0', base, '--', *patterns], repo_root).splitlines():
        if diff_line.startswith('+++ '):
            new_name = diff_line.removeprefix('+++ ')
            current = None if new_name == '/dev/null' else (repo_root / new_name.removeprefix('b/')).resolve()
        elif current is not None and (hunk := HUNK.match(diff_line)):
            start, count = int(hunk['start']), int(hunk['count'] or '1')
            changed.setdefault(current, set()).update(range(start, start + count) if count else {start + 1})

    for untracked in runGit(['ls-files', '--others', '--exclude-standard', '--', *patterns], repo_root).splitlines():
        untracked_path = (repo_root / untracked).resolve()
        line_count = len(untracked_path.read_text(encoding='utf-8', errors='replace').splitlines())
        changed.setdefault(untracked_path, set()).update(range(1, line_count + 1))
    return changed


def pageSpans(page: Path) -> Spans:
    """Map each line of a page passage to every line of the same passage. Those lines count for --since.

    Returns:
        The lines of the passage, by line. Empty for a page that cannot be read.
    """
    try:
        passages = prose.readPassages(page)
    except (OSError, UnicodeDecodeError):
        return {}
    return {line: frozenset(passage.lines) for passage in passages for line in passage.lines}


def countEntries(listed: list[str]) -> int:
    """Count the entries of one review list, from the lines of --prose, --review or --pronouns.

    A list cut by listPage() ends with the count of every entry, and that count is returned.
    """
    entries = [line for line in listed if line.strip() and line != '(none)']
    if entries and (cut := LEFT_OUT.match(entries[-1])):
        return int(cut['total'])
    return len(entries)


def findFiles(directory: Path, *patterns: str) -> list[Path]:
    """Find the files below a directory whose names match one of the globs.

    A directory below with a `.git` entry is another checkout, such as the worktree of another branch in
    .claude/worktrees/, or a submodule. The files of another checkout are not the files of this one, so the walk does
    not enter another checkout.

    Returns:
        The matching files, sorted.
    """
    found: list[Path] = []
    for current, subdirectories, names in os.walk(directory):
        subdirectories[:] = [name for name in subdirectories if not (Path(current) / name / '.git').exists()]
        found.extend(
            Path(current) / name for name in names if any(fnmatch.fnmatch(name, pattern) for pattern in patterns)
        )
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
    """Return the changed lines of a source file or a page under --since, or None without --since."""
    if changed is None:
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
