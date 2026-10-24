"""Read the comments and javadoc of a Java file as passages, for the prose checks of every language.

Each language of Narrative has a module named codeprose.py, and the language's skill directory has
that module beside agentverbs.py and wording.py. The prose checks read source files only through
the names below, so the checks run on any language with a codeprose.py.

- `GIT_PATTERN`: the git pathspec of a source file of the language
- `passages()`: the comments and doc comments of one source file, as passages
- `NOQA`: the comment that silences a finding on one line

In a Java file, a passage comes from one comment block: a run of whole-line `//` comments on
consecutive lines at one column, one trailing comment, one block comment or one javadoc. A blank
line, a pragma, a divider, a list item, `<p>` or a block tag starts a new passage, and a `<pre>`
sample is not prose. javachecks.py reads the comments through lexComments() and groupBlocks() too.

Usage, from a script in this directory:
    import codeprose
    passages = codeprose.passages(Path('PlanReader.java').read_text(encoding='utf-8'))
"""

from __future__ import annotations

import bisect
import re
from dataclasses import dataclass
from enum import Enum

from prose import Passage


### standard library only. javachecks.py imports this, and javachecks.py runs wherever python3 does

GIT_PATTERN = '*.java'
# matches:
# `// noqa`
# `// noqa: NAR017, NAR020`
NOQA = re.compile(r'//\s*noqa(?::\s*(?P<codes>[A-Z0-9, ]+))?')
# a text block, a string or character literal, a // comment or a /* comment. The literals are matched
# so that a // or /* inside one is not read as a comment
# matches:
# `"""` then a text block then `"""`
# `"a // b"`
# `'"'`
# `// a comment`
# `/** a javadoc */`
JAVA_TOKEN = re.compile(
    r'"""(?:\\.|[^\\])*?(?:"""|\Z)'
    r'|"(?:\\.|[^"\\\n])*"?'
    r"|'(?:\\.|[^'\\\n])*'?"
    r'|//[^\n]*'
    r'|/\*.*?(?:\*/|\Z)',
    re.DOTALL,
)


def passages(source: str) -> list[Passage]:
    """Read the passages of every comment block of one Java source."""
    return [passage for block in groupBlocks(lexComments(source)) for passage in blockPassages(block)]


def lexComments(source: str) -> list[Comment]:
    """Find every comment, skipping string literals, character literals and text blocks."""
    newlines = [index for index, char in enumerate(source) if char == '\n']
    comments: list[Comment] = []
    for token in JAVA_TOKEN.finditer(source):
        text = token[0]
        if not text.startswith('/'):
            continue
        start = token.start()
        line_index = bisect.bisect_left(newlines, start)
        line_start = newlines[line_index - 1] + 1 if line_index else 0
        trailing = bool(source[line_start:start].strip())
        if text.startswith('//'):
            comments.append(Comment(CommentKind.LINE, ((line_index + 1, text[2:]),), start - line_start, trailing))
            continue
        body = text[2:-2] if text.endswith('*/') and len(text) >= 4 else text[2:]
        kind = CommentKind.JAVADOC if body.startswith('*') and body.strip('*').strip() else CommentKind.BLOCK
        texts = tuple((line_index + 1 + offset, part) for offset, part in enumerate(body.removeprefix('*').split('\n')))
        comments.append(Comment(kind, texts, start - line_start, trailing))
    return comments


def groupBlocks(comments: list[Comment]) -> list[list[Comment]]:
    """Group whole-line // comments on consecutive lines at one column. Every other comment is one block."""
    blocks: list[list[Comment]] = []
    for comment in comments:
        previous = blocks[-1][-1] if blocks else None
        joins = (
            previous is not None
            and comment.kind is CommentKind.LINE
            and previous.kind is CommentKind.LINE
            and not comment.trailing
            and not previous.trailing
            and comment.column == previous.column
            and comment.first_line == previous.last_line + 1
        )
        if joins:
            blocks[-1].append(comment)
        else:
            blocks.append([comment])
    return blocks


