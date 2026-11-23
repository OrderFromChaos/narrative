# Round 13: page rules

Round 13 has the rules of `nar:page`, `nar:proposal`, `nar:brief`, `nar:runbook` and `nar:repo`. The
rules come from the user's feedback on pages that agents wrote in local sessions: proposals,
findings pages with charts, runbooks and reference pages. The user reviewed each rule in
conversation, and tested the skills on real pages before the release.

The pages and the feedback came from private work, so this directory doesn't have the transcripts.
Each example in the rules is rewritten in another domain, such as a bus network, a bakery or the
refunds of a shop. The rewrite follows step 4 of `.claude/skills/new-narrative-rule`. Each rewritten
example shows the fault and the fix of the original.

The rules haven't been through the fresh-agent tests of `new-narrative-rule` yet. `decisions.jsonl`
has one `R13-*` decision per rule, and each decision has the scope `page`. The scope rule of
`nar:repo` has the scope `core`.