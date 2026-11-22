# Labels for rules 7 and 9

19 dev units of `eval/units/round10.jsonl`, none with a gold label yet. Each label covers only the bold span, so
the other faults of a unit don't count. Answer each row with **R** (rewrite) or **K** (keep), and add a rewrite if
you have one. Example reply: `1 R, 2 K, 3 R "signed error"`.

- Rule 7: a contrast with `, not Y`, where Y is not in the code.
- Rule 9: a clause in place of the domain's word for the thing, such as `the bytes that don't belong to a team` →
  `the unassigned bytes`.

## Rule 7: `, not Y`

| # | unit | sentence, with the span in bold |
|---|---|---|
| 1 | f9ba35ce | A file with 10,000 bad rows emits one record at the default level**, not 10,000**. |
| 2 | eacefdb1 | one unreadable file in a tree of 100,000 is a line in a tally**, not a reason to stop**. |
| 3 | 2269a85a | The marker tracks side effects**, not containers**. |
| 4 | cc03fbdd | that case is NAR006's**, not this one's**. |
| 5 | 8a6cdd39 | Those are outputs of running it**, not of changing it**, and counting them would reward an arm that happens to write fewer files. |
| 6 | 0e876e7e | A device that is configured but absent from the data is a data pipeline problem**, not a drift problem**, so it is logged and left out of the summary |
| 7 | 2b586790 | One skip path**, not one per reason**: the two differ in a single token |
| 8 | 6bef66a1 | **Signed, not absolute**: a bias drifting one way is what a calibration check is looking for |
| 9 | 6bef66a1 | **fsum, not sum**: the errors are small differences of large values |
| 10 | bd961170 | WARN is a leading indicator**, not a smaller failure** |
| 11 | 418dc937 | **The tally, not the item.** |
| 12 | 86b7469c | Require a docstring wherever the contract is complex**, not merely where the body is long**. |
| 13 | 52797ada | Returns: One result covering every prose file**, not one result per file**. |
| 14 | 44994d0b | Scoped to signatures**, not calls** (R2b-B1) |
| 15 | ce1a54e2 | Require a docstring wherever the contract is complex**, not merely where the body is long**. |
| 16 | 06ea2e2d | The reconciliation is a join**, not a total**. |
| 17 | 56727c10 | ``accepted`` and ``rejected`` count records**, not lines** |

Rows 8 and 9 are one unit, so a rewrite in either row makes the unit a rewrite.

## Rule 9: a clause in place of the domain's word

| # | unit | sentence, with the span in bold |
|---|---|---|
| 18 | 749b5091 | **bytes that no team total carries** (a comment in a quota report) |
| 19 | 47c2a677 | **The rules that no off-the-shelf tool implements.** (the module comment of checks.py) |
| 20 | 7d4ec7b8 | **The nine rules that no off-the-shelf tool implements.** (an older copy of row 19) |

Rows 18 to 20 also break rule 1 (`no` on the subject). The question is whether a domain word fits, such as
`unassigned bytes` or `the custom rules`.
