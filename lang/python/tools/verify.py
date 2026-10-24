"""Run the whole Narrative toolchain over a path and report one line per tool.

Use this instead of calling the tools by hand. A hand-rolled loop counts findings by grepping tool
output, so a missing or misresolved binary produces empty output and reads as a pass. This script
resolves every tool to an absolute path and exits 2 if any one of them is absent, so a green result
means the tools ran.

This is the whole pipeline. Give it any path, and every Python file below the path is checked, so
no workflow is chosen at run time. A Markdown, HTML or plain text file named on the command line,
such as a README or a published page, gets the two prose checks only: the wording checks of checks.py
and agentverbs.py. pyproject.toml is required only when Python files are checked.

Unless nothing was checked, the output ends with three review lists, over the Python files and the
pages: every sentence, every subject that cannot act paired with the subject's verb, and every
sentence with a pronoun. On a failing run the lists are printed after the findings. Without --since,
each list stops after 1000 entries, with the command for the next 1000.

With --since REF, only the Python files that the diff against merge-base(HEAD, REF) adds or changes
are checked, and only the findings and list entries on changed lines are reported. A finding on a
`def` or `class` line counts for every line of the definition, and a finding in a comment or
docstring counts for every line of the passage. Under --since, a fix of `ruff check` is applied
only when the fix edits a changed line, and `ruff format` formats only the changed lines. A page is
checked whole.

The spaCy results of each passage are kept in .narrative_cache/ in the current directory, so a run
after a small change parses only the changed passages.

Order matters. `ruff check --fix` and `ruff format` converge in that order and not the other.

Usage:
    $ python3 verify.py src/                 # every .py below src/
    $ python3 verify.py src/loader.py src/report.py
    $ python3 verify.py . --no-fix           # report only, change nothing
    $ python3 verify.py . --venv .lintenv    # a venv other than the shared one (SHARED_VENV)
    $ python3 verify.py README.md docs/report.html
    $ python3 verify.py . --since origin/main     # only lines changed since merge-base(HEAD, origin/main)

Exit codes:
    0  every tool passed
    1  at least one tool had a finding
    2  the toolchain or the config is missing, so nothing was checked
"""

from __future__ import annotations

import argparse
import difflib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codeprose import changeSpans
from prose import PROSE_SUFFIXES
from wording import ChangedLines, GitError, Spans, findFiles, inChange, readChangedLines


