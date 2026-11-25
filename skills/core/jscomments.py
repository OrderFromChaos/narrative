"""Find the comments of a JavaScript, TypeScript, JSX, or TSX file for the comment checks of slashcomments.py.

The lexer reads the source once, left to right, and skips every literal that can contain `//` or `/*`: a string, the
text of a template literal, a regex literal, and the text and attribute strings of a JSX element. The code in the `${}`
of a template literal and in the `{}` of a JSX element is read as code, so a comment in that code counts. A `/` opens a
regex where an expression can start, and divides after an operand. Whether a `/` opens a regex depends on the token
before the `/` and on a stack of the open brackets. A `}` that closes a block is followed by a statement, so a `/` after
the block opens a regex. A `}` that closes an object literal or the body of a function expression is an operand.

A `<` where an expression can start opens a JSX element in a .js, .mjs, .cjs, .jsx or .tsx file. The element runs to the
element's closing tag. A `<` that does not open a whole element, such as the type parameters of `<T,>(x: T) => x` in a
.tsx file, is an operator. In a .ts file, `<T>x` is a type assertion, and a `<` never opens an element.

The doc comment is the JSDoc or TSDoc `/** */` comment. In a doc comment, the inline tags such as `{@link X|text}`, the
HTML tags, and the Markdown links are read as plain text. The type and the name of a block tag such as
`@param {string} path -` are left out. An `@example` sample is left out up to the next block tag. A line comment `///`
is a plain comment, and a TypeScript directive such as `/// <reference path="x.d.ts" />` is a pragma.

Known limits, each shown by limits.js or limits.ts in core/tests/comments:
- a `/` after `await`, `yield`, or `let` opens a regex, also in a sloppy-mode script that uses the word as a name
- an HTML-like comment of Annex B of ECMAScript, `<!--` or `-->`, is read as operators
- a type literal at the end of a TypeScript type alias is read as an object literal, so a `/` on the next line divides
- a `>` that closes a TypeScript type such as `Array<number>` is read as an operator, so a `/` after the type opens a
  regex

Usage, from a script in this directory:
    import jscomments
    import slashcomments
    passages = slashcomments.passages(source, jscomments.TYPESCRIPT)
"""

from __future__ import annotations

import re
from enum import Enum

from prose import EMPHASIS, IMAGE, LINK
from slashcomments import DocMarkup, Language, Span, quotedEnd


### standard library only. The prose checks import this, and they run wherever python3 does

# the text of a comment that a tool reads, such as a linter, a type checker, a bundler, or a coverage tool
# matches:
# `eslint-disable-next-line no-console`
# `eslint quotes: ["error", "double"]`
# `global window, document`
# `@ts-expect-error: the type is wrong upstream`
# `prettier-ignore`
# `istanbul ignore next`
# `c8 ignore start`
# `#__PURE__`
# `webpackChunkName: "chart"`
# `# sourceMappingURL=index.js.map`
# `@vite-ignore`
# `@jsxImportSource preact`
# `<reference path="globals.d.ts" />`
# rejects:
# `global state is reset here`
# `the webpack chunk of the chart`
PRAGMA = re.compile(
    r'^(?:eslint-(?:disable|enable|env)\b|eslint\s+[@\w/-]+\s*:'
    r'|globals?\s+[\w$]+(?:\s*:\s*\w+)?(?:\s*,\s*[\w$]+(?:\s*:\s*\w+)?)*\s*,?\s*$'
    r'|exported\s+[\w$]+(?:\s*,\s*[\w$]+)*\s*$'
    r'|js[hl]int\s+\w+\s*:|tslint:(?:disable|enable)'
    r'|@ts-(?:ignore|expect-error|nocheck|check)\b|prettier-ignore|(?:istanbul|c8|v8)\s+ignore\b'
    r'|[#@]__[A-Z_]+__$|webpack[A-Z]\w*\s*:|[#@]\s*source(?:Mapping)?URL=|@vite-ignore\b'
    r'|@jsx(?:ImportSource|Frag|Runtime)?\s|<(?:reference|amd-module|amd-dependency)\b'
    r'|@flow\b|@noflow\b|\$Flow(?:FixMe|Ignore|ExpectedError|Issue)\b|@(?:format|prettier)$'
    r'|biome-ignore\b|deno-(?:lint|fmt)-ignore\b|oxlint-(?:disable|enable)\b|#(?:end)?region\b'
    r'|@(?:jest|vitest)-environment\b|NOSONAR\b)',
)


