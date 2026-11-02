"""Cases for checks.py --rewrap, with one rule of the re-wrap in each docstring or comment.

A ragged paragraph is filled again up to column 120. The product is a float.

Usage:
    $ python3 cases.py --a-sample-indented-past-the-body-stays-as-written --even-when-the-line-is-long-enough-to-run-past-column-120

- a list item opens a paragraph, and the next lines of the item hang under the text of the item, past the marker of the
  item
- the second item
"""

import re


### a divider stays as written ######################################################################################

# matches:
# `float,` and a note on the same line that stays, because a label keeps each line below the label as written
# `a`
# rejects:
# `b`
WORD = re.compile(r'\S+')


def fill(first: int, second: int) -> int:
    """Fill the plan, with a summary that is ragged.

    A line that ends a sentence is joined to the next sentence. The next sentence follows on the same line.

    Args:
        first: the first value, read from the plan file, which must exist on disk before the call is made by the caller
        second: the second value, on one line that runs past column 120, so the next lines hang by four columns of
            indent

    Returns:
        The sum of the two values, on a line that is ragged and filled again.

    Raises:
        ValueError: never
    """
    # a run of whole-line comments at one column is one block. Its lines are filled again as one paragraph.
    #
    # a line with noqa keeps its words, so the noqa stays on its line  # noqa: NAR017
    # and the line below starts a new paragraph.
    return first + second  # a trailing comment over the limit stays on its line, because the line has code before it


def short() -> int:
    """A one-line docstring stays on its line, even past column 120, because a split of the line would move the closing quotes."""
    return 1


def closing() -> int:
    """A docstring whose last line has the closing quotes after the text is filled with the quotes on the last word."""
    return 2
