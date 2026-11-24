"""Find the comments of a Verilog or SystemVerilog file for slashcomments.py.

Both languages are read by the lexical rules of IEEE 1800-2023 SystemVerilog. Valid IEEE 1364-2005 Verilog has the same
comments under those rules. These literals can contain `//` or `/*` and are skipped:

    "a // b \\" c"                     a string, with backslash escapes
    \\bus//a                            an escaped identifier, up to the next whitespace
    `"msg // x `\\`"y`\\`"`"             a macro string of a define body, with its escaped quotes
    `include <a//b.svh>                the angle-bracket form of include
    `protected ... `endprotected       an encrypted region of the Verilog-XL form

A triple-quoted string of 1800-2023 is skipped too, over several lines and up to the next three quotes that a backslash
doesn't escape.

A `'` never opens a literal, because Verilog doesn't have a character literal: `'0`, `8'hFF`, `'{a, b}`, and `int'(x)`
are code. A `pragma protect key_block` or `pragma protect data_block` line can be a directive or a `//` comment. After
such a line, the base64 lines up to the next directive are skipped.

A `//` comment in the body of a macro definition ends at the line break. By IEEE 1800 section 22.5.1, the comment is not
part of the macro text. A comment line that ends with the backslash of the macro continuation is a pragma, so the
re-wrap leaves the line as written. The backslash of a `//` line is left out of the prose. A line of a `/* */` comment
that ends with the backslash is left out of the prose as a whole.

`/**`, `/*!`, `///`, and `//!` open a doc comment. A doc comment can have the Doxygen block tags such as `@brief`,
`@param`, and `@return`. The four are the doc comment openers of Doxygen. Doxygen reads Verilog through a filter, and
the TerosHDL documenter reads `//!`. A comment line that is a directive of a synthesis or lint tool, such as
`synopsys translate_off` or `verilator lint_off WIDTH`, or an SPDX tag, is a pragma and not prose.

Usage, from a script in this directory:
    import slashcomments
    import verilogcomments
    passages = slashcomments.passages(source, verilogcomments.SYSTEMVERILOG)
"""

from __future__ import annotations

import re

from slashcomments import DocMarkup, Language, Span, lexWith, neverMatches, quotedEnd


### standard library only. The prose checks import this, and they run wherever python3 does

# the text of a comment that a tool reads as a directive. After a tool name such as `synopsys`, a directive word has an
# underscore or is in the list
# matches:
# `synopsys translate_off`
# `synthesis keep`
# `pragma protect begin_protected`
# `verilator lint_off WIDTH`
# `spyglass disable_block W164a`
# `cadence map_to_mux`
# `coverage off`
# `VCS coverage on`
# `coverage off -item b 1`
# `SPDX-License-Identifier: Apache-2.0`
# rejects:
# `synthesis of the adder`
# `coverage on the FSM states`
PRAGMA = re.compile(
    r'^(?:synopsys|synthesis|pragma|exemplar|cadence|altera|verilator|spyglass)\s+'
    r'(?:[a-z]+_\w+|keep|preserve|noprune|attribute|template|enum|protect|coverage|public|clocker|forceable|sformat'
    r'|disable|enable)\b'
    r'|^(?:VCS\s+)?coverage\s+(?:(?:on|off)(?:\s+-|$)|[a-z]+_\w+)'
    r'|^SPDX-[A-Za-z-]+:',
)


def lexVerilog(source: str) -> list[Span]:
    return lexWith(source, skipLiteral, line_splice=False)


def skipLiteral(source: str, index: int) -> int | None:
    """Return the end of the literal or encrypted region that starts at `index`, or None when neither starts there."""
    char = source[index]
    if char == '"':
        return tripleQuotedEnd(source, index) if source.startswith('"""', index) else quotedEnd(source, index)
    if char == '\\':
        found = re.compile(r'\s').search(source, index + 1)
        return found.start() if found else len(source)
    if char == '`':
        return directiveEnd(source, index)
    if char == '\n':
        return encryptedEnd(source, index)
    return None


def tripleQuotedEnd(source: str, start: int) -> int:
    """Return the offset after the closing `\"\"\"` of a triple-quoted string.

    An unclosed string runs to the end of the source.
    """
    index = start + 3
    while index < len(source):
        if source[index] == '\\':
            index += 2
        elif source.startswith('"""', index):
            return index + 3
        else:
            index += 1
    return len(source)


