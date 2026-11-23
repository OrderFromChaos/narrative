---
name: brief
description: Write or review a findings brief in the Narrative house style: a page on an investigation in progress, such as a root-cause analysis, kept current. Current best understanding only, a status on each claim, data sources first, an executive summary, one fact on one page, and next steps. Loads nar:page and nar:core.
---
**Before you write or review the page, load the skills `nar:core` and `nar:page` with the Skill
tool**, unless they are loaded already. `nar:core` has the sentence rules, and `nar:page` has the
rules for each page. This skill adds the rules for one kind of page.

# Narrative: findings briefs

A brief is a findings page on an investigation in progress, such as a root-cause analysis, shared
with the people who work on the problem and kept current. Examples are `Route 12 Delays`, `Depot
Logs` and `Collapsed Sourdough`.

**Keep the page current.** (R13-brief-current) Update the page in the same session as the data
arrives. Delete superseded text, finished plans, stale counts and answered questions when you add
new text.

**Give each claim a status, and change the status with the data.** (R13-brief-status) Use confirmed,
strong evidence or hypothesis. Raise or lower a status as data arrives. Don't leave `inferred` or
`working assumption` on a fact confirmed by data in hand. Before you label a claim, check the data
already collected, such as exports, logs and photos.

**Describe the data sources before the data.** (R13-brief-sources) Give each source in a line, with
how far to trust the source. A timetable from another city's bus operator is a plausible guess, and
isn't a fact.

**Open with the title and an executive summary** (**Structure** in `nar:page`), and leave out a
digest of the sections. (R13-brief-summary)

**State a fact on one page, and link to that page from the other pages.** (R13-brief-one-page) The
GPS charts, route maps and fault codes live on the depot logs page. The brief has the conclusions
and links to the depot logs page.

**List the next investigation steps, and record what the user ruled out.** (R13-brief-next) Don't
reopen a ruled-out question. `A driver change doesn't fix the Monday delay` ends that line of
inquiry.

**Put the runs of an investigation in one test-plan table.** (R13-test-plan) Give the table a row
for each planned or finished run, and a column for each condition the runs vary. Write yes or no in
each condition cell, and give each of the two values a colour. Add a Done column and a Result
column. Give each run a fixed name that is unique on the page, such as `Bake 2`, never `This bake`.
When a condition of a new run doesn't have a column, add the column, or split a column with two
conditions, such as `Flour and proof` into `Flour` and `Proof`.

| Run | New flour | Long proof | Warm room | Steam | Fan oven | Done | Result |
|---|---|---|---|---|---|---|---|
| Bake 1, old flour, short proof | no | no | yes | no | no | 05-16 | loaf 2 cm lower |
| Bake 2, new flour, short proof | yes | no | yes | no | no | not yet | |
| Steam test | yes | yes | yes | yes | no | not yet | |

## Verify the page

Run the `verify.py` of this skill on the page, as under **Verify a page** in `nar:page`:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" docs/report.html --no-fix
```

Take **Prose review** of `nar:core` on the lists of the run. Then read the page against the
checklist of `nar:page`, and against each rule of this skill, one rule at a time.