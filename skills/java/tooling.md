# Tooling: what enforces what

Every check here was tested against two fixtures, one that breaks the rule and one that does not, in
`lang/java/tests/fixtures/` of the narrative repository:
`python3 lang/java/tests/run_fixtures.py --gradle <gradle>`.
**Enabling a rule does not make it fire. Test it.**

Tested with JDK 25, Gradle 9.4.0, PMD 7.28.0, Checkstyle 13.5.0, spotless 8.3.0 with Eclipse 4.19 and
the GTNH formatter config, and the shared lint venv (Python 3.11, spaCy 3.8.16 with
`en_core_web_md` 3.8.0). End to end on PlanNH `origin/dev` under GTNHGradle and RFG.

## Environments

Use **uv** for the lint venv. Every language skill has the same `requirements-lock.txt`, so the Java
and Python skills run in one venv. (R10-uv)

`wording.py`, `agentverbs.py`, `prose.py`, `words.json` and `requirements-lock.txt` are in `core/tools/`
of the narrative repository, and `build_skills.py` copies them into `skills/java/`. Change them in
`core/tools/`, then run `python3 build_skills.py`. `build_skills.py --check` exits 1 when a file in
`skills/` differs from the source.

## The split

| Layer | Job |
|---|---|
| spotless | all whitespace and line breaking, with the GTNH Eclipse config of the project |
| javac `-Xlint:rawtypes,unchecked` | raw types and unchecked operations (`NAR121`) |
| Checkstyle | naming (`NAR130`) and the parameter limit (`NAR131`), with `checkstyle.xml` |
| PMD | the structural checks, as XPath rules in `pmd-ruleset.xml`, plus four built-in rules |
| `javachecks.py` | comments and javadoc with a lexer, the prose checks, the checks on comments (`NAR118` to `NAR120`, `NAR125`), the comment and javadoc lookups of `NAR110`, `NAR116` and `NAR117`, then noqa and `--since` over every finding. With `--rewrap`, `javachecks.py` re-wraps comments in place instead. `verify.py` runs the re-wrap before Gradle unless `--no-fix` is given |
| `codeprose.py` | the lexer that reads Java comments and javadoc into passages for the prose checks |
| `wording.py`, `agentverbs.py`, `prose.py` | the prose checks of every language: `NAR012` to `NAR018`, and `NAR020` to `NAR022` |
| `narrative.init.gradle` | the Checkstyle and PMD tasks and the javac flags, added to the build with no project file change |
| `verify.py` | the gate, one Gradle run, then `javachecks.py`, with the toolchain guards |

Run order: spotless, then compileJava, then Checkstyle and PMD, then `javachecks.py`. `verify.py`
runs them in that order, so use `verify.py` rather than reproducing the sequence.

A Markdown, HTML or plain text file named to `verify.py` gets the prose checks only, also when
named beside Java sources. `javachecks.py` runs those checks. In a page, `<!-- noqa: NAR017 -->`
silences a code on the same line.

## The codes

