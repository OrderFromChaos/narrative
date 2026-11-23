---
name: runbook
description: Write or review a runbook in the Narrative house style: a step-by-step manual for a reader who acts on each step, with equipment or data at risk. No reader work, terse steps, one path in order, checks with actions, and hazards first. Loads nar:page and nar:core.
---
**Before you write or review the page, load the skills `nar:core` and `nar:page` with the Skill
tool**, unless they are loaded already. `nar:core` has the sentence rules, and `nar:page` has the
rules for each page. This skill adds the rules for one kind of page.

# Narrative: runbooks

A runbook is a step-by-step manual for a reader who acts on each step, with equipment or data at
risk, such as `docs/till-update.md` for backing up, updating and restoring the software of a shop's
tills. The reader follows the steps in order and acts on each step.

**No reader work.** (R13-runbook-no-work) The reader can follow each step exactly as written. To
follow a step, the reader never substitutes a value, fills in a placeholder, merges a list of
changes into earlier steps, copies a value from elsewhere into a command, or recalls a choice from
an earlier step. Write out each variant in full (each shop, each till, each update), and repeat
steps across variants. Rewrite `For the north shop, use version 4.2 and profile north-0` and `Take
steps 1-9 on the second till, with these changes` as full steps. A pointer is fine only to steps the
reader runs unchanged, such as `steps 1-3 of "Back up the till database"`, or to a table cell with
the exact value.

**Terse steps.** (R13-runbook-terse) Write each step as an imperative action, then at most one line
on the result: what the reader sees, or where the output is, such as `This copies the backup to
D:\backups\north-2\.` Keep a sentence of explanation only when a reader without the sentence is
likely to make a mistake. Delete background that doesn't change a step, and delete the evidence for
a conclusion. Don't explain how the tools work, such as how the backup tool compresses files. Give
the explanation in a reply when the reader asks.

**One path, in order.** (R13-runbook-one-path) Give one way to do each step: the way proven on the
equipment, with an instruction to stop and ask on an error. Put a fallback in a separate, labelled
section. Put the sections and steps in the order the reader performs them, so each step uses only
the artifacts of earlier sections. Reference sections, such as a restore, go last.

**Checks with actions.** (R13-runbook-checks) In each check, give the expected result first, then
each other result with the action for that result.

**Hazards first.** (R13-runbook-hazards) Mark a step that blocks normal operation, or that can't be
undone, in bold at the step, before the reader acts.

**Write each dialog's settings one per line**, as `Field: value`, with the defaults marked. Explain
a setting only when the setting is a trap. (R13-runbook-settings)

## Verify the page

Run the `verify.py` of this skill on the page, as under **Verify a page** in `nar:page`:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" docs/report.html --no-fix
```

Take **Prose review** of `nar:core` on the lists of the run. Then read the page against the
checklist of `nar:page`, and against each rule of this skill, one rule at a time.