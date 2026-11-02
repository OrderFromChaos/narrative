"""Check Java sources for the rules of the Java skill, and merge the PMD, Checkstyle and javac reports.

Comments and javadoc are read with a lexer, not a parser, so the comments of a file are read even when the file uses
syntax newer than a Java grammar. The prose checks are the ones of every language: the wording checks of wording.py
(NAR012 to NAR016, NAR018) and the agent-verb checks of agentverbs.py (NAR017, NAR020, NAR021, NAR022). The structural
checks are PMD XPath rules in pmd-ruleset.xml. Every tool finding is mapped to a NAR code here.

With --rewrap, javachecks.py checks nothing. Each paragraph of the javadoc and the whole-line // comments is filled
again up to column 120 in place, by rewrap.py, and under --since only a paragraph with a changed line. Without --rewrap,
NAR125 flags each paragraph that the re-wrap would change.

Usage:
    $ python3 javachecks.py src/main/java/com/example/PlanReader.java
    $ python3 javachecks.py src/main/java --since origin/dev
    $ python3 javachecks.py src/main/java --pmd build/narrative/pmd.xml --checkstyle build/narrative/checkstyle.xml
    $ python3 javachecks.py src/main/java --prose
    $ python3 javachecks.py src/main/java --prose --from-sentence 1001
    $ python3 javachecks.py src/main/java --prose --from-pair 1001
    $ python3 javachecks.py src/main/java README.md docs/page.html
    $ python3 javachecks.py src/main/java README.md docs/page.html --prose
    $ python3 javachecks.py src/main/java --cache build/narrative/prose-cache.json
    $ python3 javachecks.py src/main/java --rewrap --since origin/dev

One line per finding, and a warning has the word `warning` before the warning's code:

    src/main/java/com/example/PlanReader.java:42: NAR017 'report names'
    src/main/java/com/example/PlanReader.java:57: warning NAR119 FIXME in a comment

With --since REF, a finding is reported only when its lines overlap the lines that the diff against merge-base(HEAD,
REF) adds or changes. The lines of a prose finding are the lines of the finding's passage. For a finding on a method,
they are the lines of the method, and for a finding on a type, the line of the type's declaration.

With --cache PATH, the spaCy results of each passage are kept in PATH between runs, keyed by the text of the passage.
The cache is discarded when agentverbs.py, words.json, spaCy or the spaCy model changes, and spaCy is loaded only when a
passage is not in the cache.

A Markdown, HTML or plain text page named on the command line gets the prose checks, and with --prose, the lists cover
the page too. Under --since, a page passage is checked and listed when a line of the passage changed.

With --prose and without --since, each of the three lists stops after 1000 entries, with the command for the next 1000
entries of that list. --from-sentence, --from-pair and --from-pronoun print only the list they name, from the given
entry. With --all-sentences, every entry is listed.

Exit codes:
    0  no finding. Warnings may be printed
    1  at least one finding
    2  a file or a report could not be read, --since names no commit, or the diff changes no line
"""

from __future__ import annotations

import argparse
import bisect
import itertools
import re
import sys
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import agentverbs
import rewrap
import wording
from codeprose import JAVA_TOKEN, Comment, CommentKind, blockPassages, commentBlocks, groupBlocks, lexComments
from prose import PROSE_SUFFIXES, Passage, readPassages


SKIPPED_DIRS = frozenset({'.git', '.gradle', 'build', 'run', 'out', 'bin'})
# matches:
# `NAR017`
# `NAR113-gtnh`
CODE = r'NAR\d{3}(?:-[a-z]+)?'
# Checkstyle check name, without the Check suffix: the NAR code
CHECKSTYLE_CODES = {
    'MethodName': 'NAR130',
    'MemberName': 'NAR130',
    'ParameterName': 'NAR130',
    'LambdaParameterName': 'NAR130',
    'LocalVariableName': 'NAR130',
    'LocalFinalVariableName': 'NAR130',
    'StaticVariableName': 'NAR130',
    'ConstantName': 'NAR130',
    'TypeName': 'NAR130',
    'PackageName': 'NAR130',
    'ParameterNumber': 'NAR131',
}
EXIT_SUCCESS = 0
EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2