def blockPassages(block: list[Comment]) -> list[Passage]:
    """Split one comment block into passages of prose.

    A blank line, a pragma, a divider or a list item starts a new passage. `<p>`, `<li>` and each
    block tag start one too in javadoc, and a `<pre>` sample is not prose.
    """
    # matches:
    # `NOPMD`
    # `CHECKSTYLE:OFF`
    # `spotless:on`
    # `@formatter:off`
    # `noqa: NAR017`
    # `noinspection unchecked`
    # rejects:
    # `the formatter keeps this line`
    PRAGMA = re.compile(
        r'^(?:NOPMD|CHECKSTYLE:(?:ON|OFF)|spotless:(?:on|off)|@formatter:(?:on|off)|noinspection\b|noqa\b)',
    )
    # matches:
    # `----------`
    # `==========`
    DIVIDER = re.compile(r'^[-=#~*/]{4,}$')
    passages: list[Passage] = []
    current: Passage | None = None
    in_sample = False
    javadoc = block[0].kind is CommentKind.JAVADOC
    for number, raw_text in (pair for comment in block for pair in comment.texts):
        text = raw_text.strip() if block[0].kind is CommentKind.LINE else cleanBlockLine(raw_text)
        if javadoc:
            in_sample, text = stripSample(in_sample, text)
        breaks, list_item, text = splitMarkup(text, javadoc=javadoc)
        if not text or PRAGMA.search(text) or DIVIDER.match(text):
            current = None
            continue
        if breaks or list_item or current is None:
            current = Passage((number,), (text,), list_item)
            passages.append(current)
        else:
            current = current.extendedBy(number, text)
            passages[-1] = current
    return passages


def cleanBlockLine(raw_text: str) -> str:
    """Remove the leading `*` of a line of a block comment or javadoc."""
    text = raw_text.strip()
    return text.removeprefix('*').strip() if text.startswith('*') else text


def stripSample(in_sample: bool, text: str) -> tuple[bool, str]:
    """Blank the lines of a `<pre>` sample, and return whether the next line is still in the sample."""
    if '<pre>' in text or in_sample:
        return '</pre>' not in text, ''
    return False, text


def splitMarkup(text: str, *, javadoc: bool) -> tuple[bool, bool, str]:
    """Turn inline javadoc markup into backticks and plain text.

    Returns:
        Whether the line starts a new passage, whether the line opens a list item, and the plain text.
    """
    # matches:
    # `{@code List.copyOf}`
    # `{@link PlanReader#read(Path)}`
    # `{@linkplain PlanReader the reader}`
    INLINE_TAG = re.compile(r'\{@(?:code|literal|link|linkplain|value)\s+([^}]*)\}')
    # matches:
    # `@param planPath where the plan file is`
    # `@throws PlanException when the file has no machine count`
    # `@return the plans, sorted by name`
    NAMED_TAG = re.compile(r'^@(?:param|throws|exception)\s+\S+\s*|^@(?:return|deprecated)\b\s*')
    DROPPED_TAG = re.compile(r'^@(?:see|since|author|version|serial\w*|apiNote|implNote|implSpec|hidden)\b')
    list_item = bool(re.match(r'^[-*]\s', text))
    if not javadoc:
        return False, list_item, text

    if DROPPED_TAG.match(text):
        return True, False, ''
    breaks = bool(re.match(r'^<p>', text, re.IGNORECASE))
    if tag := NAMED_TAG.match(text):
        breaks = True
        text = text[tag.end() :]
    list_item = list_item or bool(re.match(r'^<li>', text, re.IGNORECASE))
    text = INLINE_TAG.sub(lambda inline: f'`{inline[1].strip()}`', text)
    text = re.sub(r'</?code>', '`', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    return breaks, list_item, ' '.join(text.split())


### vocabulary #########################################################################################


class CommentKind(Enum):
    LINE = 'line'
    BLOCK = 'block'
    JAVADOC = 'javadoc'


@dataclass(frozen=True)
class Comment:
    """One comment as written. `texts` has the line number and the text of each line of the comment."""

    kind: CommentKind
    texts: tuple[tuple[int, str], ...]
    column: int
    trailing: bool

    @property
    def first_line(self) -> int:
        return self.texts[0][0]

    @property
    def last_line(self) -> int:
        return self.texts[-1][0]
