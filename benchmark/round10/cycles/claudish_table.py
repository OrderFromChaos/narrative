"""Recompute the Claudish feature table, per 100 comment blocks, with 95% intervals in brackets.

A rate is the share of blocks with at least one match, in every column. Each argument is a range of
cycles and adds one column of skill runs.

Usage:
    $ python3 claudish_table.py 7-13 14-15
"""

import io
import json
import math
import os
import re
import subprocess
import sys
import sysconfig
import tokenize
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
# the shared venv of SKILL.md, Setup. Its Python has spaCy and en_core_web_md
DATA_HOME = Path(os.environ.get('LOCALAPPDATA') or os.environ.get('XDG_DATA_HOME') or Path.home() / '.local' / 'share')
TAGGER_PYTHON = DATA_HOME / 'narrative' / 'lintenv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
TAGGER = '''import json, sys, spacy
nlp = spacy.load('en_core_web_md')
words = set(sys.argv[1:])
texts = json.load(sys.stdin)
print(json.dumps([any(t.lower_ in words and t.pos_ in ('VERB', 'AUX') for t in doc) for doc in nlp.pipe(texts)]))
'''
SITE = next((REPO / '.lintenv/lib').glob('python3*/site-packages'))
PRAGMA = re.compile(r'#\s*(?:noqa|type:|pylint:|pragma|fmt:|ruff:|mypy:)|#!|#\s*-\*-')
DIVIDER = re.compile(r'^#\s*[-=#~*]{4,}')

FEATURES = [
    ('`, not` contrast', r',\s+not\s+\w'),
    ('dash (` -- ` or `—`)', r'\s--\s|—'),
    ('absolutes: every, never, whole, exactly', r'\b(?:every|never|whole|exactly)\b'),
    ('`the one` / `one place`', r'\bthe one\b|\bone place\b'),
    ('deliberately, on purpose, by design', r'\b(?:deliberately|on purpose|by design)\b'),
    ('`rather than` / `instead of`', r'\b(?:rather than|instead of)\b'),
    ('`, so` joining clauses', r',\s+so\s+(?!that\b)\w'),
    ('semicolon', r';\s'),
    (
        'agentive verb: finds, knows, wants, sees, asks, decides, owns',
        r'\b(?:finds|knows|wants|sees|asks|decides|owns)\b',
    ),
    (
        'container verb, tagged as a verb: holds, carries, lives, keeps, names, states',
        r'\b(?:holds|carries|lives|keeps|names|states)\b',
    ),
    ('intensifier: genuine, real, actually, really, truly', r'\b(?:genuine|genuinely|real|actually|really|truly)\b'),
    ('article before a backticked identifier', r'\b(?:the|a|an)\s+`'),
    ('`because`', r'\bbecause\b'),
    ('passive (`is`/`are`/`was`/`be` + `-ed`)', r'\b(?:is|are|was|were|be|been)\s+\w+ed\b'),
    ('changelog: now, no longer, used to, the old', r'\b(?:now|no longer|used to|the old)\b'),
    ('hedge: usually, likely, probably, might, seems', r'\b(?:usually|likely|probably|might|seems)\b'),
    ('first person: we, our, us, I', r'\b(?:[Ww]e|[Oo]ur|[Uu]s|I)\b'),
    ('TODO, NOTE, FIXME, XXX, HACK', r'\b(?:TODO|NOTE|FIXME|XXX|HACK)\b'),
    ('possessive `own`', r"\b(?:its|their|\w+'s) own\b"),
]
CASE_SENSITIVE = {'TODO, NOTE, FIXME, XXX, HACK', 'first person: we, our, us, I'}
# a match counts only when spaCy tags the word VERB or AUX. Most of these words are also nouns
VERB_ONLY = {
    'container verb, tagged as a verb: holds, carries, lives, keeps, names, states': (
        'holds', 'carries', 'lives', 'keeps', 'names', 'states'
    ),
}
Z = 1.96
# `Claude #` of the round 10 README's Claudish section. These are the comment blocks Claude wrote
# into `#` files before 2026-10-01 21:11 UTC, from the user's private transcripts, counted as above
CLAUDE_BLOCKS = 2962
CLAUDE_RATES = {
    'median words': 22,
    'p90 words': 79,
    'blocks of more than one sentence': 41.6,
    '`, not` contrast': 7.9,
    'dash (` -- ` or `—`)': 17.5,
    'absolutes: every, never, whole, exactly': 22.0,
    '`the one` / `one place`': 2.3,
    'deliberately, on purpose, by design': 1.9,
    '`rather than` / `instead of`': 14.0,
    '`, so` joining clauses': 24.4,
    'semicolon': 15.7,
    'agentive verb: finds, knows, wants, sees, asks, decides, owns': 2.2,
    'container verb, tagged as a verb: holds, carries, lives, keeps, names, states': 7.9,
    'intensifier: genuine, real, actually, really, truly': 6.3,
    'article before a backticked identifier': 2.3,
    '`because`': 7.8,
    'passive (`is`/`are`/`was`/`be` + `-ed`)': 17.3,
    'changelog: now, no longer, used to, the old': 2.7,
    'hedge: usually, likely, probably, might, seems': 0.3,
    'first person: we, our, us, I': 1.0,
    'TODO, NOTE, FIXME, XXX, HACK': 0.3,
    'possessive `own`': 7.2,
}


