r"""Flag comments and docstrings whose subject cannot act, and clauses with their subject cut.

NAR017 is an agent verb on a subject that cannot act. NAR020 is a clause with no subject before
`, so`: `Named, so a recreated container gets it back`. The rewrite has a subject: `Named volumes
persist when a container is recreated`.

`a period ranks by its newest snapshot` makes a period rank, and `the report names it` makes a
report speak. A subject acts when it is a person, an animal, a role such as `caller`, or a pronoun
for one. A noun made from a verb with no person sense in common use, such as `solver`, is the name
of a program and cannot act. A verb counts as mental when its most frequent WordNet sense is
cognition, communication or perception, or when it is on MIND_EXTRA. A verb counts as an agent verb
when VerbNet puts its most frequent sense in a class in which each frame has an animate subject:
`the default config sends the job`, `the fallback places the file`. Verbs on LITERAL never count,
and `show` is fine after a noun on PAGE_PARTS: `the table below shows the totals`. A British
spelling is read as the American one that the word lists use: `honour` as `honor`.

There are six ways to read a subject and its verb, because the parse of a terse comment is often
wrong on words that are both noun and verb (`a plan marks`):
- the dependency parse: a nominal subject of a verb, with `that` and `which` read as the noun
  their clause attaches to
- a coordinated verb takes the subject of its clause: `the file is malformed, or names a zone`
- a verb joined by `and` or `or` to a verb of the same form takes its subject: `the scan can stop
  early and list no files`
- an `-ing` modifier with an object takes the noun before it as subject: `a policy deciding it`
- agreement: after a singular determiner, a noun followed by an `-s` word makes that word a verb
- a modal: `a policy can judge`
The coordination and agreement readings take mental verbs only. They read an `-s` word as a verb
without the parse, and agent verbs such as `bill` and `rule` are also nouns. A passive verb with
`by` and a verb such as `pick` in `tries to pick` are not read: on the test corpus, most such pairs
are verbs that code performs, such as `keyed by resource id`.

It imports spaCy and loads its `en_core_web_md` model, both pinned in requirements-lock.txt.
verify.py runs it with the interpreter of the lint venv.

A directory expands to its Python files. A Markdown, HTML or plain text file is checked when it is
named, through prose.py.

Usage, with the shared lint venv of SKILL.md (Scripts\python.exe in place of bin/python on Windows):
    $ ~/.local/share/narrative/lintenv/bin/python agentverbs.py src/ README.md docs/report.html
    src/join.py:73: NAR017 'period ranks': agent verb on a subject that cannot act
    src/store.py:12: NAR020 'Named': clause with no subject before ", so"
    README.md:40: NAR017 'table shows': agent verb on a subject that cannot act
    $ ~/.local/share/narrative/lintenv/bin/python agentverbs.py --review src/ README.md
    src/join.py:40: 'path breaks'
    $ ~/.local/share/narrative/lintenv/bin/python agentverbs.py --lines sample.txt
    $ ~/.local/share/narrative/lintenv/bin/python agentverbs.py --score gold.tsv
    precision 1.00, recall 0.91 (29 of 32 found, 0 false)

A line with `# noqa: NAR017`, `# noqa: NAR020` or a bare `# noqa` is skipped for that code. In a page,
the comment is `<!-- noqa: NAR017 -->`.

`--review` lists every other subject that cannot act, with its verb, for the manual prose review:
a verb outside LITERAL that is not stative, such as `breaks` or `stays`. An `-s` word that the parse
reads as a noun after another noun, where only a verb fits, is on the list too: `the path breaks`.
A reader decides whether the subject can perform the verb. The list is no finding, and the exit code
is 0.

Exit codes:
    0  nothing flagged, or a review list printed
    1  at least one line flagged
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

import prose
import spacy
from prose import Passage
from spacy.language import Language
from spacy.tokens import Doc, Token


CODE = 'NAR017'
MESSAGE = 'agent verb on a subject that cannot act'
FRAGMENT_CODE = 'NAR020'
FRAGMENT_MESSAGE = 'clause with no subject before ", so"'
WORDS_PATH = Path(__file__).resolve().parent / 'words.json'
MODEL = 'en_core_web_md'

# verbs whose most frequent WordNet sense is not a mind class, but which make their subject a mind
MIND_EXTRA = frozenset({'keep', 'hold', 'carry', 'own', 'want', 'need', 'find', 'mark', 'treat', 'care'})
# what code does, and stative verbs for a relation rather than an act
LITERAL = frozenset({
    'return', 'raise', 'read', 'write', 'call', 'skip', 'parse', 'yield', 'print', 'log', 'match',
    'compare', 'accept', 'reject', 'contain', 'count', 'sort', 'map', 'have', 'be', 'fail', 'admit',
    'split', 'follow', 'drop', 'stop', 'start', 'run', 'pass', 'take', 'mean', 'imply', 'indicate',
    'look', 'seem', 'appear', 'specify', 'require', 'signal', 'point', 'check', 'will', 'decode',
    'encode', 'subtract', 'refer', 'resolve', 'iterate', 'compute', 'rewrite', 'use', 'open', 'close',
    'copy', 'shadow', 'nest', 'implement', 'put', 'import', 'reach', 'remove', 'collect', 'load',
    'feed', 'receive',
})  # fmt: skip
ROLES = frozenset({
    'i', 'you', 'we', 'he', 'she', 'they', 'who', 'someone', 'nobody', 'everyone', 'user', 'caller',
    'reader', 'developer', 'operator', 'customer', 'maintainer', 'reviewer', 'whoever', 'anyone',
    'anybody', 'somebody', 'person', 'people', 'agent',
})  # fmt: skip
# noun.person in WordNet, but programs in code
PROGRAMS = frozenset({
    'scanner', 'exporter', 'importer', 'writer', 'sender', 'receiver', 'listener', 'watcher',
    'worker', 'server', 'client', 'scheduler', 'runner', 'checker', 'validator', 'formatter',
    'handler', 'parser', 'loader', 'reporter',
})  # fmt: skip
SINGULAR_DETERMINERS = frozenset({'a', 'an', 'each', 'every', 'this', 'its', 'one'})
# a container verb counts only with an object: `a file holds whole bytes`, not `the invariant holds`  # noqa: NAR016
CONTAINER_VERBS = frozenset({'hold', 'keep', 'carry', 'own'})
# an object or clause that makes a verb take the VerbNet frame with an animate subject
AGENT_OBJECTS = frozenset({'dobj', 'iobj', 'dative', 'ccomp', 'xcomp', 'prt'})
MODALS = frozenset({'can', 'cannot', 'could', 'would', 'will', 'may', 'might', 'must', 'should'})
# matches:
# `raw_at`
# `f()`
# `mixedCase`
# rejects:
# `plain`
IDENTIFIER = re.compile(r'[_()`.\[\]]|[a-z][A-Z]')
PRAGMA = re.compile(r'(?:noqa|type:|pragma|fmt:|ruff:|pylint:|mypy:)')
# matches:
# `# noqa`
# `# noqa: NAR017, NAR020`
NOQA = re.compile(r'#\s*noqa(?::\s*(?P<codes>[A-Z0-9, ]+))?')
# a quoted span is code or an example, not a sentence of the comment
# matches:
# a span in backticks
# `'name'`
# rejects:
# `don't`
QUOTED = re.compile(r"`[^`]*`|(?<!\w)'[^'\n]+'(?!\w)")
AGREEMENT_WINDOW = 5
# nouns for a part of the page, which may take `show`: `the table below shows the totals`
PAGE_PARTS = frozenset({
    'table', 'figure', 'diagram', 'graph', 'chart', 'plot', 'image', 'screenshot', 'example',
    'comparison', 'illustration', 'page',
})  # fmt: skip
# British spellings, and the American ones that WordNet lists: `honour`, `recognise`, `analyse`
SPELLINGS = (('our', 'or'), ('ise', 'ize'), ('yse', 'yze'))
SO_JOIN = re.compile(r',\s+so\b')
# the parse of a longer clause before `, so` is unreliable
FRAGMENT_MAX_WORDS = 8
# Google-style docstring sections, whose indented entries are prose
SECTION_HEADER = re.compile(r'(?:Args|Arguments|Returns|Yields|Raises|Attributes|Notes?):$')


def main() -> int:
    """Check the paths given, list their subject and verb pairs for review, or flag or score a text file.

    Returns:
        1 when a line is flagged, otherwise 0. Scoring and the review list always return 0.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('paths', nargs='*', type=Path)
    parser.add_argument('--lines', type=Path, help='flag each line of a plain text file')
    parser.add_argument('--score', type=Path, help='score against a label<TAB>text file')
    parser.add_argument('--review', action='store_true', help='list every other subject that cannot act, with its verb')
    args = parser.parse_args()

    reader = SentenceReader.load(WORDS_PATH)
    if args.score:
        return scoreLabels(reader, args.score)
    if args.review:
        for checked_file in discoverFiles(args.paths):
            for line, pair in reviewFile(reader, checked_file):
                print(f'{checked_file}:{line}: {pair!r}')
        return 0
    if args.lines:
        flagged = 0
        for text in args.lines.read_text(encoding='utf-8').splitlines():
            if hits := [*reader.agentVerbs(text), *(f'{head},' for head in reader.fragments(text))]:
                flagged += 1
                print(f'{text}   <- {"; ".join(hits)}')
        return 1 if flagged else 0

    findings: list[Finding] = []
    for checked_file in discoverFiles(args.paths):
        findings.extend(checkFile(reader, checked_file))
    for finding in findings:
        message = MESSAGE if finding.code == CODE else FRAGMENT_MESSAGE
        print(f'{finding.checked_file}:{finding.line}: {finding.code} {finding.hit!r}: {message}')
    return 1 if findings else 0


