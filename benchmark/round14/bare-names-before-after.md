# R14-bare-name: before and after

R14-bare-name reads a name in a javadoc `{@link}`, `{@linkplain}` or `{@code}` tag as the bare name, and puts the pair
of that name and the verb on review list 2. This file has every sentence that the change adds to the list, in two
corpora:

- GT5-Unofficial `gregtech/api/logic`, branch `processingspec/5-eye-of-harmony`: 21 new pairs over 327 sentences
- PlanNH `src/main/java`, commit `52a71d6`: 38 new pairs over 1,416 sentences

1 pair of GT5-Unofficial and 7 pairs of PlanNH were on the list before the change, with `value` in place of the name,
such as `value registers` for `NodeWidget registers`. The other 20 and 31 pairs are new.

Each pair has one of three verdicts:

- **Rewrite**: a reader of the bare sentence can't tell the argument or the result of a call. The after text writes the call and
  the result.
- **Keep**: the bare sentence still reads correctly.
- **Parse noise**: the pair isn't the subject and the verb of the sentence. The bare name changed the parse.

| Corpus | New pairs | Rewrite | Keep | Parse noise |
|---|---|---|---|---|
| GT5-Unofficial | 21 | 6 | 13 | 2 |
| PlanNH | 38 | 10 | 17 | 11 |

The after texts fix the bare-name fault only. Several PlanNH sentences have other faults, such as a semicolon, `says`
or a vague `it`. Those faults aren't fixed here.

## GT5-Unofficial

### Rewrite

| File | Before | After |
|---|---|---|
| `ModifierKind.java:123` | `{@link ProcessingSpec.Builder#range}` sets the range of a kind ranged per machine in each machine's spec. | For a kind ranged per machine, set the range in each machine's spec with `{@link ProcessingSpec.Builder#range}`. |
| `ProcessingLogic.java:727` | `{@link #successfullyConsumedInputs}` does not necessarily mean `{@link #checkRecipeResult}` being successful, when duration or power is overflowed. | When the duration or the power overflows, `{@link #successfullyConsumedInputs}` can be true and `{@link #checkRecipeResult}` a failure. |
| `ProcessingSpec.java:104` | The formula of this quantity returns a speed. `{@link Builder#speed}` sets the formula. | The formula of this quantity returns a speed. Set the formula with `{@link Builder#speed}`. |
| `ProcessingSpec.java:348` | Resolves the recipe as `{@link #resolve}` does. | Returns the same numbers as `{@link #resolve}`. |
| `ProcessingSpec.java:50` | … and `{@link #calculate}` runs the recipe. | … and `{@link #calculate}` returns the `{@link ProcessingRun}` of one run of the recipe. |
| `ProcessingSpec.java:922` | Refuses a recipe where `{@code met}` is false. `{@code failure}` gives the result. | Refuses a recipe when `{@code met}` returns false. `{@code failure}` returns the `{@code CheckRecipeResult}` of the refusal. |

### Keep

| File | Sentence | Pair |
|---|---|---|
| `MachineMode.java:11` | `{@link …MTEMultiBlockBase#getMachineModes}` returns a multiblock's modes as `{@code MachineMode}` records. | `getMachineModes returns` |
| `Modifier.java:20` | A `{@code Modifier}` reads the value of one machine for a `{@link ModifierKind}`. | `Modifier reads` |
| `ModifierKind.java:22` | A `{@code ModifierKind}` is a value that a `{@link ProcessingSpec}` reads, such as a coil tier, an item count or momentum. | `ProcessingSpec reads` |
| `ProcessingInputs.java:15` | `{@code ProcessingInputs}` has what a `{@link ProcessingSpec}` reads. | `ProcessingSpec reads` |
| `ProcessingRun.java:12` | `{@code getDisplayString()}` then returns the reason printed in the machine GUI, such as the coil heat the recipe requires | `getDisplayString returns` |
| `ProcessingSpec.java:46` | A `{@code ProcessingSpec}` computes how a multiblock runs recipes from the multiblock's energy hatches, mode and `{@link ModifierKind}` values. | `ProcessingSpec computes` |
| `ProcessingSpec.java:49` | `{@link #getModifiers}` returns the kinds the spec reads, … | `getModifiers returns` |
| `ProcessingSpec.java:531` | `{@link #describeMode}` writes the lines of each mode. | `describeMode writes` |
| `ProcessingSpec.java:1051` | `{@link ProcessingSpec#describeMode}` writes the lines of those terms. | `describeMode writes` |
| `ProcessingSpec.java:720` | A `{@code parallel}` of 4 and a `{@code factor}` of 2 give 8 at the first tier. | `parallel give` |
| `ProcessingSpec.java:788` | A `{@code base}` of 1 and a `{@code perTier}` of 1 give 200% at the first tier. | `base give` |
| `ProcessingSpec.java:730` | From `{@code min}` to `{@code max}` per voltage tier as `{@code kind}` rises from 0 to the max of `{@code kind}`'s range. | `kind rises` |
| `ProcessingSpec.java:838` | From `{@code min}` to `{@code max}` as `{@code kind}` rises from 0 to the max of `{@code kind}`'s range. | `kind rises` |

