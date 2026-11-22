# Findings from your labels of 2026-11-21

Your labels and notes are saved in
`~/.local/share/narrative/eval-private/runs/claudish-rules/batch/open_question_labels.md`.

A correction first. I wrote in the header of the labelling file that every example came from code written before
2023. The standard library examples came from Python 3.14, which is from 2025. Python 3.10 is from 2021, and the
comments of Q1 items 3, 8 and 11 aren't in Python 3.10, so those comments are from 2021 or later. Q5 item 3 is in the test package, which the build of 3.10 on
this machine doesn't have. You labelled Q1 items 3 and 8 B. Q4 items 7 and 8 are a setter javadoc and a class
javadoc, so the heading "field javadocs" was wrong for those two items.

## Q1. The form of a Fence

8 G and 4 B. The forms of the G comments:

| form | items |
|---|---|
| the step, then `so that` and the failure. The comment uses the names of the code | 2 (`Pause early so that "ssl_protocol.data_received()" doesn't have a chance to get called before "ssl_protocol.connection_made()".`) |
| the step with `to avoid` or `prevent`, often after an issue id | 1, 5, 11 |
| the step with `because` and the mechanism | 6 |
| `We cannot` and the simple version, then the reason | 4 |
| a known weakness and the reason that the weakness is harmless | 9 (`We may register the exit function more than once because of a thread race, but that is harmless`) |
| a label, then a rule for the developer | 10 (`Child process.` / `This must never return, hence os._exit()!`) |

The B comments are 3 (a colon join, and too long), 7 (`This makes sure…`, which a better name would replace), 8 (the
danger without the step that the code takes, and a weak free modifier), 12 (too long, and `three conditions` that the
reader can't resolve).

Each G comment is one sentence, or a label and one sentence. The two-sentence form of the skill, the fact and then the
step, isn't among the G comments. The `X would` form alone is in 2 of the 4 B comments.

You warned on items 1 and 6 that a copy of the form by an agent would be slop.

## Q3. `NAR116`

3 Y, 9 N, and 2 either way.

| metric | Y and either way | N |
|---|---|---|
| more than 3 parameters | 1 of 5 | 5 of 9 |
| more than 20 body lines | 4 of 5 | 3 of 9 |
| cyclomatic complexity 8 or more | 3 of 5 | 0 of 9 |
| a name for when the method runs (`on…`, `update…`, `do…`), or a call with an obfuscated name (`p_75823_1_`) | 4 of 5 | 1 of 9 (`doRender()`, whose body is empty) |

Your reasons were these. N: the reader learns from the name what the method does, or the method has one line. Y: the
reader learns from the name only when the method runs, or the method calls obfuscated names. Probably Y: a public method that many
developers call.

The number of parameters isn't a predictor of a Y. A candidate rule fits all 14 labels: more than 20 body lines, and
a name for when the method runs or a call with an obfuscated name. The candidate comes from the 14 labels, so the fit isn't
evidence. In the sample of 416 human methods over the current threshold, the candidate flags 17.

## Q4. `The` and `A` as the first word

- Later sentences that open with `The`: 3 G. Item 2 is outside the question.
- The first word of a javadoc: items 7, 8 and 10 are G, and items 5, 6, 9, 11, 12 and 13 are B.

Most of the B items are a noun phrase for the identifier, with little more:

| item | javadoc | identifier |
|---|---|---|
| 5 | `The size of this stratum (number of lines)` | field `size` |
| 6 | `The key into the annotation which contains the injection points` | field `atKey` |
| 9 | `A class representing a set of 2 objects as defined by the type parameters.` | class `Pair` |
| 12 | `A mark of the mob spawn overlay.` | enum `MobOverlayStyle` |
| 13 | `A GL display list of the mob spawn overlay.` | class `MobOverlayDisplayList` |

Item 11, `A generic Interface for just setting the amount of contained Items` on `IDigitalChest`, is vague more than a
repeat. The G item 8, `The style for a scroll pane, see ScrollPane.`, has a pointer to another class.

## Q5. Openers with a platform

4 G for the human openers, and B for Claude's `Beside the splits file of an older version,`. Rule 6 leaves an opener
with a platform out.

## Two more rules from your notes

- **No docstring on a one-line function.** Your notes on Q3 items 7 and 10 and Q4 item 7. The skill already has
  `Don't write a docstring for a function that only returns a constant`.
- **A design comment goes by the constant or in the docstring.** Your note on Q1 item 1: the comment on reading by
  chunks is about `chunk_size`.

## The author of Q5 item 4

Peter Åstrand wrote the comment with the table in `subprocess.py`, in his subprocess module. Fredrik Lundh committed
the module to CPython on 2004-10-12, in commit [5b3687df2e](https://github.com/python/cpython/commit/5b3687df2e)
("Added Peter Astrand's subprocess module"). By `git blame` on GitHub:

- Gregory P. Smith changed one line, `are -1 when not using PIPEs. The child objects are -1`, in 2010, in commit
  [fb94c5f1e5](https://github.com/python/cpython/commit/fb94c5f1e5). I didn't read the 2004 wording of that line.
- A commit of 2023 ([3a4c44bb1e](https://github.com/python/cpython/commit/3a4c44bb1e), gh-87474) moved the block
  without a change to the text.