| Code | Rule | Check |
|---|---|---|
| `NAR012` to `NAR016`, `NAR018` | wording in comments and javadoc | `checks.py` |
| `NAR017`, `NAR020`, `NAR021`, `NAR022` | an agent verb on a subject that cannot act, a clause with no subject before `, so`, a clause joined by `as` or `, where`, `it` or `its` after two or more singular nouns in one sentence | `agentverbs.py` |
| `NAR101` | a method above its first caller in the class (J1-P02) | PMD |
| `NAR102` | two or more `null` arguments (J1-P03) | PMD |
| `NAR103` | a stream inside a stream lambda (J1-P06) | PMD |
| `NAR104` | a fully-qualified name outside the imports (J1-P08) | PMD |
| `NAR105` | `ordinal()` in NBT, packet or Gson code (J1-P17) | PMD |
| `NAR106` | an abstract class that is not sealed (J1-P18, J1-F05) | PMD |
| `NAR107` | a `default` arm in a switch over an enum or a sealed type of the project (J1-P19) | PMD |
| `NAR108` | an array component in a record (J1-P22) | PMD |
| `NAR109` | an exception class whose name does not end in `Exception`, or any `Error` subclass (J1-P23) | PMD |
| `NAR110` | a mutable static field with no comment for the reason (J1-P27) | PMD, then `javachecks.py` |
| `NAR111` | `+` or `format()` in a log message (J1-P28) | PMD |
| `NAR112` | `+` in user-facing text (J1-P04) | PMD |
| `NAR113` | literal user-facing text (J1-S15) | PMD |
| `NAR114` | `new` or `.stream()` in a `draw*` or `render*` method (J1-S03) | PMD |
| `NAR115` | a `java.io.File` operation (J1-P14) | PMD |
| `NAR116` | a method with more than 3 parameters or more than 20 body lines and no javadoc (J1-P34) | PMD, then `javachecks.py` |
| `NAR117` | a `throw new X` with no `@throws X` line in the javadoc of such a method (J1-P34) | `javachecks.py` |
| `NAR118` | a top-level type with no javadoc (J1-F3) | `javachecks.py` |
| `NAR119` | a FIXME, as a warning (J1-F4) | `javachecks.py` |
| `NAR120` | a return contract in a `//` comment at the top of a method | `javachecks.py` |
| `NAR121` | a raw-type or unchecked warning of javac (J1-P10) | javac |
| `NAR122` | a type with more than 4 names below the outermost one (NAR005) | PMD |
| `NAR123` | `&&` inside `\|\|` without parentheses (R2b-B4) | PMD |
| `NAR124` | a package-private member in main sources (J1-A02) | PMD |
| `NAR125` | a javadoc line with room for the first word of the next line (J1-F02). `javachecks.py --rewrap` re-wraps the paragraph (J1-F08) | `javachecks.py` |
| `NAR130` | a name outside the Java convention (J1-P01) | Checkstyle |
| `NAR131` | more than 3 parameters (J1-P03) | Checkstyle |
| `NAR140` | a concrete collection type in a signature, a field or a local, except `EnumMap` and `EnumSet` (J1-P11, J1-F03) | PMD LooseCoupling, `allowedTypes` |
| `NAR141` | a field that could be `final` (J1-P21) | PMD ImmutableField |
| `NAR142` | a catch of `Exception`, `RuntimeException`, `NullPointerException`, `Throwable` or `Error` (J1-P24, J1-F04) | PMD AvoidCatchingGenericException |
| `NAR144` | a rethrow that drops the cause (Q21) | PMD PreserveStackTrace |

A PMD rule or a Checkstyle check with no entry in `PMD_CODES` or `CHECKSTYLE_CODES` of
`javachecks.py` is exit 2, so no finding of a new rule is printed without a code.

## The configs

`pmd-ruleset.xml` and `checkstyle.xml` are the configs. Read the files for the settings themselves.
Below is *why* each non-obvious setting is there.

- **SRG and MCP names.** An override of a Minecraft method has names such as `func_145825_b`,
  `field_70170_p` and `p_145827_0_`. They are allowed in the Checkstyle patterns, and ParameterName
  has `ignoreOverridden`.
- **ParameterNumber** has `max = 3` and `ignoreOverriddenMethods`, because the signature of an
  override comes from the platform.
- The **LocalFinalVariableName** pattern has UPPER_SNAKE too, for the local compile-time constants of
  **Constants** in `SKILL.md`.
- **NAR107** has the XPath comment `(: SEALED_TYPES :)`. `verify.py` replaces it with one
  `pmd-java:typeIs()` test per sealed type found in the sources, because XPath has no test for a
  sealed type. The name of a nested sealed type is the file name, a dot and the type name, so a
  sealed type nested two levels deep is not tested.
