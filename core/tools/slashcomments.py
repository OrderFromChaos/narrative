"""Turn the `//` and `/* */` comments of a source file into passages for the prose checks and blocks for the re-wrap.

C, C++, JavaScript, TypeScript, and Verilog share these two comment forms. The languages differ in the literals that can
contain `//` or `/*`, such as a C++ raw string, a JavaScript regex literal, or a Verilog escaped identifier. The module
of each language, such as ccomments.py, defines a `Language`, and `Language.lex()` returns the comment spans of a source
file. This module reads the spans as comments, groups them into blocks, and splits the blocks into passages.

Each of these is a comment block:
- a run of whole-line comments on consecutive lines at one column, with one opener such as `//` or `///`
- one trailing comment
- one `/* */` comment

 In a passage of prose, a blank line, a pragma, a divider, a
list item, a fence of three backticks, and a block tag of a doc comment start a new passage, and the lines of a sample
such as `\\code`
... `\\endcode` are left out. A block for the re-wrap is a run of whole-line comments, or one `/* */` comment over
several lines. A trailing comment, a one-line `/* */` comment, and a `//` comment continued by a backslash are never
re-wrapped. In a `/* */` comment, the line of the opener and the line of `*/` are fixed.

Usage, from a script in this directory:
    import ccomments
    import slashcomments
    passages = slashcomments.passages(source, ccomments.CPP)
"""

from __future__ import annotations

import bisect
import re
from collections.abc import Callable
from dataclasses import dataclass

from prose import Passage
from rewrap import Line


### standard library only. The prose checks import this, and they run wherever python3 does

# matches:
# `// noqa`
# `/* noqa: NAR017, NAR020 */`
NOQA = re.compile(r'(?://|/\*)\s*noqa(?::\s*(?P<codes>(?:[A-Z0-9]+(?:-[a-z]+)?[, ]*)+))?')
# matches:
# `----------`
# `==========`
# `**********`
# `**`, the body of the banner `/****/`
DIVIDER = re.compile(r'^(?:[-=#~*/+_]{4,}|\*+)$')
# a backslash at the end of a line, or with only spaces or tabs after the backslash. gcc splices lines at either form
# matches:
# `\` then the line break
# `\  ` then the line break
SPLICE = re.compile(r'\\[ \t]*\r?$')
# matches:
# `noqa: NAR017`
NOQA_PRAGMA = re.compile(r'^noqa\b')
# matches:
# `- one item`
# `2. the second step`
LIST_ITEM = re.compile(r'^(?:[-*+]|\d+[.)])\s')
# the kind of a comment block in dumpPassages(), by whether the block has `//` comments and whether the block is a doc
BLOCK_KINDS = {(True, False): 'line', (True, True): 'doc-line', (False, False): 'block', (False, True): 'doc'}


def passages(source: str, language: Language) -> list[Passage]:
    blocks = groupBlocks(readComments(source, language))
    return [passage for block in blocks for passage in blockPassages(block, language)]


def dumpPassages(source: str, language: Language) -> list[str]:
    """List each passage as `first-last kind: text`. The expected files of the tests have this form.

    The kind is `line`, `doc-line`, `block`, or `doc`, after `trailing ` for a trailing comment. A passage of one line
    has the line number alone in place of `first-last`.
    """
    dumped: list[str] = []
    for block in groupBlocks(readComments(source, language)):
        first = block[0]
        kind = BLOCK_KINDS[first.line_comment, first.doc]
        prefix = 'trailing ' if first.trailing else ''
        for passage in blockPassages(block, language):
            first_line, last_line = passage.lines[0], passage.lines[-1]
            lines = str(first_line) if first_line == last_line else f'{first_line}-{last_line}'
            dumped.append(f'{lines} {prefix}{kind}: {passage.text}')
    return dumped


def strippedSource(source: str, language: Language) -> str:
    """Replace each comment with one space and keep the line breaks inside the comment."""
    pieces: list[str] = []
    cursor = 0
    for span in language.lex(source):
        pieces.append(source[cursor : span.start])
        pieces.append(' ' + '\n' * source.count('\n', span.start, span.end))
        cursor = span.end
    pieces.append(source[cursor:])
    return ''.join(pieces)


