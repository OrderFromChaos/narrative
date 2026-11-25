---
name: new-narrative-rule
description: Add or change a rule in the Narrative skill, tested on fresh agents before the rule reaches skill/. Use when the user rejects text that narrative wrote or kept, or asks for a new rule.
---

# Adding a rule to the Narrative skill

1. **Get the dataset, and label the dataset.** Collect the text the user rejected, the text before
   narrative ran, and the user's rewrite if there is one. Old versions of a file are in the session
   transcripts under `~/.claude/projects/`. Supplied artifacts stay out of the repository. Split
   each input into units: a sentence, or a clause after `, so` or a semicolon. Label each unit from
   the user's rewrite as `cut`, as rewritten by one rule, or as `keep`. Label every unit before any
   agent runs, and never change a label after you have seen an output.
2. **Confirm the current behaviour.** Run fresh agents with the current `skill/SKILL.md` on the
   dataset: one on the text before narrative, one on the narrative output. Leave the gold rewrite and any hypothesis
   out of the prompt. Record what each agent changed and the rule each agent cited. Score
   each output (**Scoring**). These scores are the baseline.
3. **Design the rule, and get the user's acceptance.** Show the rule text and the before and after
   for the dataset, then ask. The rule fixes narrative output. The text before narrative is only
   the baseline.
   De-poison each draft by step 5 before you show the draft.
4. **Generalize the rule.** Rewrite each example in another domain, so the examples aren't from the
   dataset. An agent copies the example of a rule word for word. Make the fix of each example the
   fix you want most often, such as a cut before a rewrite, and make the text after the arrow pass
   the skill. Make the text before the arrow break the new rule only, so the reader sees which fault
   the rule is about. Put the text after the arrow of each example through the review lists too, and rewrite
   the text until the lists are empty. An imperative in a rule is a command that an agent follows in
   every case. Write `may` for a permission: `Write a list of two items inline` → `A list of two
   items may be inline`. Open the rule with one bold imperative sentence, and add a sentence or an
   example only where the rule is unclear without the sentence or the example. A bold noun phrase, such as `The steps for a
   page that exists.`, is a label in place of a rule.
5. **De-poison the rule text.** Run the checks of `.claude/skills/self-consistency-narrative/`
   (sections 2 and 3) on the rule text, and check each comment example as a comment. Read the
   rule text against the user's Claudish patterns and against the new rule itself. Fix each finding,
   and run the checks again after every edit. Then read each draft of the batch as an agent that
   loads the skill and never saw this session. Name each page, version and tool in full, so you don't
   write `the other page`, `the version` or `the reader's tools` for a thing from this session.
6. **Test the rule inside the full skill.** Insert the rule into a full copy of `skill/SKILL.md` in
   the scratchpad, and run fresh agents with that copy on the original dataset. Do not paste the
   rule into the prompt. The test is whether an agent follows the rule among every other rule of
   the skill. Score each output.
7. **Show the scores, and ask the user for final approval.** Show the score table next to the
   baseline, each agent's output beside the user's rewrite, and every difference. If the user
   rejects the result, refine the rule and go back to step 3. Do not tune the rule to one sentence
   of the dataset.
8. **After approval, add the rule to `skill/`, then de-poison the skill.** Run the full
   self-consistency pass. Some older examples are usually wrong under a new rule. Put each
   conflicting example to the user before changing the example.

## Scoring

Score each rule separately, over the units of every input. For one rule:

- true positive: the agent took the rule's action on a unit with that rule's label
- false positive: the agent took the rule's action on a unit with another label
- false negative: the agent left a unit with that rule's label unchanged, or took another action

Precision is TP / (TP + FP), and recall is TP / (TP + FN). Report the counts as well as the ratios,
for each input and for all inputs together. When a rule has fewer than ten labelled units, recall changes by more than ten points for each unit, so run each input on three agents and add up the
counts.