### Parse noise

| File | Sentence | Pair |
|---|---|---|
| `ProcessingSpec.java:289` | The lowest value of an ordered `{@code kind}` that passes the recipe's requirements, … | `that passes`: the subject of `passes` is the value |
| `ProcessingSpec.java:922` | Refuses a recipe where `{@code met}` is false. | `where met` |

## PlanNH

### Rewrite

The facts of the after texts come from the code, except where the last column has another source.

| File | Before | After | Source of the fact |
|---|---|---|---|
| `balancer/Balancer.java:33` | `{@link Graph#balance()}` thunks the mode here. | Not written. | `Graph.balance()` doesn't call `Balancer.run()` at `52a71d6`. The author has to say what the sentence is about, or cut the sentence. |
| `balancer/Balancer.java:252` | A node missing from `{@code copyCounts}` reads zero - the way a chart with no solve-derived quantities is presented. | A node missing from `{@code copyCounts}` has a count of zero, the same as on a chart without a solve. | the comment |
| `balancer/Note.java:10` | … and `{@link #severity()}` colours it. | … and `{@link #severity()}` sets the colour of the note. | the comment |
| `balancer/PortRef.java:7` | `{@code input}` distinguishes the two port lists. | `{@code input}` is true for a port of the input list, and false for a port of the output list. | the record `PortRef(UUID nodeId, int portIndex, boolean input)` |
| `balancer/SolveResult.java:16` | A rejected solve: no point, and `{@code rejection}` says why. | A rejected solve doesn't have a point, and `{@code rejection}` has the reason. | the comment |
| `balancer/Solver.java:21` | `{@link ModelBuilder#portRows(boolean)}` already lets the OUTPUT / INPUT stage express its own (extern-free) family without a bespoke builder. | `{@link ModelBuilder#portRows(boolean)}` writes the rows of the OUTPUT or INPUT stage, without externs. The two stages don't use another builder. | the comment, not checked in `ModelBuilder` |
| `setting/TargetKind.java:19` | Null for a kind the chart cannot edit: `{@link Pin#EXTENT}` arrives per solve, not on a machine. | Null for a kind that the player can't edit on the chart. The solver sets `{@link Pin#EXTENT}` on each solve, and the config of a machine doesn't have an extent. | the comment, and the `switch` of `TargetKind.of()` |
| `gui/layout/ChartLayouter.java:315` | Loose machines and group frames only, for the reason `{@link #chartCorner()}` gives. | Loose machines and group frames only, the same set that `{@link #chartCorner()}` measures. | the javadoc of `chartCorner()` |
| `gui/node/PortWidget.java:85` | Which side of the machine this port is on. A `{@link PortType}` cannot answer it: a catalyst is the same type either way, … | Which side of the machine this port is on. The side isn't part of the `{@link PortType}`, because a catalyst has the same type on either side, … | the comment |
| `balancer/Chain.java:15` | `{@link #run(SolveContext)}` drives the chain pass by pass: … | `{@link #run(SolveContext)}` runs the passes of the chain in order: … | the comment |

### Keep