def main() -> int:
    """Check the Java files below the given paths, merge the tool reports, and print the findings."""
    parser = argparse.ArgumentParser(description='Check Java sources for the narrative-gtnh rules.')
    parser.add_argument(
        'paths',
        nargs='+',
        type=Path,
        help='Java files, directories to search for them, and pages',
    )
    parser.add_argument('--pmd', type=Path, help='the XML report of the narrativePmd task')
    parser.add_argument('--checkstyle', type=Path, help='the XML report of the narrativeCheckstyle task')
    parser.add_argument('--javac', type=Path, help='the Gradle output of the compileJava run')
    parser.add_argument('--since', help='report only lines changed since merge-base(HEAD, SINCE)')
    parser.add_argument(
        '--prose',
        action='store_true',
        help='list every sentence of every comment, javadoc and page, and the review lists',
    )
    paging = parser.add_mutually_exclusive_group()
    paging.add_argument('--from-sentence', type=int, help='with --prose, list only the sentences, from this one')
    paging.add_argument('--from-pair', type=int, help='with --prose, list only the subject-verb pairs, from this one')
    paging.add_argument('--from-pronoun', type=int, help='with --prose, list only the pronoun sentences, from this one')
    parser.add_argument('--all-sentences', action='store_true', help='with --prose, list every entry of every list')
    parser.add_argument('--cache', type=Path, help='a file that keeps the spaCy results between runs')
    parser.add_argument('--rewrap', action='store_true', help='fill the javadoc and // comments again, in place')
    args = parser.parse_args()

    java_paths = discoverJava(args.paths)
    page_paths = [path for path in args.paths if path.suffix.lower() in PROSE_SUFFIXES]
    if not java_paths and not page_paths:
        print(f'javachecks.py: no .java file below {", ".join(map(str, args.paths))}', file=sys.stderr)
        return EXIT_UNREADABLE

    try:
        tool_findings = readToolReports(args.pmd, args.checkstyle, args.javac)
        changed = (
            wording.readChangedLines(args.since, (java_paths or page_paths)[0].parent, '*.java') if args.since else None
        )
    except (ReportError, wording.GitError) as exc:
        print(f'javachecks.py: {exc}', file=sys.stderr)
        return EXIT_UNREADABLE

    if changed is not None and not changed:
        print(f'javachecks.py: no line changed since {args.since}', file=sys.stderr)
        return EXIT_UNREADABLE

    # under --since, a file with no changed line can have no finding
    if changed is not None:
        java_paths = [java_path for java_path in java_paths if java_path.resolve() in changed]
    if args.rewrap:
        for java_path in java_paths:
            source = java_path.read_text(encoding='utf-8')
            changed_lines = changed[java_path.resolve()] if changed is not None else None
            rewrapped = rewrap.rewrapSource(source, commentBlocks(source), changed_lines)
            if rewrapped != source:
                java_path.write_text(rewrapped, encoding='utf-8')
                print(f'{java_path}: re-wrapped')
        return EXIT_SUCCESS

    reader = agentverbs.CachedReader.open(args.cache)
    if args.prose:
        starts = {
            '--from-sentence': args.from_sentence,
            '--from-pair': args.from_pair,
            '--from-pronoun': args.from_pronoun,
        }
        flag, first = next(((flag, first) for flag, first in starts.items() if first is not None), (None, 1))
        cache = ['--cache', str(args.cache)] if args.cache else []
        list_page = (
            None
            if changed is not None or args.all_sentences
            else ListPage(flag, first, [*map(str, args.paths), *cache])
        )
        for line in proseInventory(reader, java_paths, page_paths, changed, list_page):
            print(line)
        reader.save()
        return EXIT_SUCCESS

    findings: list[JavaFinding] = []
    for java_path in java_paths:
        findings.extend(checkFile(reader, java_path, tool_findings.get(java_path.resolve(), []), changed))
    for page_path in page_paths:
        findings.extend(checkPage(reader, page_path, changed))
    reader.save()
    for finding in findings:
        print(finding)
    failing = [finding for finding in findings if not finding.warning]
    file_count = len(java_paths) + len(page_paths)
    print(f'{len(failing)} findings, {len(findings) - len(failing)} warnings over {file_count} files')
    return EXIT_FINDINGS if failing else EXIT_SUCCESS