TOOLS = ('ruff', 'pylint', 'mypy', 'vermin')
# agentverbs.py imports these, so they must be importable by the venv's interpreter
PARSER_MODULES = ('spacy', 'en_core_web_md')
PYTHON_FLOOR = '3.11'
# %LOCALAPPDATA% on Windows. $XDG_DATA_HOME, or ~/.local/share, on Linux and macOS
DATA_HOME = Path(os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
# the venv that the Setup step of SKILL.md creates, one per machine
SHARED_VENV = DATA_HOME / 'narrative' / 'lintenv'
# a Windows venv has its executables in Scripts, with an .exe suffix
VENV_BIN = 'Scripts' if sys.platform == 'win32' else 'bin'
VENV_PYTHON = 'python.exe' if sys.platform == 'win32' else 'python'
SKIPPED = frozenset({'.venv', 'venv', '.lintenv', '.git', 'build', 'dist', '__pycache__'})
# the spaCy results of agentverbs.py, in the directory of the run. .ruff_cache and .mypy_cache are there too
CACHE_DIR = Path('.narrative_cache')
# under --since, the most times that fixes are applied to one file. A fix that overlaps another is applied the next time
FIX_ROUNDS = 10
EXIT_SUCCESS = 0
EXIT_FINDINGS = 1
EXIT_NO_TOOLCHAIN = 2


def main() -> int:
    """Resolve the toolchain, run every check, and print one line per tool.

    Returns:
        0 when everything passed, 1 on findings, 2 when a tool could not be found.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--venv', type=Path, default=SHARED_VENV)
    parser.add_argument('--config', type=Path, default=Path('pyproject.toml'))
    parser.add_argument('--no-fix', action='store_true', help='report only, do not rewrite files')
    parser.add_argument(
        '--all-sentences',
        action='store_true',
        help='list every entry of the review lists, not the first 1000 of each',
    )
    parser.add_argument('--since', help='report only lines changed since merge-base(HEAD, SINCE)')
    args = parser.parse_args()
    print(f'narrative skill: {readInstalledVersion()}')

    toolchain = resolveToolchain(args.venv)
    if toolchain.missing:
        lock = Path(__file__).resolve().parent / 'requirements-lock.txt'
        install = f'uv pip install --python {args.venv / VENV_BIN / VENV_PYTHON} -r {lock}'
        print(f'toolchain incomplete: {", ".join(toolchain.missing)} not found', file=sys.stderr)
        print(f'  looked in {args.venv / VENV_BIN} and on PATH', file=sys.stderr)
        print(f'  fix: uv venv --python {PYTHON_FLOOR} {args.venv} && {install}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    code = discoverPython(args.paths)
    pages = [target for target in args.paths if target.is_file() and target.suffix.lower() in PROSE_SUFFIXES]
    try:
        changed = readChangedLines(args.since, Path.cwd(), '*.py') if args.since else None
    except GitError as exc:
        print(f'verify.py: {exc}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    if changed is not None:
        code = [path for path in code if path.resolve() in changed]
    if not code and not pages:
        print('nothing to check: no .py files found, and no .md, .html or .txt file named', file=sys.stderr)
        if changed is not None:
            print(
                f'  under --since, a .py file is checked only when a line changed since {args.since}',
                file=sys.stderr,
            )
        return EXIT_NO_TOOLCHAIN

    results: list[Result] = []
    if code:
        if (config_problem := checkConfig(args.config)) is not None:
            return config_problem
        code_targets = [str(p) for p in code]
        try:
            results.extend(runCodeTools(toolchain, args.config, code_targets, fix=not args.no_fix, since=args.since))
        except GitError as exc:
            print(f'verify.py: {exc}', file=sys.stderr)
            return EXIT_NO_TOOLCHAIN

    checker = Path(__file__).resolve().parent / 'checks.py'
    prose_targets = [str(p) for p in [*code, *pages]]
    since = ['--since', args.since] if args.since else []
    results.append(gradeChecks(run([sys.executable, str(checker), *prose_targets, *since])))
    if code:
        vermin_cmd = [toolchain.paths['vermin'], '--no-tips', f'-t={PYTHON_FLOOR}-', '--violations']
        results.append(gradeVermin(run([*vermin_cmd, *[str(p) for p in code]])))
    agent_verbs = Path(__file__).resolve().parent / 'agentverbs.py'
    cache = ['--cache', str(prepareCache())]
    results.append(gradeAgentVerbs(run([toolchain.python, str(agent_verbs), *prose_targets, *since, *cache])))

    width = max(len(r.tool) for r in results)
    for result in results:
        print(f'{result.tool:<{width}}  {result.summary}')

    failed = [r for r in results if not r.passed]
    if failed:
        # nobody should need to re-run a tool by hand to see why the tool failed
        for result in failed:
            print(f'\n--- {result.tool} ---')
            print(result.detail.rstrip() or '(no output)')

        # the lists are the same with or without findings. Fixing a finding rewrites sentences and changes the lists
        print('\n=== review lists from a failing run. Fix the findings above, then read the lists of the next run ===')
        printReviewLists(toolchain.python, [*prose_targets, *since], cache, all_sentences=args.all_sentences)
        print(f'\n{len(failed)} of {len(results)} checks failed')
        return EXIT_FINDINGS

    print(f'\nall {len(results)} checks passed')
    print('A pass is no evidence about the rules that no check implements. Read the lists below.')
    printReviewLists(toolchain.python, [*prose_targets, *since], cache, all_sentences=args.all_sentences)
    return EXIT_SUCCESS


def printReviewLists(python: str, arguments: list[str], cache: list[str], *, all_sentences: bool) -> None:
    """Print the three lists for Prose review in SKILL.md: sentences, agent verbs and pronouns.

    Args:
        python: The interpreter with the parser modules installed, for agentverbs.py.
        arguments: Every Python file and every page checked in this run, then the --since option.
        cache: The --cache option of agentverbs.py.
        all_sentences: List every entry, not only the first 1000 of each list.
    """
    checker = Path(__file__).resolve().parent / 'checks.py'
    agent_verbs = Path(__file__).resolve().parent / 'agentverbs.py'
    every = ['--all-sentences'] if all_sentences else []
    inventory = run([sys.executable, str(checker), '--prose', *every, *arguments])
    print('\n--- every sentence of every comment, docstring and page: read each against SKILL.md, Comments ---')
    print(inventory.text.rstrip() or '(none)')
    review = run([python, str(agent_verbs), '--review', *every, *arguments, *cache])
    print('\n--- every subject that cannot act, with its verb: can that subject perform that verb? ---')
    print(review.text.rstrip() or '(none)')
    pronouns = run([python, str(agent_verbs), '--pronouns', *every, *arguments, *cache])
    print('\n--- every sentence with a pronoun, after the one before it: which noun does each pronoun stand for? ---')
    print(pronouns.text.rstrip() or '(none)')


def checkConfig(config: Path) -> int | None:
    """Check that the config is a pyproject.toml with every Narrative section, and print the fix if not.

    Presence is not enough. Every real project already has a pyproject.toml, so present-but-wrong is
    the usual state. A tool with no Narrative section runs with the tool's defaults, and then double
    quotes and snake_case functions pass.

    Returns:
        None when the config is usable, otherwise the exit code for a missing toolchain.
    """
    snippet = Path(__file__).resolve().parent / 'pyproject-snippet.toml'
    # ruff reads any other file name as a ruff.toml, with the keys at the top level instead of under [tool.ruff]
    if config.name != 'pyproject.toml':
        print(f'config at {config} is not named pyproject.toml', file=sys.stderr)
        print(f'  fix: copy or merge {snippet} into a file named pyproject.toml', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    absent = missingConfigSections(config)
    if absent:
        print(f'config at {config} is not a Narrative config', file=sys.stderr)
        print(f'  missing: {", ".join(absent)}', file=sys.stderr)
        print('  the tools would fall back to their defaults and report a clean run', file=sys.stderr)
        print(f'  fix: merge {snippet} into {config}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN
    return None


def runCodeTools(
    toolchain: Toolchain,
    config: Path,
    targets: list[str],
    *,
    fix: bool,
    since: str | None,
) -> list[Result]:
    """Fix and format the Python files unless told not to, then run ruff, pylint and mypy.

    Order matters. `ruff check --fix` and `ruff format` converge in that order and not the other.
    Under --since, a fix is applied only when the fix edits a changed line, only the changed lines are
    formatted and checked for format, and the findings of ruff check, pylint and mypy are cut to the
    changed lines.

    Returns:
        One result per tool, in the order they ran.

    Raises:
        GitError: git fails when the changed lines are read again after a fix.
    """
    ruff_config = ['--config', str(config)]
    changed = readChangedLines(since, Path.cwd(), '*.py') if since else None
    if fix and since is None:
        run([toolchain.paths['ruff'], 'check', *ruff_config, '--fix', '-q', *targets])
        run([toolchain.paths['ruff'], 'format', *ruff_config, '-q', *targets])
    elif fix and since is not None and changed is not None:
        fixChangedLines(toolchain.paths['ruff'], ruff_config, targets, changed=changed)
        # a fix or ruff format can add or remove lines, so the changed lines are read again after each
        changed = readChangedLines(since, Path.cwd(), '*.py')
        formatRanges(toolchain.paths['ruff'], ruff_config, targets, changed, check=False)
        changed = readChangedLines(since, Path.cwd(), '*.py')

    check_cmd = [toolchain.paths['ruff'], 'check', *ruff_config, '--output-format=concise']
    mypy_cmd = [toolchain.paths['mypy'], '--config-file', str(config), '--strict', '--no-error-summary']
    if changed is None:
        format_output = run([toolchain.paths['ruff'], 'format', *ruff_config, '--check', *targets])
    else:
        format_output = formatRanges(toolchain.paths['ruff'], ruff_config, targets, changed, check=True)
    results = [
        gradeRuffCheck(run([*check_cmd, *targets])),
        gradeFormat(format_output),
        gradePylint(run([toolchain.paths['pylint'], f'--rcfile={config}', *targets])),
        gradeMypy(run([*mypy_cmd, *targets])),
    ]
    if changed is None:
        return results
    return [result if result.tool == 'ruff format' else keepChangedLines(result, changed) for result in results]


def fixChangedLines(ruff: str, ruff_config: list[str], targets: list[str], *, changed: ChangedLines) -> None:
    """Apply each safe fix of `ruff check` that edits a changed line, and no other fix.

    `ruff check --fix` has no line range. So each file is checked through stdin, and each fix of the
    JSON output is applied whole or not at all, the same as with `ruff check --fix`. A fix can leave a
    new finding with a fix, so the check runs again, up to FIX_ROUNDS times.
    """
    for target in targets:
        path = Path(target)
        source = path.read_text(encoding='utf-8')
        text = source
        lines = set(changed.get(path.resolve(), set()))
        for _ in range(FIX_ROUNDS):
            command = [ruff, 'check', *ruff_config, '--output-format=json', '--stdin-filename', target, '-']
            checked = subprocess.run(command, input=text, capture_output=True, text=True, check=False)
            if checked.returncode not in {0, 1}:
                break

            edits = changedLineEdits([RuffFix.parse(entry) for entry in json.loads(checked.stdout)], lines)
            if not edits:
                break

            fixed = applyEdits(text, edits)
            lines = movedLines(text, fixed, lines)
            text = fixed
        if text != source:
            path.write_text(text, encoding='utf-8')


def changedLineEdits(fixes: list[RuffFix | None], lines: set[int]) -> list[RuffEdit]:
    """Choose the edits of each safe fix with an edit on a changed line, leaving out a fix that overlaps a chosen one.

    Returns:
        The edits of the chosen fixes. The fixes left out are offered again on the next round.
    """
    chosen: list[RuffEdit] = []
    for fix in fixes:
        if fix is None or fix.applicability != 'safe' or not any(edit.rows() & lines for edit in fix.edits):
            continue
        if any(edit.overlaps(other) for edit in fix.edits for other in chosen):
            continue
        chosen.extend(fix.edits)
    return chosen


def applyEdits(text: str, edits: list[RuffEdit]) -> str:
    """Replace the text of each edit, from the last edit to the first, so an earlier position stays valid."""
    starts = [0, *itertools.accumulate(len(line) for line in text.splitlines(keepends=True))]
    for edit in sorted(edits, key=lambda edit: edit.start, reverse=True):
        first = starts[edit.start[0] - 1] + edit.start[1] - 1
        last = starts[edit.end[0] - 1] + edit.end[1] - 1
        text = text[:first] + edit.content + text[last:]
    return text


def movedLines(old_text: str, new_text: str, lines: set[int]) -> set[int]:
    """Map changed lines from the text before a round of fixes to the text after the round.

    A line that a fix wrote is a changed line too, because a fix is applied only on a changed line.
    """
    moved: set[int] = set()
    matcher = difflib.SequenceMatcher(a=old_text.splitlines(), b=new_text.splitlines(), autojunk=False)
    for tag, old_first, old_end, new_first, new_end in matcher.get_opcodes():
        if tag == 'equal':
            moved.update(
                new_first + 1 + offset for offset, old in enumerate(range(old_first + 1, old_end + 1)) if old in lines
            )
        else:
            moved.update(range(new_first + 1, new_end + 1))
    return moved


def formatRanges(
    ruff: str,
    ruff_config: list[str],
    targets: list[str],
    changed: ChangedLines,
    *,
    check: bool,
) -> Output:
    """Run `ruff format --range` once per run of changed lines in each file, to format or to check.

    Returns:
        The output of every run, with the highest exit code.
    """
    outputs: list[Output] = []
    for target in targets:
        lines = sorted(changed.get(Path(target).resolve(), set()))
        # a new range starts at each line that does not follow the line before
        starts = [line for index, line in enumerate(lines) if index == 0 or lines[index - 1] != line - 1]
        ends = [line for index, line in enumerate(lines) if index == len(lines) - 1 or lines[index + 1] != line + 1]
        for first, last in zip(starts, ends, strict=True):
            mode = ['--check'] if check else ['-q']
            outputs.append(run([ruff, 'format', *ruff_config, *mode, f'--range={first}-{last}', target]))
    return Output(max((output.code for output in outputs), default=0), ''.join(output.text for output in outputs))


def keepChangedLines(result: Result, changed: ChangedLines) -> Result:
    """Keep each line of a tool's output with a finding on a changed line.

    The lines of a finding come from codeprose.changeSpans(). An output with no line of the form
    `path.py:line:`, such as the error of a tool that did not start, is kept whole.

    Returns:
        The result with the kept lines, failed when a line is kept.
    """
    # matches:
    # `src/plan.py:12:5: E501 Line too long (121 > 120)`
    # `src/plan.py:30: error: Missing return statement  [return]`
    LOCATED = re.compile(r'^(?P<path>.+?\.py):(?P<line>\d+):')
    located = [(text, match) for text in result.detail.splitlines() if (match := LOCATED.match(text))]
    if not located:
        return result

    spans: dict[Path, Spans] = {}
    kept: list[str] = []
    for text, match in located:
        path = Path(match['path']).resolve()
        spans_of_file = spans.setdefault(path, changeSpans(path))
        if inChange(changed.get(path, set()), spans_of_file, int(match['line'])):
            kept.append(text)
    summary = f'{len(kept)} findings on changed lines' if kept else 'clean on changed lines'
    return Result(result.tool, not kept, summary, '\n'.join(kept))


def prepareCache() -> Path:
    """Create CACHE_DIR with a .gitignore of `*`, so git leaves the cache out. ruff and mypy do the same.

    Returns:
        The path of the cache file of agentverbs.py.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    ignore_path = CACHE_DIR / '.gitignore'
    if not ignore_path.exists():
        ignore_path.write_text('*\n', encoding='utf-8')
    return CACHE_DIR / 'prose-cache.json'


def discoverPython(paths: list[Path]) -> list[Path]:
    """Find every Python file at or below the given paths.

    A directory expands to everything below the directory, so one command covers a whole project. The
    worktrees of other branches below the directory are left out.
    """
    code: list[Path] = []
    for target in paths:
        found = findFiles(target, '*.py') if target.is_dir() else [target]
        code.extend(f for f in found if f.suffix == '.py' and not SKIPPED & set(f.parts))

    return code


def missingConfigSections(pyproject_path: Path) -> list[str]:
    """List the Narrative config sections missing from this file.

    Returns:
        Human-readable descriptions of what is absent. Empty when the config is usable.
    """
    if not pyproject_path.is_file():
        return [f'{pyproject_path} does not exist']

    try:
        text = pyproject_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        return [f'unreadable: {exc}']

    # TODO: parse with tomllib. A pattern can match inside a comment or under another table.
    required = (
        (r'\[tool\.ruff\]', '[tool.ruff]'),
        (r'\[tool\.ruff\.lint\]', '[tool.ruff.lint]'),
        (r'function-naming-style', '[tool.pylint.basic] function-naming-style'),
        (r'strict\s*=\s*true', '[tool.mypy] strict = true'),
    )

    return [label for pattern, label in required if not re.search(pattern, text)]


def readInstalledVersion() -> str:
    """Return the commit and date that install.sh wrote to INSTALLED beside this script."""
    stamp = Path(__file__).resolve().parent / 'INSTALLED'
    try:
        return stamp.read_text(encoding='utf-8').strip()
    except FileNotFoundError:
        return f'not installed by install.sh, running from {stamp.parent}'


def resolveToolchain(venv: Path) -> Toolchain:
    """Find every tool as an absolute path.

    A relative path breaks the moment anything changes directory, and then a missing binary looks
    like a clean run. The venv comes first, then PATH, and anything absent is reported.

    Args:
        venv: Directory of a virtual environment, searched before PATH.

    Returns:
        The resolved absolute paths, the interpreter that runs agentverbs.py, and the names of any
        tool or module that could not be found.
    """
    resolved: dict[str, str] = {}
    missing: list[str] = []

    for tool in TOOLS:
        # which() adds the .exe suffix on Windows
        in_venv = shutil.which(tool, path=str(venv / VENV_BIN))
        if in_venv:
            resolved[tool] = str(Path(in_venv).resolve())
            continue

        on_path = shutil.which(tool)
        if on_path:
            resolved[tool] = on_path
            continue

        missing.append(tool)

    # not resolved. The symlink's target runs without the venv's packages
    venv_python = (venv / VENV_BIN / VENV_PYTHON).absolute()
    python = str(venv_python) if venv_python.is_file() else sys.executable
    probe = 'import importlib.util, sys; sys.exit(any(importlib.util.find_spec(m) is None for m in sys.argv[1:]))'
    if run([python, '-c', probe, *PARSER_MODULES]).code != 0:
        missing.append(' and '.join(PARSER_MODULES))

    return Toolchain(resolved, python, tuple(missing))


def run(command: list[str]) -> Output:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return Output(completed.returncode, completed.stdout + completed.stderr)


def countFindingLines(output: Output) -> int:
    suffixes = ('.py', *PROSE_SUFFIXES)
    return sum(1 for line in output.text.splitlines() if any(f'{suffix}:' in line for suffix in suffixes))


def gradeRuffCheck(output: Output) -> Result:
    found = countFindingLines(output)
    return Result('ruff check', output.code == 0, 'clean' if output.code == 0 else f'{found} findings', output.text)


def gradeFormat(output: Output) -> Result:
    return Result('ruff format', output.code == 0, 'clean' if output.code == 0 else 'would reformat', output.text)


def gradePylint(output: Output) -> Result:
    found = countFindingLines(output)
    return Result('pylint', output.code == 0, 'clean' if output.code == 0 else f'{found} findings', output.text)


def gradeMypy(output: Output) -> Result:
    found = countFindingLines(output)
    return Result('mypy --strict', output.code == 0, 'clean' if output.code == 0 else f'{found} errors', output.text)


def gradeChecks(output: Output) -> Result:
    found = countFindingLines(output)
    return Result('checks.py', output.code == 0, 'clean' if output.code == 0 else f'{found} findings', output.text)


def gradeAgentVerbs(output: Output) -> Result:
    found = countFindingLines(output)
    return Result('agentverbs.py', output.code == 0, 'clean' if output.code == 0 else f'{found} findings', output.text)


def gradeVermin(output: Output) -> Result:
    # Vermin fails a file with no minimum version unless given `--violations`. A file with no version-specific
    # syntax shows as `~2, ~3` and counts as target-not-met.
    if output.code == 0:
        return Result('vermin', True, f'{PYTHON_FLOOR} or lower', output.text)

    lines = output.text.strip().splitlines()
    return Result('vermin', False, lines[-1] if lines else 'failed', output.text)


### vocabulary #########################################################################################


@dataclass(frozen=True)
class RuffEdit:
    """One edit of a ruff fix. A position is a row and a column, counted from 1, and the end is not part of the edit."""

    start: tuple[int, int]
    end: tuple[int, int]
    content: str

    def rows(self) -> set[int]:
        """Return the rows the edit covers. An end at column 1 ends at the row before, unless the edit inserts there."""
        last = self.end[0] - 1 if self.end[1] == 1 and self.end[0] > self.start[0] else self.end[0]
        return set(range(self.start[0], last + 1))

    def overlaps(self, other: RuffEdit) -> bool:
        # two edits that touch at one position overlap too, so their order never matters
        return self.start <= other.end and other.start <= self.end


@dataclass(frozen=True)
class RuffFix:
    applicability: str
    edits: list[RuffEdit]

    @classmethod
    def parse(cls, diagnostic: dict[str, Any]) -> RuffFix | None:
        """Read the fix of one diagnostic of `ruff check --output-format=json`, or None for no fix."""
        fix = diagnostic.get('fix')
        if not fix:
            return None
        edits = [
            RuffEdit(
                (edit['location']['row'], edit['location']['column']),
                (edit['end_location']['row'], edit['end_location']['column']),
                edit['content'],
            )
            for edit in fix['edits']
        ]
        return cls(fix['applicability'], edits)


@dataclass(frozen=True)
class Output:
    code: int
    text: str


@dataclass(frozen=True)
class Result:
    tool: str
    passed: bool
    summary: str
    detail: str


@dataclass(frozen=True, slots=True)
class Toolchain:
    paths: Mapping[str, str]
    python: str
    missing: tuple[str, ...]


if __name__ == '__main__':
    sys.exit(main())
