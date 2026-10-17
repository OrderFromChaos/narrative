# A/B run: `narrative` against `narrative-lite`

Run on 2026-10-15, branch `narrative-lite`, with the lite text after its de-poisoning pass. The cut
list is in `lite_coverage.md`.

## Result

**On this sample, the lite skill is no faster and no cheaper to apply, and its output is about the
same.**

- Wall time over all 12 cells: full 2,623 s, lite 2,521 s (4% less).
- Input tokens over all API calls: full 21.6M, lite 22.5M (4% more).
- Tool calls: full 178, lite 200.
- Correctness is equal: every V6 report matches `EXPECTED.md`, and every C2 cell passes 20 of 20
  tests.

The sample is small: two agents per cell, and one task of each kind. A difference of a few percent
is inside run-to-run spread. The skill text is about 15k tokens of a final context near 200k on V6,
and less than 10% of the cost of a run. Most of the time goes to the task: reading the spec, writing
the package, and running and testing it.

## Method

Same method as "Trial: procedural against priority framing" in `README.md`.

- **Arms:** `full` is `skill/` and `lite` is `skill-lite/`, each installed by `install.sh` to a
  scratch directory with a neutral name (`style-f`, `style-l`).
- **Tasks:**
  - a fresh write of `validation/v6_report_contract/TASK.md`, with `EXPECTED.md` and `fixture/`
  - `C2_fourth_finding` and `C4_thread_field` from `validation/harness/changes/`, each on a copy of
    `validation/v5_billing_reconcile/full`
- **Agents:** two fresh agents per cell, 12 in total, at most 4 at a time, both arms in each batch.
  The prompts differ only in the cell and skill paths, and say nothing about comments.
- **Scoring:** a final `verify.py --no-fix` with each skill's config, then conformance:
  - V6: the report JSON against the `EXPECTED.md` block, outside the three exempt values
  - C2 and C4: `validation/harness/conformance/conformance.py`

  Then churn from `measure_change.py` on the package, and the Claudish features of
  `benchmark/round10/cycles/claudish_table.py`. Comment blocks for C2 and C4 are the blocks absent
  from the pristine package, including rewritten ones.

## Cost per cell

Two agents per cell, written `run 1 / run 2`. The context figure is the subagent token count in the
completion notice.

| task | arm | wall time (s) | tool calls | final context tokens |
|---|---|---|---|---|
| V6 | full | 921 / 841 | 48 / 48 | 221,735 / 221,124 |
| V6 | lite | 786 / 791 | 56 / 49 | 199,046 / 198,311 |
| C2 | full | 234 / 263 | 20 / 27 | 132,445 / 144,851 |
| C2 | lite | 257 / 260 | 26 / 23 | 125,251 / 119,606 |
| C4 | full | 161 / 202 | 16 / 19 | 130,087 / 131,838 |
| C4 | lite | 226 / 201 | 24 / 22 | 125,944 / 117,864 |

- **V6:** lite is about 10% faster and ends with about 22k fewer context tokens. It makes more
  calls, so its summed input tokens are close to full's (13.9M against 13.6M).
- **C2 and C4:** lite is as fast or slower. The context saving per call is about 10k tokens, and
  extra tool calls cancel it.

## Output per cell

| cell | verify.py | conformance | churn (lines) | code lines | docstring words | new comment blocks |
|---|---|---|---|---|---|---|
| full V6 run 1 | pass | matches | | 751 | 1,138 | 7 |
| full V6 run 2 | pass | matches | | 712 | 1,051 | 8 |
| lite V6 run 1 | pass | matches | | 717 | 1,183 | 7 |
| lite V6 run 2 | pass | matches | | 748 | 1,337 | 16 |
| full C2 run 1 | 17 + 27 prose findings | 20 of 20 | 100 | 616 | 428 | 1 |
| full C2 run 2 | 17 + 27 | 20 of 20 | 89 | 618 | 258 | 2 |
| lite C2 run 1 | 15 + 23 | 20 of 20 | 101 | 616 | 382 | 2 |
| lite C2 run 2 | 17 + 27 | 20 of 20 | 97 | 619 | 411 | 1 |
| full C4 run 1 | 12 + 23 | 5 of 20 | 71 | 612 | 435 | 1 |
| full C4 run 2 | 12 + 23 | 5 of 20 | 68 | 612 | 405 | 1 |
| lite C4 run 1 | 10 + 21 | 5 of 20 | 80 | 612 | 528 | 1 |
| lite C4 run 2 | 10 + 21 | 5 of 20 | 90 | 622 | 528 | 1 |