def scoreLabels(reader: SentenceReader, labels_path: Path) -> int:
    """Compare the check with hand labels: `agent` or `ok`, a tab, then the line.

    Returns:
        0, after printing precision, recall and every disagreement.
    """
    found = false = missed = labelled = 0
    for row in labels_path.read_text(encoding='utf-8').splitlines():
        label, text = row.split('\t', 1)
        hits = reader.agentVerbs(text)
        labelled += label == 'agent'
        if hits and label == 'agent':
            found += 1
        elif hits:
            false += 1
            print(f'false: {text}   <- {"; ".join(hits)}')
        elif label == 'agent':
            missed += 1
            print(f'missed: {text}')

    precision = found / max(found + false, 1)
    recall = found / max(labelled, 1)
    print(f'precision {precision:.2f}, recall {recall:.2f} ({found} of {labelled} found, {false} false)')
    return 0


def discoverFiles(paths: list[Path]) -> list[Path]:
    """Expand each directory to the Python files below it, and keep each file named.

    A page below a directory is left out, so a run over `src/` does not check every README and
    vendored HTML file in it.

    Returns:
        The files to check, in the order given.
    """
    files: list[Path] = []
    for target in paths:
        files.extend(sorted(target.rglob('*.py')) if target.is_dir() else [target])
    return files


