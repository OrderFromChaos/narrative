# De-poisoning: the examples that need your choice

The clear violations of rules 1, 6, 7 and 15 in `core/`, `lang/`, the tools and the README are rewritten. The items
below are examples or sentence forms where a rewrite changes an example of a rule, or where more than one rewrite fits.
Each item has the text now, and the text after each option.

## 1. Option openers in the help text of the tools (33 sentences)

`NAR026` flags an opener with a command-line option or a parameter, such as `With --since REF,`, `Under --since,` and
`` With `changed_lines`, ``. The sentences are in the module docstrings of `verify.py`, `checks.py`, `javachecks.py`,
`agentverbs.py`, `rewrap.py`, `wording.py` and `build_skills.py`, and `--help` prints most of them.

Now:

- `With --since REF, only the Python files that the diff against merge-base(HEAD, REF) adds or changes are checked`
- `Under --since, only a paragraph with a changed line is re-wrapped.`
- `With --rewrap, checks.py checks nothing.`

**A. A clause after `when`, by rule 6:**

- `When --since REF is given, only the Python files that the diff against merge-base(HEAD, REF) adds or changes are
  checked`
- `When --since is given, only a paragraph with a changed line is re-wrapped.`
- `When --rewrap is given, checks.py doesn't run a check.`

**B. The option as the subject:**

- `--since REF limits the check to the Python files that the diff against merge-base(HEAD, REF) adds or changes`
- `--since limits the re-wrap to the paragraphs with a changed line.`
- `--rewrap re-wraps the comments, and checks.py doesn't run a check.`

**C. Keep the opener for an option, and leave `--option` and a backticked parameter out of `NAR026`**, the same as
`On Windows,`. The 33 sentences stay as they are, except `checks nothing` → `doesn't run a check` (rule 1).

## 2. The Fence example of rule 7, which you flagged on 2026-11-21

Now, in **Sentence form** of `core/rules/comments.md`:

`the vendor rounds tax per line, not per invoice. Round each line before the sum`

- **A.** `the vendor rounds the tax of each line. Round each line before the sum`
- **B.** Replace the example with the Fence example above it: `the API returns 200 with an error body for a bad key.
  Check the body too`

## 3. Four good examples that open with `The`

You said on 2026-11-21 that an opener with `The` is Claudish, and chose the identifier first.

| file | now | proposed |
|---|---|---|
| `core/rules/comments.md` | `Bound to one machine` → `The modifier is bound to one machine` | `Bound to one machine` → `` `LicenseKey` is bound to one machine `` |
| `lang/java/rules/javadoc-rules.md` | `The call doesn't write a file, send a packet or change a world` | `` `preview()` doesn't write a file, send a packet or change a world `` |
| `lang/python/rules/docstring-rules.md` | `The call doesn't write a file, print output or log an event` | `` `dryRun()` doesn't write a file, print output or log an event `` |
| `lang/python/rules/docstring-rules.md` | `The first malformed field stops the read.` | `` `readPolicy()` stops at the first malformed field. `` |

The `Returns:` example `The number of rows this call added. A repeat run adds 0.` stays: a `Returns:` entry names the
returned value.

## 4. The Marker example with a label and a colon

Now: `read-only: NEVER write to the audited readings`

- **A.** `NEVER write to the audited readings`
- **B.** Keep. A Marker is a label by its definition.

## 5. A sentence about regression tests, beside rule 2b

Now, in `lang/python/rules/testing.md`: `Example-based tests cover specific regressions on top.`

Rule 2b says: no test only because a bug was fixed.

- **A.** `Example-based tests cover specific cases on top of the properties.`
- **B.** Cut the sentence.

## 6. The README

- `NAR026` flags `Over a few weekends, I rated hundreds of A/B examples` and `At C1 the guided agent extracted a shared
  parser`. Both openers are a time, and not a condition. Proposed: leave the README as it is, and note the form in
  `checks.md` as a known false positive.
- The list of GTNH habits: `no allocation in a draw method, no ordinal() saved to NBT, a switch over an enum with no
  default`. Each item is a label. Proposed: keep, by the label exception of **Sentence form**.

## Answers of 2026-11-21

1. B, with a pass for extra articles. `--since` limits any file of a git diff, so the rewrites don't name Python files.
2. Neither. The flag was on `, not per invoice`, so the example is now `the vendor rounds tax per line. Round each line
   before the sum`.
3. As proposed.
4. A.
5. B. The sentence is cut.
6. The README is half your own writing, so the prose checks don't apply to the README. The README rewrites of this pass
   stay, and so does the list of GTNH habits.
