# Skill text proposals from the review of past sessions

Each item is a rule change, so each one waits for your choice. An approved item is then tested on fresh agents with
`/new-narrative-rule` before the item goes into `core/` or `lang/`. The finding numbers (1.1, 2.1, ...) are the sections of the
review plan.

| # | Change | Fixes |
|---|---|---|
| B1 | five-line step summary at the top of `nar:python`, `nar:gtnh` and `nar:core` | prose review skipped, skill read in part |
| B2 | skill descriptions: load when planning, and load nar:python too for Python files in a GTNH mod | skill not loaded while planning, wrong language skill |
| B3 | batching: fix every finding of one run, then run once more | one fix, then a full re-run |
| B4 | no filtering of verify output, and a kept finding is kept for one pass only | findings dismissed outside the three cases |
| B5 | leaving a sentence under the three cases needs no `noqa` | every finding rewritten |
| B6 | `--since` as the way to check only what changed, in any repo | output filtered by hand |
| B7 | published pages: no changelog wording | changelog text in DESIGN.md |
| B8 | Prose review step 3: a missing log entry is no proof by itself | from session 1bee1d0f |
| B9 | in a report, the text of each option before and after the change | "I can't pick unless I can see the options" |
| D1 | upstream findings on lines a PR changed: fix, or list and ask | 27 `NAR116` findings left in GT5 |
| D2 | Mixin `noqa` exceptions in nar:gtnh | `noqa` approval stretched |

---

## B1. Step summary at the top

**Status:** approved 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `lang/python/rules/intro.md`, `lang/java/rules/intro.md` and `core/rules/intro.md`, in place of the line
that points to **Procedures**.

**Before** (python):

> **The steps to run while writing and before you finish are in Procedures, the last section.**

**After:**

> **The steps, in short. The details are in Procedures, the last section.**
> 1. Load `nar:core` and this skill before you plan a change, not only before you edit.
> 2. Make a batch of edits, then run `verify.py` once for the batch.
> 3. Read the findings and the three review lists of that run. Do not filter the output with `grep`, `head` or `tail`.
> 4. Fix every finding and answer every list entry from that one run, then run `verify.py` once more.
> 5. In the report, say how many entries of each list you read, such as `read 212 of 212 sentences`.

**Why:** in 3 sessions the procedures at line ~800 of 885 were never read. In one session the model piped the output
of 66 of 67 runs, so no list was read.

---

## B2. Skill descriptions

**Status:** approved 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `skills.toml`.

**Before** (python, the last two sentences):

> Use for any Python written in or for this codebase, when laying out modules or packages, and when reviewing a diff
> against this style. Always load nar:core with this skill: ...

**After:**

> Use for any Python written in or for this codebase, when planning a change, when laying out modules or packages, and
> when reviewing a diff against this style. Always load nar:core with this skill: ...

**Before** (gtnh):

> Use for any Java written in or for a GTNH mod, and when reviewing a Java diff against this style.

**After:**

> Use for any Java written in or for a GTNH mod, when planning a change, and when reviewing a Java diff against this
> style. For Python files in the same repository, load nar:python too, or load nar:code in place of both.

**Why:** you rejected four plans with "follow /nar:gtnh". Two sessions edited Python with only nar:gtnh loaded.

---

## B3. Batching

**Status:** approved 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `core/rules/prose-review.md`, the last line.

**Before:**

> Fix what fails and run `verify.py` again.

**After:**

> Fix every finding and answer every list entry from one run, then run `verify.py` once more. Do not run `verify.py`
> after each single fix.

**Why:** 43 of 75 Java runs in GT5 came after one edit or none, about 89 minutes of waiting.

---

## B4. No filtering, and a kept finding covers one pass

**Status:** approved 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `core/rules/comments.md`, after the three cases of **A finding is information**.

**Before:** nothing.

**After:**

> Do not drop a finding from the output, with `grep -v` or otherwise. A finding that you take for a tool error goes
> in your report with the file and line. When the user decides to keep a finding, keep only that finding, and only in
> that pass.

**Why:** in GT5 the model ran `grep -v NAR101\|NAR116` 33 times. One decision to keep one `NAR101` became "earlier passes left
NAR116 and NAR101 by decision".

---

## B5. No `noqa` for a sentence left under the three cases

**Status:** approved 2026-11-01 with the review-list sentence reworded, waiting for the `/new-narrative-rule` test.

**Where:** `core/rules/comments.md`, under **Never add a `noqa` yourself**, and `core/rules/prose-review.md:30`.

**Before:**

> **Never add a `noqa` yourself.** The exceptions are under **noqa** in **Comments in <language>**, in the skill
> `nar:<language>`. (R11-findings)

**After:**

> **Never add a `noqa` yourself.** The exceptions are under **noqa** in **Comments in <language>**, in the skill
> `nar:<language>`. For a sentence left under case 1, 2 or 3, add no `noqa`: leave the sentence and the finding, and
> list the sentence in your report. Rewrite a sentence from a review list only when the sentence fails a step of
> **Prose review**. (R11-findings)

In `core/rules/prose-review.md:30`, the same change.

**Before:**

> An entry on a review list is a question, not a finding. When the subject can do the verb in the domain's sense, ...

**After:**

