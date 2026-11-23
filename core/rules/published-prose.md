### Published prose

A README, a doc page or an HTML report that you write follows the prose rules of this skill, as a
comment does. Which part of a page the rules cover depends on the skill loaded with this one:
**Scope of a change** in `nar:repo` for a page in a code repository, and **Verify a page** in
`nar:page` for a page outside one. Name each page to the `verify.py` of that skill. For a page in a
repository, the command is under **Pages** in **Comments in <language>**, in the skill
`nar:<language>`.

Write a page about the current code and data, with no changelog wording such as `now`, `no longer`,
or `was changed to`. Changelog wording belongs only in a changelog file that already exists in the
repository, such as `CHANGELOG.md`. Do not create a changelog file unless the user asks for one.
(R11-page-changelog)

State the current fact and the condition of the fact. Don't write the history of the page, such
as an earlier figure or a change of mind: `far smaller than it first looked` → `9% less code on a
spec with fixed outputs`. (R12-page-history)

A heading is the name of the topic: `What goes in a body, and what does not` → `Docstring body`.
(R12-topic-heading)

Open a README with the benefit to the reader. Give a number for the benefit when you have one.
Then put a cost of adoption in a short caveat, and then an example. Put evidence and process in
other documents, and link to those documents from the README. (R12-readme-order)

In instructions for an agent, such as a skill or a prompt, don't use a verb of perception such as
`see`, `look`, or `notice`. Name the act: `see the list` → `read the list`. (R12-no-perception-verb)

Only the wording checks and `agentverbs.py` run on a page. `verify.py` writes the lists of
**Prose review** for each named page too. When `--since` is given, only the passages of a page with a
changed line are checked and listed. Take the steps of **Prose review** for each sentence you wrote, and
handle each finding by the rule **A finding is information**. (R10-published-prose,
R11-page-inventory)