def lexScript(source: str) -> list[Span]:
    return Lexer(source, jsx=True).lexFile()


def lexTypeScript(source: str) -> list[Span]:
    return Lexer(source, jsx=False).lexFile()


class Lexer:
    """The comment spans found so far, and the offset of the next character to read."""

    def __init__(self, source: str, *, jsx: bool) -> None:
        self.source = source
        self.jsx = jsx
        self.index = 0
        self.spans: list[Span] = []

    def lexFile(self) -> list[Span]:
        """Find the comment spans of the whole source.

        A hashbang line such as `#!/usr/bin/env node` is not a comment.
        """
        if self.source.startswith('#!'):
            end = self.source.find('\n')
            self.index = len(self.source) if end == -1 else end
        self.scanCode(embedded=False)
        return self.spans

    def scanCode(self, *, embedded: bool) -> bool:
        """Read code up to the end of the source or, when `embedded`, up to the `}` that closes a `${` or a JSX `{`.

        When the `}` is found, the offset is after the `}` on return.

        Returns:
            Whether the closing `}` was found. Always False for the code of a whole file.
        """
        frame = Frame(embedded=embedded)
        while True:
            if self.skipTrivia():
                frame.newline = True
            if self.index >= len(self.source):
                return False
            if self.readToken(frame):
                return True

    def skipTrivia(self) -> bool:
        """Skip one run of whitespace and comments, and record the comments.

        Returns:
            Whether the whitespace or a block comment of the run has a line break.
        """
        source = self.source
        newline = False
        while self.index < len(source):
            char = source[self.index]
            if char in LINE_BREAKS:
                newline = True
                self.index += 1
            elif char.isspace() or char == '\ufeff':
                self.index += 1
            elif source.startswith('//', self.index):
                line_break = LINE_BREAK.search(source, self.index)
                end = line_break.start() if line_break else len(source)
                self.spans.append(Span(self.index, end))
                self.index = end
            elif source.startswith('/*', self.index):
                close = source.find('*/', self.index + 2)
                end = len(source) if close == -1 else close + 2
                newline = newline or any(mark in source[self.index : end] for mark in LINE_BREAKS)
                self.spans.append(Span(self.index, end))
                self.index = end
            else:
                break
        return newline

    def readToken(self, frame: Frame) -> bool:
        """Read one token, and set in the frame whether an expression or a statement can start after the token.

        Returns:
            Whether the token is the `}` that closes an embedded frame.
        """
        source = self.source
        char = source[self.index]
        if char == '/':
            if frame.expression_allowed:
                self.index = regexEnd(source, self.index)
                frame.accept('', expression_allowed=False)
            else:
                self.index += 2 if source.startswith('/=', self.index) else 1
                frame.accept('/', expression_allowed=True)
        elif char in '\'"':
            self.index = quotedEnd(source, self.index)
            frame.accept('', expression_allowed=False)
        elif char == '`':
            self.skipTemplate()
            frame.accept('', expression_allowed=False)
        elif number := NUMBER.match(source, self.index):
            self.index = number.end()
            frame.accept('', expression_allowed=False)
        elif word := WORD.match(source, self.index):
            self.index = word.end()
            self.readWord(word[0], frame)
        elif char == '{':
            self.index += 1
            frame.openBrace()
        elif char == '}':
            self.index += 1
            return frame.closeBrace()
        elif char in '([':
            self.index += 1
            frame.openBracket(char)
        elif char in ')]':
            self.index += 1
            frame.closeBracket(char)
        elif char == '<' and self.jsx and frame.expression_allowed and self.readJsx():
            frame.accept('', expression_allowed=False)
        else:
            punctuator = PUNCTUATOR.match(source, self.index)
            self.index = punctuator.end() if punctuator else self.index + 1
            frame.readPunctuator(punctuator[0] if punctuator else char)
        return False

    def readWord(self, word: str, frame: Frame) -> None:
        """Read a keyword or a name. A word after `.` or `?.` is a property name, even a word such as `return`."""
        if frame.previous in ('.', '?.') or word not in KEYWORDS:
            frame.accept('', expression_allowed=False)
        elif word in ('function', 'class'):
            # in `{ class: 'x' }` and `{ function: f }`, the keyword is a property name
            if not FOLLOWED_BY_COLON.match(self.source, self.index):
                frame.openFunction(word)
            else:
                frame.accept('', expression_allowed=False)
        elif word == 'async' or word == 'of':
            self.readContextualWord(word, frame)
        else:
            frame.accept(word, expression_allowed=True, statement_start=word in STATEMENT_KEYWORDS)

    def readContextualWord(self, word: str, frame: Frame) -> None:
        """Read `async` before `function` as part of the function, and `of` in the head of a `for` as a keyword."""
        if word == 'async' and ASYNC_FUNCTION.match(self.source, self.index):
            return
        if word == 'of' and frame.top is Context.STATEMENT_PAREN:
            frame.accept('of', expression_allowed=True)
            return
        frame.accept('', expression_allowed=False)

    def skipTemplate(self) -> None:
        """Skip a template literal and the code of each `${}` expression in the literal. Comments in the code count."""
        source = self.source
        self.index += 1
        while self.index < len(source):
            char = source[self.index]
            if char == '\\':
                self.index += 2
            elif char == '`':
                self.index += 1
                return
            elif source.startswith('${', self.index):
                self.index += 2
                self.scanCode(embedded=True)
            else:
                self.index += 1
        self.index = min(self.index, len(source))

    def readJsx(self) -> bool:
        """Skip the JSX element at `<`, or leave the offset at `<` when a whole element doesn't start there.

        When the element is incomplete, the comments found inside the element are dropped too.
        """
        if GENERIC_ARROW.match(self.source, self.index):
            return False
        start, recorded = self.index, len(self.spans)
        if self.skipJsxElement():
            return True
        self.index = start
        del self.spans[recorded:]
        return False

    def skipJsxElement(self) -> bool:
        """Skip one JSX element or fragment from `<`: the opening tag, the children, and the closing tag.

        Returns:
            False when the text from `<` is not a whole element, such as a closing tag with another name.
        """
        source = self.source
        self.index += 1
        self.skipTrivia()
        name = ''
        if found := JSX_NAME.match(source, self.index):
            name = found[0]
            self.index = found.end()
            self.skipTypeArguments()
        elif not source.startswith('>', self.index):
            return False
        while True:
            self.skipTrivia()
            if source.startswith('/>', self.index):
                self.index += 2
                return bool(name)
            if source.startswith('>', self.index):
                self.index += 1
                break
            if not (name and self.skipJsxAttribute()):
                return False
        return self.skipJsxChildren(name)

    def skipTypeArguments(self) -> None:
        """Skip the type arguments of a TSX element, such as `<string>` in `<Select<string> value="a" />`."""
        if not self.source.startswith('<', self.index):
            return
        depth = 0
        for offset in range(self.index, len(self.source)):
            depth += {'<': 1, '>': -1}.get(self.source[offset], 0)
            if depth == 0:
                self.index = offset + 1
                return

    def skipJsxAttribute(self) -> bool:
        """Skip one attribute of an opening tag: `{...props}`, `name`, or `name=` and a string, `{}` or an element.

        A backslash doesn't escape in a JSX attribute string, so `"\\"` is a whole string.
        """
        source = self.source
        if source.startswith('{', self.index):
            self.index += 1
            return self.scanCode(embedded=True)
        attribute = JSX_NAME.match(source, self.index)
        if attribute is None:
            return False
        self.index = attribute.end()
        self.skipTrivia()
        if not source.startswith('=', self.index):
            return True
        self.index += 1
        self.skipTrivia()
        char = source[self.index : self.index + 1]
        if char in ('"', "'"):
            close = source.find(char, self.index + 1)
            self.index = close + 1
            return close != -1
        if char == '{':
            self.index += 1
            return self.scanCode(embedded=True)
        return char == '<' and self.skipJsxElement()

    def skipJsxChildren(self, name: str) -> bool:
        """Skip the text, the `{}` expressions, and the child elements up to the closing tag of `name`.

        A `//` or `/*` in the text of an element is text. A comment in a `{}` expression counts.
        """
        source = self.source
        while (delimiter := JSX_CHILD_DELIMITER.search(source, self.index)) is not None:
            self.index = delimiter.start()
            if delimiter[0] == '{':
                self.index += 1
                if not self.scanCode(embedded=True):
                    return False
                continue
            closing_tag = JSX_CLOSING_TAG.match(source, self.index)
            if closing_tag is None:
                if not self.skipJsxElement():
                    return False
                continue
            self.index = closing_tag.end()
            found = JSX_NAME.match(source, self.index)
            closing = found[0] if found else ''
            self.index = found.end() if found else self.index
            self.skipTrivia()
            if closing != name or not source.startswith('>', self.index):
                return False
            self.index += 1
            return True
        return False