def readComments(source: str, language: Language) -> list[Comment]:
    """Read each span that `language.lex()` returns as a `Comment`: the opener, the lines, and the column.

    Raises:
        SpanError: a span does not start with `//` or `/*`, or overlaps the span before.
    """
    newlines = [index for index, char in enumerate(source) if char == '\n']
    comments: list[Comment] = []
    previous_end = 0
    for span in language.lex(source):
        text = source[span.start : span.end]
        if not text.startswith(('//', '/*')) or span.start < previous_end:
            raise SpanError(f'{language.name}: span {span.start}-{span.end} is not a comment: {text[:20]!r}')
        previous_end = span.end
        line_index = bisect.bisect_left(newlines, span.start)
        line_start = newlines[line_index - 1] + 1 if line_index else 0
        opener = readOpener(text)
        closed = text.startswith('/*') and text.endswith('*/') and len(text) >= len(opener) + 2
        body = text[len(opener) : -2 if closed else None]
        # in a C or C++ line comment and in a macro body of C, C++, or Verilog, the compiler joins a line that ends with
        # a backslash to the next line. The backslash is not prose
        parts = [SPLICE.sub('', part.removesuffix('\r')) for part in body.split('\n')]
        comments.append(
            Comment(
                opener=opener,
                texts=tuple((line_index + 1 + offset, part) for offset, part in enumerate(parts)),
                column=span.start - line_start,
                trailing=bool(source[line_start : span.start].strip()),
                doc=opener.removesuffix('<') in language.doc_openers,
            ),
        )
    return comments


def readOpener(comment_text: str) -> str:
    """Return the opener of a comment: `//`, `///`, `//!`, `/*`, `/**`, or `/*!`, then `<` for a trailing doc comment.

    `////` and `/***` open a divider, and `/**/` is an empty comment, so their opener is `//` or `/*`.
    """
    # matches:
    # `///` then `<`
    # `/**` then `<`
    # rejects:
    # `////`
    # `/***`
    # `/**/`
    DOC_OPENER = re.compile(r'^(?:///(?!/)|//!|/\*\*(?![*/])|/\*!)<?')
    if found := DOC_OPENER.match(comment_text):
        return found[0]
    return comment_text[:2]


def groupBlocks(comments: list[Comment]) -> list[list[Comment]]:
    """Group the whole-line comments with one opener on consecutive lines at one column. Other comments are blocks."""
    blocks: list[list[Comment]] = []
    for comment in comments:
        previous = blocks[-1][-1] if blocks else None
        joins = (
            previous is not None
            and comment.line_comment
            and previous.line_comment
            and not comment.trailing
            and not previous.trailing
            and comment.opener == previous.opener
            and comment.column == previous.column
            and comment.first_line == previous.last_line + 1
            and len(previous.texts) == 1
            and len(comment.texts) == 1
        )
        if joins:
            blocks[-1].append(comment)
        else:
            blocks.append([comment])
    return blocks


def blockPassages(block: list[Comment], language: Language) -> list[Passage]:
    """Split one comment block into passages of prose by the rules in the module docstring."""
    markup = language.markup
    doc = block[0].doc
    passages: list[Passage] = []
    current: Passage | None = None
    in_sample = False
    in_fence = False
    dropping = False
    for number, raw_text in (pair for comment in block for pair in comment.texts):
        text = raw_text.strip() if block[0].line_comment else cleanStarLine(raw_text)
        fence = text.startswith('```')
        in_fence = in_fence != fence
        if fence or in_fence or DIVIDER.match(raw_text.strip()):
            current = None
            dropping = False
            continue
        if doc:
            in_sample, text = stripSample(markup, in_sample, text)
        starts = doc and markup.block_tag.match(text) is not None
        # the lines of a dropped tag such as `@see` run up to a blank line or the next block tag
        dropping = dropping and bool(text) and not starts
        if doc and (dropping or markup.dropped_tag.match(text)):
            dropping = True
            text = ''
        elif doc and (tag := markup.named_tag.match(text)):
            text = text[tag.end() :]
        list_item = LIST_ITEM.match(text) is not None or (doc and markup.list_item.match(text) is not None)
        if doc:
            text = ' '.join(markup.plain(text).split())
        if not text or NOQA_PRAGMA.match(text) or language.pragma.search(text) or DIVIDER.match(text):
            current = None
            continue
        if starts or list_item or current is None:
            current = Passage((number,), (text,), list_item)
            passages.append(current)
        else:
            current = current.extendedBy(number, text)
            passages[-1] = current
    return passages


def cleanStarLine(raw_text: str) -> str:
    """Remove the margin `*` of a line of a `/* */` comment."""
    text = raw_text.strip()
    return text.removeprefix('*').strip() if text.startswith('*') else text


