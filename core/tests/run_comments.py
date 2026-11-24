"""Check the comment readers of core/tools against expected files, and against gcc and node.

Each fixture is core/tests/comments/<directory>/<name>.<suffix>. codeprose.py reads the fixture by the language of the
suffix.
- `python3 core/tools/codeprose.py FILE` must print the passages of `<name>.passages`.
- Where `<name>.expected.<suffix>` exists, the re-wrap of a copy at column 120 must equal that file, and a second
  re-wrap must change nothing.
- An oracle reads the source with the comments that the reader found replaced by spaces. For C and C++, the text must
  equal what `gcc -fpreprocessed -E` strips, compared with no whitespace and no backslash-newline. For JavaScript and
  TypeScript, the stripped source must pass `node --check` wherever the fixture passes it, as a CommonJS or an ES
  module, whichever parses the fixture. TypeScript is checked after `module.stripTypeScriptTypes()` of node. Verilog,
  JSX and TSX have no oracle here.

When the program of an oracle is not installed, the oracle is reported as `skipped`. A fixture that `node --check`
rejects as written is reported as `unchecked`. Neither counts as a pass.

--corpus also runs the oracles over the C and C++ headers below /usr/include, and over the scripts bundled with node.
The corpus run reads up to --limit files of each kind. The corpus run uses one CPU.

Usage:
    $ python3 core/tests/run_comments.py
    $ python3 core/tests/run_comments.py --only cpp
    $ python3 core/tests/run_comments.py --corpus --limit 300

Exit codes:
    0  every check passed
    1  at least one check failed
"""

from __future__ import annotations

