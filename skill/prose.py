"""Read the prose of a Markdown, HTML or plain text file as passages, for checks.py and agentverbs.py.

A passage is one paragraph, heading, list item or table cell, with the line number of each of its
lines. Code is left out: fenced blocks in Markdown, and `pre`, `script` and `style` in HTML.
Inline code stays in backticks, so it is read as code and not as a sentence.

A finding in a page is silenced with an HTML comment on the same line, `<!-- noqa: NAR017 -->`,
or `<!-- noqa -->` for every code. Markdown renders no such comment.

Usage, from a script in this directory:
    from prose import PROSE_SUFFIXES, readPassages
    passages = readPassages(Path('README.md'))
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


### standard library only. checks.py imports this, and checks.py runs wherever python3 does

PROSE_SUFFIXES = frozenset({'.md', '.markdown', '.html', '.htm', '.txt'})
# matches:
# `<!-- noqa -->`
# `<!-- noqa: NAR017, NAR013 -->`
NOQA_COMMENT = re.compile(r'<!--\s*noqa(?::\s*(?P<codes>[A-Z0-9, ]+?))?\s*-->')
# matches:
# a fence of three or more backticks or tildes, with or without a language
FENCE = re.compile(r'\s*(?:```|~~~)')
# matches:
# `## Usage`
HEADING = re.compile(r'#{1,6}\s+')
# matches:
# `- item`
# `* item`
# `12. item`
LIST_MARKER = re.compile(r'(?:[-*+]|\d+[.)])\s+')
# matches:
# `|---|:--:|`
TABLE_RULE = re.compile(r'\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?')
# matches:
# `![diagram](flow.svg)`, dropped
# `[the guide](guide.md)`, kept as `the guide`
IMAGE = re.compile(r'!\[[^\]]*\]\([^)]*\)')
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')
# matches:
# `**bold**` and `__bold__`, whose markers the parser reads as words
EMPHASIS = re.compile(r'\*\*|__')
# elements whose text is not prose
SKIPPED_ELEMENTS = frozenset({'pre', 'script', 'style', 'template', 'head', 'noscript'})
# elements that sit inside a sentence. Every other element ends one passage and starts the next
INLINE_ELEMENTS = frozenset({
    'a', 'abbr', 'b', 'cite', 'code', 'data', 'dfn', 'em', 'i', 'kbd', 'mark', 'q', 's', 'samp',
    'small', 'span', 'strong', 'sub', 'sup', 'time', 'tspan', 'u', 'var', 'wbr',
})  # fmt: skip
# inline elements whose text is code, kept in backticks
CODE_ELEMENTS = frozenset({'code', 'kbd', 'samp', 'var'})


def readPassages(prose_file: Path) -> list[Passage]:
    """Read one Markdown, HTML or plain text file into passages, chosen by its suffix.

    Returns:
        The passages in line order.
    """
    text = prose_file.read_text(encoding='utf-8')
    suffix = prose_file.suffix.lower()
    if suffix in ('.html', '.htm'):
        return htmlPassages(text)
    if suffix in ('.md', '.markdown'):
        return markdownPassages(text)
    return paragraphPassages(text)


def suppressedCodes(source: str) -> dict[int, set[str]]:
    """Map each line with a `<!-- noqa -->` comment to the codes it silences.

    Returns:
        Line number to the set of codes, or `{'ALL'}` for a bare `<!-- noqa -->`.
    """
    suppressed: dict[int, set[str]] = {}
    for number, line in enumerate(source.splitlines(), start=1):
        for pragma in NOQA_COMMENT.finditer(line):
            codes = {code.strip() for code in (pragma['codes'] or '').split(',') if code.strip()}
            suppressed.setdefault(number, set()).update(codes or {'ALL'})
    return suppressed


def markdownPassages(markdown: str) -> list[Passage]:
    """Split Markdown into paragraphs, headings, list items, quotes and table cells.

    A line indented under a list item continues it. Front matter, fenced code, table rules and
    HTML comments are left out.

    Returns:
        The passages in line order.
    """
    passages: list[Passage] = []
    open_passage = False
    in_fence = False
    lines = markdown.splitlines()
    front_matter_end = frontMatterEnd(lines)
    for number, raw in enumerate(lines, start=1):
        if number <= front_matter_end:
            continue
        if FENCE.match(raw):
            in_fence = not in_fence
            open_passage = False
            continue
        line = NOQA_COMMENT.sub('', raw).strip()
        if in_fence or not line or line.startswith('<!--'):
            open_passage = False
            continue
        line = line.lstrip('>').strip()
        if line.startswith('|') or TABLE_RULE.fullmatch(line):
            if not TABLE_RULE.fullmatch(line):
                cells = (cell.strip() for cell in line.strip('|').split('|'))
                passages.extend(Passage((number,), (inlineText(cell),)) for cell in cells if cell)
            open_passage = False
            continue
        if start := HEADING.match(line) or LIST_MARKER.match(line):
            list_item = start.re is LIST_MARKER
            passages.append(Passage((number,), (inlineText(line[start.end() :]),), list_item))
            # a heading is one line, and a list item takes the indented lines after it
            open_passage = list_item
            continue
        if open_passage:
            passages[-1] = passages[-1].extendedBy(number, inlineText(line))
        else:
            passages.append(Passage((number,), (inlineText(line),)))
            open_passage = True
    return passages


def frontMatterEnd(lines: list[str]) -> int:
    """Find the closing `---` of YAML front matter at the top of a Markdown file.

    Returns:
        Its line number, or 0 when the file opens with no front matter.
    """
    if not lines or lines[0].strip() != '---':
        return 0
    return next((number for number, line in enumerate(lines[1:], start=2) if line.strip() == '---'), 0)


def inlineText(markdown: str) -> str:
    """Strip images, link targets and emphasis markers from one line of Markdown, keeping backticks.

    Returns:
        The line without Markdown syntax.
    """
    return EMPHASIS.sub('', LINK.sub(r'\1', IMAGE.sub('', markdown))).strip()


def htmlPassages(html: str) -> list[Passage]:
    """Split HTML into the text of its block elements, such as `p`, `li`, `td` and `figcaption`.

    Returns:
        The passages in line order.
    """
    reader = HtmlProse()
    reader.feed(html)
    reader.close()
    return reader.passages()


def paragraphPassages(text: str) -> list[Passage]:
    """Split plain text into paragraphs, one passage per run of lines without a blank line.

    Returns:
        The passages in line order.
    """
    passages: list[Passage] = []
    open_passage = False
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            open_passage = False
        elif open_passage:
            passages[-1] = passages[-1].extendedBy(number, line)
        else:
            passages.append(Passage((number,), (line,)))
            open_passage = True
    return passages


### vocabulary #########################################################################################


@dataclass(frozen=True)
class Passage:
    """Consecutive lines of prose, read as one text.

    A list item can open with a term and a dash, so the dash check of checks.py skips it.
    """

    lines: tuple[int, ...]
    texts: tuple[str, ...]
    list_item: bool = False

    @property
    def text(self) -> str:
        return ' '.join(self.texts)

    def extendedBy(self, number: int, text: str) -> Passage:
        return Passage((*self.lines, number), (*self.texts, text), self.list_item)

    def lineOf(self, hit: str) -> int:
        """Find the line of a hit such as `summary shows`.

        A hit can be split over two lines, so a line with the last word stands in for a line with
        every word.

        Returns:
            The first line with every word of the hit, else the first line with its last word, else
            the first line of the passage.
        """
        words = hit.split()
        lines = list(zip(self.lines, self.texts, strict=True))
        for wanted in (words, words[-1:]):
            for number, text in lines:
                if all(re.search(rf'\b{re.escape(word)}\b', text) for word in wanted):
                    return number
        return self.lines[0]


class HtmlProse(HTMLParser):
    """Collect the text of each block element of an HTML document, with its line numbers."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.list_depth = 0
        # line number to text, for the passage being read
        self.pending: dict[int, str] = {}
        self.pending_list_item = False
        self.done: list[Passage] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIPPED_ELEMENTS:
            self.skip_depth += 1
        elif tag in CODE_ELEMENTS and not self.skip_depth:
            self.handle_data('`')
        elif tag not in INLINE_ELEMENTS:
            self.endPassage()
            self.pending_list_item = tag == 'li'

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIPPED_ELEMENTS:
            self.skip_depth = max(self.skip_depth - 1, 0)
        elif tag in CODE_ELEMENTS and not self.skip_depth:
            self.handle_data('`')
        elif tag not in INLINE_ELEMENTS:
            self.endPassage()

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        first_line = self.getpos()[0]
        for offset, part in enumerate(data.split('\n')):
            number = first_line + offset
            self.pending[number] = self.pending.get(number, '') + part

    def endPassage(self) -> None:
        lines = [(number, ' '.join(text.split())) for number, text in sorted(self.pending.items())]
        lines = [(number, text) for number, text in lines if text]
        if lines:
            numbers, texts = zip(*lines, strict=True)
            self.done.append(Passage(tuple(numbers), tuple(texts), self.pending_list_item))
        self.pending = {}
        self.pending_list_item = False

    def passages(self) -> list[Passage]:
        self.endPassage()
        return self.done