def regexEnd(source: str, start: int) -> int:
    """Return the offset after the flags of the regex literal at `start`. A `/` in a class such as `[/]` is a char."""
    index = start + 1
    in_class = False
    while index < len(source):
        char = source[index]
        if char == '\\' and source[index + 1 : index + 2] not in LINE_BREAKS:
            index += 2
            continue
        if char in LINE_BREAKS:
            return index
        if char == '/' and not in_class:
            flags = REGEX_FLAGS.match(source, index + 1)
            return flags.end() if flags else index + 1
        in_class = (in_class or char == '[') and char != ']'
        index += 1
    return index


def plainJsdoc(text: str) -> str:
    """Turn the inline markup of one line of JSDoc or TSDoc into plain text and backticks.

    A link becomes the link's text, or the target in backticks when the link doesn't have text.
    """
    text = LINK_TAG.sub(
        lambda tag: (tag['label'] or tag['text'] or tag['words'] or '').strip() or f'`{tag["target"]}`',
        text,
    )
    text = INLINE_TAG.sub(lambda tag: f'`{tag["body"].strip()}`' if tag['body'] and tag['body'].strip() else '', text)
    text = CODE_TAG.sub('`', text)
    text = HTML_TAG.sub(' ', text)
    text = IMAGE.sub('', text)
    text = LINK.sub(r'\1', text)
    return EMPHASIS.sub('', text)


