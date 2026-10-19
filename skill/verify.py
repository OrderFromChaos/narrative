"""Run the whole Narrative toolchain over a path and report one line per tool.

Use this instead of calling the tools by hand. A hand-rolled loop counts findings by grepping tool
output, so a missing or misresolved binary produces empty output and reads as a pass. This script
resolves every tool to an absolute path and exits 2 if any one of them is absent, so a green result
means the tools ran.

This is the whole pipeline. Give it any path, and every Python file below the path is checked, so
no workflow is chosen at run time. A Markdown, HTML or plain text file named on the command line,
such as a README or a published page, gets the two prose checks only: the wording checks of checks.py
and agentverbs.py. pyproject.toml is required only when Python files are checked.

Order matters. `ruff check --fix` and `ruff format` converge in that order and not the other.

Usage:
    $ python3 verify.py src/                 # every .py below src/
    $ python3 verify.py src/loader.py src/report.py
    $ python3 verify.py . --no-fix           # report only, change nothing
    $ python3 verify.py . --venv .lintenv    # a venv other than the shared one (SHARED_VENV)
    $ python3 verify.py README.md docs/report.html

Exit codes:
    0  every tool passed
    1  at least one tool had a finding
    2  the toolchain or the config is missing, so nothing was checked
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from prose import PROSE_SUFFIXES


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
    parser.add_argument('--all-sentences', action='store_true', help='list every sentence, not the first 1000')
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
    if not code and not pages:
        print('nothing to check: no .py files found, and no .md, .html or .txt file named', file=sys.stderr)
        return EXIT_NO_TOOLCHAIN

    results: list[Result] = []
    if code:
        if (config_problem := checkConfig(args.config)) is not None:
            return config_problem
        results.extend(runCodeTools(toolchain, args.config, [str(p) for p in code], fix=not args.no_fix))

    checker = Path(__file__).resolve().parent / 'checks.py'
    prose_targets = [str(p) for p in [*code, *pages]]
    results.append(gradeChecks(run([sys.executable, str(checker), *prose_targets])))
    if code:
        vermin_cmd = [toolchain.paths['vermin'], '--no-tips', f'-t={PYTHON_FLOOR}-', '--violations']
        results.append(gradeVermin(run([*vermin_cmd, *[str(p) for p in code]])))
    agent_verbs = Path(__file__).resolve().parent / 'agentverbs.py'
    results.append(gradeAgentVerbs(run([toolchain.python, str(agent_verbs), *prose_targets])))

    width = max(len(r.tool) for r in results)
    for result in results:
        print(f'{result.tool:<{width}}  {result.summary}')

    failed = [r for r in results if not r.passed]
    if failed:
        # nobody should need to re-run a tool by hand to see why the tool failed
        for result in failed:
            print(f'\n--- {result.tool} ---')
            print(result.detail.rstrip() or '(no output)')

        print(f'\n{len(failed)} of {len(results)} checks failed')
        return EXIT_FINDINGS

    print(f'\nall {len(results)} checks passed')
    print('A pass is no evidence about the rules that no check implements. Read the lists below.')
    if code:
        every = ['--all-sentences'] if args.all_sentences else []
        inventory = run([sys.executable, str(checker), '--prose', *every, *[str(p) for p in code]])
        print('\n--- every sentence of every comment and docstring: read each against SKILL.md, Comments ---')
        print(inventory.text.rstrip() or '(none)')
    review = run([toolchain.python, str(agent_verbs), '--review', *prose_targets])
    print('\n--- every subject that cannot act, with its verb: can that subject perform that verb? ---')
    print(review.text.rstrip() or '(none)')
    pronouns = run([toolchain.python, str(agent_verbs), '--pronouns', *prose_targets])
    print('\n--- every sentence with a pronoun, after the one before it: which noun does each pronoun stand for? ---')
    print(pronouns.text.rstrip() or '(none)')
    return EXIT_SUCCESS


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


def runCodeTools(toolchain: Toolchain, config: Path, targets: list[str], *, fix: bool) -> list[Result]:
    """Fix and format the Python files unless told not to, then run ruff, pylint and mypy.

    Order matters. `ruff check --fix` and `ruff format` converge in that order and not the other.

    Returns:
        One result per tool, in the order they ran.
    """
    if fix:
        run([toolchain.paths['ruff'], 'check', '--config', str(config), '--fix', '-q', *targets])
        run([toolchain.paths['ruff'], 'format', '--config', str(config), '-q', *targets])

    ruff_config = ['--config', str(config)]
    check_cmd = [toolchain.paths['ruff'], 'check', *ruff_config, '--output-format=concise']
    mypy_cmd = [toolchain.paths['mypy'], '--config-file', str(config), '--strict', '--no-error-summary']
    return [
        gradeRuffCheck(run([*check_cmd, *targets])),
        gradeFormat(run([toolchain.paths['ruff'], 'format', *ruff_config, '--check', *targets])),
        gradePylint(run([toolchain.paths['pylint'], f'--rcfile={config}', *targets])),
        gradeMypy(run([*mypy_cmd, *targets])),
    ]


def discoverPython(paths: list[Path]) -> list[Path]:
    """Find every Python file at or below the given paths.

    A directory expands to everything below the directory, so one command covers a whole project.
    """
    code: list[Path] = []
    for target in paths:
        found = sorted(target.rglob('*.py')) if target.is_dir() else [target]
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