def stripSample(markup: DocMarkup, in_sample: bool, text: str) -> tuple[bool, str]:
    """Blank the lines of a sample of a doc comment, and return whether the next line is still in the sample.

    When `sample_end` is None, a sample such as JSDoc `@example` runs up to the next block tag, and the line of that
    block tag is prose.
    """
    if in_sample:
        if markup.sample_end is None:
            if markup.block_tag.match(text) and not markup.sample_start.match(text):
                return False, text
            return True, ''
        return markup.sample_end.search(text) is None, ''
    if not (start := markup.sample_start.match(text)):
        return False, text
    if markup.sample_end is None:
        return True, ''
    return markup.sample_end.search(text, start.end()) is None, ''


def commentBlocks(source: str, language: Language) -> list[list[Line]]:
    """Read the whole-line comments and the `/* */` comments over several lines as the blocks that rewrap.py fills."""
    lines = source.split('\n')
    blocks: list[list[Line]] = []
    for block in groupBlocks(readComments(source, language)):
        first = block[0]
        if first.trailing:
            continue
        if first.line_comment and len(first.texts) == 1:
            blocks.append(slashLines(lines, block, language))
        elif not first.line_comment and first.last_line > first.first_line:
            blocks.append(starLines(lines, first, language))
    return blocks


def slashLines(lines: list[str], block: list[Comment], language: Language) -> list[Line]:
    """Read a run of whole-line `//` comments. A pragma, a divider, a sample, and a line with a noqa are fixed.

    In a doc comment, a block tag opens a paragraph.
    """
    read: list[Line] = []
    in_sample = False
    for comment in block:
        raw = lines[comment.first_line - 1].removesuffix('\r')
        body = raw[comment.column + len(comment.opener) :]
        text = body.strip()
        margin = raw[: comment.column + len(comment.opener)] + body[: len(body) - len(body.lstrip())]
        sample = False
        if comment.doc:
            in_sample, prose_text = stripSample(language.markup, in_sample, text)
            sample = bool(text) and not prose_text
        read.append(fixedOrOpening(Line(comment.first_line, margin, text), comment, language, sample=sample, raw=raw))
    return read


def starLines(lines: list[str], comment: Comment, language: Language) -> list[Line]:
    """Read the lines of one `/* */` comment, each with the margin up to the text.

    The margin is the indent and, when every inner line has one, the `*` of the line. The line of the opener and the
    line of `*/` are fixed, and so are a sample of a doc comment and a line of HTML tags alone, such as `<p>`.
    """
    # matches:
    # `<p>`
    # `</li></ul>`
    TAGS_ALONE = re.compile(r'^(?:</?\w+[^>]*>\s*)+$')
    numbers = [number for number, _text in comment.texts]
    inner = [lines[number - 1] for number in numbers[1:-1] if lines[number - 1].strip()]
    starred = bool(inner) and all(line.lstrip().startswith('*') for line in inner)
    margin_pattern = re.compile(r'^\s*\*(?!/)\s*' if starred else r'^\s*')
    read: list[Line] = []
    in_sample = False
    for number in numbers:
        raw = lines[number - 1].removesuffix('\r')
        margin = margin_pattern.match(raw)
        margin_text = margin[0] if margin else ''
        text = raw[len(margin_text) :].rstrip()
        edge = number in (numbers[0], numbers[-1])
        sample = False
        if comment.doc and not edge:
            in_sample, prose_text = stripSample(language.markup, in_sample, text)
            sample = bool(text) and not prose_text
        line = Line(number, margin_text, text, fixed=edge or margin is None or TAGS_ALONE.match(text) is not None)
        read.append(fixedOrOpening(line, comment, language, sample=sample, raw=raw))
    return read


def fixedOrOpening(line: Line, comment: Comment, language: Language, *, sample: bool, raw: str) -> Line:
    """Mark a pragma, a divider, a sample, and a line with a noqa as fixed, and a doc comment block tag as opening."""
    pragma = bool(NOQA_PRAGMA.match(line.text) or language.pragma.search(line.text) or DIVIDER.match(line.text))
    # a re-wrap of a line spliced to the next line would move the backslash into the middle of a line, and break the
    # macro
    spliced = SPLICE.search(raw) is not None
    fixed = line.fixed or sample or pragma or spliced or NOQA.search(raw) is not None
    opens = comment.doc and not fixed and language.markup.block_tag.match(line.text) is not None
    return Line(line.number, line.margin, line.text, fixed, 0 if opens else None)