### vocabulary #########################################################################################


class Context(Enum):
    """Each `Context` is an open bracket, a `function` or `class` keyword before the body, or the code of a whole frame.

    The code of a whole file is TOP, and the code of a `${}` or a JSX `{}` is EMBEDDED.

    A `function` or `class` keyword opens a FUNCTION_EXPRESSION or a FUNCTION_DECLARATION. braceContext() replaces that
    context with an EXPRESSION_BODY or a BLOCK at the `{` of the body.
    """

    TOP = 'top'
    EMBEDDED = 'embedded'
    BLOCK = 'block'
    OBJECT = 'object'
    EXPRESSION_BODY = 'expression body'
    STATEMENT_PAREN = 'statement paren'
    EXPRESSION_PAREN = 'expression paren'
    BRACKET = 'bracket'
    FUNCTION_EXPRESSION = 'function expression'
    FUNCTION_DECLARATION = 'function declaration'


# the contexts of statements, such as a block or the body of a function
STATEMENT_CONTEXTS = frozenset({Context.TOP, Context.BLOCK, Context.EXPRESSION_BODY})
BRACE_CONTEXTS = frozenset({Context.BLOCK, Context.OBJECT, Context.EXPRESSION_BODY})
FUNCTION_CONTEXTS = frozenset({Context.FUNCTION_EXPRESSION, Context.FUNCTION_DECLARATION})
CLOSING_CONTEXTS = {
    ')': frozenset({Context.STATEMENT_PAREN, Context.EXPRESSION_PAREN}),
    ']': frozenset({Context.BRACKET}),
}


