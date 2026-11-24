r"""Find the comments of a C or C++ source file for slashcomments.py, and read the Doxygen markup.

A `//` or `/*` opens a comment only outside a literal. The lexer follows the rules of gcc and skips these literals
whole:

    "a // b"  '"'  '\''  L"x"  u8'x'      a string or character literal, with an encoding prefix
    "abc\                                  a line splice inside a string
    1'000'000  0x1'FF  .5e+1'0             a pp-number, whose `'` is a digit separator of C++14 and C23
    #include <sys//x.h>                    a header name, also in `__has_include(<...>)`
    R"--(a )" // b)--"                     a C++ raw string, also after `L`, `u`, `U` or `u8`

A character literal with no closing quote, such as the `'` of `don't` in a `#if 0` group, ends at the line break, so a
`//` later on that line is not a comment. C doesn't have raw strings: in a C file, `R"x(` is the identifier `R` and a
string.

In a doc comment (`///`, `//!`, `/**`, or `/*!`, then `<` for a trailing one), Doxygen markup is read too. Each section
command, such as `\param[in] name` or `@return`, opens a passage. The first line of `\see`, `\author`, and the other
sections of references and metadata is left out. A `\code` or `\verbatim` sample is left out. `\c word`, `\p name`, and
`\ref X` become a code span.

Usage, from a script in this directory:
    import ccomments
    import slashcomments
    passages = slashcomments.passages(source, ccomments.CPP)
"""

from __future__ import annotations

import re
from functools import partial

from slashcomments import DocMarkup, Language, Span, lexWith


### standard library only. The prose checks import this, and they run wherever python3 does

# matches:
# `"a // b"`
# `'\''`
# `"abc\` then a line break then `def"`
# `'unclosed` up to the line break
QUOTED = re.compile(r'"(?:\\\r\n|\\.|[^"\\\n])*"?' + r"|'(?:\\\r\n|\\.|[^'\\\n])*'?", re.DOTALL)
# a pp-number, the token of the preprocessor for a number. An `e+` or `p-` is part of the number
# matches:
# `1'000'000`
# `0x1'FF`
# `.5e+1'0`
# `12_km`
PP_NUMBER = re.compile(r"\.?[0-9](?:[eEpP][+-]|'[0-9A-Za-z_]|[0-9A-Za-z_.$])*")
# matches:
# `u8R`
# `__has_include`
# `$tmp`
IDENTIFIER = re.compile(r'[A-Za-z_$\x80-\U0010ffff][0-9A-Za-z_$\x80-\U0010ffff]*')
RAW_PREFIXES = frozenset({'R', 'LR', 'uR', 'UR', 'u8R'})
# the opening quote and the delimiter of a raw string. The delimiter has up to 16 characters, and doesn't have a space,
# a parenthesis, or a backslash
# matches:
# `"(`
# `"--(`
# rejects:
# `"a b(`
RAW_OPENING = re.compile(r'"([^ ()\\\t\v\f\n]{0,16})\(')
# a directive whose `<...>` is a header name. The directive opens with `#` or the digraph `%:` at the start of the line
# matches:
# `#include <sys//x.h>`
# `#  include_next <a.h>`
# `#import <Foundation/Foundation.h>`
# `%:include <sys//x.h>`
INCLUDE = re.compile(r'(?:#|%:)[ \t]*(?:include|include_next|import)[ \t]*<[^>\n]*>')
# the header name after `__has_include` or `__has_include_next`
# matches:
# `(<sys//x.h>)`
# ` ( <a.h>`
HAS_INCLUDE_ARGUMENT = re.compile(r'\s*\(\s*<[^>\n]*>')
HAS_INCLUDE = frozenset({'__has_include', '__has_include_next'})


def lexC(source: str) -> list[Span]:
    return lexWith(source, partial(skipLiteral, raw_strings=False), line_splice=True)


def lexCpp(source: str) -> list[Span]:
    return lexWith(source, partial(skipLiteral, raw_strings=True), line_splice=True)


def skipLiteral(source: str, start: int, *, raw_strings: bool) -> int | None:
    """Return the end of the literal, identifier, pp-number, or header name at `start`, or None for any other character.

    An identifier and a pp-number are skipped whole, so the `'` of a digit separator never opens a character literal.
    """
    char = source[start]
    if char in '"\'':
        found = QUOTED.match(source, start)
        return found.end() if found else None
    if char in '#%':
        line_start = source.rfind('\n', 0, start) + 1
        include = INCLUDE.match(source, start)
        return include.end() if include and not source[line_start:start].strip() else None
    if number := PP_NUMBER.match(source, start):
        return number.end()
    if not (identifier := IDENTIFIER.match(source, start)):
        return None
    end = identifier.end()
    if raw_strings and identifier[0] in RAW_PREFIXES and (opening := RAW_OPENING.match(source, end)):
        close = source.find(f'){opening[1]}"', opening.end())
        return len(source) if close == -1 else close + len(opening[1]) + 2
    if identifier[0] in HAS_INCLUDE and (argument := HAS_INCLUDE_ARGUMENT.match(source, end)):
        return argument.end()
    return end


