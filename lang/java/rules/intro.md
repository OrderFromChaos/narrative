
# Narrative Java

**0% of reader effort on rote diffing, 100% on design.** (R2b-P0) Every rule below is a case of
that, or of the second principle, to prefer what the type checker and IDE can follow.

Four near-identical lines that differ in one token make the reader compare them token by token, and
every comparison is a chance to miss the difference. One parameterised call removes the comparison.

This is the root of DRY, of one-name-for-one-thing, of consistent ordering, and of the ban on
gratuitous variation. When two rules conflict, follow the rule under which the reader diffs less.

Second principle, for representation choices: **prefer what the type checker and IDE can follow**,
even when a looser form is more flexible. The type checker here is javac. (R3-P2-rank)

**The steps to run while writing and before you finish are in Procedures, the last section.**

**This document applies to every file, however many there are.** `architecture.md` adds what happens
**between** packages: which package may use which, where a shared type belongs, when one class
becomes several, and how a mod contains an optional mod. Read it when the change spans more than one
package or touches another mod. `tooling.md` has the job of each tool and the defaults that break a
rule here. Read it before you change a config.

The reason for each rule is in the rule's text, so read the rule and not the id after the rule. The
ids are provenance. They resolve in `benchmark/decisions.jsonl` in the source repository,
`github.com/OrderFromChaos/narrative`. That repository does not ship with the skill. **A rule with no id and no check behind the rule does not belong here.**