def lexWith(source: str, skip_literal: Callable[[str, int], int | None], *, line_splice: bool) -> list[Span]:
    """Find the comments of a source file whose literals `skip_literal` can skip one at a time, left to right.

    A `//` opens a line comment and a `/*` opens a block comment, unless `skip_literal` returns the end of a literal
    that starts at the same offset. When `line_splice` is true, a backslash at the end of a line continues a line
    comment. C and C++ splice lines this way. An unclosed block comment runs to the end of the source.
    """
    spans: list[Span] = []
    index = 0
    while index < len(source):
        if source.startswith('//', index):
            end = lineCommentEnd(source, index, line_splice=line_splice)
            spans.append(Span(index, end))
            index = end
        elif source.startswith('/*', index):
            close = source.find('*/', index + 2)
            end = len(source) if close == -1 else close + 2
            spans.append(Span(index, end))
            index = end
        elif (literal_end := skip_literal(source, index)) is not None:
            index = max(literal_end, index + 1)
        else:
            index += 1
    return spans


def lineCommentEnd(source: str, start: int, *, line_splice: bool) -> int:
    """Return the offset of the line break that ends a line comment, or the end of the source."""
    end = source.find('\n', start)
    while line_splice and end != -1 and SPLICE.search(source, start, end) is not None:
        end = source.find('\n', end + 1)
    return len(source) if end == -1 else end


def quotedEnd(source: str, start: int, *, multiline: bool = False) -> int:
    """Return the offset after the closing quote of the string that opens at `start`.

    A backslash escapes the next character. An unclosed string ends at the line break, or with `multiline` at the end of
    the source.
    """
    quote = source[start]
    index = start + 1
    while index < len(source):
        char = source[index]
        if char == '\\':
            index += 3 if source.startswith('\r\n', index + 1) else 2
        elif char == quote:
            return index + 1
        elif char == '\n' and not multiline:
            return index
        else:
            index += 1
    return len(source)


def neverMatches() -> re.Pattern[str]:
    return re.compile(r'(?!)')


def plainUnchanged(text: str) -> str:
    return text


### vocabulary #########################################################################################


@dataclass(frozen=True)
class Span:
    """A `Span` has the offsets of one comment in the source, from `//` or `/*` up to the line break or after `*/`."""

    start: int
    end: int


@dataclass(frozen=True)
class DocMarkup:
    """The markup of the doc comments of a language, such as Doxygen or JSDoc.

    A line that `block_tag` matches opens a passage and a paragraph. `named_tag` matches the part of a tag line that is
    not prose, such as `@param {string} name -`, and `dropped_tag` a tag whose whole line is not prose, such as `@see`.
    A sample opens at a line that `sample_start` matches. The sample ends after a line that `sample_end` matches. When
    `sample_end` is None, the sample ends before the next block tag. `plain()` turns the inline markup of one line into
    plain text and backticks.
    """

    block_tag: re.Pattern[str]
    named_tag: re.Pattern[str]
    dropped_tag: re.Pattern[str]
    list_item: re.Pattern[str]
    sample_start: re.Pattern[str]
    sample_end: re.Pattern[str] | None
    plain: Callable[[str], str]


NO_MARKUP = DocMarkup(
    block_tag=neverMatches(),
    named_tag=neverMatches(),
    dropped_tag=neverMatches(),
    list_item=neverMatches(),
    sample_start=neverMatches(),
    sample_end=None,
    plain=plainUnchanged,
)


@dataclass(frozen=True)
class Language:
    """A `Language` is one language of the `//` and `/* */` family. The module of the language defines the value.

    `lex()` returns the comment spans in source order. `doc_openers` lists the openers of a doc comment, such as `/**`
    and `///`. `pragma` matches the text of a tool directive that is not prose, such as `NOLINT` or `eslint-disable`.
    """

    name: str
    suffixes: tuple[str, ...]
    lex: Callable[[str], list[Span]]
    doc_openers: frozenset[str]
    markup: DocMarkup
    pragma: re.Pattern[str]


@dataclass(frozen=True)
class Comment:
    """A `Comment` is one comment as written. `texts` has the line number and the text of each line. The text doesn't
    include the opener and `*/`."""

    opener: str
    texts: tuple[tuple[int, str], ...]
    column: int
    trailing: bool
    doc: bool

    @property
    def first_line(self) -> int:
        return self.texts[0][0]

    @property
    def last_line(self) -> int:
        return self.texts[-1][0]

    @property
    def line_comment(self) -> bool:
        return self.opener.startswith('//')


class SpanError(RuntimeError):
    pass
