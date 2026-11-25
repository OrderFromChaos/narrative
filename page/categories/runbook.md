# Narrative: runbooks

A runbook is a step-by-step manual for a reader who acts on each step, with equipment or data at
risk, such as `docs/till-update.md` for backing up, updating and restoring the software of a shop's
tills. The reader follows the steps in order and acts on each step.

**Write each step so that the reader can follow the step exactly as written.** (R13-runbook-no-work)
To follow a step, the reader never substitutes a value, fills in a placeholder, merges a list of
changes into earlier steps, copies a value from elsewhere into a command, or recalls a choice from
an earlier step. Write out each variant in full (each shop, each till, each update), and repeat
steps across variants. Rewrite `For the north shop, use version 4.2 and profile north-0` and `Take
steps 1-9 on the second till, with these changes` as full steps. A pointer is fine only to steps the
reader runs unchanged, such as `steps 1-3 of "Back up the till database"`, or to a table cell with
the exact value.

**Keep each step terse.** (R13-runbook-terse) Write each step as an imperative action, then at most
one line on the result: what the reader sees, or where the output is, such as `This copies the
backup to D:\backups\north-2\.` Keep a sentence of explanation only when a reader without the
sentence is likely to make a mistake. Delete background that doesn't change a step, and delete the
evidence for a conclusion. Don't explain how the tools work, such as how the backup tool compresses
files. Give the explanation in a reply when the reader asks.

**Give one path through the steps, in order.** (R13-runbook-one-path) Give one way to do each step:
the way proven on the equipment, with an instruction to stop and ask on an error. Put a fallback in
a separate, labelled section. Put the sections and steps in the order the reader performs them, so
each step uses only the artifacts of earlier sections. Reference sections, such as a restore, go
last.

**Give an action for each result of a check.** (R13-runbook-checks) In each check, give the expected
result first, then each other result with the action for that result.

**Mark each hazard before the reader acts.** (R13-runbook-hazards) A hazard is a step that blocks
normal operation, or a step that can't be undone. Mark the step in bold.

**Write each dialog's settings one per line**, as `Field: value`, with the defaults marked. Explain
a setting only when the setting is a trap. (R13-runbook-settings)

