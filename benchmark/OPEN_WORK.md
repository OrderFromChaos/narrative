# Open work after the core and language split

Written on 2026-10-24, after the split of the shared rules into `core/`. Work on an item here starts
from master, after the user commits the split.

## Where things are

- `core/rules/`, `core/tools/`: the rules and the prose checks of every language. They are built
  into the skill `nar:core`.
- `lang/python/`, `lang/java/`: the rules and tools of one language. `nar:python` and `nar:gtnh`
  tell the agent to load `nar:core` with the Skill tool.
- `skills.toml`, `build_skills.py`, `assemble.py`: the build of `skills/`. When `nar:code` loads,
  Claude Code runs `assemble.py`, and the output is the list of skills to load for the repository.
- `eval/`: the labelled units, the labeller, and the confusion-matrix eval. `eval/run.py agent
  --skill nar:python` runs fresh agents on the plugin `nar`, with the Skill tool.
- `benchmark/java-merge/`: the drift between the two copies of the shared rules, and the rulings.
- Runs bill to the user's Max plan: about $0.24 per 20-unit eval session at list rates, and $10 at
  list rates is about 10% of a 5-hour window. Check the plan usage before a large run.

## 1. Bronze importers (plan step 1d)

Build `eval/import_pr.py` and `eval/import_transcripts.py` on the schema in `eval/schema.py`.

- **PRs.** These 5 Angelica PRs were flagged as slop by the Angelica maintainer. All are closed, in
  Java:
  - https://github.com/GTNewHorizons/Angelica/pull/2050
  - https://github.com/GTNewHorizons/Angelica/pull/1930
  - https://github.com/GTNewHorizons/Angelica/pull/1929
  - https://github.com/GTNewHorizons/Angelica/pull/1928
  - https://github.com/GTNewHorizons/Angelica/pull/1887

  The comment and javadoc units of the added lines, and the sentences of the PR body, are bronze
  `cut`. Comments that maintainers added in merged PRs of the same repository are bronze `keep`, so
  specificity can be measured. Later PRs are picked by hand.
- **Transcripts.** Units of Write and Edit tool calls in `~/.claude/projects/`. A session before
  2026-08-12 that never loads narrative is pre-narrative. A session where the user reminds the agent
  to use narrative after code was written has bronze candidates before that message. Never label a
  unit from the rewrite that narrative made, because the score would then compare the skill with the
  output of the skill.
  The output goes to the private store, `~/.local/share/narrative/eval-private/`.
- **Work repos.** The importers take a repo path or a PR export that the user names on the command
  line. No agent browses a work area unasked. The units go to `eval-private/work/<repo>/`, with
  `confidential: true` on each unit. A review comment on a work PR, such as "remove this comment",
  gives a bronze label to the commented lines. An agent run skips confidential units unless
  `--allow-confidential` is given.
- **Noise.** For each bronze source, the user labels a seeded sample of 30 units with
  `eval/label.py`. The measured accuracy of the source of the labels is next to each bronze matrix
  in the report.

## 2. new-narrative-rule against the eval (plan step 1e)

The skill is at `.claude/skills/new-narrative-rule/SKILL.md`. Rewrite its steps:

- label new units into the `dev` split only
- the baseline is `eval/run.py` on dev, and the test of a rule runs on dev, then once on `test`
- the change must not make any cell of the gold matrix worse, beyond the interval of the cell and
  beyond the human ceiling (81%, in `eval/standards.toml`)
- never read test units while drafting a rule
- compare with the human ceiling only on units that the rules were not written from, labelled at
  the current standard. The round-10 units are the material the rules were written from

In the same pass, `self-consistency-narrative` scores `benchmark/round10/agentverb/gold.tsv` with
`agentverbs.py --score`, and that check allows no drop. Replace it with the deterministic predictor
of `eval/run.py` on the full gold set.

## 3. The colon rule and the Fence examples, through new-narrative-rule

