"""Fill the paragraphs of comments again up to column 120, for the re-wrap of every language.

The prose checks read each comment as one joined text. After an edit of that text, the line breaks of the first draft
remain: `The product is` / `a` / `float, …`. The re-wrap joins the lines of each paragraph and fills them again, so that
the first word of each next line would pass column 120 on the line before. No word changes, only the line breaks.

The codeprose.py of each language reads the comments of one source file into blocks of `Line`: the margin before the
text, such as `    # ` or `     * `, and the text. A block is a run of comment lines that can share paragraphs, such as
one javadoc or a run of `#` lines at one column. This module splits each block into paragraphs and fills each paragraph.
Three kinds of line end a paragraph:

- a blank line, and a fixed line. The reader marks a pragma or a `<pre>` sample as fixed. In every language, a line in a
  ``` fence, a table row, a line of one code span and the label `matches:` or `rejects:` are fixed, and so is each line
  after such a label at the label's margin, up to a blank line
- a line indented past the margin of the paragraph, such as a sample in a `#` comment. Such a line is fixed too
- a line that opens a list item, a block tag or an entry of a docstring section. That line starts the next paragraph

Usage, from a script in this directory:
    import codeprose
    import rewrap
    source = rewrap.rewrapSource(source, codeprose.commentBlocks(source), changed_lines=None)
"""

from __future__ import annotations

import re
from dataclasses import dataclass


### standard library only. checks.py and javachecks.py import this, and both run wherever python3 does

# the last column of a comment line, counted from column 0 of the line. The GTNH Eclipse formatter splits a comment line
# past this column, and a Python line past this column is a ruff E501 finding
WIDTH = 120
# a code span or an inline tag such as `{@link Plan#read}` is not split, so a word is the whole span or tag. The spaces
# inside a span stay as written
# matches:
# `{@link Plan#read(Path, int)}`
# ``(`dict[str, list[float]]`)``
# `float,`
# `` ``` ``, three backticks and no code span
WORD = re.compile(r'(?:[^\s`]*(?<!`)`(?!`)[^`]*`(?!`))+[^\s`]*|\{@[^}]*\}\S*|\S+')
# the marker of a list item, whose next lines hang under the text of the item
# matches:
# `- one item`
# `* one item`
# `2. the second step`
# rejects:
# `-1 is the default`
LIST_MARKER = re.compile(r'^(?:[-*]|\d+[.:)])\s+')
# a line of a sample, kept as written
# matches:
# `` `float,` ``
# `| TEAM | USED |`
# rejects:
# `` `verify.py` checks the file ``
SAMPLE = re.compile(r'^(?:`[^`]*`|\|.*)$')
# the label over the strings that a regex matches or rejects, in the comment above the regex
LABEL = re.compile(r'^(?:matches|rejects):$')
RULE = 'NAR125'
DETAIL = f'paragraph not filled up to column {WIDTH}. verify.py re-wraps the paragraph'


def rewrapSource(source: str, blocks: list[list[Line]], changed_lines: set[int] | None) -> str:
    """Fill each paragraph of the blocks again. Under --since, only a paragraph with a changed line.

    Returns:
        The source, with only the line breaks of the filled paragraphs changed.
    """
    lines = source.split('\n')
    replacements = [
        replacement
        for paragraph in paragraphsOf(blocks, changed_lines)
        if (replacement := refill(lines, paragraph)) is not None
    ]
    # replace from the bottom up, because a replacement can change the number of every later line
    for replacement in sorted(replacements, key=lambda replacement: replacement.first_line, reverse=True):
        lines[replacement.first_line - 1 : replacement.last_line] = replacement.new_lines
    return '\n'.join(lines)


def unfilledLines(source: str, blocks: list[list[Line]], changed_lines: set[int] | None) -> list[int]:
    """List the first line of each paragraph that the re-wrap would change.

    Returns:
        The line numbers, in order.
    """
    lines = source.split('\n')
    return [
        replacement.first_line
        for paragraph in paragraphsOf(blocks, changed_lines)
        if (replacement := refill(lines, paragraph)) is not None
    ]


def paragraphsOf(blocks: list[list[Line]], changed_lines: set[int] | None) -> list[Paragraph]:
    """Split every block into paragraphs. Under --since, keep only the paragraphs with a changed line."""
    found = [paragraph for block in blocks for paragraph in splitBlock(block)]
    if changed_lines is None:
        return found
    return [paragraph for paragraph in found if changed_lines & {line.number for line in paragraph.lines}]