import argparse
import difflib
import importlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = TESTS_DIR / 'comments'
CODEPROSE_PATH = TESTS_DIR.parent / 'tools' / 'codeprose.py'
MANIFEST_PATH = TESTS_DIR.parents[1] / 'skills.toml'
# the gcc options of each suffix. A `.h` file is C++ to the readers, so gcc reads a `.h` file as C++ too
C_OPTIONS = ('-x', 'c', '-std=c2x')
CPP_OPTIONS = ('-x', 'c++', '-std=c++23')
GCC_OPTIONS_OF_SUFFIX = {
    '.c': C_OPTIONS,
    '.h': CPP_OPTIONS,
    '.cc': CPP_OPTIONS,
    '.cpp': CPP_OPTIONS,
    '.cxx': CPP_OPTIONS,
    '.hh': CPP_OPTIONS,
    '.hpp': CPP_OPTIONS,
}
# the pragmas that `gcc -fpreprocessed -E` reads and leaves out of the output
# matches:
# `#pragma once`
# `#  pragma GCC system_header`
# `#pragma push_macro("min")`
CONSUMED_PRAGMA = re.compile(
    r'^[ \t]*#[ \t]*pragma[ \t]+(?:once|GCC[ \t]+system_header|push_macro|pop_macro)\b.*$',
    re.MULTILINE,
)
NODE_SUFFIXES = frozenset({'.js', '.mjs', '.cjs', '.ts', '.mts', '.cts'})
TYPESCRIPT_SUFFIXES = frozenset({'.ts', '.mts', '.cts'})
# the module kinds in which node can parse a file of each suffix, CommonJS first
MODULE_SUFFIXES = {
    '.js': ('.cjs', '.mjs'),
    '.ts': ('.cjs', '.mjs'),
    '.cjs': ('.cjs',),
    '.cts': ('.cjs',),
    '.mjs': ('.mjs',),
    '.mts': ('.mjs',),
}
C_CORPUS = Path('/usr/include')
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def main() -> int:
    """Check every fixture, then the corpus with --corpus, and print each failure and the totals."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--only', help='check only the fixtures of this directory, such as cpp')
    parser.add_argument('--corpus', action='store_true', help='also run the oracles over system headers and npm')
    parser.add_argument('--limit', type=int, default=0, help='with --corpus, check at most this many files of each')
    args = parser.parse_args()

    tally = Tally()
    for fixture in findFixtures(args.only):
        checkFixture(fixture, tally)
    if args.corpus:
        runCorpus(args.limit, tally)
    if (problem := suffixProblem()) is not None:
        tally.failures.append(problem)
    for failure in tally.failures:
        print(failure, end='\n\n')
    print(tally.summary())
    return EXIT_FAILURE if tally.failures else EXIT_SUCCESS


def suffixProblem() -> str | None:
    """Compare the `suffixes` of [core] in skills.toml with the suffixes that codeprose.py reads.

    Returns:
        A description of the difference, or None when the two lists are equal.
    """
    sys.path.insert(0, str(CODEPROSE_PATH.parent))
    codeprose = importlib.import_module('codeprose')
    with MANIFEST_PATH.open('rb') as manifest:
        listed = set(tomllib.load(manifest)['core'].get('suffixes', ()))
    read = set(codeprose.LANGUAGE_OF_SUFFIX)
    if listed == read:
        return None
    return f'skills.toml [core] suffixes: missing {sorted(read - listed)}, extra {sorted(listed - read)}'


def findFixtures(only: str | None) -> list[Path]:
    """List each fixture source file. An expected re-wrap file and an expected passages file are not fixtures."""
    directories = [FIXTURES_DIR / only] if only else sorted(path for path in FIXTURES_DIR.iterdir() if path.is_dir())
    return [
        path
        for directory in directories
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix != '.passages' and '.expected.' not in path.name
    ]


def checkFixture(fixture: Path, tally: Tally) -> None:
    shown = fixture.relative_to(FIXTURES_DIR)
    tally.cases += 1
    dumped = runCodeprose(fixture)
    if dumped.returncode != 0:
        tally.failures.append(f'{shown}: codeprose.py exited {dumped.returncode}: {dumped.stderr.strip()}')
        return

    read = dumped.stdout.splitlines()
    expected_path = fixture.with_suffix('.passages')
    if not expected_path.exists():
        tally.failures.append(f'{shown}: no {expected_path.name}. The passages as read:\n' + '\n'.join(read))
    elif read != (expected := expected_path.read_text(encoding='utf-8').splitlines()):
        diff = difflib.unified_diff(expected, read, 'expected', 'read', lineterm='')
        tally.failures.append(f'{shown}: the passages differ from {expected_path.name}\n' + '\n'.join(diff))

    rewrapped_path = fixture.with_name(f'{fixture.stem}.expected{fixture.suffix}')
    if rewrapped_path.exists():
        checkRewrap(fixture, rewrapped_path, tally)
    runOracle(shown, fixture, tally)


def checkRewrap(fixture: Path, rewrapped_path: Path, tally: Tally) -> None:
    """Re-wrap a copy of the fixture twice. The first result must equal the expected file, and the second the first."""
    shown = fixture.relative_to(FIXTURES_DIR)
    once = runCodeprose(fixture, '--rewrap').stdout
    with tempfile.TemporaryDirectory() as work_dir:
        copy_path = Path(work_dir) / fixture.name
        copy_path.write_text(once, encoding='utf-8')
        twice = runCodeprose(copy_path, '--rewrap').stdout
    expected = rewrapped_path.read_text(encoding='utf-8')
    if once != expected:
        diff = difflib.unified_diff(expected.splitlines(), once.splitlines(), 'expected', 're-wrapped', lineterm='')
        tally.failures.append(f'{shown}: the re-wrap differs from {rewrapped_path.name}\n' + '\n'.join(diff))
    elif twice != once:
        tally.failures.append(f'{shown}: a second re-wrap changed the file')


def runOracle(shown: Path, source_path: Path, tally: Tally) -> None:
    """Compare the comments that the reader found with what gcc or node reads, for the suffixes that have an oracle."""
    suffix = source_path.suffix
    if suffix not in GCC_OPTIONS_OF_SUFFIX and suffix not in NODE_SUFFIXES:
        return
    program = 'gcc' if suffix in GCC_OPTIONS_OF_SUFFIX else 'node'
    if shutil.which(program) is None:
        tally.skipped.add(program)
        return
    try:
        source = source_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return
    result = runCodeprose(source_path, '--stripped')
    if result.returncode != 0:
        tally.failures.append(f'{shown}: codeprose.py --stripped exited {result.returncode}: {result.stderr.strip()}')
        return

    if program == 'gcc':
        tally.oracle_runs += 1
        if (problem := gccProblem(source, result.stdout, GCC_OPTIONS_OF_SUFFIX[suffix])) is not None:
            tally.failures.append(f'{shown}: gcc oracle: {problem}')
    elif (module_suffix := nodeModuleSuffix(source, suffix)) is None:
        tally.unchecked.append(str(shown))
    else:
        tally.oracle_runs += 1
        if not nodeAccepts(result.stdout, suffix, module_suffix):
            tally.failures.append(f'{shown}: node oracle: node --check rejects the source with the comments removed')


def gccProblem(source: str, stripped: str, gcc_options: tuple[str, ...]) -> str | None:
    """Remove the whitespace from the reader's stripped source and from gcc's output, then compare the two texts.

    `gcc -fpreprocessed` removes comments without splicing lines first, so the source is spliced before gcc reads the
    source. gcc also drops the lines of the pragmas in CONSUMED_PRAGMA from the output, so those lines are removed from
    both texts.

    Returns:
        A description of the first difference, or None when the two match.
    """
    result = subprocess.run(
        ['gcc', '-fpreprocessed', '-dD', '-E', '-P', '-w', *gcc_options, '-'],
        input=unsplice(source),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return f'gcc exited {result.returncode}: {result.stderr.strip()[:300]}'
    ours = ''.join(CONSUMED_PRAGMA.sub('', unsplice(stripped)).split())
    theirs = ''.join(CONSUMED_PRAGMA.sub('', result.stdout).split())
    if ours == theirs:
        return None
    offset = next((index for index, pair in enumerate(zip(ours, theirs, strict=False)) if pair[0] != pair[1]), None)
    offset = min(len(ours), len(theirs)) if offset is None else offset
    window = slice(max(offset - 40, 0), offset + 40)
    return f'the texts differ at {offset}, reader {ours[window]!r}, gcc {theirs[window]!r}'


def unsplice(source: str) -> str:
    # gcc splices a backslash and the line break after the backslash, also when spaces are between the backslash and the
    # line break
    return re.sub(r'\\[ \t]*\r?\n', '', source)


def nodeModuleSuffix(source: str, suffix: str) -> str | None:
    """Find the module kind in which node parses a source: `.cjs` for CommonJS, `.mjs` for an ES module.

    `node --check` of a `.js` file with `import` or `export` exits 0 without parsing the file, so each source is checked
    as `.cjs` or as `.mjs`. A `.js` or `.ts` source can be either.

    Returns:
        The suffix of the first kind that parses, or None when neither does.
    """
    candidates = MODULE_SUFFIXES[suffix]
    return next((candidate for candidate in candidates if nodeAccepts(source, suffix, candidate)), None)


def nodeAccepts(source: str, suffix: str, module_suffix: str) -> bool:
    """Check that node parses a source as the module kind of `module_suffix`."""
    # node prints the source with each type annotation replaced by spaces, or exits 1 on syntax that
    # stripTypeScriptTypes() rejects, such as an enum
    STRIP_TYPES = (
        "const m = require('node:module'); let t = ''; process.stdin.on('data', d => t += d);"
        " process.stdin.on('end', () => process.stdout.write(m.stripTypeScriptTypes(t)));"
    )
    if suffix in TYPESCRIPT_SUFFIXES:
        stripped = subprocess.run(
            ['node', '-e', STRIP_TYPES],
            input=source,
            capture_output=True,
            text=True,
            check=False,
        )
        if stripped.returncode != 0:
            return False
        source = stripped.stdout
    with tempfile.TemporaryDirectory() as work_dir:
        checked_path = Path(work_dir) / f'checked{module_suffix}'
        checked_path.write_text(source, encoding='utf-8')
        result = subprocess.run(['node', '--check', str(checked_path)], capture_output=True, check=False)
    return result.returncode == 0


def runCodeprose(source_path: Path, *options: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(CODEPROSE_PATH), *options, str(source_path)]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def runCorpus(limit: int, tally: Tally) -> None:
    """Run the oracles over a fixed random sample of the system headers, and of the scripts bundled with node."""
    headers = sorted(path for path in C_CORPUS.rglob('*') if path.suffix in ('.h', '.hpp') and path.is_file())
    node = shutil.which('node')
    node_modules = Path(node).resolve().parents[1] / 'lib' / 'node_modules' if node else None
    scripts = sorted(
        path
        for path in (node_modules.rglob('*') if node_modules else ())
        if path.suffix in NODE_SUFFIXES and path.is_file()
    )
    sampler = random.Random(0)
    for corpus in (headers, scripts):
        picked = sampler.sample(corpus, min(limit, len(corpus))) if limit else corpus
        for source_path in picked:
            tally.corpus_files += 1
            runOracle(source_path, source_path, tally)


### vocabulary #########################################################################################


@dataclass
class Tally:
    """The counts and the failures of one run."""

    cases: int = 0
    corpus_files: int = 0
    oracle_runs: int = 0
    failures: list[str] = field(default_factory=list)
    unchecked: list[str] = field(default_factory=list)
    skipped: set[str] = field(default_factory=set)

    def summary(self) -> str:
        parts = [
            f'{len(self.failures)} failures',
            f'{self.cases} fixtures',
            f'{self.corpus_files} corpus files',
            f'{self.oracle_runs} oracle runs',
        ]
        if self.unchecked:
            parts.append(f'unchecked by node, rejected as written: {", ".join(self.unchecked)}')
        if self.skipped:
            parts.append(f'skipped, not installed: {", ".join(sorted(self.skipped))}')
        return '. '.join(parts)


if __name__ == '__main__':
    sys.exit(main())
