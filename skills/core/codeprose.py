"""Read the comments of a C, C++, JavaScript, TypeScript, or Verilog file as passages for the prose checks of nar:core.

Each language of Narrative has a module named codeprose.py, and the skill directory has that module beside agentverbs.py
and wording.py. The prose checks read source files only through the names below, so the checks run on any language with
a codeprose.py. Here the language of a file comes from the file's suffix, and the file is read through slashcomments.py
and the module of the language: ccomments.py, jscomments.py or verilogcomments.py.

- `GIT_PATTERNS`: the git pathspecs of the source files of the languages
- `passages()`: the passages of the comments and doc comments of one source file
- `NOQA`: the comment that silences a finding on one line
- `changeSpans()`: for each line of a comment, the lines that count for --since
- `commentBlocks()`: the comment lines of one source file in the blocks that rewrap.py fills

Usage:
    $ python3 codeprose.py src/engine.cpp                 # print each passage, as in the expected files of the tests
    $ python3 codeprose.py --stripped src/engine.cpp      # print the source with each comment replaced by a space
    $ python3 codeprose.py --rewrap --width 80 src/engine.cpp     # print the source with the comments re-wrapped

Usage, from a script in this directory:
    import codeprose
    passages = codeprose.passages(Path('engine.cpp').read_text(encoding='utf-8'), '.cpp')
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import ccomments
import jscomments
import rewrap
import slashcomments
import verilogcomments
from prose import Passage
from rewrap import Line
from slashcomments import NOQA, Language
from wording import Spans


### standard library only. The prose checks import this, and they run wherever python3 does

# the language of each suffix. A suffix such as `.C` is looked up as written first, then in lower case
LANGUAGE_OF_SUFFIX = {
    suffix: language
    for language in (*ccomments.LANGUAGES, *jscomments.LANGUAGES, *verilogcomments.LANGUAGES)
    for suffix in language.suffixes
}
GIT_PATTERNS = tuple(sorted(f'*{suffix}' for suffix in LANGUAGE_OF_SUFFIX))
__all__ = ['GIT_PATTERNS', 'NOQA', 'changeSpans', 'commentBlocks', 'languageOf', 'passages']
EXIT_SUCCESS = 0
EXIT_UNKNOWN_SUFFIX = 2


def main() -> int:
    """Print the passages, the stripped source, or the re-wrapped source of each file named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('paths', nargs='+', type=Path)
    shown = parser.add_mutually_exclusive_group()
    shown.add_argument('--stripped', action='store_true', help='print the source with each comment replaced by a space')
    shown.add_argument('--rewrap', action='store_true', help='print the source with the comments re-wrapped')
    parser.add_argument('--width', type=int, default=rewrap.WIDTH, help='with --rewrap, the last column of a comment')
    args = parser.parse_args()

    for source_path in args.paths:
        if not readable(source_path.suffix):
            print(f'codeprose.py: no comment reader for {source_path.suffix!r} files: {source_path}', file=sys.stderr)
            return EXIT_UNKNOWN_SUFFIX
        source = source_path.read_text(encoding='utf-8')
        language = languageOf(source_path.suffix)
        if args.stripped:
            sys.stdout.write(slashcomments.strippedSource(source, language))
        elif args.rewrap:
            blocks = slashcomments.commentBlocks(source, language)
            sys.stdout.write(rewrap.rewrapSource(source, blocks, None, width=args.width))
        else:
            print(*slashcomments.dumpPassages(source, language), sep='\n')
    return EXIT_SUCCESS


def passages(source: str, suffix: str) -> list[Passage]:
    return slashcomments.passages(source, languageOf(suffix))


def commentBlocks(source: str, suffix: str) -> list[list[Line]]:
    return slashcomments.commentBlocks(source, languageOf(suffix))


def changeSpans(checked_file: Path) -> Spans:
    """Map each line of a comment passage to every line of the passage. Those lines count for --since.

    Returns:
        A map from each line to the lines of the line's passage. Empty for a file that cannot be read.
    """
    try:
        source = checked_file.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return {}
    found = passages(source, checked_file.suffix)
    return {line: frozenset(passage.lines) for passage in found for line in passage.lines}


def readable(suffix: str) -> bool:
    return suffix in LANGUAGE_OF_SUFFIX or suffix.lower() in LANGUAGE_OF_SUFFIX


def languageOf(suffix: str) -> Language:
    return LANGUAGE_OF_SUFFIX.get(suffix) or LANGUAGE_OF_SUFFIX[suffix.lower()]


if __name__ == '__main__':
    sys.exit(main())
