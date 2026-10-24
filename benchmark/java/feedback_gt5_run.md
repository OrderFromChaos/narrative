# Feedback from the GT5 run: findings and proposals

Source: `~/Dropbox/OrderedSetCode/cloned-gtnh/narrative-java-feedback.md` (GT5-Unofficial PRs 1 and 2,
2026-10-17). Each claim below was checked on 2026-10-17 against this repo, the installed skill and a
scratch clone of GT5-Unofficial at `e2f5409`. Nothing in the skill has changed yet. Each item ends
with the decision to make.

## 1. Rejected sentences: every one passes the checks today

All 10 sentences went into one scratch `Sample.java` and through `javachecks.py`. There were 0
findings, and the subject-verb review list was `(none)`.

| feedback row | sentence | existing SKILL.md rule it breaks | why no check fired |
|---|---|---|---|
| "X is Y, as Z, so A" | `The product is a float, as in the machines' code, so the truncation to whole parallels matches.` | **A javadoc is about its class alone** (R9-02), **two sentences over a connective** (R10-period-join) | no check for `as` or for two connectives |
| "The X as Y verbs it" | `The tier as per-tier terms and their tooltips count it.` | **stand-in** `it` (R10-stand-in) | `count` is in `LITERAL` |
| "As X" opener | `As the EBF.` / `As {@link OverclockCalculator#ofNoOverclock}.` | **every clause has a subject and a verb** (R10-subject-verb) | NAR020 checks only the form before `, so` |
| "As X" opener | `One run of a recipe, as {@link ResolvedRecipe#calculate} works it out.` | **stand-in** `it` | no check for `as`. `works` is in no list |
| trailing ", where Y" | `The values machines of this kind take, where the spec has no range for it.` | **stand-in** `it`, **connective** | `take` is in `LITERAL`. No check for `, where` |
| unresolved "it" | `@throws IllegalArgumentException for {@link ModifierKind#VOLTAGE}. Add energy hatches for it` | **pronoun at the start of a sentence** / **stand-in** | no pronoun check |
| unresolved "it" | `Its value is the energy hatches' voltage tier. {@link ProcessingInputs} takes no value for it.` | same | same |
| subject can't do the verb | `The machine's spec inputs read the value, and the conformance test writes it on a copy of the machine.` | **only verbs for what code literally does** | `read` and `write` are in `LITERAL` for any subject |
| subject can't do the verb | `A saved index out of range reads as the first mode.` / `The mode that runs {@code recipeMap}` | same | `read` and `run` are in `LITERAL` |
| ", so" tail | `Whether some terms differ by mode, so the mode is an input a planner sets.` | **every clause has a subject and a verb** | for NAR020, `terms` is the subject, and the `Whether` that makes the clause subordinate is ignored | <!-- noqa: NAR020 -->

**The main miss was the review list, not the rules.** 9 of the 10 rows break a rule that is
already in SKILL.md. The **Prose review** steps (SKILL.md line 842: name the subject and verb, name each
noun phrase's referent) would have caught them, but in that run the lists never printed (item 2.1).
So item 2.1 is the first fix.

**Where the check fixes go.** `agentverbs.py` and `checks.py` are byte-identical copies from
narrative-python. A change to either goes into narrative-python first, then `sync_prose.py` copies
it here. Each change below also changes what narrative-python reports on Python code.

### D1. `LITERAL` verbs: exempt only with a direct object and a code subject

Today `LITERAL` (`agentverbs.py:92`) exempts 65 verbs, among them `read`, `write`, `run`, `count` and
`take`, for any subject. Proposal (the feedback's): the exemption applies only when both are true:

- the verb has a direct object, so `reads as the first mode` is not exempt
- the subject is code: a `{@link}` or backticked name, `this`, or a noun such as method, function,
  class, loader or test

Otherwise the pair goes to the review list, not to a finding.

```java
/** {@link PlanLoader} reads the plan file. */                 // exempt: code subject, direct object
/** A saved index out of range reads as the first mode. */     // listed: no direct object
/** The mode that runs {@code recipeMap}. */                   // listed: "mode" is not code
```

Cost: more pairs in the review list on narrative-python code. I have not measured how many.
**Decide:** adopt, adopt with only the direct-object half, or leave as is.

### D2. Connectives `as` and `, where`

R10-period-join names `which` and `since`. Proposal: name `as` and `, where` too, and add a check
that flags:

- a sentence that starts with `As` and has no verb: `As the EBF.`
- `, as in`, and `as <subject> <verb> it`: `as {@link ResolvedRecipe#calculate} works it out`
- `, where` after a noun phrase, in a comment (not in Markdown, where `, where` often introduces
  a definition)

In the rewrite, the fact is stated without `as`:

```java
/** The product is a float, as in the machines' code, so the truncation to whole parallels matches. */
/** The product is truncated to whole parallels. */            // the float claim was false anyway (item 4)

/** As the EBF. */
/** Overclocks by the EBF's heat rule: one extra 4x for every 900 K over the recipe's heat. */
```

(The EBF, Electric Blast Furnace, rewrite is an illustration only. I did not check its heat rule.)
**Decide:** adopt the rule text, the check, both, or neither. The check would get the next free
narrative-python code.

### D3. Pronouns: list, don't flag

spaCy has no coreference resolution (linking `it` to its noun), so a finding on `it` would be a
guess. Proposal: a third review list, every `it`, `its` and `that` used as a pronoun, each with its
sentence and the sentence before it. The review step (name the referent) already exists.
**Decide:** adopt or not.

### D4. NAR020 on a subordinate clause

Proposal: NAR020 also fires when the clause before `, so` is subordinate (it opens with `Whether`,
`If`, `Because` or `When`) and the sentence has no main clause before `, so`. This is a narrow fix
of an existing check. **Decide:** adopt or not.

## 2. Tooling

### 2.1 The prose lists never print on a PR to upstream: confirmed

`skill/verify.py:138-142` returns after the findings and prints the lists only when there are 0
findings. In a PR, upstream lines in the diff always have findings, so the lists never print.
Proposal: with `--since`, always print the lists after the findings. They cover only the changed
lines, so they stay short. Without `--since`, keep today's behaviour, because on GT5 the full list
is about 22,000 comments. **Decide:** adopt or not. This is a tooling fix with no style decision.

### 2.2 Spotless leaves edited javadoc ragged: confirmed, from the formatter config

The GTNH Eclipse formatter config (`gtnhShared/spotless.eclipseformat.xml`, the copy in
`gtnh-determinism/probe-build`) sets `org.eclipse.jdt.core.formatter.join_lines_in_comments` to
`false`. Spotless splits a comment line over 120 columns and never joins short lines. So after an
edit, this stays:

```java
     * The product is
     * a
     * float, as in the machines' code, ...
```

Proposal, both parts:

- SKILL.md, under Layout: "After editing a comment paragraph, re-wrap the whole paragraph to 120
  columns yourself. Spotless splits long lines but never joins short ones."
- A narrative-java check, with the next free NAR1xx code: a comment line in a paragraph where the first word of the
  next line fits on it within 120 columns. It skips `<pre>` blocks, `@` tag lines, list items, and
  a line that ends a sentence.

**Decide:** the doc line, the check, both, or neither.

### 2.3 Speed: no action

In the feedback, a run took 47 to 55 s over 13 to 29 changed files before today's speed work. The
installed skill now takes 17 s for a warm run (cached results, no change since the last run) over all
3,383 files, and 16 s for `--since HEAD~1` over 4 files. That `--since` run had compileJava
`UP-TO-DATE`. A run where the compile step has to run takes longer.

## 3. Rules that conflicted with the code

### D5. NAR140 and `EnumMap` / `EnumSet`

The feedback is right. Both copy constructors depend on the argument's runtime type when it is empty
(JDK javadoc of `EnumMap(Map)` and `EnumSet.copyOf(Collection)`):

```java
Map<Tier, Integer> limits = new HashMap<>();
new EnumMap<>(limits);           // IllegalArgumentException: empty and not an EnumMap
EnumSet.copyOf(new HashSet<Tier>());   // IllegalArgumentException, same reason
```

Typed as `EnumMap`, the field rules that out at compile time. Proposal: set PMD `LooseCoupling`'s
`allowedTypes` property to `java.util.EnumMap` and `java.util.EnumSet`, and add one sentence to the
SKILL.md rule. Also, per SKILL.md line 206, NAR140 covers "a concrete collection in a signature", but
PMD's LooseCoupling covers fields and locals too. Change the text to say so. **Decide:** adopt or not.

### D6. NAR142 and degrade-and-report

A test that runs each machine and logs every failure follows the **Degrade and report** rule
(J1-P25). The machine code is GT's, so its exceptions cannot be listed in the test:

```java
for (MTEMultiBlockBase machine : machines) {
    try {
        checkConformance(machine);
    } catch (RuntimeException exception) {    // noqa: NAR142, degrade and report
        failures.add(machine.getLocalName() + ": " + exception);
    }
}
```

Two problems in SKILL.md:

- Per line 329, NAR142 covers `Exception`, `Throwable` and `Error`. PMD's
  `AvoidCatchingGenericException` covers `RuntimeException` and `NullPointerException` too.
- The rule names one exception (`NoClassDefFoundError` at the optional-mod boundary) but not this
  one.

Proposal: list all five types, and name `catch (RuntimeException)` in a degrade-and-report loop over
code from another mod as the second allowed case, with a `noqa`. **Decide:** adopt or not.

### D7. NAR106 and a sealed abstract class with shared fields

`ModifierKind` is `abstract sealed`, with 7 fields shared by `IntKind` and `LongKind`. With an
interface, both records or classes repeat the 7 fields. You kept the class. Options:

- A: exempt `abstract sealed` classes in the XPath: `[not(@Sealed = true())]`
- B: keep NAR106 as is. A kept class gets a `noqa: NAR106` and a reason

**Decide:** A or B.

### D8. NAR130 and upstream naming

GT5's `MultiblockTooltipBuilder` has `private final String TT_machineType`, `TT_StaticParallels`
and others. Checkstyle's MemberName flags each new `TT_*` field. SKILL.md has no rule for this case.
Proposal: one line under **In a PR to another project**: "A new name follows the convention of the
names beside it in the upstream file. Mark it `noqa: NAR130`." **Decide:** adopt or not.

## 4. Outside a linter's reach

The false float claim already breaks **A javadoc is about its class alone** (R9-02): the claim was
about the machines' code. Prose review step 3 (check the claim on every path) would also have
caught it. No new rule is needed. Item 2.1 makes the review list appear, and D2's `as in` check would
have pointed at this sentence.

## Rulings and status (2026-10-17)

| item | ruling | status |
|---|---|---|
| D1 `LITERAL` narrowing | the full proposal, after the data below | `reviewPairs()` lists a `LITERAL` verb unless it has a direct object and a code subject (R11-literal-review) |
| D2 `as`, `, where` | yes | `NAR021` in narrative-python `agentverbs.py`, rule text in the SKILL.md of each repo (R11-connective-as-where) |
| D3 pronoun list | yes | `agentverbs.py --pronouns`, the third list of both `verify.py` scripts and of `javachecks.py --prose` (R11-pronoun-list) |
| D4 NAR020 subordinate | yes | `fragments()` counts a clause opened by a word on `SUBORDINATORS` (R11-nar020-subordinate) |
| 2.1 lists with findings | yes | with `--since`, `verify.py` prints the lists after the findings (J1-F01) |
| 2.2 ragged javadoc | yes | SKILL.md Layout rule and `NAR125` in `javachecks.py` (J1-F02) |
| D5 `EnumMap`, `EnumSet` | yes | LooseCoupling `allowedTypes`, SKILL.md and tooling.md (J1-F03) |
| D6 degrade-and-report catch | yes | SKILL.md names the second exception and the five types (J1-F04) |
| D7 sealed abstract class | yes, read as option A | the NAR106 XPath leaves out `sealed` (J1-F05) |
| D8 upstream names | ask the user in these cases | SKILL.md: ask before a name that follows an upstream convention `NAR130` rejects (J1-F06) |

Of the rejected sentences of item 1, all but one now get a finding or a review-list line. The one
is `A saved index out of range reads as the first mode.`: the parse makes `range reads` a noun
phrase, so no subject and verb come out. The shorter `A saved index reads as the first mode.` is
listed.

## D1 data: what the `LITERAL` narrowing would move to the review list

Method: every comment and javadoc passage of four corpora, parsed by `agentverbs.py`. A pair is a
subject that cannot act with a verb on `LITERAL` (leaving out `be`, `have`, `will`). Today none of
these pairs is listed or flagged. Under the D1 proposal, a pair stays exempt only with a direct object
and a code subject (`{@link}` or backticked name, an identifier, `this`, or a noun such as method,
class, test, loader). Every other pair would go to the review list, not to a finding. The script is
in the session scratchpad, not in the skill.

| corpus | passages | pairs | full proposal | no-object half only | `read`/`write`/`run` only |
|---|---|---|---|---|---|
| narrative-python `skill/*.py` | 270 | 62 | 49 | 31 | 10 |
| narrative-java scripts | 126 | 26 | 16 | 7 | 0 |
| PlanNH `src` | 1520 | 383 | 366 | 166 | 131 |
| GT5-Unofficial, 400 random files | 2228 | 118 | 96 | 39 | 22 |

So the full proposal adds about 24 review lines per 100 passages in PlanNH, and 4 per 100 in GT5.
Under `--since`, only the changed lines count.

Sentences on the review list under the full proposal, picked at random:

```text
the spec runs it at its fixed cost                          (spec runs)       GT5, the processingspec PR
The kinds the function reads                                (function reads)  GT5, the processingspec PR
if the inputs lack a kind the spec reads                    (spec reads)      GT5, the processingspec PR
The settings the engine reads, clamped the same way …       (engine reads)    PlanNH
Commits a point the way the chain reads it                  (chain reads)     PlanNH
a node's settings receive the recipe and the node           (settings receive) PlanNH
the layout runs while the chart is on screen                (layout runs)     PlanNH
We do this even when the recipe fails, …                    (recipe fails)    GT5
This setter also runs on the client when the value is synced (setter runs)    GT5
so a pass means every check ran                             (pass means)      narrative-java
For a pure deletion, the line after it counts as changed.   (it counts)       narrative-java
On second call, it contains correct text to update …        (it contains)     GT5
```

The first six look like the rejected rows (`The machine's spec inputs read the value`, `The mode that
runs {@code recipeMap}`). The last six are ordinary uses that a reader would pass. The narrower
variants in the table cut the volume, but both kinds remain in each:

- **no-object half only**: lists `A saved index out of range reads as the first mode` and `the
  recipe fails`. It drops `the spec runs it` and `the mode that runs recipeMap`, which have objects.
- **`read`/`write`/`run` only**: lists `the spec runs it`, `the engine reads`, `the layout runs`,
  `this setter also runs on the client`.

**Decide:** the full proposal, a narrower variant, or no change. Any of them adds review lines, not
findings.
