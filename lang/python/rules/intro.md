
# Narrative Python

**0% of reader effort on rote diffing, 100% on design.** (R2b-P0) Every rule below is a case of
that, or of the second principle, to prefer what the type checker and IDE can follow.

Four near-identical lines that differ in one token make the reader compare them token by token, and
every comparison is a chance to miss the difference. One parameterised call removes the comparison.

This is the root of DRY, of one-name-for-one-thing, of consistent ordering, and of the ban on
gratuitous variation. When two rules conflict, follow the rule under which the reader diffs less.

Second principle, for representation choices: **prefer what the type checker and IDE can follow**,
even when a looser form is more flexible. State in a `dict[str, Any]` passes `mypy --strict` only
with a `cast()` or a key lookup at every use. Typed attributes pass with neither. (R3-P2-rank)

**The steps to run while writing and before you finish are in Procedures, the last section.**

**This document applies to every file, however many there are.** Naming, layout, types, errors and
docstrings apply to each module of a package exactly as they apply to a single-file program.

`architecture.md` adds what happens **between** files: which module may import which, where a shared
type belongs, when one file becomes several, and which modules may import a third-party dependency.
Read it when the program spans more than one module or imports a third-party package. Skip it for a
single-file program, where none of `architecture.md` applies.

The reason for each rule is in the rule's text, so read the text and not the id after the rule. The
ids are provenance. They resolve in `benchmark/decisions.jsonl` in the source repository,
`github.com/OrderFromChaos/narrative`. That repository does not ship with the skill. **A rule
with no id and no linter behind the rule does not belong here.**

