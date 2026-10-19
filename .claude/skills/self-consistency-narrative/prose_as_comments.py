"""Write the comment examples of the skill documents as Python files, so agentverbs.py can read them.

`SKILL_examples.py` has every comment example of `SKILL.md`, from backticks in the prose and from
code blocks, as a trailing comment on the line of the example's source. agentverbs.py skips backticked
text in prose, and reads each trailing comment as a separate passage, so each example is checked
alone. The prose of the documents is checked directly: `agentverbs.py skill/SKILL.md`.

Usage:
    $ python3 prose_as_comments.py OUT_DIR
    $ .lintenv/bin/python skill/agentverbs.py OUT_DIR
    OUT_DIR/SKILL_examples.py:769: NAR017 'vendor documents': agent verb on a subject that cannot act
"""

import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
DOCUMENTS = ('skill/SKILL.md', 'skill/architecture.md', 'skill/tooling.md')
# matches:
# a backticked `# vendor closes idle sockets at 60 s`
# rejects:
# a backticked `x = 1`
INLINE_COMMENT = re.compile(r'`#\s+([^`]+)`')
# matches:
# `x = 1  # sorted`
# `# sorted`
# rejects:
# `'#' in text`
CODE_COMMENT = re.compile(r'(?:^|\s)#\s+(.+)$')


def main() -> int:
    """Write the examples file of each skill document into the directory given."""
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for document in DOCUMENTS:
        source = REPO / document
        markdown = source.read_text(encoding='utf-8')
        (out_dir / f'{source.stem}_examples.py').write_text(commentExamples(markdown))
    return 0


def commentExamples(markdown: str) -> str:
    """Write the comment examples of a Markdown document as Python, one output line per input line.

    Raises:
        Nothing. Any text is accepted.
    """
    examples: list[str] = []
    in_code = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            examples.append('')
            continue

        if in_code:
            found = CODE_COMMENT.search(line)
            comments = [found.group(1)] if found and not stripped.startswith('###') else []
        else:
            comments = INLINE_COMMENT.findall(line)
        examples.append(f'_ = 0  # {" / ".join(comments)}' if comments else '')
    return '\n'.join(examples) + '\n'


if __name__ == '__main__':
    sys.exit(main())