def checkFile(reader: SentenceReader, checked_file: Path) -> list[Finding]:
    """Flag every comment and docstring passage of a Python file, or every passage of a page.

    A passage is checked as one text, so a sentence wrapped over several lines is parsed whole. In a
    Python file, a noqa on any line of a passage silences that code for the whole passage. In a page,
    where a paragraph can run to many sentences, a noqa silences only the findings on the line of the comment.

    Returns:
        One finding per agent verb and per clause with no subject, on the line of its last word.
    """
    source = checked_file.read_text(encoding='utf-8')
    if checked_file.suffix.lower() in prose.PROSE_SUFFIXES:
        suppressed = prose.suppressedCodes(source)
        findings = passageFindings(reader, checked_file, prose.readPassages(checked_file), set(), set())
        return [f for f in findings if not (suppressed.get(f.line, set()) & {f.code, 'ALL'})]
    passages = [*commentPassages(source), *docstringPassages(ast.parse(source))]
    return passageFindings(
        reader,
        checked_file,
        passages,
        silencedLines(source, CODE),
        silencedLines(source, FRAGMENT_CODE),
    )


def passageFindings(
    reader: SentenceReader,
    checked_file: Path,
    passages: list[Passage],
    agent_silenced: set[int],
    fragment_silenced: set[int],
) -> list[Finding]:
    """Flag each passage, leaving out a code for every passage with a line in its silenced set.

    Returns:
        The findings in passage order.
    """
    findings: list[Finding] = []
    for passage in sorted(passages, key=lambda passage: passage.lines[0]):
        if not agent_silenced & set(passage.lines):
            for hit in reader.agentVerbs(passage.text):
                findings.append(Finding(checked_file, passage.lineOf(hit), CODE, hit))
        if not fragment_silenced & set(passage.lines):
            for head in reader.fragments(passage.text):
                findings.append(Finding(checked_file, passage.lineOf(head), FRAGMENT_CODE, head))
    return findings