- **Prose findings in C2 and C4** are `checks.py` + `agentverbs.py` counts. The pristine package has
  17 + 27, from an older skill. Every agent reports none on a line it wrote. A lower count means the
  agent rewrote old sentences that it touched.
- **C4 passes 5 of 20 in every cell, in both arms.** C4 makes `account_id` a required column, and
  the V5 suite writes billing files without it. A correct C4 rejects those files.
- **Docstring words** are higher in lite: V6 1,260 against 1,095 on average, and C4 528 against 420.
  In C4, the lite agents rewrote more of the v5 docstrings, which counts every rewritten docstring
  as new.

## Comment blocks, pooled by arm

The `### vocabulary` divider is excluded. Rates are per 100 blocks, with 95% intervals. Every
feature not listed is 0 in both arms. The container-verb row is a plain match, without the spaCy
verb tag of `claudish_table.py`.

| feature | full | lite |
|---|---|---|
| blocks | 20 | 28 |
| median words | 13 [9, 18] | 10 [9, 14] |
| p90 words | 32 [18, 38] | 22 [15, 34] |
| more than one sentence (%) | 65.0 [43.3, 81.9] | 53.6 [35.8, 70.5] |
| absolutes: every, never, whole, exactly | 10.0 [2.8, 30.1] | 7.1 [2.0, 22.6] |
| `, so` joining clauses | 5.0 [0.9, 23.6] | 0.0 [0.0, 12.1] |
| container verb: holds, carries, lives, keeps, names, states | 5.0 [0.9, 23.6] | 0.0 [0.0, 12.1] |
| passive | 25.0 [11.2, 46.9] | 25.0 [12.7, 43.4] |

No column is worse for lite outside its interval. Every interval overlaps.

## Comments that differ between the arms

Both arms wrote the same comments for the same facts: the dated database-history Source comment in
every C2 and C4 cell, and `bool subclasses Python int. Reject it too`, the `isdigit()` fence and the
`executemany()` NamedTuple comment in every V6 cell.

Lite comments with no counterpart in full:

- `Grace answers whether a finding is worth failing the run over, and only a billing line that
  bought nothing is. A region_mismatch or sku_mismatch finding has a cost too, and never fails the
  run.`
  - lite C2 run 1, an edit of a comment from v5
  - The agent verb `Grace answers` and the metaphor `bought nothing` are still in the comment from
    the v5 text. The v5 container verb is gone.
  - `verify.py` failed on the older findings, so the Prose review list never printed. The lite
    review covers changed sentences, and the subject of this sentence was not rewritten.
- Five end-of-line field labels in lite V6 run 2: `basename of the record's source file` (twice),
  `JSON array of basenames`, `one per rejected record` and `sorted basenames of the files of the
  finding's accepted records`. These are the reason for that run's 16 blocks. Each label is a unit or a
  shape absent from the annotation. Two labels are the same text.
- `?9 is seen_at in both first_seen_at and last_seen_at. first_seen_at is absent from DO UPDATE`
  (lite V6 run 1). The first sentence is hard to read without the SQL beside it.
- `In SQLite, NULL values in a UNIQUE column never conflict. With a key of several columns, a finding
  with a NULL would be inserted again on every run. finding_key is one JSON text value.` (lite V6
  run 2), a Source comment with no counterpart in full, because the full runs used a key with no NULL
  column.

Full comments with no counterpart in lite:

- `The default rules file is inside input_dir. Check input_dir first, so a missing directory raises
  InputDirectoryError and not RulesError.` (full V6 run 1)
- `reports are compared byte for byte with other implementations. Do NOT change indent, ensure_ascii
  or the final LF` (full V6 run 1). Lite V6 run 2 wrote the same rule as `serialisation as fixed by
  the task spec. Keep indent, ensure_ascii and newline as written`.
- `ALTER TABLE appends this column to an older database. Keep it last here too` (full C2 run 2)

## Findings for the skill, not for the comparison

- **In an edit of code with older prose findings, `verify.py` never passes, so neither arm reaches
  the Prose review list.** The edit agents that mention a review did it by hand. The list prints
  only after a passing run, so the lite limit to changed text had no effect here.
- Five edit agents, three full and two lite, reported that `store.py` uses a tuple alias where a
  `NamedTuple` is the skill's rule for rows, and left it in place, as `COMMON.md` requires.
- Every V6 agent used `datetime` and not `pendulum`, because the task allows only the standard
  library. Three agents gave that reason in their reports.

## What the result means for a lite skill

The skill text is a small part of what an agent reads in a run, so the saving from a shorter text
is small. In this run, extra tool calls cancelled that saving. The steps that take time are the
procedures, such as repeated `verify.py` runs and testing by hand, and the task work. To apply the
skill faster, change those steps, not only the rule text.
