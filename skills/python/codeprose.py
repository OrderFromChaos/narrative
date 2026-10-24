"""Read the comments and docstrings of a Python file as passages, for the prose checks of every language.

Each language of Narrative has a module named codeprose.py, and the language's skill directory has
that module beside agentverbs.py and wording.py. The prose checks read source files only through
the names below, so the checks run on any language with a codeprose.py.

- `GIT_PATTERN`: the git pathspec of a source file of the language
- `passages()`: the comments and doc comments of one source file, as passages
- `NOQA`: the comment that silences a finding on one line
- `changeSpans()`: the lines that count for --since, by line

In a Python file, a passage is a run of whole-line comments at one column, one trailing comment, or a
run of docstring lines.

Usage, from a script in this directory:
    import codeprose
    passages = codeprose.passages(Path('loader.py').read_text(encoding='utf-8'))
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

from prose import Passage
from wording import Spans


### standard library only. checks.py imports this, and checks.py runs wherever python3 does

GIT_PATTERN = '*.py'
# matches:
# `# noqa`
# `# noqa: NAR017, NAR020`
NOQA = re.compile(r'#\s*noqa(?::\s*(?P<codes>[A-Z0-9, ]+))?')
PRAGMA = re.compile(r'(?:noqa|type:|pragma|fmt:|ruff:|pylint:|mypy:)')
# Google-style docstring sections, whose indented entries are prose
SECTION_HEADER = re.compile(r'(?:Args|Arguments|Returns|Yields|Raises|Attributes|Notes?):$')


def passages(source: str) -> list[Passage]:
    """Read every comment passage and every docstring passage of one Python file.

    Raises:
        SyntaxError: the source does not parse.
    """
    return [*commentPassages(source), *docstringPassages(ast.parse(source))]


def commentPassages(source: str) -> list[Passage]:
    """Group comments into passages: a run of whole-line comments at one column, or one trailing comment.

    Returns:
        The passages in line order.
    """
    passages: list[Passage] = []
    run_column = -1
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT:
            continue
        text = token.string.lstrip('#').strip()
        whole_line = token.line[: token.start[1]].strip() == ''
        if not text or PRAGMA.match(text):
            run_column = -1
            continue
        joins_run = (
            whole_line and passages and run_column == token.start[1] and passages[-1].lines[-1] == token.start[0] - 1
        )
        if joins_run:
            passages[-1] = passages[-1].extendedBy(token.start[0], text)
        else:
            passages.append(Passage((token.start[0],), (text,)))
        run_column = token.start[1] if whole_line else -1
    return passages


def docstringPassages(tree: ast.Module) -> list[Passage]:
    passages: list[Passage] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if ast.get_docstring(node) is None or not isinstance(node.body[0], ast.Expr):
            continue
        literal = node.body[0].value
        if not isinstance(literal, ast.Constant) or not isinstance(literal.value, str):
            continue
        previous_offset = -2
        for offset, text in proseLines(literal.value):
            number = literal.lineno + offset
            if offset == previous_offset + 1:
                passages[-1] = passages[-1].extendedBy(number, text)
            else:
                passages.append(Passage((number,), (text,)))
            previous_offset = offset
    return passages


def proseLines(docstring: str) -> list[tuple[int, str]]:
    """Pick the sentences out of a docstring, leaving out pasted samples.

    A line indented past the body is a sample, such as a table or program output, unless the line is
    an entry under a section header such as `Returns:`.

    Returns:
        Line offset within the docstring, and the stripped line.
    """
    raw_lines = docstring.splitlines()
    body = [line for line in raw_lines[1:] if line.strip()]
    margin = min((len(line) - len(line.lstrip()) for line in body), default=0)
    picked: list[tuple[int, str]] = []
    in_section = False
    for offset, line in enumerate(raw_lines):
        stripped = line.strip()
        if not stripped or stripped.startswith(('$', '>>>')):
            continue
        indent = len(line) - len(line.lstrip())
        if offset == 0 or indent <= margin:
            in_section = SECTION_HEADER.match(stripped) is not None
            picked.append((offset, stripped))
        elif in_section:
            picked.append((offset, stripped))
    return picked


def changeSpans(checked_file: Path) -> Spans:
    """Map a line of a Python file to the lines that count for --since when a finding is on that line.

    A finding on the line of a `def` or `class` counts for every line of the definition. A finding on a
    line of a comment or docstring passage counts for every line of the passage. Any other line counts
    for itself, and is not in the map.

    Returns:
        The lines of the definition or the passage, by line. Empty for a file that cannot be read or parsed.
    """
    try:
        source = checked_file.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return {}

    spans: Spans = {}
    for passage in [*commentPassages(source), *docstringPassages(tree)]:
        spans.update(dict.fromkeys(passage.lines, frozenset(passage.lines)))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) and node.end_lineno is not None:
            spans[node.lineno] = frozenset(range(node.lineno, node.end_lineno + 1))
    return spans