def plainDoxygen(text: str) -> str:
    r"""Turn the inline Doxygen markup of one line into plain text and code spans.

            \c size, \p count and \ref Plan::read.   ->   `size`, `count` and `Plan::read`.
            <tt>x</tt> is \f$x^2\f$ \& more          ->   `x` is `x^2` & more

    An HTML tag that does not format text, such as `<int>` in `vector<int>`, stays as written.
    """
    # matches:
    # `\li the first item`
    LIST_COMMAND = re.compile(r'^[\\@](?:li|arg)\s+')
    # matches:
    # `<tt>size</tt>`
    # `<code>Plan::read()</code>`
    HTML_CODE = re.compile(r'<(tt|code)>(.*?)</\1>', re.IGNORECASE)
    # matches:
    # `<b>`
    # `</em>`
    # `<br/>`
    # rejects:
    # `<int>`
    HTML_FORMAT = re.compile(r'</?(?:b|i|em|strong|u|s|small|sup|sub|br|p|center|span|div)\b[^>]*>', re.IGNORECASE)
    # matches:
    # `&lt;`
    # `&amp;`
    ENTITY = re.compile(r'&(lt|gt|amp|quot|nbsp);')
    ENTITY_TEXT = {'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'nbsp': ' '}
    text = LIST_COMMAND.sub('', text)
    text = HTML_CODE.sub(lambda code: f'`{code[2]}`', text)
    text = HTML_FORMAT.sub('', text)
    text = ENTITY.sub(lambda entity: ENTITY_TEXT[entity[1]], text)
    return INLINE_COMMAND.sub(plainCommand, text)


def plainCommand(command: re.Match[str]) -> str:
    r"""Return the plain text of one inline command that `INLINE_COMMAND` matched.

    The punctuation after the word of `\c`, `\p`, or `\ref`, and a `)` with no `(` in the word, stay outside the code
    span: `(see \c size).` gives `` (see `size`). ``.
    """
    if command['escaped'] is not None:
        return command['escaped'].removeprefix('\\')
    if command['formula'] is not None:
        return f'`{command["formula"].strip()}`'
    if command['link_text'] is not None:
        return command['link_text'].strip()
    if command['ref_text'] is not None:
        return command['ref_text']
    if command['newline'] is not None:
        return ' '
    word = command['word']
    core = word.rstrip('.,;:!?')
    while core.endswith(')') and core.count(')') > core.count('('):
        core = core[:-1].rstrip('.,;:!?')
    if command['name'] in ('c', 'p', 'ref'):
        return f'`{core}`{word[len(core) :]}'
    return word


### vocabulary #########################################################################################


# matches:
# `\c size`
# `@p count`
# `\ref Plan::read "the read function"`
# `\link Plan the plan \endlink`
# `\f$x^2\f$`
# `\\`, an escaped backslash
# `\n`, a line break
# rejects:
# `\note`
# `user@c` in `user@c.org`
INLINE_COMMAND = re.compile(
    r'(?P<escaped>\\(?:---|--|::|[\\@&$#<>%".|]))'
    r'|[\\@]f\$(?P<formula>.*?)[\\@]f\$'
    r'|[\\@]link\s+\S+\s+(?P<link_text>.*?)[\\@]endlink'
    r'|(?<![\w@\\])[\\@]ref\s+\S+?\s+"(?P<ref_text>[^"]*)"'
    r'|(?<![\w@\\])[\\@](?P<newline>n)\b'
    r'|(?<![\w@\\])[\\@](?P<name>c|p|ref|a|b|e|em)\s+(?P<word>\S+)',
)
DOXYGEN = DocMarkup(
    # a command that opens a section of a doc comment, or a list item
    # matches:
    # `\param[in] path the file to read`
    # `@return the count`
    # `\see Plan::read`
    # `-# the second step`
    # rejects:
    # `\c size is the count`
    block_tag=re.compile(
        r'^(?:[\\@](?:param|tparam|returns?|result|retval|throws?|exception|brief|short|details|note|warning|attention'
        r'|pre|post|invariant|remarks?|deprecated|todo|bug|test|see|sa|authors?|version|date|since|copyright|li|arg)'
        r'\b|-#\s)',
    ),
    # matches:
    # `\param[in,out] buffer `
    # `@param count - `
    # `\throws std::out_of_range `
    # `\retval 0 `
    # `@brief `
    named_tag=re.compile(
        r'^[\\@](?:t?param\s*(?:\[[\w, ]*\])?\s+\S+(?:\s+[-:](?=\s))?|retval\s+\S+|(?:throws?|exception)\s+\S+)\s*'
        r'|^[\\@](?:returns?|result|brief|short|details|note|warning|attention|pre|post|invariant|remarks?|deprecated'
        r'|todo|bug|test)\b\s*',
    ),
    # a section of references or metadata, whose first line is not prose
    # matches:
    # `\see Plan::read`
    # `@author A. Writer`
    # `\since 2.1`
    dropped_tag=re.compile(r'^[\\@](?:see|sa|authors?|version|date|since|copyright)\b'),
    # matches:
    # `\li the first item`
    # `-# the first step`
    list_item=re.compile(r'^(?:[\\@](?:li|arg)\s|-#\s)'),
    # matches:
    # `\code`
    # `@code{.cpp}`
    # `\verbatim`
    # `\f[`
    # `<pre>`
    sample_start=re.compile(
        r'^(?:[\\@](?:code|verbatim|dot|msc|startuml|latexonly|htmlonly|xmlonly|manonly|rtfonly|docbookonly)\b'
        r'|[\\@]f[\[{]|<pre>)',
    ),
    # matches:
    # `\endcode`
    # `@endverbatim`
    # `\f]`
    # `</pre>`
    sample_end=re.compile(
        r'[\\@](?:endcode|endverbatim|enddot|endmsc|enduml|endlatexonly|endhtmlonly|endxmlonly|endmanonly|endrtfonly'
        r'|enddocbookonly)\b|[\\@]f[\]}]|</pre>',
    ),
    plain=plainDoxygen,
)
# the text of a comment that is a directive to a tool. A Doxygen command whose argument is the rest of the line, such as
# `\file` or `\defgroup`, is a directive too. A directive line stays as written in the re-wrap
# matches:
# `NOLINTNEXTLINE(bugprone-branch-clone)`
# `clang-format off`
# `IWYU pragma: keep`
# `LCOV_EXCL_START`
# `cppcheck-suppress nullPointer`
# `SPDX-License-Identifier: MIT`
# `FALLTHRU`
# `falls through.`
# `NOTREACHED`
# `<vector> -*- C++ -*-`
# `vim: set ts=8:`
# `\file plan.h`
# `@{`
# rejects:
# `fall through to the default case when the count is zero`
PRAGMA = re.compile(
    r'^(?:NOLINT(?:NEXTLINE|BEGIN|END)?\b|clang-format\s+(?:off|on)\b|IWYU\s+pragma:|(?:LCOV|GCOV|GCOVR)_EXCL_\w+'
    r'|cppcheck-suppress|NOSONAR\b|coverity\[|SPDX-[\w-]+:|-V\d'
    r'|(?:NOTREACHED|ARGSUSED|VARARGS|LINTED|LINTLIBRARY|PRINTFLIKE|SCANFLIKE|CONSTCOND)\d*\b'
    r'|(?:lint\s+)?-fallthrough\s*$|@fallthrough@$'
    r'|(?i:(?:else,? |intentional(?:ly)? )?fall(?:s | |-)?thr(?:ough|u))[ \t.!]*(?:-.*)?$'
    r'|(?:vim?|ex):\s'
    r'|[\\@](?:file|class|struct|union|enum|fn|def|var|typedef|namespace|interface|property|concept|headerfile'
    r'|defgroup|ingroup|addtogroup|weakgroup|name|mainpage|page|section|subsection|subsubsection|paragraph|par|anchor'
    r'|cond|endcond|internal|endinternal|copydoc|copybrief|copydetails|overload|example|include|snippet|image'
    r'|relates|relatesalso|memberof|private|protected|public|nosubgrouping|hideinitializer|showinitializer)\b'
    r'|[\\@][{}]$)'
    r'|-\*-.*-\*-',
)
DOC_OPENERS = frozenset({'///', '//!', '/**', '/*!'})
C = Language(
    name='C',
    suffixes=('.c',),
    lex=lexC,
    doc_openers=DOC_OPENERS,
    markup=DOXYGEN,
    pragma=PRAGMA,
)
# a `.h` file is read as C++. The two lexers differ only at a raw string such as `R"(x)"`
CPP = Language(
    name='C++',
    # fmt: off
    suffixes=(
        '.cpp',
        '.cc',
        '.cxx',
        '.c++',
        '.C',
        '.hpp',
        '.hh',
        '.hxx',
        '.h++',
        '.h',
        '.ipp',
        '.tpp',
        '.tcc',
        '.inl',
        '.ixx',
        '.cppm',
        '.cu',
        '.cuh',
    ),
    # fmt: on
    lex=lexCpp,
    doc_openers=DOC_OPENERS,
    markup=DOXYGEN,
    pragma=PRAGMA,
)
LANGUAGES = (C, CPP)