From the user's notes on the gold labels, in `eval/units/labels.jsonl`:

- **A new rule:** no clause joined by a colon, and no stylised `X: Y` opening, such as
  `pinned serialisation: …`. The reason is the same as for the semicolon of `NAR013`.
- **Fence examples in `lang/python/rules/comments-python.md`:**
  - `# bool subclasses Python int. Reject it too` against the gold `need to guard against bools as
    well (bools are ints in Python)`
  - `# isdigit() admits non-ASCII digits such as '²'. Check isascii() too` against the gold: use
    `re.compile('[0-9]+')`, and write no comment
    The user also rates this example acceptable as a comment. The point of the example is the named
    alternative, `Check isascii() too`, because agents often name the fence and leave out the
    alternative. For now, the gold label of the unit `isdigit() alone admits non-ASCII digits such as
    '²'` is a rewrite into this example, although the original is acceptable too. In every run, the
    agent with the skill rewrites that unit to this example word for word. Finer metric rules for such
    cases come later.
- The `as X, for Y` form, such as `as typed, for the report's input_dir`. The user would write
  `as originally typed`, and still rated the comment acceptable.
- Other notes for the same pass: `identical`, not `byte-identical`, for a text report. `two` and
  `implementations` in `two implementations must write …` are vague or over-specific.

## 4. Why more comments pass with the composable skill

On the gold dev units in context (51 units, 3 runs each), today's skill against `nar:python` +
`nar:core`, with the current labels:

| | today's skill | composable |
|---|---|---|
| sensitivity | 0.848 | 0.768 |
| accuracy | 0.843 | 0.771 |
| MCC | 0.468 | 0.373 |

The intervals overlap, but the user counts a drop of about 10 points in sensitivity or specificity
as meaningful, whatever the significance. Find the cause before the composable skill ships widely:

