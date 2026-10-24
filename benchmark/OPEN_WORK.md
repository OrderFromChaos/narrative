# Open work after the core and language split

Written on 2026-10-24, after the split of the shared rules into `core/`. Work on an item here starts
from master, after the user commits the split.

## Where things are

- `core/rules/`, `core/tools/`: the rules and the prose checks of every language. They are built
  into the skill `nar:core`.
- `lang/python/`, `lang/java/`: the rules and tools of one language. `nar:python` and `nar:java`
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

## 3. The colon rule and the Fence examples, through new-narrative-rule

From the user's notes on the gold labels, in `eval/units/labels.jsonl`:

- **A new rule:** no clause joined by a colon, and no stylised `X: Y` opening, such as
  `pinned serialisation: …`. The reason is the same as for the semicolon of `NAR013`.
- **Fence examples in `lang/python/rules/comments-python.md`:**
  - `# bool subclasses Python int. Reject it too` against the gold `need to guard against bools as
    well (bools are ints in Python)`
  - `# isdigit() admits non-ASCII digits such as '²'. Check isascii() too` against the gold: use
    `re.compile('[0-9]+')`, and write no comment
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

## 5. For the user

- Commit the branch, after review.
- Archive the narrative-java repository, with a README line pointing to `nar@narrative`.