class Frame:
    """A `Frame` is the state of the code of a whole file, or of one `${}` or JSX `{}` expression.

    `previous` is the keyword or punctuator before the offset, or empty after a name or a literal. `expression_allowed`
    is whether an expression can start at the offset, so that a `/` opens a regex. `statement_start` is whether a
    statement can start at the offset, so that a `{` opens a block. `newline` is whether a line break comes after the
    previous token. For each context, `questions` has the number of ternary `?` before the offset that don't have a `:`
    yet.
    """

    def __init__(self, *, embedded: bool) -> None:
        self.contexts = [Context.EMBEDDED if embedded else Context.TOP]
        self.questions = [0]
        self.previous = ''
        self.expression_allowed = True
        self.statement_start = not embedded
        self.newline = False

    @property
    def top(self) -> Context:
        return self.contexts[-1]

    def accept(self, previous: str, *, expression_allowed: bool, statement_start: bool = False) -> None:
        self.previous = previous
        self.expression_allowed = expression_allowed
        self.statement_start = statement_start
        self.newline = False

    def push(self, context: Context) -> None:
        self.contexts.append(context)
        self.questions.append(0)

    def popTo(self, depth: int) -> Context:
        """Close every context from `depth` up, and return the context at `depth`."""
        closed = self.contexts[depth]
        del self.contexts[depth:]
        del self.questions[depth:]
        return closed

    def openFunction(self, keyword: str) -> None:
        """Open a function or class as an expression or as a declaration.

        The kind depends on the token before the keyword.
        """
        expression = self.expression_allowed and not self.statement_start and self.previous != 'default'
        self.push(Context.FUNCTION_EXPRESSION if expression else Context.FUNCTION_DECLARATION)
        self.accept(keyword, expression_allowed=False)

    def openBrace(self) -> None:
        self.push(self.braceContext())
        self.accept('{', expression_allowed=True, statement_start=self.top in STATEMENT_CONTEXTS)

    def braceContext(self) -> Context:
        """Return the context that a `{` opens: a block, an object literal, or the body of a function or class."""
        if self.top in FUNCTION_CONTEXTS and self.previous not in TYPE_PUNCTUATORS:
            # the `{` of a type comes after one of TYPE_PUNCTUATORS. In `function f(): { a: number } {`, the first `{`
            # opens a type and the second `{` opens the body
            marker = self.popTo(len(self.contexts) - 1)
            return Context.EXPRESSION_BODY if marker is Context.FUNCTION_EXPRESSION else Context.BLOCK
        if self.previous in (')', '=>', '>'):
            # `>` ends the type parameters of a TypeScript declaration such as `interface Box<T> {`
            return Context.BLOCK
        if self.previous == ':':
            # a statement starts after the `:` of a label or a `case`. Any other `:` is followed by an expression or a
            # type
            return Context.BLOCK if self.statement_start else Context.OBJECT
        if self.previous in ('return', 'yield'):
            # a line break after `return` or `yield` ends the statement
            return Context.BLOCK if self.newline else Context.OBJECT
        if self.statement_start:
            return Context.BLOCK
        return Context.OBJECT if self.expression_allowed else Context.BLOCK

    def closeBrace(self) -> bool:
        """Close the innermost brace. After a block, a statement starts, and after an object literal, an operator.

        Returns:
            Whether the `}` closes the `${}` or JSX `{}` of an embedded frame.
        """
        depth = max((depth for depth, context in enumerate(self.contexts) if context in BRACE_CONTEXTS), default=0)
        if depth == 0:
            self.accept('}', expression_allowed=True, statement_start=True)
            return self.contexts[0] is Context.EMBEDDED
        closed = self.popTo(depth)
        block = closed is Context.BLOCK
        self.accept('}', expression_allowed=block, statement_start=block)
        return False

    def openBracket(self, bracket: str) -> None:
        if bracket == '[':
            self.push(Context.BRACKET)
        else:
            control = self.previous in ('if', 'while', 'for', 'with')
            self.push(Context.STATEMENT_PAREN if control else Context.EXPRESSION_PAREN)
        self.accept(bracket, expression_allowed=True)

    def closeBracket(self, bracket: str) -> None:
        """Close the innermost `(` or `[`. After the head of an `if`, `while`, `for`, or `with`, a statement starts."""
        openers = CLOSING_CONTEXTS[bracket]
        depth = max((depth for depth, context in enumerate(self.contexts) if context in openers), default=0)
        control = depth > 0 and self.popTo(depth) is Context.STATEMENT_PAREN
        self.accept(bracket, expression_allowed=control, statement_start=control)

    def readPunctuator(self, punctuator: str) -> None:
        """Update the frame after an operator or another punctuator.

        `++` and `--` count as postfix. A `!` after an operand on the same line is the non-null assertion of TypeScript.
        """
        if punctuator in ('++', '--') or (punctuator == '!' and not self.expression_allowed and not self.newline):
            self.accept(punctuator, expression_allowed=False)
            return
        if punctuator == '?':
            self.questions[-1] += 1
        elif punctuator == ':' and self.questions[-1]:
            self.questions[-1] -= 1
            self.accept(':', expression_allowed=True)
            return
        elif punctuator == ';':
            self.questions[-1] = 0
            if self.top in FUNCTION_CONTEXTS:
                # an overload or a declared function of TypeScript doesn't have a body. Close the function at the `;`
                self.popTo(len(self.contexts) - 1)
        labelled = punctuator == ':' and self.top in STATEMENT_CONTEXTS
        self.accept(punctuator, expression_allowed=True, statement_start=punctuator == ';' or labelled)