- **NAR110** has exemptions for `@Mod.Instance`, `@SidedProxy`, loggers, and the fields of a class that is
  annotated `@Config` or whose name ends in `Config` or `Configuration`.
- A type-pattern switch over a type that is not sealed, such as an NEI handler object, needs a
  `default` arm, and `NAR107` leaves the switch alone.

## Caches

Everything below is in `build/narrative/` of the project, and a repeat run skips the covered work.

- `prose-cache.json`: the spaCy results of each comment passage, keyed by the passage text. It is
  discarded when `agentverbs.py`, `words.json`, spaCy or the spaCy model changes. spaCy is loaded
  only for a passage that is not in `prose-cache.json`.
- `checkstyle.cache`, and the incremental cache of the PMD task: the files with no change since the
  last run are not analysed again.
- `javac.log`: the output of the last compile.
- The reports themselves. A Checkstyle or PMD task with no changed input is up to date, and the
  task's report stays valid.

Under `--since`, only the passages on changed lines go to spaCy, Checkstyle and PMD read only the
changed files, and an empty diff is exit 2 before Gradle starts.

## Gotchas

**tree-sitter-java 0.23.5 cannot parse current GTNH code.** Record patterns
(`instanceof Settlement.Stalled(Note reason)`), unnamed variables (`case Foo _, Bar _ ->`) and
annotated varargs (`Object @NotNull... names`) are `ERROR` nodes, in 13 of 221 PlanNH files. Its
last grammar commit was in December 2024. So comments come from a lexer in `javachecks.py`, and the
syntax checks are PMD rules.

**The default PMD of the Gradle pmd plugin is too old.** Gradle 9.4 has PMD 7.13.0, and the first PMD
with Java 25 is 7.16.0. PMD 7.28.0 is set in the init script.

**A PMD violation of a method is at the method name.** A violation on a `MethodDeclaration` has the
line of the name as both the first and the last line. `javachecks.py` finds the end of a `NAR116`
method by brace matching, with comments and literals blanked, for `NAR117` and for `--since`.

**A parenthesised union with predicates matched nothing in PMD 7.28.**
`//(MethodCall[@MethodName = 'str'] | ConstructorCall[...])/ArgumentList/StringLiteral` has no
match, while each branch alone has one. Write a flat union of full paths, `//A[...]/B | //C[...]/B`.

**In a rule message, `{}` is read by PMD as a MessageFormat argument**, and every match of the rule
is then an exception in the PMD log. No braces in a message.

**`AvoidCatchingThrowable` is deprecated in PMD 7.28**, for removal in PMD 8. `AvoidCatchingGenericException`
now covers `Throwable` and `Error`, by exact type, so `catch (NoClassDefFoundError)` passes.

**javac with `-XDrawDiagnostics` prints the file name only**, and not the directory, so a warning
is ambiguous in a project with two `Flagged.java` files. The init script uses the standard format, which has the full path.

**compileJava prints no warning when it is up to date.** Incremental compilation is off in the init
script, so a compile covers every file. `verify.py` keeps the output of the last compile as
`javac.log` and reads `javac.log` again while compileJava is up to date.

**In GTNHGradle, the Checkstyle extension is set after an `allprojects` block runs**
(`CodeStyleModule.java`), so a value set there is overwritten. Separate tasks are registered in the
init script, inside `gradle.projectsEvaluated`. A `Checkstyle` task of Gradle has to have `configDirectory`
set.

**The configuration cache is on in GTNH projects.** `verify.py` passes `--no-configuration-cache`.

**spotless wraps a `//` comment over 120 columns**, and a trailing `// noqa: NARxxx` moves to the next
line as `// // noqa: NARxxx`. So a noqa covers every line of the comment block, and the code line
after a whole-line block.

**In `<pre>{@code …}</pre>`, spotless moves each tag to a separate line.** A plain `<pre>` block and
consecutive `//` lines keep their alignment.

**A warning about the JDK `jrt-fs.jar` on the aux classpath is in the PMD output. It is harmless.**
