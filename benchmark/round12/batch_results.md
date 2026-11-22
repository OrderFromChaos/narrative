# Batch test of rules 2 to 16

Run 20261121-194026 of `eval/run.py agent --mode review` had 97 units, and 3 runs for each arm. 1 confidential unit
wasn't sent. The
baseline arm is the current `nar:core` and `nar:gtnh`, rule 1 included. The test arm is the same skill with rules 2 to
16 of `proposals_claudish_rules.md`, version 4. The run took 8.7 minutes and cost $8.01: $3.85 for the baseline and
$4.16 for the test arm.

In one run, a hit is the action of the rule on a unit with the label of the rule. A cut of the whole sentence counts
as a hit when the fault goes with the sentence. Every score below is my reading of each output. The first version of
this table had mechanical scores for rules 1, 2, 6, 7, 10 and 13. On 2026-11-21 you asked for an audit, and the
mechanical scores were too low in every case: the last column has them.

| rule | units | baseline | test arm | sensitivity of the test arm | mechanical score, base and test |
|---|---|---|---|---|---|
| 1: negate the verb (both arms have rule 1) | 12 | 36 of 36 | 36 of 36 | 100% | 27 and 27 of 36 |
| 2: no changelog | 21 | 19 of 63 | 49 of 63 | 78% | 7 and 29 cuts of 63 |
| 3: name the actor | 7 | 0 of 21 | 15 of 21 | 71% | |
| 4: one fact in one place | 8 | 0 of 24 | 6 of 24 | 25% | |
| 5: technique and a checked defect | 7 | 0 of 21 | 3 of 21 | 14% | |
| 6: a condition is a clause | 6 | 8 of 18 | 18 of 18 | 100% | 8 and 9 of 18 |
| 7: no `X, not Y` | 16 | 23 of 48 | 48 of 48 | 100% | 13 and 34 of 48 |
| 8: text for players | 7 | 0 of 21 | 9 of 21 | 43% | |
| 9: the domain's word | 4 | 0 of 12 | 0 of 12 | 0% | |
| 10: no constant values | 2 | 0 of 6 | 6 of 6 | 100% | 0 and 3 of 6 |
| 12: no noun phrase for the identifier | 6 | 0 of 18 | 18 of 18 | 100% | |
| 13: no free modifier | 7 | 5 of 21 | 18 of 21 | 86% | 1 and 6 of 15, before 2 relabels |

The cuts count too, so a rule with many cuts can score well on a unit that another rule cut, such as rule 6 on the
changelog units: 9 of the 18 hits of the test arm are cuts by rule 2.

Rules 11, 14, 15 and 16 have no units of their own. Rule 11 is a change to a check, and the agents of the run don't
run the checks.

## The outputs

- **Rule 3**: the test arm named the program in 5 of the 7 units: `The server doesn't remove the lines of the lost
  milestones from the audit log`, `LiveSplit records the split's Real Time when the client catches up`. Agents of the
  baseline kept `stay`, `gets` and `is left out` in every run.
- **Rule 12**: the test arm rewrote all 6 javadocs with a verb. In 4 of the 18 outputs the verb is an imperative on a
  class, such as `Compile the mob spawn overlay quads into one GL display list.` You chose form B for rule 12, the
  identifier as the subject. The chains of `of` stay in 2 outputs: `the quads of each chunk column in the box
  of a MobOverlayScan`.
- **Rule 8**: the test arm cut the formula, the vanilla up-arrow line and the line on the chat limit in all 3 runs.
  The arm left `Spill` and `Use held block` in every run, so the bullet on the player's word had no effect.
- **Rule 9**: no output of either arm used a domain word. The test arm wrote `Off-the-shelf tools don't implement these
  rules`, or cut `bytes that no team total carries`.
