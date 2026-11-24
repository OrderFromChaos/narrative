"""Run the prose checks of nar:core over the comments of C, C++, JavaScript, TypeScript, and Verilog files, and pages.

A language with a Narrative skill, such as Python or Java, is checked by the verify.py of that skill. This verify.py
checks the languages whose comments codeprose.py reads, and a Markdown, HTML, or plain text page named on the command
line. A directory expands to the files of those languages below the directory. A path of `-` is a page read from stdin,
Markdown, or the suffix given with --stdin-suffix.

The steps, in order:
1. Each paragraph of a comment is filled again up to the line limit of the file. --since limits the re-wrap to
   paragraphs with a changed line. --no-fix skips the re-wrap, and each paragraph that the re-wrap would change is a
   NAR125 finding.
2. The wording checks NAR012 to NAR016 and NAR018 of wording.py run over the comment passages and the pages.
3. agentverbs.py runs with the interpreter of the lint venv.
4. verify.py writes four review lists to review-lists.txt in the cache directory. The path of the file and the number of
   entries in each list are on the last line of the output.

The four review lists:
- every sentence
- every subject that cannot act and the subject's verb
- every sentence with a pronoun
- every sentence with a free modifier

verify.py looks for the line limit of a file in the directory of the file and in each directory above the file up to the
repository root. The limit comes from the first of these directories with one of these files:
- an `.editorconfig` section for the file with `max_line_length`
- for a C or C++ file, a `.clang-format`
- for a JavaScript or TypeScript file, a prettier config

When a `.clang-format` doesn't have `ColumnLimit`, the limit is the limit of the `BasedOnStyle` style. When a prettier
config doesn't have `printWidth`, the limit is 80, the prettier default. If the directories up to the repository root
don't have one of these files, the limit is 120.

--since REF limits the check to the files and pages that the diff against merge-base(HEAD, REF) adds or changes, and
limits the findings and list entries to passages with a changed line. Each review list stops after 1000 entries, and the
last line of the list is the command for the next 1000. --since removes the limit.

Usage:
    $ python3 verify.py src/                     # every C, C++, JavaScript, TypeScript, and Verilog file below src/
    $ python3 verify.py src/engine.cpp README.md
    $ python3 verify.py . --since origin/main
    $ python3 verify.py . --no-fix               # report only, change nothing
    $ printf '%s\\n' "$DRAFT" | python3 verify.py - --cache-dir /tmp/narrative     # a page from stdin

Exit codes:
    0  every check passed
    1  at least one check had a finding
    2  the lint venv is missing, nothing was checked, a named file has no comment reader, or git failed for --since
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import codeprose
import prose
import rewrap
import wording
from wording import ChangedLines, Finding


# agentverbs.py imports these, so they must be importable by the venv's interpreter
PARSER_MODULES = ('spacy', 'en_core_web_md')
PYTHON_FLOOR = '3.11'
# %LOCALAPPDATA% on Windows. On Linux and macOS, $XDG_DATA_HOME, else ~/.local/share
DATA_HOME = Path(os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
# the lint venv of every language skill. A machine has one lint venv
SHARED_VENV = DATA_HOME / 'narrative' / 'lintenv'
# a Windows venv has its executables in Scripts, and the name of each executable ends in .exe
VENV_PYTHON = Path('Scripts/python.exe') if sys.platform == 'win32' else Path('bin/python')
SKIPPED = frozenset({'.git', 'node_modules', 'build', 'dist', 'out', 'vendor', 'third_party', '.narrative_cache'})
# the default cache directory: the spaCy results of agentverbs.py, a page read from stdin, and the four review lists
CACHE_DIR = Path('.narrative_cache')
LISTS_NAME = 'review-lists.txt'
STDIN_PATH = Path('-')
DEFAULT_WIDTH = rewrap.WIDTH
# the printWidth default of prettier
PRETTIER_WIDTH = 80
# the ColumnLimit of each BasedOnStyle of clang-format. clang-format doesn't limit lines when ColumnLimit is 0. LLVM is
# the style when the config doesn't have BasedOnStyle
CLANG_FORMAT_WIDTHS = {
    'llvm': 80,
    'google': 80,
    'chromium': 80,
    'mozilla': 80,
    'webkit': 0,
    'microsoft': 120,
    'gnu': 79,
}
C_SUFFIXES = frozenset({'.c', '.h', '.cc', '.cpp', '.cxx', '.hh', '.hpp', '.hxx', '.ipp', '.c++', '.h++'})
SCRIPT_SUFFIXES = frozenset({'.js', '.mjs', '.cjs', '.jsx', '.ts', '.mts', '.cts', '.tsx'})
EXIT_SUCCESS = 0
EXIT_FINDINGS = 1
EXIT_NO_TOOLCHAIN = 2


def main() -> int:
    """Check the named files and pages, print one line per check, and write the review lists."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--venv', type=Path, default=SHARED_VENV, help=f'the lint venv (default: {SHARED_VENV})')
    parser.add_argument('--no-fix', action='store_true', help='report only, do not re-wrap comments')
    parser.add_argument('--all-sentences', action='store_true', help='list every entry of the review lists')
    parser.add_argument('--from-sentence', type=int, default=1, help='start the list of sentences at this sentence')
    parser.add_argument('--since', help='report only lines changed since merge-base(HEAD, SINCE)')
    parser.add_argument('--cache-dir', type=Path, default=CACHE_DIR, help=f'the cache directory (default: {CACHE_DIR})')
    parser.add_argument('--stdin-suffix', default='.md', help='the suffix of a page read from stdin (default: .md)')
    args = parser.parse_args()
    print(f'narrative skill: {readInstalledVersion()}')

    python = args.venv.absolute() / VENV_PYTHON
    if not parserInstalled(python):
        lock = Path(__file__).resolve().parent / 'requirements-lock.txt'
        print(f'toolchain incomplete: {" and ".join(PARSER_MODULES)} not found for {python}', file=sys.stderr)
        print(
            f'  fix: uv venv --python {PYTHON_FLOOR} {args.venv} && uv pip install --python {python} -r {lock}',
            file=sys.stderr,
        )
        return EXIT_NO_TOOLCHAIN

    cache_dir = prepareCache(args.cache_dir)
    paths = [readStdinPage(cache_dir, args.stdin_suffix) if path == STDIN_PATH else path for path in args.paths]
    unreadable = [path for path in paths if path.is_file() and not (wording.isPage(path) or readable(path))]
    for path in unreadable:
        print(f'verify.py: no comment reader for {path}. For Python or Java, run the verify.py of that skill')
    if unreadable:
        return EXIT_NO_TOOLCHAIN

    sources = discoverSources(paths)
    pages = [path for path in paths if path.is_file() and wording.isPage(path)]
    try:
        changed = wording.readChangedLines(args.since, Path.cwd(), *codeprose.GIT_PATTERNS) if args.since else None
    except wording.GitError as exc:
        print(f'verify.py: {exc}', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    if changed is not None:
        sources = [path for path in sources if path.resolve() in changed]
    if not sources and not pages:
        print('nothing to check: no source file that codeprose.py reads, and no .md, .html or .txt file named')
        return EXIT_NO_TOOLCHAIN

    results: list[Result] = []
    if not args.no_fix:
        results.append(rewrapSources(sources, changed))
    results.append(checkWording(sources, pages, changed))
    targets = [str(path) for path in [*sources, *pages]]
    since = ['--since', args.since] if args.since else []
    cache = ['--cache', str(cache_dir / 'prose-cache.json')]
    agent_verbs = Path(__file__).resolve().parent / 'agentverbs.py'
    results.append(gradeAgentVerbs(run([str(python), str(agent_verbs), *targets, *since, *cache])))

    width = max(len(result.tool) for result in results)
    for result in results:
        print(f'{result.tool:<{width}}  {result.summary}')
    # the detail of a passing re-wrap has a line per re-wrapped file. Each line has the column of the file
    for result in results:
        if result.passed and result.detail:
            print(result.detail)
    failed = [result for result in results if not result.passed]
    for result in failed:
        print(f'\n--- {result.tool} ---')
        print(result.detail.rstrip() or '(no output)')
    print(f'\n{len(failed)} of {len(results)} checks failed' if failed else f'\nall {len(results)} checks passed')

    lists_path = cache_dir / LISTS_NAME
    review = ReviewRun(
        python=str(python),
        paths=[*sources, *pages],
        options=[*since, *cache],
        from_sentence=args.from_sentence,
        all_sentences=args.all_sentences,
        changed=changed,
    )
    counts = writeReviewLists(review, lists_path)
    if counts is None:
        print('verify.py: a review list command failed, so no review list was written', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN
    if failed:
        print(f'Review lists of this failing run: {counts} in {lists_path}. Take Prose review from the next run.')
        return EXIT_FINDINGS
    print(f'Prose review: read the {counts} in {lists_path}')
    return EXIT_SUCCESS


def discoverSources(paths: list[Path]) -> list[Path]:
    """Find every file at or below the given paths that codeprose.py reads. Build and vendored directories are
    skipped."""
    found: list[Path] = []
    for target in paths:
        if target.is_dir():
            below = wording.findFiles(target, *codeprose.GIT_PATTERNS)
            found.extend(path for path in below if not SKIPPED & set(path.relative_to(target).parts))
        elif codeprose.readable(target.suffix):
            found.append(target)
    return found


def rewrapSources(sources: list[Path], changed: ChangedLines | None) -> Result:
    """Fill the paragraphs of the comments of each file again up to the line limit of the file, and write the file."""
    rewrapped: list[str] = []
    for source_path in sources:
        source = source_path.read_text(encoding='utf-8')
        width = readLineLimit(source_path)
        blocks = codeprose.commentBlocks(source, source_path.suffix)
        filled = rewrap.rewrapSource(source, blocks, wording.changedLinesOf(changed, source_path), width=width)
        if filled != source:
            source_path.write_text(filled, encoding='utf-8')
            rewrapped.append(f'{source_path}: re-wrapped at column {width}')
    return Result('rewrap', True, f'{len(rewrapped)} files re-wrapped', '\n'.join(rewrapped))


def checkWording(sources: list[Path], pages: list[Path], changed: ChangedLines | None) -> Result:
    """Run the wording checks and NAR125 over each file, and the wording checks over each page."""
    findings: list[Finding] = []
    for source_path in sources:
        found = checkSource(source_path)
        if (changed_lines := wording.changedLinesOf(changed, source_path)) is not None:
            spans = codeprose.changeSpans(source_path)
            found = [f for f in found if f.code == 'NAR000' or wording.inChange(changed_lines, spans, f.line)]
        findings.extend(found)
    for page in pages:
        found = wording.checkPage(page)
        if (changed_lines := wording.changedLinesOf(changed, page)) is not None:
            spans = wording.pageSpans(page)
            found = [f for f in found if f.code == 'NAR000' or wording.inChange(changed_lines, spans, f.line)]
        findings.extend(found)
    findings.sort(key=lambda finding: (str(finding.checked_file), finding.line))
    detail = '\n'.join(
        f'{finding}: {wording.RULES[finding.code]}' if finding.code in wording.RULES else str(finding)
        for finding in findings
    )
    return Result('wording', not findings, 'clean' if not findings else f'{len(findings)} findings', detail)


def checkSource(source_path: Path) -> list[Finding]:
    """Flag the wording of the comment passages of one file, and each paragraph that the re-wrap would change.

    Returns:
        Every finding that no `// noqa` on the line of the finding silences, or a single NAR000 for a file that cannot
        be read.
    """
    try:
        source = source_path.read_text(encoding='utf-8')
    except OSError as exc:
        return [Finding(source_path, 0, 'NAR000', f'unreadable: {exc.strerror}')]
    except UnicodeDecodeError as exc:
        return [Finding(source_path, 0, 'NAR000', f'not UTF-8: {exc.reason}')]

    passages = codeprose.passages(source, source_path.suffix)
    prose_lines = [line for passage in passages for line in zip(passage.lines, passage.texts, strict=True)]
    list_items = {passage.lines[0] for passage in passages if passage.list_item}
    findings = wording.wordingFindings(prose_lines, list_items, source_path)
    width = readLineLimit(source_path)
    blocks = codeprose.commentBlocks(source, source_path.suffix)
    detail = f'paragraph not filled up to column {width}. verify.py re-wraps the paragraph'
    findings.extend(
        Finding(source_path, number, rewrap.RULE, detail)
        for number in rewrap.unfilledLines(source, blocks, None, width=width)
    )
    silenced = silencedCodes(source)
    return [finding for finding in findings if not silenced.get(finding.line, set()) & {finding.code, 'ALL'}]


def silencedCodes(source: str) -> dict[int, set[str]]:
    """Map each line with a `// noqa` to the codes that the noqa silences, or `{'ALL'}` for a bare `// noqa`."""
    silenced: dict[int, set[str]] = {}
    for number, line in enumerate(source.splitlines(), start=1):
        if found := codeprose.NOQA.search(line):
            codes = {code.strip() for code in (found['codes'] or '').split(',') if code.strip()}
            silenced[number] = codes or {'ALL'}
    return silenced


def readLineLimit(source_path: Path) -> int:
    """Find the last column of a comment line of one file from the configs in the module docstring.

    Returns:
        The column, or DEFAULT_WIDTH when the configs up to the repository root don't have a line limit.
    """
    resolved = source_path.resolve()
    for directory in resolved.parents:
        if (width := editorconfigWidth(directory, resolved)) is not None:
            return width
        if resolved.suffix.lower() in C_SUFFIXES and (width := clangFormatWidth(directory)) is not None:
            return width
        if resolved.suffix.lower() in SCRIPT_SUFFIXES and (width := prettierWidth(directory)) is not None:
            return width
        if (directory / '.git').exists():
            break
    return DEFAULT_WIDTH


def editorconfigWidth(directory: Path, source_path: Path) -> int | None:
    """Read `max_line_length` from the last section of `directory/.editorconfig` with the key that matches the file.

    Returns:
        The width, or None when the sections for the file don't have the key or the value is `off`.
    """
    # matches:
    # `[*.{c,h}]`
    SECTION = re.compile(r'^\s*\[(?P<glob>.+)\]\s*$')
    # matches:
    # `max_line_length = 100`
    MAX_LINE = re.compile(r'^\s*max_line_length\s*=\s*(?P<value>\w+)', re.IGNORECASE)
    try:
        lines = (directory / '.editorconfig').read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    relative = source_path.relative_to(directory).as_posix()
    width: int | None = None
    matching = False
    for line in lines:
        if section := SECTION.match(line):
            matching = editorconfigMatches(section['glob'], relative)
        elif matching and (setting := MAX_LINE.match(line)):
            value = setting['value']
            width = int(value) if value.isdigit() else None
    return width


def editorconfigMatches(glob: str, relative: str) -> bool:
    """Decide whether an `.editorconfig` section glob such as `*.{c,h}` or `src/**.js` matches `relative`.

    `relative` is the path of the source file from the directory of the `.editorconfig`.

    A glob with no `/` matches the file name in any directory below, and `{a,b}` matches either word.
    """
    # matches:
    # `{c,h}`
    BRACES = re.compile(r'\{([^{}]*,[^{}]*)\}')
    if found := BRACES.search(glob):
        return any(
            editorconfigMatches(glob[: found.start()] + word + glob[found.end() :], relative)
            for word in found[1].split(',')
        )
    pattern = glob.lstrip('/').replace('**', '*')
    if '/' not in glob:
        return fnmatch.fnmatchcase(relative.rsplit('/', 1)[-1], pattern)
    return fnmatch.fnmatchcase(relative, pattern)


def clangFormatWidth(directory: Path) -> int | None:
    """Read the line limit from `.clang-format` or `_clang-format` in `directory`.

    Returns:
        `ColumnLimit`, else the limit of `BasedOnStyle`, else the LLVM limit. None when `directory` doesn't have a
        config, or when the limit is 0. clang-format doesn't limit the line length at 0.
    """
    # matches:
    # `ColumnLimit: 100`
    COLUMN_LIMIT = re.compile(r'^ColumnLimit:\s*(?P<width>\d+)', re.MULTILINE)
    # matches:
    # `BasedOnStyle: Google`
    BASED_ON = re.compile(r'^BasedOnStyle:\s*(?P<style>\w+)', re.MULTILINE)
    for name in ('.clang-format', '_clang-format'):
        try:
            config = (directory / name).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        if limit := COLUMN_LIMIT.search(config):
            width = int(limit['width'])
        elif style := BASED_ON.search(config):
            width = CLANG_FORMAT_WIDTHS.get(style['style'].lower(), CLANG_FORMAT_WIDTHS['llvm'])
        else:
            width = CLANG_FORMAT_WIDTHS['llvm']
        return width or None
    return None


def prettierWidth(directory: Path) -> int | None:
    """Read `printWidth` from a prettier config in `directory`, or from the `prettier` key of `package.json`.

    Returns:
        The width, PRETTIER_WIDTH for a config with no `printWidth`, or None with no config.
    """
    # matches:
    # `"printWidth": 100`
    # `printWidth: 100`
    PRINT_WIDTH = re.compile(r'["\']?printWidth["\']?\s*[:=]\s*(?P<width>\d+)')
    for name in (
        '.prettierrc',
        '.prettierrc.json',
        '.prettierrc.json5',
        '.prettierrc.yaml',
        '.prettierrc.yml',
        '.prettierrc.toml',
    ):
        try:
            config = (directory / name).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        found = PRINT_WIDTH.search(config)
        return int(found['width']) if found else PRETTIER_WIDTH
    try:
        package = json.loads((directory / 'package.json').read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    settings = package.get('prettier') if isinstance(package, dict) else None
    if not isinstance(settings, dict):
        return None
    width = settings.get('printWidth', PRETTIER_WIDTH)
    return width if isinstance(width, int) else PRETTIER_WIDTH


def writeReviewLists(review: ReviewRun, lists_path: Path) -> str | None:
    """Write the four lists of Prose review to `lists_path`: sentences, agent verbs, pronouns, and free modifiers.

    Returns:
        The number of entries in each list, such as
        `12 sentences, 3 pairs, 1 pronoun sentences and 2 free modifier sentences`. None when the command of a list
        exits nonzero.
    """
    agent_verbs = Path(__file__).resolve().parent / 'agentverbs.py'
    every = ['--all-sentences'] if review.all_sentences else []
    targets = [str(path) for path in review.paths]
    sentences = listSentences(review.paths, review.changed)
    if review.changed is None and not review.all_sentences:
        option = ['verify.py', '--no-fix', '--from-sentence']
        sentences = wording.listPage(
            sentences,
            review.from_sentence,
            unit='sentences',
            option=option,
            arguments=targets,
        )
    review_lists = (
        (
            'sentences',
            '--- every sentence of every comment and page: read each against nar:core, Comments ---',
            Output(0, '\n'.join(sentences)),
        ),
        (
            'pairs',
            '--- every subject that cannot act, with its verb: can that subject perform that verb? ---',
            run([review.python, str(agent_verbs), '--review', *every, *targets, *review.options]),
        ),
        (
            'pronoun sentences',
            '--- every sentence with a pronoun, after the one before it: which noun does each pronoun stand for? ---',
            run([review.python, str(agent_verbs), '--pronouns', *every, *targets, *review.options]),
        ),
        (
            'free modifier sentences',
            '--- every sentence with a free modifier, a phrase without a verb after a comma: write the phrase as a'
            ' clause or a separate sentence, or cut the phrase ---',
            run([review.python, str(agent_verbs), '--free-modifiers', *every, *targets, *review.options]),
        ),
    )
    if any(listed.code != 0 for _unit, _heading, listed in review_lists):
        return None

    written: list[str] = []
    counts: list[str] = []
    for unit, heading, listed in review_lists:
        written.extend([heading, listed.text.rstrip() or '(none)', ''])
        counts.append(f'{wording.countEntries(listed.text.splitlines())} {unit}')
    lists_path.write_text('\n'.join(written), encoding='utf-8')
    return f'{", ".join(counts[:-1])} and {counts[-1]}'


def listSentences(paths: list[Path], changed: ChangedLines | None) -> list[str]:
    """List every sentence of every comment passage and page passage as `path:line: sentence`.

    The sentences of each file are in line order.

    When `changed` is given, only the passages with a changed line are listed.
    """
    listed: list[str] = []
    for checked_path in paths:
        if wording.isPage(checked_path):
            passages = prose.readPassages(checked_path)
        else:
            passages = codeprose.passages(checked_path.read_text(encoding='utf-8'), checked_path.suffix)
        changed_lines = wording.changedLinesOf(changed, checked_path)
        kept = [passage for passage in passages if changed_lines is None or changed_lines & set(passage.lines)]
        sentences = sorted((pair for passage in kept for pair in passage.sentences()), key=lambda pair: pair[0])
        listed.extend(f'{checked_path}:{line}: {sentence}' for line, sentence in sentences)
    return listed


def readable(source_path: Path) -> bool:
    return codeprose.readable(source_path.suffix)


def parserInstalled(python: Path) -> bool:
    if not python.is_file():
        return False
    probe = 'import importlib.util, sys; sys.exit(any(importlib.util.find_spec(m) is None for m in sys.argv[1:]))'
    return run([str(python), '-c', probe, *PARSER_MODULES]).code == 0


def prepareCache(cache_dir: Path) -> Path:
    """Create the cache directory with a .gitignore of `*`, so git leaves the cache out.

    Returns:
        The cache directory.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    ignore_path = cache_dir / '.gitignore'
    if not ignore_path.exists():
        ignore_path.write_text('*\n', encoding='utf-8')
    return cache_dir


def readStdinPage(cache_dir: Path, suffix: str) -> Path:
    """Save the page on stdin in the cache directory, so the checks can read the page as a file.

    Returns:
        The path of the saved page.
    """
    page_path = cache_dir / f'stdin{suffix}'
    page_path.write_text(sys.stdin.read(), encoding='utf-8')
    return page_path


def readInstalledVersion() -> str:
    """Name the installed version: the plugin and the plugin commit, the stamp of install.sh, or the directory.

    Each version in the plugin cache is at `<cache>/<marketplace>/<plugin>/<commit>/skills/<skill>/`.
    """
    skill_dir = Path(__file__).resolve().parent
    in_cache = len(skill_dir.parents) > 4 and skill_dir.parents[4].name == 'cache' and skill_dir.parent.name == 'skills'
    if in_cache:
        plugin_root = skill_dir.parents[1]
        return f'plugin {plugin_root.parent.name}@{plugin_root.parents[1].name} at {plugin_root.name}'
    try:
        return (skill_dir / 'INSTALLED').read_text(encoding='utf-8').strip()
    except FileNotFoundError:
        return f'running from {skill_dir}'


def run(command: list[str]) -> Output:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return Output(completed.returncode, completed.stdout + completed.stderr)


def gradeAgentVerbs(output: Output) -> Result:
    found = sum(1 for line in output.text.splitlines() if re.match(r'^\S+:\d+: NAR\d{3}', line))
    return Result('agentverbs.py', output.code == 0, 'clean' if output.code == 0 else f'{found} findings', output.text)


### vocabulary #########################################################################################


@dataclass(frozen=True)
class Output:
    code: int
    text: str


@dataclass(frozen=True)
class ReviewRun:
    """What the review lists of one run cover. `options` has the --since and --cache options of agentverbs.py."""

    python: str
    paths: list[Path]
    options: list[str]
    from_sentence: int
    all_sentences: bool
    changed: ChangedLines | None


@dataclass(frozen=True)
class Result:
    tool: str
    passed: bool
    summary: str
    detail: str


if __name__ == '__main__':
    sys.exit(main())
