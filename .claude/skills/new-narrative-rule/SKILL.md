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
   dataset: one on the text before narrative, one on the narrative output. Give no gold rewrite and
   no hypothesis in the prompt. Record what each agent changed and the rule each agent cited. Score
   each output (**Scoring**). These scores are the baseline.
3. **Design the rule, and get the user's acceptance.** Show the rule text and the before and after
   for the dataset, then ask. The rule fixes narrative output, not the text before narrative.
4. **Generalize the rule.** Rewrite each example in another domain, so no example is taken from the
   dataset.
5. **De-poison the rule text.** Run the checks of `.claude/skills/self-consistency-narrative/`
   (sections 2 and 3) on the rule text, and check each comment example as a comment. Read the
   rule text against the user's Claudish patterns and against the new rule itself. Fix each finding,
   and run the checks again after every edit.
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
for each input and for all inputs together. With fewer than ten labelled units for a rule, recall
changes by more than ten points for each unit, so run each input on three agents and add up the
counts.