def discoverJava(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for target in paths:
        candidates = wording.findFiles(target, '*.java') if target.is_dir() else [target]
        found.extend(path for path in candidates if path.suffix == '.java' and not SKIPPED_DIRS & set(path.parts))
    return found


def readToolReports(pmd_path: Path | None, checkstyle_path: Path | None, javac_path: Path | None) -> ToolFindings:
    """Read the three reports into findings keyed by resolved file path.

    Raises:
        ReportError: a given report does not exist, or is malformed.
    """
    findings: ToolFindings = defaultdict(list)
    reports = (
        *(readPmdReport(pmd_path) if pmd_path else []),
        *(readCheckstyleReport(checkstyle_path) if checkstyle_path else []),
        *(readJavacWarnings(javac_path) if javac_path else []),
    )
    for tool_finding in reports:
        findings[tool_finding.java_path].append(tool_finding)
    return findings


def readPmdReport(report_path: Path) -> list[ToolFinding]:
    """Read a PMD XML report.

    Raises:
        ReportError: the report is missing, is not XML, or has a rule with no NAR code.
    """
    findings: list[ToolFinding] = []
    for file_element in parseReport(report_path).iter():
        if not file_element.tag.endswith('file'):
            continue
        java_path = Path(file_element.attrib['name']).resolve()
        for violation in file_element:
            rule = violation.attrib['rule']
            if rule not in PMD_CODES:
                raise rejectReport(report_path, f'PMD rule {rule} has no NAR code in PMD_CODES')
            code, scope = PMD_CODES[rule]
            first, last = int(violation.attrib['beginline']), int(violation.attrib['endline'])
            message = ' '.join((violation.text or '').split())
            findings.append(ToolFinding(java_path, first, last, code, message, scope))
    return findings


def readCheckstyleReport(report_path: Path) -> list[ToolFinding]:
    """Read a Checkstyle XML report.

    Raises:
        ReportError: the report is missing, is not XML, or has a check with no NAR code.
    """
    findings: list[ToolFinding] = []
    for file_element in parseReport(report_path).iter('file'):
        java_path = Path(file_element.attrib['name']).resolve()
        for error in file_element.iter('error'):
            check = error.attrib['source'].rsplit('.', 1)[-1].removesuffix('Check')
            if check not in CHECKSTYLE_CODES:
                raise rejectReport(report_path, f'Checkstyle check {check} has no NAR code in CHECKSTYLE_CODES')
            line = int(error.attrib['line'])
            findings.append(
                ToolFinding(java_path, line, line, CHECKSTYLE_CODES[check], error.attrib['message'], Scope.LINE),
            )
    return findings


def readJavacWarnings(log_path: Path) -> list[ToolFinding]:
    """Read the raw-type and unchecked warnings of javac from the Gradle output of compileJava.

    Raises:
        ReportError: the log is missing.
    """
    # matches:
    # `/src/Plan.java:12: warning: [rawtypes] found raw type: List`
    # `/src/Plan.java:30: warning: [unchecked] unchecked call to add(E) as a member of the raw type List`
    # rejects:
    # `Note: Plan.java uses unchecked or unsafe operations.`
    WARNING = re.compile(r'^(?P<path>.+\.java):(?P<line>\d+): warning: \[(?:rawtypes|unchecked)\] (?P<detail>.*)$')
    if not log_path.is_file():
        raise rejectReport(log_path, 'the javac log does not exist')

    findings: list[ToolFinding] = []
    for raw_line in log_path.read_text(encoding='utf-8', errors='replace').splitlines():
        if warning := WARNING.match(raw_line):
            line = int(warning['line'])
            java_path = Path(warning['path']).resolve()
            findings.append(ToolFinding(java_path, line, line, 'NAR121', warning['detail'], Scope.LINE))
    return findings


def parseReport(report_path: Path) -> ElementTree.Element:
    """Parse one XML report.

    Raises:
        ReportError: the report does not exist, or is not XML.
    """
    if not report_path.is_file():
        raise rejectReport(report_path, 'the report does not exist')

    try:
        return ElementTree.parse(report_path).getroot()
    except ElementTree.ParseError as exc:
        raise rejectReport(report_path, f'not XML ({exc})') from exc


def rejectReport(report_path: Path, reason: str) -> ReportError:
    return ReportError(f'{report_path}: {reason}')


def proseInventory(
    reader: agentverbs.CachedReader,
    java_paths: list[Path],
    page_paths: list[Path],
    changed: ChangedLines | None,
    list_page: ListPage | None,
) -> list[str]:
    """List every sentence of every comment and page, every review pair that is not a NAR017 finding, and every pronoun.

    With a ListPage, each list printed stops after wording.LIST_PAGE entries, with the command for the next entries of
    that list. Under --since, a passage of a source file or a page is listed when a line of the passage changed.
    """
    sentences: list[str] = []
    pairs: list[str] = []
    pronouns: list[str] = []
    readings = [
        (path, readComments(path.read_text(encoding='utf-8', errors='replace')).passages) for path in java_paths
    ]
    readings.extend((path, readPassages(path)) for path in page_paths)
    for file_path, passages in readings:
        for passage in passages:
            if inChange(changed, file_path, set(passage.lines)):
                sentences.extend(f'{file_path}:{line}: {sentence}' for line, sentence in passage.sentences())
                pairs.extend(
                    f'{file_path}:{passage.lineOf(pair)}: {pair!r}' for pair in reader.reviewPairs(passage.text)
                )
                pronouns.extend(
                    f'{file_path}:{sentenceLine(passage, sentence)}: {pronoun_words}: {sentence!r}'
                    + (f' after {previous!r}' if previous else '')
                    for pronoun_words, sentence, previous in reader.pronounSentences(passage.text)
                )
    review_lists = (
        (
            '--from-sentence',
            'sentences',
            '--- every sentence of every comment, javadoc and page: read each against SKILL.md, Comments ---',
            sentences,
        ),
        (
            '--from-pair',
            'pairs',
            '--- every subject that cannot act, with its verb: can that subject perform that verb? ---',
            pairs,
        ),
        (
            '--from-pronoun',
            'pronoun sentences',
            '--- every sentence with a pronoun, after the one before it: which noun does each pronoun stand for? ---',
            pronouns,
        ),
    )
    listed: list[str] = []
    for flag, unit, heading, entries in review_lists:
        if list_page is not None and list_page.flag not in {None, flag}:
            continue
        shown = entries
        if list_page is not None:
            first = list_page.first if list_page.flag == flag else 1
            option = ['javachecks.py', '--prose', flag]
            shown = wording.listPage(entries, first, unit=unit, option=option, arguments=list_page.arguments)
        listed.extend([heading, *(shown or ['(none)'])])
    return listed


def sentenceLine(passage: Passage, sentence: str) -> int:
    """Find the line on which a sentence of a passage starts. `Passage.text` is the lines joined by single spaces."""
    offset = max(passage.text.find(sentence), 0)
    ends = list(itertools.accumulate(len(text) + 1 for text in passage.texts))
    return passage.lines[min(bisect.bisect_right(ends, offset), len(passage.lines) - 1)]


def checkPage(reader: agentverbs.CachedReader, page_path: Path, changed: ChangedLines | None) -> list[JavaFinding]:
    """Run the wording checks of wording.py and the agent-verb checks of agentverbs.py on one page.

    Under --since, a finding is kept when a line of the finding's passage changed.

    Returns:
        The findings, sorted by line, or only the NAR000 finding of wording.py for a page that cannot be read.
    """
    worded = [JavaFinding(page_path, found.line, found.code, found.detail) for found in wording.checkPage(page_path)]
    if any(finding.code == 'NAR000' for finding in worded):
        return worded

    changed_lines = wording.changedLinesOf(changed, page_path)
    if changed_lines is not None:
        spans = wording.pageSpans(page_path)
        worded = [finding for finding in worded if wording.inChange(changed_lines, spans, finding.line)]
    verbs = [
        JavaFinding(page_path, found.line, found.code, repr(found.hit))
        for found in agentverbs.checkFile(reader, page_path, changed_lines)
    ]
    return sorted([*worded, *verbs], key=lambda finding: (finding.line, finding.code))


def checkFile(
    reader: agentverbs.CachedReader,
    java_path: Path,
    tool_findings: list[ToolFinding],
    changed: ChangedLines | None,
) -> list[JavaFinding]:
    """Run the prose and comment checks on one file, add the file's tool findings, then apply noqa and --since.

    Returns:
        The findings and warnings that survive, sorted by line.
    """
    source = java_path.read_text(encoding='utf-8', errors='replace')
    lines = source.splitlines()
    reading = readComments(source)
    # a finding on a passage counts under --since when a line of the passage changed
    passages = [passage for passage in reading.passages if inChange(changed, java_path, set(passage.lines))]
    passage_lines = {line: frozenset(passage.lines) for passage in passages for line in passage.lines}
    prose_lines = [pair for passage in passages for pair in zip(passage.lines, passage.texts, strict=True)]
    candidates: list[tuple[JavaFinding, frozenset[int]]] = []

    for worded in wording.wordingFindings(prose_lines, reading.list_items, java_path):
        finding = JavaFinding(java_path, worded.line, worded.code, worded.detail)
        candidates.append((finding, passage_lines.get(worded.line, frozenset({worded.line}))))
    for passage in passages:
        coded_hits = (
            (agentverbs.CODE, reader.agentVerbs(passage.text)),
            (agentverbs.FRAGMENT_CODE, reader.fragments(passage.text)),
            (agentverbs.CONNECTIVE_CODE, reader.connectives(passage.text, page=False)),
            (agentverbs.PRONOUN_CODE, reader.ambiguousPronouns(passage.text)),
        )
        for code, hits in coded_hits:
            for hit in hits:
                candidates.append(
                    (JavaFinding(java_path, passage.lineOf(hit), code, repr(hit)), frozenset(passage.lines)),
                )
    candidates.extend((finding, frozenset({finding.line})) for finding in commentFindings(java_path, lines, reading))
    masked = maskLiterals(source) if any(tool_finding.code == 'NAR116' for tool_finding in tool_findings) else ''
    for tool_finding in tool_findings:
        # a PMD violation of a method is at the method name. The end of a NAR116 method is found by the method's braces
        last_line = (
            methodEndLine(masked, tool_finding.first_line) if tool_finding.code == 'NAR116' else tool_finding.last_line
        )
        span = frozenset(range(tool_finding.first_line, last_line + 1))
        line_span = span if tool_finding.scope is Scope.SPAN else frozenset({tool_finding.first_line})
        located = ToolFinding(
            java_path,
            tool_finding.first_line,
            last_line,
            tool_finding.code,
            tool_finding.message,
            tool_finding.scope,
        )
        candidates.extend((finding, line_span) for finding in resolveToolFinding(located, lines, reading))

    kept = [
        finding
        for finding, span in candidates
        if not silenced(reading.silenced, finding) and inChange(changed, java_path, set(span))
    ]
    return sorted(kept, key=lambda finding: (finding.line, finding.code))


def maskLiterals(source: str) -> str:
    """Return the source with every comment and literal blanked, keeping each newline."""
    return JAVA_TOKEN.sub(lambda token: re.sub(r'[^\n]', ' ', token[0]), source)


def methodEndLine(masked: str, first_line: int) -> int:
    """Return the line of the brace that closes the method declared at `first_line`.

    A method with no body ends at the semicolon.
    """
    offset = sum(len(line) + 1 for line in masked.split('\n')[: first_line - 1])
    opening = min(
        (position for position in (masked.find('{', offset), masked.find(';', offset)) if position >= 0),
        default=-1,
    )
    if opening < 0 or masked[opening] == ';':
        return masked.count('\n', 0, max(opening, offset)) + 1

    depth = 0
    for position in range(opening, len(masked)):
        if masked[position] == '{':
            depth += 1
        elif masked[position] == '}':
            depth -= 1
            if depth == 0:
                return masked.count('\n', 0, position) + 1
    return masked.count('\n') + 1


def readComments(source: str) -> CommentReading:
    """Lex the comments of a Java source and turn them into prose lines, passages and noqa scopes."""
    comments = lexComments(source)
    blocks = groupBlocks(comments)
    prose_lines: list[tuple[int, str]] = []
    list_items: set[int] = set()
    passages: list[Passage] = []
    for block in blocks:
        for passage in blockPassages(block):
            passages.append(passage)
            prose_lines.extend(zip(passage.lines, passage.texts, strict=True))
            if passage.list_item:
                list_items.add(passage.lines[0])
    return CommentReading(comments, blocks, prose_lines, list_items, passages, noqaScopes(blocks))


def noqaScopes(blocks: list[list[Comment]]) -> dict[int, frozenset[str]]:
    """Map each line to the codes that a noqa silences there.

    The scope of a noqa in a comment block is every line of the block, plus the code line after a whole-line block. A //
    comment over 120 columns is wrapped by spotless, so a trailing noqa can end up on the next line of the block.
    """
    # matches:
    # `noqa: NAR017`
    # `noqa: NAR104, NAR112-gtnh`
    # `noqa`
    NOQA = re.compile(rf'\bnoqa(?::\s*(?P<codes>{CODE}(?:\s*,\s*{CODE})*))?')
    scopes: dict[int, frozenset[str]] = {}
    for block in blocks:
        codes: set[str] = set()
        for _number, text in (pair for comment in block for pair in comment.texts):
            if pragma := NOQA.search(text):
                codes.update(re.findall(CODE, pragma['codes']) if pragma['codes'] else {'ALL'})
        if not codes:
            continue
        covered = set(range(block[0].first_line, block[-1].last_line + 1))
        if not block[0].trailing:
            covered.add(block[-1].last_line + 1)
        for number in covered:
            scopes[number] = scopes.get(number, frozenset()) | codes
    return scopes


def commentFindings(java_path: Path, lines: list[str], reading: CommentReading) -> list[JavaFinding]:
    """Run the checks on comments and source lines: type javadoc, FIXME, return contracts and unfilled paragraphs."""
    # matches:
    # `public final class PlanReader {`
    # `sealed interface Settlement permits Solved, Stalled {`
    # `public record Plan(String name, int machineCount) {}`
    # rejects:
    # `    class Nested {`
    # `classMap.put(key, value);`
    TOP_LEVEL_TYPE = re.compile(
        r'^(?:(?:public|protected|private|abstract|final|sealed|non-sealed|static|strictfp)\s+)*'
        r'(?:class|interface|enum|record|@interface)\s+(?P<name>\w+)',
    )
    # matches:
    # `returns null when the plan file is absent`
    # `the result is sorted by name`
    # rejects:
    # `return early when the plan is empty`
    RETURN_CONTRACT = re.compile(r'^(?:returns?\b(?! early)|null when\b|the result\b|a returned\b)', re.IGNORECASE)
    # matches:
    # `public Plan read(Path planPath) throws PlanException {`
    # `private static int count(final List<Plan> plans) {`
    # rejects:
    # `if (plan == null) {`
    # `for (final Plan plan : plans) {`
    METHOD_OPENING = re.compile(
        r'^(?!(?:if|for|while|switch|try|catch|else|do|synchronized|return)\b)'
        r'[\w<>\[\], .@?]*\w\s*\([^;]*\)\s*(?:throws\s+[\w., ]+)?\{$',
    )
    findings: list[JavaFinding] = []
    javadoc_ends = {comment.last_line for comment in reading.comments if comment.kind is CommentKind.JAVADOC}
    in_comment = {number for comment in reading.comments for number, _text in comment.texts if not comment.trailing}
    for number, text in enumerate(lines, start=1):
        declaration = TOP_LEVEL_TYPE.match(text)
        if declaration and number not in in_comment and lineAboveAnnotations(lines, number) not in javadoc_ends:
            detail = f'{declaration["name"]} has no javadoc. A top-level type has one of at least one sentence'
            findings.append(JavaFinding(java_path, number, 'NAR118', detail))

    for comment in reading.comments:
        for number, text in comment.texts:
            if re.search(r'\bFIXME\b', text):
                findings.append(JavaFinding(java_path, number, 'NAR119', 'FIXME in a comment', warning=True))

    for block in reading.blocks:
        first = block[0]
        opening = first.texts[0][1].strip()
        previous_code = lines[first.first_line - 2].strip() if first.first_line > 1 else ''
        if first.kind is CommentKind.LINE and RETURN_CONTRACT.match(opening) and METHOD_OPENING.search(previous_code):
            detail = 'return contract in a comment at the top of a method. Put it in the javadoc, or cut it'
            findings.append(JavaFinding(java_path, first.first_line, 'NAR120', detail))

    source = '\n'.join(lines)
    for number in rewrap.unfilledLines(source, commentBlocks(source), None):
        findings.append(JavaFinding(java_path, number, rewrap.RULE, rewrap.DETAIL))
    return findings


def lineAboveAnnotations(lines: list[str], declaration_line: int) -> int:
    """Return the number of the line above a declaration and above the declaration's annotation lines.

    An annotation can span lines, such as `@Mod(` and then one line per element up to the closing `)`. The lines of such
    an annotation count as annotation lines when the annotation's first line starts with `@`.
    """
    number = declaration_line - 1
    while number > 0:
        if lines[number - 1].lstrip().startswith('@'):
            number -= 1
            continue
        start = annotationStart(lines, number)
        if start is None:
            return number
        number = start - 1
    return number


def annotationStart(lines: list[str], last_line: int) -> int | None:
    """Find the first line of a multi-line annotation that ends on `last_line`, by the balance of the parentheses.

    Returns:
        The number of the line that starts with `@` and opens the parentheses that close on `last_line`. None when
        `last_line` closes no parenthesis, or when the line with the matching `(` does not start with `@`.
    """
    # matches a literal, whose parentheses are not code:
    # `"(beta)"`
    # `')'`
    LITERAL = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    depth = 0
    for number in range(last_line, 0, -1):
        code = LITERAL.sub('', lines[number - 1])
        depth += code.count(')') - code.count('(')
        if depth <= 0:
            return number if number < last_line and code.lstrip().startswith('@') else None
    return None


def resolveToolFinding(tool_finding: ToolFinding, lines: list[str], reading: CommentReading) -> list[JavaFinding]:
    """Turn a tool finding into JavaFindings, with a look at the comments of the file for two codes.

    - NAR110: a mutable static field. With a comment for the reason, above the field or after the field on the same
      line, there is no finding
    - NAR116: a method over the javadoc threshold. With no javadoc above the method, the finding is reported. With one,
      NAR117 is reported for each `throw new X` in the method where X is absent from the throws clause and from the
      `@throws` lines of the javadoc

    Returns:
        No finding for NAR110 with a reason comment, else one finding or more.
    """
    line = tool_finding.first_line
    match tool_finding.code:
        case 'NAR110':
            above = {comment.last_line for comment in reading.comments}
            beside = {comment.first_line for comment in reading.comments if comment.trailing}
            if lineAboveAnnotations(lines, line) in above or line in beside:
                return []
            return [JavaFinding(tool_finding.java_path, line, 'NAR110', tool_finding.message)]
        case 'NAR116':
            javadoc = javadocAbove(reading, lines, line)
            if javadoc is None:
                return [JavaFinding(tool_finding.java_path, line, 'NAR116', tool_finding.message)]
            return missingThrowsTags(tool_finding, lines, javadoc)
        case _:
            return [JavaFinding(tool_finding.java_path, line, tool_finding.code, tool_finding.message)]


def javadocAbove(reading: CommentReading, lines: list[str], declaration_line: int) -> str | None:
    end = lineAboveAnnotations(lines, declaration_line)
    for comment in reading.comments:
        if comment.kind is CommentKind.JAVADOC and comment.last_line == end:
            return '\n'.join(text for _number, text in comment.texts)
    return None


def missingThrowsTags(tool_finding: ToolFinding, lines: list[str], javadoc: str) -> list[JavaFinding]:
    """List each exception thrown in the method, absent from the method's throws clause, with no `@throws` line."""
    method_lines = lines[tool_finding.first_line - 1 : tool_finding.last_line]
    signature = ' '.join(method_lines[: next((i for i, text in enumerate(method_lines) if '{' in text), 0) + 1])
    declared = (
        set(re.findall(r'\w+', signature.split('throws', 1)[1].split('{', 1)[0])) if 'throws' in signature else set()
    )
    documented = set(re.findall(r'@throws\s+(?:[\w$]+\.)*([\w$]+)', javadoc))
    findings: list[JavaFinding] = []
    for offset, text in enumerate(method_lines):
        for thrown in re.findall(r'\bthrow\s+new\s+(?:[\w$]+\.)*([\w$]+)\s*\(', text):
            if thrown not in declared and thrown not in documented:
                detail = f'{thrown} is thrown and has no @throws line in the javadoc'
                findings.append(JavaFinding(tool_finding.java_path, tool_finding.first_line + offset, 'NAR117', detail))
    return findings


def silenced(scopes: dict[int, frozenset[str]], finding: JavaFinding) -> bool:
    silencing = {finding.code, 'ALL', BARE_CODES.get(finding.code, finding.code)}
    return bool(scopes.get(finding.line, frozenset()) & silencing)


def inChange(changed: ChangedLines | None, java_path: Path, span: set[int]) -> bool:
    return changed is None or bool(changed.get(java_path.resolve(), set()) & span)


### vocabulary #########################################################################################


class Scope(Enum):
    """The lines of a reported node that count for --since: the node's first line, or every line."""

    LINE = 'line'
    SPAN = 'span'


# PMD rule name: the NAR code, and the Scope of the reported node
PMD_CODES = {
    'NAR101': ('NAR101', Scope.LINE),
    'NAR102': ('NAR102', Scope.SPAN),
    'NAR103': ('NAR103', Scope.SPAN),
    'NAR104': ('NAR104', Scope.SPAN),
    'NAR105': ('NAR105', Scope.SPAN),
    'NAR106': ('NAR106', Scope.LINE),
    'NAR107': ('NAR107', Scope.SPAN),
    'NAR108': ('NAR108', Scope.SPAN),
    'NAR109': ('NAR109', Scope.LINE),
    'NAR110': ('NAR110', Scope.SPAN),
    'NAR111': ('NAR111', Scope.SPAN),
    'NAR112': ('NAR112-gtnh', Scope.SPAN),
    'NAR113': ('NAR113-gtnh', Scope.SPAN),
    'NAR114': ('NAR114-gtnh', Scope.SPAN),
    'NAR115': ('NAR115', Scope.SPAN),
    'NAR116': ('NAR116', Scope.SPAN),
    'NAR122': ('NAR122', Scope.SPAN),
    'NAR123': ('NAR123', Scope.SPAN),
    'NAR124': ('NAR124-gtnh', Scope.LINE),
    'LooseCoupling': ('NAR140', Scope.SPAN),
    'ImmutableField': ('NAR141', Scope.SPAN),
    'AvoidCatchingGenericException': ('NAR142', Scope.SPAN),
    'PreserveStackTrace': ('NAR144', Scope.SPAN),
}
# the bare code of each code of the GTNH environment, from before the -gtnh suffix. A noqa with the bare code still
# silences the finding, so the noqa comments of merged PRs keep working
BARE_CODES = {
    'NAR112-gtnh': 'NAR112',
    'NAR113-gtnh': 'NAR113',
    'NAR114-gtnh': 'NAR114',
    'NAR124-gtnh': 'NAR124',
}


class ReportError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommentReading:
    comments: list[Comment]
    blocks: list[list[Comment]]
    prose_lines: list[tuple[int, str]]
    list_items: set[int]
    passages: list[Passage]
    silenced: dict[int, frozenset[str]]


@dataclass(frozen=True)
class ToolFinding:
    java_path: Path
    first_line: int
    last_line: int
    code: str
    message: str
    scope: Scope

    def lines(self) -> tuple[int, int]:
        return self.first_line, self.last_line


@dataclass(frozen=True)
class JavaFinding:
    java_path: Path
    line: int
    code: str
    detail: str
    warning: bool = False

    def __str__(self) -> str:
        prefix = 'warning ' if self.warning else ''
        return f'{self.java_path}:{self.line}: {prefix}{self.code} {self.detail}'


@dataclass(frozen=True)
class ListPage:
    """The part of the three lists that --prose prints.

    `flag` is the option of the one list to print, from entry `first`, or None for every list from entry 1. The
    arguments are the paths and the cache, for the command of the next entries.
    """

    flag: str | None
    first: int
    arguments: list[str]


ToolFindings = dict[Path, list[ToolFinding]]
ChangedLines = wording.ChangedLines


if __name__ == '__main__':
    sys.exit(main())