> Rewrite a sentence from a review list only when the sentence fails a step of **Prose review**. When the subject can
> do the verb in the domain's sense, ...

The record of `R11-review-question` has the old wording, so add a note with the new wording to the record.

**Why:** in session 25b37d82 the model rewrote quoted rule examples "because the skill rules out adding noqa", and
about 40 review-list entries. You rejected the wording "is a question, not a finding": an entry is a sentence to check,
not a question.

---

## B6. `--since` in any repository

**Status:** approved 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `lang/python/rules/verify.md` and `lang/java/rules/verify.md`, before **In a PR to another project**.

**Before:** `--since` appears only under **In a PR to another project**.

**After:**

> **To check only what changed, pass `--since` with the commit before your edits**, in any repository: `--since HEAD`
> for uncommitted edits, or `--since main` on a branch. In a repository with no commits, name the changed files as
> paths, and do not filter the output. In a stacked PR, pass `--since` with the branch that you created the PR's branch
> from, such as the branch of PR 2 for PR 3.

**Why:** in a repository with no commits, the model filtered the output by about 30 hand-typed file names and
reported "clean" with 55 findings left. `--since HEAD` covers uncommitted edits: `wording.py` diffs the working tree
against `merge-base(HEAD, REF)`.

---

## B7. No changelog wording in a page

**Status:** approved 2026-11-01 with the changelog exception reworded, waiting for the `/new-narrative-rule` test.

**Where:** `core/rules/published-prose.md`, after the first paragraph.

**Before:** the changelog ban is in the **Never** list for comments only (`comments.md:135`).

**After:**

> Write a page about the current code and data, with no changelog wording such as `now`, `no longer` or
> `was changed to`. Changelog wording belongs only in a changelog file that already exists in the repository, such as
> `CHANGELOG.md`. Do not create a changelog file unless the user asks for one.

**Why:** you flagged changelog-style text in DESIGN.md. The page-redundancy drafts tested in session 3e4e718d are in
no file of this repository, so there is nothing to re-check. A redundancy rule would be a new `/new-narrative-rule`
round.

---

## B8. A missing log entry is no proof by itself

**Status:** approved 2026-11-01 with the example reworded, waiting for the `/new-narrative-rule` test.

**Where:** `core/rules/prose-review.md`, step 3.

**Before:**

> 3. List the code paths that reach the line: each branch, each caller, each failure. Check the claim on every path.

**After:**

> 3. List the code paths that reach the line: each branch, each caller, each failure. Check the claim on every path.
>    A missing log entry is not proof that the event never happened. Before you write a claim such as
>    `the log has no stop event, so the server never stopped`, check that the code logs a stop event on every path
>    where the server can stop.

**Why:** in session 1bee1d0f the model wrote a state as fact from a missing log event.

---

## B9. Options shown in full

**Status:** approved 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `core/rules/prose-review.md`, a new last paragraph.

**Before:** nothing.

**After:**

> **When you ask the user to choose in a report, show the text of each option before and after the change.** With
> only an id such as `B3`, or a path to a file, the user cannot compare the options.

**Why:** your words: "I can't pick unless I can see the options".

---

## D1. Upstream findings on lines the PR changed

**Status:** option b chosen 2026-11-01, waiting for the `/new-narrative-rule` test.

**Where:** `lang/java/rules/verify.md` and `lang/python/rules/verify.md`, under **In a PR to another project**.

**Now:** "a finding on a line the diff does not touch is not the PR's to fix". The skill has no rule for an older finding
on a line the PR does change. In GT5, the model left 27 `NAR116` findings on methods whose bodies the model edited.

**Option a, fix them:**

> Fix every finding on a line that you change in the PR, even when the finding is older than your change, such as a
> `NAR116` on a method whose body you edit.

**Option b, list and ask once:**

> List each finding that was already on the base branch under `upstream findings kept`, and ask the user once whether
> to fix those findings.

---

## D2. Mixin `noqa` exceptions in nar:gtnh

**Status:** approved 2026-11-01 as a bullet list, with `NAR140` on a `@Shadow` field added, waiting for the
`/new-narrative-rule` test.

**Where:** `lang/java/rules/comments-java.md`, under **noqa**.

**Before:**

> The exceptions to **Never add a `noqa` yourself** are the three `noqa` uses prescribed in this skill: `NAR104` for
> two types of one name, `NAR142` in a degrade-and-report loop, and `NAR130` once the user approves an upstream name.

**After:**

> The exceptions to **Never add a `noqa` yourself** are the `noqa` uses prescribed in this skill:
> - `NAR104` for two types of one name
> - `NAR142` in a degrade-and-report loop
> - `NAR130` once the user approves an upstream name
> - in a Mixin class:
>   - `NAR130` for a member with the mod's `modid$` prefix
>   - `NAR106` for the abstract Mixin class
>   - `NAR131` for an injector method whose parameters Mixin fixes
>   - `NAR140` for a `@Shadow` field, whose type must match the target class

**Open question inside D2:** a `@Shadow` field must have the type of the target class's field, so `NAR140` (a concrete
collection type) cannot be fixed there. Add `NAR140` on a `@Shadow` field to the list too?

**Why:** you approved the three Mixin marks in session ee28724a. The lead agent then also marked `NAR140`, which a
subagent had declined.