| File | Sentence | Pair |
|---|---|---|
| `client/UnsupportedPackException.java:110` | Draw the lines that `{@link #initGui}` wrapped, centred on the screen. | `initGui wrapped` |
| `client/UnsupportedPackException.java:25` | FML logs the message before `{@code refreshResources()}` loads the lang files, … | `refreshResources loads` |
| `client/UnsupportedPackException.java:31` | `{@link #initGui}` runs after that refresh and reads the screen text from the lang file. | `initGui runs` |
| `flowchart/MachineGroup.java:7` | A plain `{@link Group}` frames a part of the chart and says nothing about the hardware; … | `Group frames` |
| `balancer/External.java:4` | The `{@link SolutionView}` rebuilds these the same way the committed point's externals read, … | `SolutionView rebuilds` |
| `balancer/SolutionView.java:162` | … `{@code excludeComponent}` skips the consumer's own component (-1 checks everything). | `excludeComponent skips` |
| `balancer/Solver.java:405` | … `{@link SolutionView}` reports them as boundary "imports" chips. | `SolutionView reports` |
| `alternatives/Enumerator.java:210` | Whether a stored `{@link ChoiceKey}` still names a support on this chart, or null when it does not. | `ChoiceKey names` |
| `gui/CanvasWidget.java:159` | The live half is `{@link #nodeWidgets2}`, which `{@code NodeWidget}` registers itself into … | `NodeWidget registers` |
| `gui/PortGeometry.java:5` | … pin `{@code i}` sits at `y = (i + 1) * SPACING + ORIGIN` on its node edge. | `i sits` |
| `gui/layout/ChartLayouter.java:378` | … not the 20 that `{@code HeaderTextWidget}` happens to declare. | `HeaderTextWidget happens` |
| `gui/summary/SummaryBody.java:20` | … (the same child-subtree swap `{@code DynamicSyncedWidget}` does) … | `DynamicSyncedWidget does` |
| `gui/summary/SummaryFlow.java:10` | Without this, `{@link AbstractParentWidget#canClickThrough()}` returns `false` whenever the flow has a background or hover background, … | `canClickThrough returns` |
| `gui/tooltips/TooltipBuilder.java:157` | A `{@link #group}` already indents its body, … | `group indents` |
| `gui/tooltips/TooltipTheme.java:13` | `{@code RichText}` flattens a line to one formatted string … | `RichText flattens` |
| `balancer/Chain.java:17` | Guards: a stage that `{@link Outcome.Fail fails}` stops the run … | `stage stops` |
| `nei/NodeLookupContext.java:7` | ItemStacks stay at the NEI boundary and wiring happens via `{@code Port#canConnect}`. | `wiring happens` |

### Parse noise

| File | Sentence | Pair |
|---|---|---|
| `flowchart/Summary.java:147` | One `{@link Line}` per section, in the order the panel reads them. | `Line reads`: the subject is the panel |
| `flowchart/Summary.java:194` | The `{@link Mode}` the current `{@link #lines}` were derived for; … | `Mode derives` |
| `flowchart/Summary.java:66` | … the amount-bearing `{@link Measure}` rows … | `Measure rows`: a noun compound |
| `balancer/Balancer.java:104` | … a stored `{@link ChoiceKey}` to honour … | `ChoiceKey honour` |
| `balancer/Balancer.java:97` | … and the point stays the solver's own. | `ChoiceKey stays`: the subject is the point |
| `balancer/Chain.java:17` | a stage that `{@link Outcome.Fail fails}` … | `that fails`: `fails` is the label of the link |
| `balancer/Solver.java:14` | … `{@link ModelBuilder}` - a stage declares its variables, … | `ModelBuilder declares`: the subject is the stage |
| `balancer/SolverMessage.java:109` | … with `{@code args}` spliced into it. | `args spliced`: a participle |
| `balancer/StageAudit.java:6` | … an empty array when pass 1 left nothing to fix. | `array left`: the subject is pass 1 |
| `setting/SettingDef.java:52` | … the widget hands `{@code edit}` the change itself … | `hands edit`: the subject is the widget |
| `gui/tooltips/TooltipBuilder.java:130` | … for a value a lang sentence carries. | `entry carries`: the subject is the sentence |

## What the change drops

The bare names change the parse of some sentences, and 4 pairs of PlanNH leave the list: `event fires`
(`Balancer.java:41`), `conservation rows` (`ModelBuilder.java:190`), `pass left` (`StageAudit.java:6`) and
`cost searches` (`GateCountStage.java:22`).
