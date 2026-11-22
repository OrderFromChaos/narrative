# Conflicts for the de-poisoning pass

Text of the skill that breaks a rule of round 12. Each item goes to you before a change.

| rule | text of the skill | where |
|---|---|---|
| 1 | about 120 sentences with `no`, `nothing` or `none` on a subject or an object, such as `write no comment` | `core/`, `lang/`; the list is in `~/.local/share/narrative/eval-private/runs/claudish-rules/rule1/neg_hits.tsv` |
| 2b | `Example-based tests cover specific regressions on top` | `lang/python/rules/testing.md` |
| 7 | `the vendor rounds tax per line, not per invoice`, flagged by you on 2026-11-21, and the other `X, not Y` examples | `core/rules/comments.md` |
| 12 | `Bound to one machine` → `The modifier is bound to one machine`, and 6 more examples that open with `The` | `core/rules/comments.md` and `lang/` |
| 13 | the Marker example `read-only: NEVER write to the audited readings`: a colon after a label, the form you relabelled rewrite on 2026-11-21 | `core/rules/comments.md` |
| 14 | the Fence examples in two sentences, a fact and then the step: `the API returns 200 with an error body for a bad key. Check the body too`, `migrate before load. load reads the account_id column` | `core/rules/comments.md` |
| 13 | `, such as X`, in many places. Open: you asked for more research on 2026-11-21 | `core/`, `lang/` |