def reviewFile(reader: SentenceReader, checked_file: Path) -> list[tuple[int, str]]:
    """List the subject and verb pairs of one file for review, leaving out what a NAR017 noqa silences.

    Returns:
        The line and the `subject verb` of each pair, in passage order.
    """
    source = checked_file.read_text(encoding='utf-8')
    page = checked_file.suffix.lower() in prose.PROSE_SUFFIXES
    if page:
        passages = prose.readPassages(checked_file)
        silenced = {number for number, codes in prose.suppressedCodes(source).items() if codes & {CODE, 'ALL'}}
    else:
        passages = [*commentPassages(source), *docstringPassages(ast.parse(source))]
        silenced = silencedLines(source, CODE)
    pairs: list[tuple[int, str]] = []
    for passage in sorted(passages, key=lambda passage: passage.lines[0]):
        # in a Python file a noqa covers the whole passage, as in checkFile()
        if not page and silenced & set(passage.lines):
            continue
        for pair in reader.reviewPairs(passage.text):
            if (line := passage.lineOf(pair)) not in silenced:
                pairs.append((line, pair))
    return pairs


def silencedLines(source: str, code: str) -> set[int]:
    silenced: set[int] = set()
    for number, line in enumerate(source.splitlines(), start=1):
        if (pragma := NOQA.search(line)) and (pragma['codes'] is None or code in pragma['codes']):
            silenced.add(number)
    return silenced


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

    A line indented past the body is a sample, such as a table or program output, unless it is an
    entry under a section header such as `Returns:`.

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


def americanSpelling(word: str, verbs: frozenset[str]) -> str:
    """Give the American spelling of a British verb. VerbNet lists `honor`, and WordNet lists both.

    Returns:
        The American spelling when it is a verb, otherwise the word.
    """
    for british, american in SPELLINGS:
        if british in word and (spelled := word.replace(british, american)) in verbs:
            return spelled
    return word


### vocabulary #########################################################################################


@dataclass(frozen=True)
class Finding:
    checked_file: Path
    line: int
    code: str
    hit: str