def splitBlock(block: list[Line]) -> list[Paragraph]:
    """Split one block into paragraphs, by the three kinds of line in the module docstring."""
    paragraphs: list[Paragraph] = []
    current: Paragraph | None = None
    fixed = fixedLines(block)
    base = min((len(line.margin) for line in block if line.text and line.number not in fixed), default=0)
    for line in block:
        if line.number in fixed or not line.text:
            current = None
            continue
        hang = line.hang
        if hang is None and (marker := LIST_MARKER.match(line.text)):
            hang = len(marker[0])
        if hang is None and current is not None:
            if len(line.margin) == current.continuationWidth(line):
                current = current.extendedBy(line)
                paragraphs[-1] = current
                continue
            if len(line.margin) > len(current.lines[0].margin):
                # a sample below the paragraph, such as a command indented past the text
                current = None
                continue
        if hang is None and len(line.margin) > base:
            current = None
            continue
        current = Paragraph((line,), hang or 0)
        paragraphs.append(current)
    return paragraphs


def fixedLines(block: list[Line]) -> set[int]:
    """Find the lines of a block that stay as written: the lines that the reader marks, and the samples.

    Returns:
        The line numbers.
    """
    fixed: set[int] = set()
    in_fence = False
    label_margin: int | None = None
    for line in block:
        fence = line.text.startswith('```')
        if not line.text or len(line.margin) < (label_margin or 0):
            label_margin = None
        under_label = label_margin is not None and len(line.margin) == label_margin
        if LABEL.match(line.text):
            label_margin = len(line.margin)
        if fence or in_fence or under_label or line.fixed or SAMPLE.match(line.text) or LABEL.match(line.text):
            fixed.add(line.number)
        in_fence = in_fence != fence
    return fixed


def refill(lines: list[str], paragraph: Paragraph) -> Replacement | None:
    """Fill one paragraph greedily, with no line past column WIDTH. A longer word is alone on a line.

    Returns:
        The replacement, or None when the filled lines are the lines as written.
    """
    words = WORD.findall(' '.join(line.text for line in paragraph.lines))
    margin = paragraph.continuationMargin()
    filled: list[str] = []
    current = ''
    for word in words:
        if not current:
            current = f'{paragraph.lines[0].margin if not filled else margin}{word}'
        elif len(current) + 1 + len(word) > WIDTH:
            filled.append(current)
            current = f'{margin}{word}'
        else:
            current = f'{current} {word}'
    if current:
        filled.append(current)
    first, last = paragraph.lines[0].number, paragraph.lines[-1].number
    if filled == [line.rstrip() for line in lines[first - 1 : last]]:
        return None
    return Replacement(first, last, filled)


### vocabulary #########################################################################################


@dataclass(frozen=True)
class Line:
    """One line of a comment: the line number, the margin up to the text, and the text.

    With `fixed`, the line stays as written and ends the paragraph, for a pragma or a line of a sample. With a `hang`,
    the line opens a paragraph, and the next lines of the paragraph are indented past the margin by `hang` columns.
    splitBlock() sets the hang of a list item to the width of the list marker. A `continuation` is the margin of every
    next line of a paragraph that the line opens, such as the indent under the description of a javadoc block tag.
    """

    number: int
    margin: str
    text: str
    fixed: bool = False
    hang: int | None = None
    continuation: str | None = None


@dataclass(frozen=True)
class Paragraph:
    """The lines of one paragraph, and the hang of the first line of the paragraph."""

    lines: tuple[Line, ...]
    hang: int

    def extendedBy(self, line: Line) -> Paragraph:
        return Paragraph((*self.lines, line), self.hang)

    def continuationWidth(self, line: Line) -> int:
        """Return the margin width of a line that continues the paragraph.

        Every later line of a paragraph has the margin of the second line. The second line of a list item is under the
        text of the item. A line with a margin up to the `continuation` of the first line continues the paragraph,
        because the next lines of a block tag are written at more than one indent.
        """
        continuation = self.lines[0].continuation
        if continuation is not None:
            return min(len(line.margin), len(continuation))
        if len(self.lines) > 1:
            return len(self.lines[1].margin)
        first = len(self.lines[0].margin)
        if LIST_MARKER.match(self.lines[0].text):
            return first + self.hang
        return len(line.margin) if first <= len(line.margin) <= first + self.hang else first

    def continuationMargin(self) -> str:
        if self.lines[0].continuation is not None:
            return self.lines[0].continuation
        if len(self.lines) > 1:
            return self.lines[1].margin
        return self.lines[0].margin + ' ' * self.hang


@dataclass(frozen=True)
class Replacement:
    """The new lines of a filled paragraph, in place of the lines from first_line to last_line."""

    first_line: int
    last_line: int
    new_lines: list[str]
