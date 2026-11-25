# Narrative: pages

These rules cover a page that people read, such as:
- an HTML report
- a findings page
- a proposal
- a runbook
- a README

`nar:core` covers each sentence. This skill covers the reader, the scope, the structure, the titles,
the register, the terms, and the charts and diagrams of the page. A category skill, such as
`nar:proposal`, `nar:brief` or `nar:runbook`, loads this skill and adds the rules for one kind of
page.

In these rules, the reader is the target audience of the page, named before you write (**Reader**),
never a generic reader.

**Load `nar:core`, this skill and the category skill of the page before you plan the page.** (R13-steps)

**To write a new page, name the reader and the question, write the page, and run `verify.py` once.** (R13-steps) Fix
each finding, take **Prose review** of `nar:core`, and check the page against the checklist at the end of this skill.

**To clean up a page, cut before you change a sentence.** (R14-cleanup-steps)
1. Name the reader and the question of the page.
2. Label each section `keep`, `move` or `cut` (R14-triage).
3. Make the moves and the cuts, and check that each moved fact is on the destination page.
4. Date each relative time (R14-dated).
5. Run `verify.py --cleanup`, fix each finding, and take **Prose review**.

