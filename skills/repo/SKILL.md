---
name: repo
description: The Narrative rules for a change in a code repository, such as a change to code, comments, docstrings, error messages or a README. The rules cover the scope of a change, and apply to the lines you changed, checked with verify.py --since. nar:python and nar:gtnh load this skill between nar:core and the rules of the language.
---
**Before you write or review anything, load the skill `nar:core` with the Skill tool**, unless
`nar:core` is loaded already. `nar:core` has the rules for comments, docstrings, error messages and
pages, and the steps of **Writing a comment** and **Prose review**. This skill adds the rules for a
change in a code repository.

# Narrative: changes in a code repository

These rules cover a change in a code repository. A change can touch:
- code, comments, docstrings and javadoc
- error messages and help text
- pages such as a README or a file under `docs/`

`nar:python` and `nar:gtnh` load this skill, and this skill loads `nar:core`. A page outside a
repository, such as a findings page or a proposal, follows `nar:page` in place of this skill.

## Scope of a change

**In a code repository, the rules cover the lines you changed.** (R10-published-prose,
R13-repo-scope) When you rewrite part of a page, the rules cover the section you changed. If the
rest of the page is clearly written by an LLM, suggest cleaning the rest, and do not change the rest
unasked. A page that a person wrote and you did not change is left as written, unless the user asks
for the page to be checked. Run `verify.py` with `--since`, as under **Verify** in `nar:<language>`,
so the checks and the lists cover only the lines you changed.