@dataclass(frozen=True)
class SentenceReader:
    """The parser and the word lists, loaded once per run."""

    nlp: Language
    animate_nouns: frozenset[str]
    mind_verbs: frozenset[str]
    agent_verbs: frozenset[str]
    stative_verbs: frozenset[str]
    verbs: frozenset[str]

    @classmethod
    def load(cls, words_path: Path) -> SentenceReader:
        words = json.loads(words_path.read_text(encoding='utf-8'))
        mind = (frozenset(words['mind_verbs']) | MIND_EXTRA) - LITERAL
        agent = frozenset(words['agent_verbs']) - LITERAL
        animate = (frozenset(words['animate_nouns']) | ROLES) - PROGRAMS
        stative = frozenset(words['stative_verbs'])
        return cls(spacy.load(MODEL), animate, mind, agent, stative, frozenset(words['verbs']))

    def agentVerbs(self, text: str) -> list[str]:
        """Find each subject that cannot act, paired with a verb for a mental act or an agent's act.

        Returns:
            One `subject verb` string per hit, in sentence order.
        """
        doc = self.nlp(QUOTED.sub('value', text))
        hits = {
            **self._parsedSubjects(doc),
            **self._sharedSubjects(doc),
            **self._participleSubjects(doc),
            **self._coordinatedSubjects(doc),
            **self._agreeingSubjects(doc),
            **self._modalSubjects(doc),
        }
        return [hits[index] for index in sorted(hits) if not self._pagePartShows(doc, index, hits[index])]

    def _pagePartShows(self, doc: Doc, index: int, hit: str) -> bool:
        """Tell whether a hit is a page part, such as a table, with `show` as its verb: `the table shows`.

        Returns:
            True when the verb is `show` and the subject is on PAGE_PARTS.
        """
        words = hit.split()
        verb = next((t for t in doc[index:] if t.text == words[-1]), None)
        subject = next((t for t in reversed(doc[: index + 1]) if t.text == words[0]), None)
        if verb is None or subject is None:
            return False
        return self._lemma(verb) == 'show' and subject.lemma_.lower() in PAGE_PARTS

    def reviewPairs(self, text: str) -> list[str]:
        """Find each subject that cannot act with a verb that is neither literal nor stative.

        A pair that agentVerbs() flags is left out, because it is already a finding.

        Returns:
            One `subject verb` string per pair, in sentence order.
        """
        doc = self.nlp(QUOTED.sub('value', text))
        flagged = set(self.agentVerbs(text))
        pairs: list[str] = []
        for token in doc:
            if token.dep_ != 'nsubj' or token.head.pos_ != 'VERB':
                continue
            verb = token.head
            lemma = self._lemma(verb)
            if lemma in LITERAL or lemma in self.stative_verbs or self._misreadSubject(token, verb):
                continue
            page_part = lemma == 'show' and token.lemma_.lower() in PAGE_PARTS
            if not page_part and not self._canAct(token) and (pair := f'{token.text} {verb.text}') not in flagged:
                pairs.append(pair)
        for subject, verb in self._compoundMisreadings(doc):
            if self._stem(verb) == 'show' and subject.lemma_.lower() in PAGE_PARTS:
                continue
            if (pair := f'{subject.text} {verb.text}') not in flagged and not self._canAct(subject):
                pairs.append(pair)
        return pairs

    def _compoundMisreadings(self, doc: Doc) -> list[tuple[Token, Token]]:
        """Find a noun and an `-s` word that the parse reads as one compound noun: `the path breaks`.

        In `a config value steers, but nothing else does`, the parse makes `steers` a noun with
        `value` as its modifier. After a determiner, with nothing after it that the `-s` word could
        modify, it is a verb.

        Returns:
            Each subject and verb, for a verb that is neither literal nor stative.
        """
        pairs: list[tuple[Token, Token]] = []
        for word in doc:
            if not word.lower_.endswith('s') or word.tag_ not in ('NNS', 'VBZ') or word.i == 0:
                continue
            stem = self._stem(word)
            if stem not in self.verbs or stem in LITERAL or stem in self.stative_verbs:
                continue
            noun = doc[word.i - 1]
            determined = any(t.dep_ in ('det', 'poss') for t in doc[word.left_edge.i : noun.i])
            ends_phrase = word.dep_ in ('ROOT', 'conj', 'advcl', 'ccomp') or word.i == len(doc) - 1
            # `the moves of its main line`: a word before `of` is a noun
            before_of = word.i + 1 < len(doc) and doc[word.i + 1].lower_ == 'of'
            compound = noun.dep_ in ('compound', 'amod') and noun.pos_ in ('NOUN', 'PROPN') and noun.head == word
            if compound and determined and ends_phrase and not before_of:
                pairs.append((noun, word))
        return pairs

    def fragments(self, text: str) -> list[str]:
        """Find each clause before `, so` that has no subject and is not a noun phrase or a command.

        `Named, so…` and `In float, so…` count. `constant-time comparison, so…` is a label, and
        `Sort by key, so…` is an imperative, so neither counts.

        Returns:
            The words before `, so` of each such clause, in sentence order.
        """
        heads: list[str] = []
        for clause in re.split(r'(?<=[.!?;])\s+', QUOTED.sub('value', text)):
            joint = SO_JOIN.search(clause)
            head = clause[: joint.start()].strip() if joint else ''
            if not head or len(head.split()) > FRAGMENT_MAX_WORDS:
                continue
            doc = self.nlp(head)
            root = next(token for token in doc if token.dep_ == 'ROOT')
            has_subject = any(token.dep_ in ('nsubj', 'nsubjpass', 'expl', 'csubj') for token in doc)
            has_finite_verb = any(token.tag_ in ('VBZ', 'VBP', 'VBD', 'MD') for token in doc)
            label = root.pos_ in ('NOUN', 'PROPN', 'PRON', 'NUM')
            command = doc[0].tag_ == 'VB' or root.tag_ in ('VB', 'VBG')
            interjection = doc[0].pos_ == 'INTJ'
            if not (has_subject or has_finite_verb or label or command or interjection):
                heads.append(head)
        return heads

    def _parsedSubjects(self, doc: Doc) -> dict[int, str]:
        hits: dict[int, str] = {}
        for token in doc:
            if token.dep_ != 'nsubj' or token.head.pos_ not in ('VERB', 'AUX'):
                continue
            verb = token.head
            if self._misreadSubject(token, verb):
                continue
            if not self._canAct(token) and self._needsMind(verb):
                hits[verb.i] = f'{token.text} {verb.text}'
        return hits

    def _sharedSubjects(self, doc: Doc) -> dict[int, str]:
        """Read a verb with no subject as taking the subject of the verb it is joined to.

        In `the scan can stop early and list no files`, `list` has the subject `scan`. When the
        subject is a clause such as `parsing the file`, the subject is an event, which cannot act.

        Returns:
            Verb index to `subject verb`.
        """
        hits: dict[int, str] = {}
        for verb in doc:
            # a participle is passive or shares an auxiliary, and `value` stands in for quoted code
            if verb.dep_ != 'conj' or verb.pos_ != 'VERB' or verb.tag_ == 'VBN' or verb.lower_ == 'value':
                continue
            if any(c.dep_ in ('nsubj', 'nsubjpass', 'csubj', 'expl') for c in verb.children):
                continue
            head = verb.head
            # `and` or `or` joins two verbs of the same form: `can stop and list`, `kept and showed`.
            # A parse that joins `scanned` to `report`, or clauses with no conjunction, is a misreading
            joined = verb.tag_ == head.tag_ and any(
                t.dep_ == 'cc' and t.head in (head, verb) for t in doc[head.i + 1 : verb.i]
            )
            while head.dep_ == 'conj' and head.head.i != head.i:
                head = head.head
            subject = next((c for c in head.children if c.dep_ in ('nsubj', 'nsubjpass', 'csubj')), None)
            # an imperative has no subject. Its parse sometimes takes the object for one
            imperative = head.tag_ == 'VB' and not any(c.dep_ in ('aux', 'auxpass') for c in head.children)
            if not joined or imperative or subject is None or not self._needsMind(verb):
                continue
            if subject.dep_ == 'csubj' and subject.tag_ != 'VBG':
                continue
            if subject.dep_ != 'csubj' and (self._misreadSubject(subject, head) or self._canAct(subject)):
                continue
            hits[verb.i] = f'{subject.text} {verb.text}'
        return hits

    def _participleSubjects(self, doc: Doc) -> dict[int, str]:
        """Read the noun before an `-ing` modifier as its subject: `a policy deciding which files stay`.

        A modifier with no object, such as `missing` in `the sections missing from this file`, is an
        adjective and is left out.

        Returns:
            Verb index to `subject verb`.
        """
        hits: dict[int, str] = {}
        for verb in doc:
            if verb.dep_ != 'acl' or verb.tag_ != 'VBG' or self._canAct(verb.head) or not self._needsMind(verb):
                continue
            if not any(c.dep_ in AGENT_OBJECTS for c in verb.children):
                continue
            # in `the escape hatch: marking the parameters`, the colon ends the noun phrase
            if not any(t.is_punct for t in doc[verb.head.i + 1 : verb.i]):
                hits[verb.i] = f'{verb.head.text} {verb.text}'
        return hits

    def _lemma(self, verb: Token) -> str:
        return americanSpelling(verb.lemma_.lower(), self.verbs)

    def _stem(self, word: Token) -> str:
        """Read an `-s` word as a verb: `names` as `name`, `recognises` as `recognize`."""
        return americanSpelling(word.lower_[:-1], self.verbs)

    def _needsMind(self, verb: Token) -> bool:
        lemma = self._lemma(verb)
        if lemma in CONTAINER_VERBS:
            # in `the periods its rule keeps`, the object stands before the relative clause
            return verb.dep_ in ('relcl', 'ccomp') or any(c.dep_ in ('dobj', 'attr') for c in verb.children)
        if lemma in self.mind_verbs:
            return True
        # in VerbNet, the animate subject belongs to the sense with an object: `a rule applies` is not `apply a rule`
        return lemma in self.agent_verbs and any(c.dep_ in AGENT_OBJECTS for c in verb.children)

    def _misreadSubject(self, subject: Token, verb: Token) -> bool:
        """Recognise a parse whose subject and verb are not a subject and a verb.

        Terse comments yield imperatives read as subjects, noun compounds read as clauses, and
        list items read as subjects of the verb after the list.

        Returns:
            True when the pair is a misreading and must not be flagged.
        """
        children = list(verb.children)
        clause_start = subject.i == 0 or subject.nbor(-1).pos_ in ('PUNCT', 'CCONJ')
        imperative_opener = clause_start and subject.lower_ in self.verbs and not list(subject.children)
        bare_verb_word = subject.lower_ in self.verbs and subject.tag_ == 'NN' and not list(subject.children)
        # `the code see`: a singular noun takes no base-form verb, so this is no subject and verb
        disagrees = (
            subject.tag_ in ('NN', 'NNP') and verb.tag_ in ('VB', 'VBP') and not any(c.dep_ == 'aux' for c in children)
        )
        bare_participle = verb.tag_ == 'VBN' and not any(c.dep_ in ('aux', 'auxpass') for c in children)
        # `at least one line flagged`: a past form with no object at the end of a phrase
        phrase_end = verb.i == len(verb.doc) - 1 or verb.nbor(1).is_punct
        final_participle = verb.tag_ == 'VBD' and phrase_end and not any(c.dep_ == 'dobj' for c in children)
        listed = any(c.dep_ == 'cc' for c in subject.children)
        # `the prices file`: a plural noun, then a word with no object, is a compound
        compound = (
            subject.tag_ == 'NNS'
            and verb.i == subject.i + 1
            and not any(c.dep_ in ('dobj', 'attr', 'ccomp', 'xcomp') for c in children)
        )
        # `the word lists for`: after `the`, a noun, then an `-s` word and a preposition, is a compound
        the_compound = (
            subject.tag_ == 'NN'
            and verb.tag_ == 'VBZ'
            and verb.i == subject.i + 1
            and not phrase_end
            and verb.nbor(1).pos_ == 'ADP'
            and any(c.lower_ == 'the' for c in subject.children)
        )
        other_subject = any(c.dep_ == 'nsubj' and c.i != subject.i and self._canAct(c) for c in children)
        # `withdrawn codes: kept so ...`: punctuation between the two ends the clause
        separated = any(t.is_punct for t in verb.doc[min(subject.i, verb.i) + 1 : max(subject.i, verb.i)])
        modal = verb.lower_ in MODALS
        return (
            imperative_opener
            or bare_verb_word
            or disagrees
            or bare_participle
            or final_participle
            or listed
            or separated
            or compound
            or the_compound
            or other_subject
            or modal
        )

    def _coordinatedSubjects(self, doc: Doc) -> dict[int, str]:
        hits: dict[int, str] = {}
        for token in doc:
            if token.dep_ != 'conj' or not token.lower_.endswith('s') or self._stem(token) not in self.mind_verbs:
                continue
            # a verb takes an object: `names an unknown timezone`, not `fractions of a cent`
            if token.i + 1 >= len(doc) or doc[token.i + 1].pos_ not in ('DET', 'ADJ', 'NOUN', 'PROPN', 'NUM'):
                continue
            clause = token.head
            while clause.dep_ in ('conj', 'attr', 'acomp') and clause.head.i != clause.i:
                clause = clause.head
            subjects = [c for c in clause.children if c.dep_ == 'nsubj']
            if subjects and not self._canAct(subjects[0]):
                hits[token.i] = f'{subjects[0].text} {token.text}'
        return hits

    def _agreeingSubjects(self, doc: Doc) -> dict[int, str]:
        """Read a noun and a following `-s` word as subject and verb where grammar allows only that.

        After a singular determiner, `a plan marks` cannot be a plural noun phrase. After an
        identifier or `the` that opens a relative clause, `the month raw_month names` and `every
        file the audit needs` cannot either.

        Returns:
            Verb index to `subject verb`.
        """
        hits: dict[int, str] = {}
        for token in doc[1:]:
            left = doc[token.i - 1]
            if not token.lower_.endswith('s') or left.lower_.endswith('s') or left.pos_ == 'DET':
                continue
            # `the Move it names`: after `it`, an `-s` word is a verb
            if left.lower_ == 'it' and self._stem(token) in self.mind_verbs:
                hits[token.i] = f'{left.text} {token.text}'
                continue
            if left.pos_ not in ('NOUN', 'PROPN', 'ADJ', 'NUM', 'X') or self._canAct(left):
                continue
            phrase = doc[max(0, token.i - AGREEMENT_WINDOW) : token.i]
            # a determiner before a preposition belongs to another noun phrase
            boundary = max((t.i for t in phrase if t.pos_ in ('ADP', 'PUNCT')), default=phrase.start - 1)
            determiners = [
                t.lower_ for t in phrase if t.i > boundary and (t.pos_ == 'DET' or t.lower_ in SINGULAR_DETERMINERS)
            ]
            singular = bool(determiners) and determiners[-1] in SINGULAR_DETERMINERS
            # `every file the audit needs`: a noun, then `the` and a noun, opens a relative clause
            the_index = next((t.i for t in reversed(phrase) if t.lower_ == 'the' and t.i > boundary), None)
            relative = the_index is not None and the_index > 0 and doc[the_index - 1].pos_ in ('NOUN', 'PROPN')
            singular = singular or (relative and left.tag_ in ('NN', 'NNP'))
            reduced_relative = IDENTIFIER.search(left.text) and left.i > 0 and doc[left.i - 1].pos_ in ('NOUN', 'DET')
            if (singular or reduced_relative) and self._stem(token) in self.mind_verbs:
                hits[token.i] = f'{left.text} {token.text}'
        return hits

    def _modalSubjects(self, doc: Doc) -> dict[int, str]:
        hits: dict[int, str] = {}
        for token in doc[1 : len(doc) - 1]:
            left, verb = doc[token.i - 1], doc[token.i + 1]
            if token.lower_ not in MODALS or left.pos_ not in ('NOUN', 'PROPN') or self._canAct(left):
                continue
            if self._needsMind(verb):
                hits[token.i] = f'{left.text} {token.text} {verb.text}'
        return hits

    def _canAct(self, subject: Token) -> bool:
        if subject.lower_ in ('that', 'which') and subject.head.dep_ == 'relcl':
            subject = subject.head.head
        if subject.ent_type_ == 'PERSON':
            return True
        if IDENTIFIER.search(subject.text):
            return False
        return subject.lower_ in self.animate_nouns or subject.lemma_.lower() in self.animate_nouns


if __name__ == '__main__':
    sys.exit(main())