def main() -> None:
    ranges = [tuple(int(n) for n in arg.split('-')) for arg in sys.argv[1:]]
    columns = [humanBlocks()] + [recentBlocks(first, last) for first, last in ranges]
    names = ' | '.join(f'cycles {arg}' for arg in sys.argv[1:])
    print(f'| feature | Claude, no skill | human | {names} |\n|---' + '|---' * (len(columns) + 1) + '|')
    print(f'| blocks | {CLAUDE_BLOCKS:,} | ' + ' | '.join(f'{len(s):,}' for s in columns) + ' |')
    for label, quantile in (('median words', 0.5), ('p90 words', 0.9)):
        cells = [quantileCell(sorted(len(b.split()) for b in s), quantile) for s in columns]
        print(f'| {label} | {CLAUDE_RATES[label]:g} | ' + ' | '.join(cells) + ' |')
    label = 'blocks of more than one sentence'
    cells = [rateCell(sum(sentenceCount(b) > 1 for b in s), len(s)) for s in columns]
    print(f'| {label} (%) | {claudeCell(label)} | ' + ' | '.join(cells) + ' |')
    for label, pattern in FEATURES:
        rx = re.compile(pattern) if label in CASE_SENSITIVE else re.compile(pattern, re.IGNORECASE)
        if label in VERB_ONLY:
            cells = [rateCell(countVerbs([b for b in s if rx.search(b)], VERB_ONLY[label]), len(s)) for s in columns]
        else:
            cells = [rateCell(sum(bool(rx.search(b)) for b in s), len(s)) for s in columns]
        print(f'| {label} | {claudeCell(label)} | ' + ' | '.join(cells) + ' |')


def countVerbs(blocks: list[str], words: tuple[str, ...]) -> int:
    """Count the blocks in which one of the words is tagged as a verb, with the spaCy of the shared venv."""
    if not blocks:
        return 0
    tagged = subprocess.run(
        [str(TAGGER_PYTHON), '-c', TAGGER, *words], input=json.dumps(blocks), capture_output=True, text=True, check=True
    )
    return sum(json.loads(tagged.stdout))


def wilson(hits: int, total: int) -> tuple[float, float]:
    """Wilson score interval at 95%, as percentages."""
    if total == 0:
        return (0.0, 100.0)
    share = hits / total
    centre = (share + Z**2 / (2 * total)) / (1 + Z**2 / total)
    half = Z * math.sqrt(share * (1 - share) / total + Z**2 / (4 * total**2)) / (1 + Z**2 / total)
    return (max(0.0, centre - half) * 100, min(1.0, centre + half) * 100)


def rateCell(hits: int, total: int) -> str:
    low, high = wilson(hits, total)
    return f'{hits / total * 100:.1f} [{low:.1f}, {high:.1f}]'


def claudeCell(label: str) -> str:
    # the transcripts are private, so the interval comes from the published rate and its block count
    if label not in CLAUDE_RATES:
        return ''
    return rateCell(round(CLAUDE_RATES[label] * CLAUDE_BLOCKS / 100), CLAUDE_BLOCKS)


def quantileCell(values: list[int], quantile: float) -> str:
    """The quantile with a distribution-free 95% interval from binomial order statistics."""
    count = len(values)
    spread = Z * math.sqrt(count * quantile * (1 - quantile))
    low = values[max(0, math.floor(count * quantile - spread))]
    high = values[min(count - 1, math.ceil(count * quantile + spread))]
    return f'{values[min(count - 1, int(count * quantile))]} [{low}, {high}]'


def sentenceCount(block: str) -> int:
    return len([s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z`])', block.strip()) if s])


def commentBlocks(source: str) -> list[str]:
    blocks: list[list[str]] = []
    last_line = -2
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type != tokenize.COMMENT or PRAGMA.match(token.string) or DIVIDER.match(token.string):
            continue
        text = token.string.lstrip('#').strip()
        if not text:
            continue
        full_line = token.line[: token.start[1]].strip() == ''
        if full_line and blocks and last_line == token.start[0] - 1 and blocks[-1][0] == 'full':
            blocks[-1].append(text)
        else:
            blocks.append(['full' if full_line else 'eol', text])
        last_line = token.start[0] if full_line else -2
    return [' '.join(b[1:]) for b in blocks]


def humanBlocks() -> list[str]:
    stdlib = Path(sysconfig.get_paths()['stdlib'])
    skipped = {'encodings', 'idlelib', 'site-packages', 'test', 'tests'}
    files = [p for p in stdlib.rglob('*.py') if not skipped & set(p.relative_to(stdlib).parts)]
    for package in ('mypy', 'pylint', 'astroid'):
        files += list((SITE / package).rglob('*.py'))
    blocks: list[str] = []
    for path in files:
        try:
            blocks += commentBlocks(path.read_text(encoding='utf-8'))
        except (UnicodeDecodeError, SyntaxError, tokenize.TokenError, IndentationError):
            continue
    return blocks


def recentBlocks(first: int, last: int) -> list[str]:
    blocks: list[str] = []
    for path in sorted((REPO / 'benchmark/round10/cycles').glob('cycle*_review.md')):
        if not first <= int(path.name.removeprefix('cycle').split('_')[0]) <= last:
            continue
        for item in re.split(r'\n### ', path.read_text())[1:]:
            code = re.search(r'```python\n(.*?)```', item, re.S)
            if code:
                marked = [line[8:] for line in code.group(1).splitlines() if line.startswith('>>')]
                text = ' '.join(line.split('#', 1)[1].strip() for line in marked if '#' in line)
                if text:
                    blocks.append(text)
    return blocks


main()
