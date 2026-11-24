# Narrative: changes in a code repository

These rules cover a change in a code repository. A change can touch:
- code, comments, docstrings and javadoc
- error messages and help text
- pages such as a README or a file under `docs/`

`nar:python` and `nar:gtnh` load this skill, and this skill loads `nar:core`. For a change in a
language without a Narrative skill, such as C, C++, JavaScript, or Verilog, load this skill
directly. A page outside a repository, such as a findings page or a proposal, follows `nar:page` in
place of this skill.

## Scope of a change

**In a code repository, the rules cover the lines you changed.** (R10-published-prose,
R13-repo-scope) When you rewrite part of a page, the rules cover the section you changed. If the
rest of the page is clearly written by an LLM, suggest cleaning the rest, and do not change the rest
unasked. A page that a person wrote and you did not change is left as written, unless the user asks
for the page to be checked. Run `verify.py` with `--since`, as under **Verify** in `nar:<language>`,
so the checks and the lists cover only the lines you changed. For a language without a Narrative
skill, run the `verify.py` of `nar:core`.