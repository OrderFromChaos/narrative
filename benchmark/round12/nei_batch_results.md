# The NEI batch: rule 11 and the label exception of rule 12

Run 20261122-001737 of `eval/run.py agent --mode review` had 35 units, and 3 runs for each arm. The run took 232 s and
cost about $3. The base arm is the skill of master at 5904ceb. The test arm has the new rule 11 text and the label
exception of rule 12 (`R12-label-constant`).

The units are the 25 comments that you flagged on NEI PR 1146 in the run of plugin 5904ceb, and 10 controls. A control
is a comment that you committed in NEI ce26109 after the review. The scores are by hand.

| units | runs | base | test |
|---|---|---|---|
| `addVertices` javadocs on the style constants (rewrite) | 12 | 9 kept, 3 cut | 9 labels, 3 cut |
| style and colouring labels that you committed | 18 | 12 rewritten to `{@link #addVertices} adds …`, 6 to sentences | 16 kept, 2 cut |
| javadocs and comments that you cut | 42 | 2 cut | 4 cut |
| the other 4 controls | 12 | 8 kept | 4 kept |

- **Rule 12.** The test arm rewrote `{@link #addVertices} adds a small square in the middle of the block, and doesn't
  add a tint.` to `A small square in the middle of an untinted block.` in 3 of 3 runs, the same as your wording. The
  base arm turned each style label that you committed into the `addVertices` form, and each colouring label into a
  sentence. Both arms cut the pufferfish javadoc.
- **Rule 11.** The test arm cut 4 of 42 runs, and the base arm cut 2. In review mode, an agent reads one unit and the
  skill, and doesn't get the `NAR116` list. So the list isn't part of this score. 22 of the 25 flagged comments of
  the NEI files are on the list.
- **The other controls.** Both arms rewrote the class javadoc `Spawn modes of the blocks in a box around the player. …`
  in 3 of 3 runs, to `{@code MobOverlayScan} reads the spawn mode …`. You ruled on 2026-11-22 that the rewrite is correct: the
  fault of the committed javadoc is the length. In 3 runs, the test arm added a final period to a comment of several lines.
  **Sentence form** has that rule. In 1 run, the test arm made `update()` the subject of the `chunkVersions` comment,
  and in 1 run of the test arm the `update()` javadoc got a new wording.

The units and the arms are in `~/.local/share/narrative/eval-private/runs/claudish-rules/nei-batch/`. The file
`side_by_side.md` there has the outputs side by side.