- **Rule 5**: the test arm named a technique in one unit only. The technique is `throttle`, and the unit is about the
  compile delay. No run cut a reason
  that you found false. In 57eadfc0 and 7a43c086 the test arm put the false reasons into the one-sentence Fence form of
  rule 14: `turn depth writes off so that a translucent quad doesn't hide the overlay behind the quad`.
- **Rule 13**: the test arm removed the free modifier in 18 of 21 outputs. In 5 of the 18, rule 2 cut the whole
  sentence. Both arms left `State what is true of the code now, in the present tense.` unchanged in 3 of 3 runs.
- **Rule 2**: the baseline turned most changelog sentences into the `X would` form, such as `a limit of twice the radius
  would leave a large brush floating on a cliff`. 32 of the 63 outputs have that form. The item on the Fence form in the skill has that
  form. The test arm cut 29 units, and wrote a present fact or a Fence in 20 more.
- **Rule 4**: the 6 hits are cuts. A comment with the text of the class javadoc or of a field comment stayed in every
  run. An agent of the run reads one unit and the context of the unit, and the first copy of the text can be outside
  the context.
- **Probes**: both arms changed the same 2 probes in every run. Agents of the test arm cited rules 6 and 14 on `without tz=None,
  a time with no offset parses as UTC`, and wrote `pass tz=None so that a time without a UTC offset isn't parsed as UTC`.
  `without` isn't in the list of rule 6, and you labelled the probe keep.

## After the run

- On 2026-11-21 you relabelled the probe `without tz=None, a time with no offset parses as UTC` from keep to rewrite.
  The opener is a free modifier. The changes of both arms to the probe are then hits of rule 13, and the keep probes are 7
  units. Both arms left 18 of the 21 outputs of the 7 probes unchanged, 86%. The 3 changes in each arm are on `as typed,
  for the report's input_dir`.
- The table above is sensitivity: the share of the faulty units that the agents fixed. A specificity comes from keep
  units, and 7 probes are too few for a specificity of each rule.
- In 57eadfc0 and 7a43c086, the reasons are false by your notes on pub 28 and 29. An agent of the run reads the unit
  and the context of the unit, and can't check a reason against code outside the context.

## Human comments from before 2021

Run 20261121-200659 had 31 units without labels: 25 comments and docstrings of Python 3.10, and 6 comments of 2 GTNH
repositories at the last commit before 2023. No unit is from a file of the labelling files or of the rules. The run
cost $3.87.

| arm | outputs changed | cuts | units changed in at least one run |
|---|---|---|---|
| baseline | 86 of 93 | 12 | 29 of 31 |
| test arm | 85 of 93 | 24 | 29 of 31 |

- The new rules don't add edits. The test arm changed one unit more often than the baseline:
  `Return a new path pointing to the current working directory (as returned by os.getcwd()).`, a docstring on a
  method of one line. All 3 runs cut it by rule 15.
- The test arm cuts twice as often. The rules cited on those cuts are rule 15 and rule 2, such as on `Created by
  AfterWind on 4/17/2015.`
- The baseline already changes 92% of the outputs. In a sample of 10 units, most of the edits are defensible by the
  rules of the skill, such as `Workaround for broken uuencoders by /Fredrik Lundh` → `some uuencoders write extra
  characters after the data of a line. Decode only the characters that the length byte at the start of the line
  covers`. With that baseline, no rule gets a specificity from a change rate on human comments.

## Limits

- The units are the material of the rules, so the scores aren't held-out scores.
- The mechanical tests count the form only. A rewrite that removes `, not Y` and adds another fault counts as a hit.
- The skill of the test arm has the old Fence examples, such as `the API returns 200 with an error body for a bad
  key. Check the body too`. The de-poisoning pass replaces them.

The run files are `~/.cache/narrative-eval/runs/20261121-194026-agent-dev-0.json` and `-1.json`. The outputs side by
side are in `~/.local/share/narrative/eval-private/runs/claudish-rules/batch/side_by_side.md`.
