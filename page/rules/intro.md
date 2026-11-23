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

**The steps, in short.** (R13-steps)
1. Load `nar:core`, this skill, and the category skill of the page, before you plan the page.
2. Name the target audience, and the question of the page.
3. Write the page, then run `verify.py` on the page once (**Verify a page**).
4. Fix each finding, take **Prose review** of `nar:core` for each sentence you wrote, then check the
   page against the checklist at the end of this skill.