def directiveEnd(source: str, index: int) -> int | None:
    """Return the end of a macro string, an escaped macro quote, an angle-bracket include, or an encrypted region."""
    # matches:
    # `` `include <a//b.svh> ``
    # `` `include<a.vh> ``
    ANGLE_INCLUDE = re.compile(r'`include[ \t]*<[^>\n]*>?')
    if source.startswith('`"', index):
        return macroStringEnd(source, index)
    if source.startswith('`\\`"', index):
        return index + 4
    if found := ANGLE_INCLUDE.match(source, index):
        return found.end()
    if re.compile(r'`protected\b').match(source, index):
        close = source.find('`endprotected', index)
        return len(source) if close == -1 else close
    return None


def macroStringEnd(source: str, start: int) -> int:
    """Return the offset after the closing `` `" `` of a macro string, or the line break of an unclosed one.

    An escaped macro quote `` `\\`" `` does not close the string. A backslash escapes the next character, so a backslash
    before the line break continues the string on the next line of the macro definition.
    """
    index = start + 2
    while index < len(source):
        if source.startswith('`\\`"', index):
            index += 4
        elif source.startswith('`"', index):
            return index + 2
        elif source[index] == '\\':
            index += 2
        elif source[index] == '\n':
            return index
        else:
            index += 1
    return len(source)


def encryptedEnd(source: str, newline: int) -> int | None:
    """Return the start of the next directive line after the key_block or data_block line that ends at `newline`.

    The lines between are base64, and base64 can contain `//`. Base64 doesn't have a backtick or a space, so the next
    line that opens with `` ` `` or `// pragma protect` is a directive again.
    """
    # matches:
    # `` `pragma protect data_block ``
    # `  // pragma protect key_block`
    # rejects:
    # `// pragma protect end_protected`
    ENCRYPTED_OPENER = re.compile(r'[ \t]*(?:`|//[ \t]*)pragma[ \t]+protect[ \t]+(?:key|data)_block\b[^\n]*')
    # matches:
    # `` `pragma protect end_protected ``
    # `// pragma protect data_method = "aes128-cbc"`
    DIRECTIVE_LINE = re.compile(r'^[ \t]*(?:`|//[ \t]*pragma[ \t]+protect\b)', re.MULTILINE)
    line_start = source.rfind('\n', 0, newline) + 1
    if not ENCRYPTED_OPENER.fullmatch(source, line_start, newline):
        return None
    found = DIRECTIVE_LINE.search(source, newline + 1)
    return found.start() if found else len(source)


def plainDoxygen(text: str) -> str:
    """Turn the Doxygen commands `@c word`, `@p word`, and `@ref name` into backticks."""
    # matches:
    # `@c data_in`
    # `\p width`
    # `@ref fifo_sync`
    INLINE_COMMAND = re.compile(r'[@\\](?:c|p|ref)\s+(\S+)')
    return INLINE_COMMAND.sub(lambda command: f'`{command[1]}`', text)


### vocabulary #########################################################################################


DOXYGEN = DocMarkup(
    # matches:
    # `@brief One-line summary`
    # `\param data the word`
    # rejects:
    # `\bus_a is the escaped identifier`
    # `@(posedge clk) samples data`
    block_tag=re.compile(
        r'^[@\\](?:brief|short|details|param|tparam|returns?|note|warning|deprecated|todo|author|version|date|copyright'
        r'|file|see|sa|since|ingroup|defgroup|addtogroup|code|verbatim)\b',
    ),
    # matches:
    # `@param data ` then the prose
    # `@brief ` then the prose
    named_tag=re.compile(
        r'^[@\\](?:param|tparam)(?:\[(?:in|out|in,out|inout)\])?\s+\S+\s*'
        r'|^[@\\](?:brief|short|details|returns?|note|warning|deprecated|todo)\b\s*',
    ),
    # matches:
    # `@author A. Name`
    # `\file fifo.sv`
    dropped_tag=re.compile(
        r'^[@\\](?:author|version|date|copyright|file|see|sa|since|ingroup|defgroup|addtogroup)\b',
    ),
    list_item=neverMatches(),
    sample_start=re.compile(r'^[@\\](?:code|verbatim)\b'),
    sample_end=re.compile(r'[@\\]end(?:code|verbatim)\b'),
    plain=plainDoxygen,
)
DOC_OPENERS = frozenset({'/**', '/*!', '///', '//!'})
VERILOG = Language(
    name='Verilog',
    suffixes=('.v', '.vh'),
    lex=lexVerilog,
    doc_openers=DOC_OPENERS,
    markup=DOXYGEN,
    pragma=PRAGMA,
)
SYSTEMVERILOG = Language(
    name='SystemVerilog',
    suffixes=('.sv', '.svh'),
    lex=lexVerilog,
    doc_openers=DOC_OPENERS,
    markup=DOXYGEN,
    pragma=PRAGMA,
)
LANGUAGES: tuple[Language, ...] = (VERILOG, SYSTEMVERILOG)