# the keywords that don't end an operand. A `/` after such a keyword opens a regex. readWord() reads `function`,
# `class`, `async`, and `of` apart from the other keywords. `this`, `super`, `null`, `true`, and `false` are operands,
# so they are names here
# fmt: off
KEYWORDS = frozenset({
    'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'do',
    'else', 'export', 'extends', 'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new', 'of',
    'return', 'switch', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield',
})
# fmt: on
# the keywords after which a statement starts, so that a `{` opens a block and `function` a declaration
STATEMENT_KEYWORDS = frozenset({'do', 'else', 'export', 'finally', 'try'})
# the tokens before the `{` of a type in the signature of a function, such as `: {` and `<{`
TYPE_PUNCTUATORS = frozenset({':', '<', ',', '|', '&', '=', '?', '=>', 'extends'})
LINE_BREAKS = '\n\r\u2028\u2029'
LINE_BREAK = re.compile(f'[{LINE_BREAKS}]')
# matches:
# `42`
# `0x1F`
# `1_000n`
# `.5e-3`
NUMBER = re.compile(r'(?:\d[\w.]*|\.\d[\w.]*)(?:(?<=[eE])[+-]\d\w*)?')
# a name or keyword, a private name, or a name with a Unicode escape
# matches:
# `$scope`
# `#count`
# `caf\u00e9`
WORD = re.compile(r'#?(?:[\w$\u200c\u200d]|\\u(?:[0-9a-fA-F]{4}|\{[0-9a-fA-F]+\}))+')
# matches:
# `>>>=`
# `?.`, but in `a?.5:1` only `?`
# `=>`
PUNCTUATOR = re.compile(
    r'>>>=|\.\.\.|===|!==|\*\*=|<<=|>>=|>>>|&&=|\|\|=|\?\?=|=>|==|!=|<=|>=|&&|\|\||\?\?|\?\.(?!\d)|\+\+|--'
    r'|[-+*%&|^]=|\*\*|<<|>>',
)
REGEX_FLAGS = re.compile(r'[\w$]*')
# the `:` after a keyword used as a property name, such as `class` in `{ class: 'x' }` or `function` in
# `type T = { function?: F }`
# matches:
# `:`
# ` ?:`
FOLLOWED_BY_COLON = re.compile(r'\s*\??:')
ASYNC_FUNCTION = re.compile(r'[ \t]+function\b')
# the type parameters of a generic arrow function in a .tsx file
# matches:
# `<T,>`
# `<const T,>`
# `<T extends object>`
# rejects:
# `<T>`
GENERIC_ARROW = re.compile(r'<\s*(?:const\s+)?[A-Za-z_$][\w$]*\s*(?:,|extends\b)')
# matches:
# `div`
# `Foo.Bar`
# `svg:rect`
# `data-id`
JSX_NAME = re.compile(r'[A-Za-z_$][\w$-]*(?:[:.][A-Za-z_$][\w$-]*)*')
JSX_CHILD_DELIMITER = re.compile(r'[<{]')
JSX_CLOSING_TAG = re.compile(r'<\s*/\s*')
# matches:
# `{@link Store}`
# `{@link Store|the store}`
# `{@link Store the store}`
# `{@link Store | the store}`, in TSDoc
# `[the store]{@link Store}`
# `{@linkcode Store.read}`
LINK_TAG = re.compile(
    r'(?:\[(?P<label>[^\]]*)\])?\{@link(?:code|plain)?\s+(?P<target>[^\s|}]+)'
    r'(?:\s*\|(?P<text>[^}]*)|\s+(?P<words>[^}|]*))?\}',
)
# an inline tag other than a link. A doc generator copies another doc comment in place of `{@inheritDoc}`, so the text
# of the tag isn't prose
# matches:
# `{@tutorial getting-started}`, as `getting-started`
# `{@inheritDoc Store.read}`, as nothing
INLINE_TAG = re.compile(r'\{@(?!inheritDoc\b)\w+(?:\s+(?P<body>[^}]*))?\}|\{@inheritDoc\b[^}]*\}')
CODE_TAG = re.compile(r'</?code>', re.IGNORECASE)
# the HTML tags of JSDoc. The `<` of a type such as `Promise<void>` is text
# matches:
# `<p>`
# `<a href="guide.html">`
# `</strong>`
# rejects:
# `<void>`
HTML_TAG = re.compile(
    r'</?(?:a|b|blockquote|br|caption|dd|del|div|dl|dt|em|h[1-6]|hr|i|img|ins|kbd|li|ol|p|pre|s|small|span|strong'
    r'|sub|sup|table|td|th|tr|tt|u|ul|var)\b[^>]*>',
    re.IGNORECASE,
)
# matches:
# `@param`, `@returns`, and every other block tag
# rejects:
# `@Component(`, a decorator in an `@example` sample
BLOCK_TAG = re.compile(r'^@[a-z][\w-]*(?![\w(.])')
# a type in braces with up to two levels of braces inside, such as `{{a: {b: number}}}`
TYPE = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
# the part of a tag line before the prose
# matches:
# `@param {string} [name='x'] -`
# `@param {{a: number}} obj`
# `@returns {Promise<void>}`
# `@template T -`
# `@deprecated`
NAMED_TAG = re.compile(
    rf'^@(?:param|arg|argument|property|prop)\b\s*(?:{TYPE}\s*)?(?:\[(?:[^\[\]]|\[[^\]]*\])*\]|[\w$.\[\]]+)?\s*(?:-\s+|-$)?'
    rf'|^@(?:returns?|yields?|throws|exception)\b\s*(?:{TYPE}\s*)?(?:-\s+|-$)?'
    rf'|^@(?:template|typeParam)\b\s*(?:{TYPE}\s*)?[\w$]+(?:\s*,\s*[\w$]+)*\s*(?:-\s+|-$)?'
    r'|^@(?:deprecated|summary|description|desc|remarks|privateRemarks|todo|file|fileoverview|overview|classdesc)\b\s*',
)
# a tag whose line is not prose, such as `@type {number}`, `@see Store`, or `@since 2.0`
DROPPED_TAG = re.compile(
    r'^@(?!(?:param|arg|argument|property|prop|returns?|yields?|throws|exception|template|typeParam|deprecated'
    r'|summary|description|desc|remarks|privateRemarks|todo|file|fileoverview|overview|classdesc|example)\b)'
    r'[a-z][\w-]*(?![\w(.])',
)
JSDOC = DocMarkup(
    block_tag=BLOCK_TAG,
    named_tag=NAMED_TAG,
    dropped_tag=DROPPED_TAG,
    list_item=re.compile(r'^<li\b', re.IGNORECASE),
    sample_start=re.compile(r'^@example\b'),
    sample_end=None,
    plain=plainJsdoc,
)
JAVASCRIPT = Language(
    name='JavaScript',
    suffixes=('.js', '.mjs', '.cjs'),
    lex=lexScript,
    doc_openers=frozenset({'/**'}),
    markup=JSDOC,
    pragma=PRAGMA,
)
TYPESCRIPT = Language(
    name='TypeScript',
    suffixes=('.ts', '.mts', '.cts'),
    lex=lexTypeScript,
    doc_openers=frozenset({'/**'}),
    markup=JSDOC,
    pragma=PRAGMA,
)
JSX = Language(
    name='JSX',
    suffixes=('.jsx',),
    lex=lexScript,
    doc_openers=frozenset({'/**'}),
    markup=JSDOC,
    pragma=PRAGMA,
)
TSX = Language(
    name='TSX',
    suffixes=('.tsx',),
    lex=lexScript,
    doc_openers=frozenset({'/**'}),
    markup=JSDOC,
    pragma=PRAGMA,
)
LANGUAGES: tuple[Language, ...] = (JAVASCRIPT, TYPESCRIPT, JSX, TSX)