1. Compare the predictions of the two runs per unit, at no cost, from
   `~/.cache/narrative-eval/runs/20261024-135701-agent-dev-0.json` (today's skill) and
   `-1.json` (composable). List the units that pass with the composable skill and fail with today's
   skill.
2. Name the change behind each unit. The candidates: the neutral examples that replaced the `#`
   examples in core, the code-block examples moved to `Comments in Python`, the order in which
   `nar:core` and `nar:python` reach the agent, and the instruction to load `nar:core`.
3. Test the strongest candidate on dev, such as the composable skill with the inline examples
   restored, then run both skills once on the test split.

## 5. Dead and low-impact rules

Find the rules that never change an outcome, so they can be cut or merged. The user asked for this.
Thompson sampling and ablation over rule modules were explored in a separate session. Start from
that session's notes, then measure each candidate with `eval/run.py --skill A --skill B`.

## 6. Roadmap, designed only

- **Modes.** `nar:prose` for docs, READMEs and reports, from `core/` alone. `nar:pr` for a PR
  title, body and commit messages: the core prose rules and the `--since` scope, with units imported
  from real PRs.
- **Long-horizon eval** (`validation/longrun/`). The roles run in this order:
  1. A requirements agent reads commits k to k+N of a real codebase, N about 100, and writes each
     requirement as behaviour, with no module, class or function name.
  2. A test agent writes conformance tests from the requirements alone. The builders never see them.
  3. A PM agent writes one message per feature-sized group of commits, 15 to 25 messages for 100
     commits. A script fails a message with an identifier, file name or module name of the
     real repo, and a fresh reviewer agent reads each message for architecture hints.
  4. A builder without the skill gets the messages one at a time, each in a fresh session on its
     previous output.
  5. A builder with the skill, the same way.

  The runs start from an empty repo (greenfield) and from the real repo at commit k (brownfield).
  Per step and cumulative: LOC, conformance, regressions, huge refactors (`measure_change.py`),
  token cost, and for brownfield the drift from the norms of the real repo. If the two arms converge to
  the same design, the messages were too specific, and the PM step needs coarser groups. Each arm
  runs at least 3 times. The pilot is about 30 commits, about 8 messages, one Python repo, greenfield.
- **Tool reuse.** `eval/mine_tools.py` lists the scripts that agents wrote in post-narrative
  sessions (a Write of `*.py`, a Bash heredoc) and clusters them by purpose. The user picks the
  clusters that become shared tools in `core/tools/` or `lang/*/tools/`. bugfind records the number
  of ad-hoc scripts per task.
- **Task level.** A chain harness in `experiment/bugfind`, and a Java task set from GTNH repos. The
  report has the resolved rate, the cost and the unit matrix of the comments of each run.

## 7. Outside the scope of the unit matrix

The confusion matrix of `eval/run.py` scores one thing: whether an agent with the skill marks an
existing comment, written by a model without the skill, as needing action. These are not measured:

1. **Code written with the skill from the plan stage on.** Every unit was written without the skill.
   The comments of bugfind runs and of the long-horizon builders (section 6), labelled with
   `eval/label.py`, are the material for this measure.
2. **The action taken, cut or rewrite.** Each prediction has an `action` field, and the saved runs
   in `~/.cache/narrative-eval/runs/` have the field, but in the report, cut and rewrite are one
   class. A matrix of action against the gold verdict can be built from the saved runs, with no new
   run.
3. **The quality of a rewrite.** A rewrite can be slop in other words. The saved runs have each
   `new_text`. Run the deterministic checks on those texts, and label a sample with `eval/label.py`.
4. **Durability.** Whether a later agent with the skill flags or rewrites the same comment again.
   Run the skill on the rewrites of an earlier run, and count the share of those rewrites that the
   skill changes a second time. The long-horizon eval measures the same across real steps.
5. **Code choices outside comments**, such as layout, types and errors. Only bugfind and the
   long-horizon eval have measures for these.
6. **Docs and PRs.** The units are code comments and docstrings. For pages, PR bodies and commit
   messages, units of those kinds can come from the bronze PR importer (section 1), the `nar:pr`
   mode (section 6), and `~/.cache/narrative-agentverb-case/gold_gtnh.tsv`, 341 NAR017 sentence
   labels (87 agent, 254 ok) from a published page about GTNH planner mods. No importer reads that
   file yet.
7. **The checkers and the setting of use.** In `eval/run.py agent --mode edit`, the default since
   2026-10-24, the session gets the units' files, the file tools, the whole shell and the skill's
   `verify.py`, with a request to fix the comments in place. `eval/edits.py` reads each unit's
   verdict from the diff. Only 17 of the 63 gold units with context still have their whole file in
   the repository. The files of the others were in deleted scratch directories, so the file of each
   of those units is built from the rated snippets. `--mode review` is the earlier JSON review, kept
   for comparison. In that mode on gold dev (report `20261024-172801-compare-dev`), letting the agent
   run `verify.py` raised sensitivity from 0.754 to 0.841 on the units in context, and from 0.608 to
   0.980 on the NAR017 sentences of gold.tsv. The rules were tuned on those sentences.

   In the edit mode, on the same 51 gold dev units in context (report
   `20261024-194708-agent-edit-dev-0`, 3 runs, the whole shell, and a separate grader that reads the
   git diff for the rules), sensitivity was 0.906 (125/138) and specificity 0.600 (9/15). The diff
   reader and the grader agreed on all 131 changed units. With three labels revised by the user
   (`stripped and casefolded` and `as typed, for the report's input_dir` to keep, and `isdigit()
   alone admits non-ASCII digits such as '²'` to a rewrite), the same run has sensitivity 0.948
   (128/135) and specificity 0.833 (15/18), in report `20261024-221837-agent-edit-dev`. These units
   are the material the rules were written from, so the numbers are agreement on that material, not
   on new code.

## 8. For the user

- Commit the branch, after review.
- Archive the narrative-java repository, with a README line pointing to `nar@narrative`.
