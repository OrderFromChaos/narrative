# Toolchain spikes

Run on 2026-10-17. All work was in the session scratchpad. PlanNH and GT5-Unofficial were read
only.

## 1. tree-sitter-java: fails on current GTNH code

tree-sitter 0.26.0 with tree-sitter-java 0.23.5 (the newest on PyPI, released 2024-12-21, with no
grammar commit since) parsed every `.java` file below `PlanNH/src` and `all-gtnh/GT5-Unofficial/src`.

| repo | files | files with an `ERROR` or `MISSING` node |
|---|---|---|
| PlanNH | 221 | 13 |
| GT5-Unofficial | 3475 | 1 |

Constructs that fail:

```java
settlement instanceof Settlement.Stalled(Note reason) ? reason.describe() : null    // record pattern, Java 21
case Line.Text(String key) -> new TextRow(IKey.lang(key), PlannhColors.SUMMARY_TEXT.getColor());
case NEIAEShapedRecipeHandler _, NEIAEShapelessRecipeHandler _ -> "ae2:molecular_assembler";    // unnamed variable, Java 22
public @NotNull IItemContainer registerOre(Object @NotNull... aOreNames) {    // annotated varargs
```

Result: the plan fallback applies. A hand-written lexer extracts comments, and the syntax checks are
PMD XPath rules.

## 2. PMD 7: parses Java 25 and resolves enum types

PMD 7.16.0 (2025-07-25) is the first release with Java 25 support. PMD 7.28.0 (2026-09-25) ran with
`--use-version java-25` over `PlanNH/src/main/java`, with `PlanNH/build/classes/java/main` and
`build/rfg/recompiled_minecraft-1.7.10.jar` as the aux classpath: 0 parse errors, including every
file that failed in spike 1.

With this XPath rule, the PMD report had 4 `default` arms in switches over an enum
(`CanvasWidget.java:790, 827`, `SummaryHeader.java:69, 81`):

```xml
//(SwitchStatement | SwitchExpression)
  [*[1][pmd-java:typeIs('java.lang.Enum')]]
  /*/SwitchLabel[@Default = true()]
```

PlanNH has 31 `default` arms in all. The other 27 are in type-pattern switches over NEI handler
objects (22) and in switches over strings, where `default` is needed.

XPath has no test for a `sealed` type. The sealed types of a project can be listed by a search of
its sources, and verify.py can then add one `pmd-java:typeIs('<name>')` test per type to a generated
ruleset.

## 3. jvmDowngrader: an exhaustive enum switch is safe

`Preference.measure()` in PlanNH (`data/flowchart/balancer/alternatives/Preference.java:106-110`) is
a `switch` expression over an enum with no `default` arm. In the built jar
(`build/libs/plannh-0.1.6-UI-HACKS-fix-group-drop-crash.12+a0896df06a-dirty.jar`), `javap -v` shows:

- in the Java 8 class: `new xyz/wagyourtail/jvmdg/j21/stub/java_base/J_L_MatchException`
- in `META-INF/versions/21/`: `new java/lang/MatchException`

The stub class is in `jvmdowngrader-java-api` 1.3.5, 1.3.6 and 2.0.1 (`downgraded-8` jars) in the
Gradle cache. That GTNHLib puts it on the run-time classpath of a pack is from the PlanNH memory
`plannh-targets-gtnh-nightly`, and not checked here.

## 4. spotless: `<pre>` samples survive, a long comment wraps

spotless 8.3.0 with `eclipse('4.19')` and the GTNH `spotless.eclipseformat.xml` and
`spotless.importorder` from `ExampleMod1.7.10/gtnhShared`, in a standalone Gradle 9.4.0 project.
The diff after `spotlessApply`:

```diff
- * <pre>{@code
+ * <pre>
+ * {@code
...
- * }</pre>
+ * }
+ * </pre>
...
-        // each machine needs a programmed circuit and a spare circuit, so the circuit count is twice the machine count // noqa: NAR017
+        // each machine needs a programmed circuit and a spare circuit, so the circuit count is twice the machine count
+        // // noqa: NAR017
```

- A plain `<pre>` table with aligned columns is unchanged.
- The lines inside `<pre>{@code …}</pre>` are unchanged. Only the tags move, each to a separate line.
- Consecutive `//` lines with one regex sample each are unchanged.
- A `//` comment over 120 columns wraps, and a trailing `// noqa: NARxxx` moves to the next line.
  So in narrative-java a noqa silences every line of its comment block.

## 5. Gradle init script, and verify.py end to end on PlanNH

Run on a scratch clone of PlanNH with `build/rfg` copied in, `nice -n 19`, `--max-workers 1`.

- At `680b151` (branch `fix-group-drop-crash`), compileJava fails before any narrative check:
  `PlanAPI.java:61: error: incompatible types: ItemStack cannot be converted to NBTTagCompound`. The
  output of verify.py is `gradle failed: :compileJava`, with exit 1.
- At `origin/dev` (`e406734`), with no `--since`: spotless, compileJava, narrativeCheckstyle and
  narrativePmd ran under GTNHGradle, and the javachecks.py output had 1682 findings over 225 files. `git status`
  in the clone was clean afterwards, so no project file changed.
- At `origin/dev`, with one method and one comment added to `data/MachineProfile.java` and one untracked
  file, the output of `--since origin/dev` had the 4 planted findings and no other (NAR017, NAR104 on the
  changed lines, NAR118 and NAR124 in the new file).
- Exit 2: `--since origin/dev` with no change ("no line changed since origin/dev"), `--since nosuchref`,
  `enableModernJavaSyntax = jabel`, `enableModernJavaSyntax = true`, and `--venv /nonexistent`.
- Each run took 34 s to 1 min. The estimate was 10 to 15 minutes for a fresh clone. The copied
  `build/rfg` saved the RFG setup.

- A missing JDK, with `-Dorg.gradle.java.installations.auto-detect=false` and
  `-Dorg.gradle.java.installations.auto-download=false`: exit 2, with the Gradle message
  "Cannot find a Java installation on your machine".

## 6. PMD version to pin

7.28.0, from spike 2.
