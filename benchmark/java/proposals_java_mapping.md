# Java rule proposals for narrative-java

Each row below is a Python rule with a different form in Java, or a rule from the PlanNH review checklist or
from the user. Answer by row number: `P07 accept`, `P12 amend: …`, `S03 reject`. A fork (F1 to F4)
is answered with a letter. The recommended letter is marked (rec).

Rows with no change from Python are listed at the end and need no answer. Each answer is recorded
as a `J1-` record in `benchmark/decisions.jsonl`, and no rule is written into `skill/` before its
record exists.

"check" is the enforcement: `jc` = a new check in `javachecks.py`, `PMD` or `CS` (Checkstyle) = an
existing rule, `javac` = a compiler warning, `review` = review judgement.

Rows and forks with a ✓ before the number are answered. The answers are in "Answers so far".

## Answers so far

- F1: A, `isReady()`
- F2: B, checked for boundary and I/O failures. The code for both forms is in `fork_f2_exceptions.md`
- F3: A, every top-level type
- F4: B, a warning with exit 0
- P04: amended. The user: "Please, never use + to concat string in user facing text. Use %s%s if
  you really need to concat stuff"
- P14: amended. The user: "it's generally better to treat paths as objects with operations on them
  rather than strings"
- P31: rejected. The user: "Threads are perfectly fine to use and often very good (say, not
  blocking userspace on GUIs for background work)"
- P31b: added, from the user's example (row below P31)
- S14: added by the user (row in the last table)
- S15: added by the user: "all user facing strings must be hooked in localization code"
- P23: accepted, with the wording made clear: the rule is about the exception class name
- Drops: accepted (`D accept`)
- P30: accepted. The user: "Yes, P30 is great"
- Every other P, A and S row: accepted. The user: "The rest are all accepted"

## Forks

**✓ F1. Predicate names** (Narrative Q12: `readyForScan`, not `isReadyForScan`)
- A (rec): the Java convention, `isReady()`, `hasPower()`, `canExtract()`. Forge, Minecraft, GT and
  Lombok `@Getter` use these names, so the names at a call site match the library calls beside it.
- B: the bare adjective, `ready()`. This is the form of a Lombok getter under
  `@Accessors(fluent = true)`, which PlanNH uses on enum fields.

**✓ F2. Exception classes** (Narrative Q20: subclass `RuntimeError`)
- A (rec): unchecked, `extends RuntimeException`, and every exception that the method throws has a
  `@throws` javadoc line (the NAR004 analog). A checked exception thrown inside a lambda for a JDK
  functional interface, or inside an override of a Minecraft or Forge method, is a compile error
  unless it is caught there. The code for each call site is in `fork_f2_exceptions.md`.
- B: checked for boundary and I/O failures, so a call site without a `try` or a `throws` clause
  for one is a compile error (the second principle). Unchecked for everything else.

**✓ F3. Javadoc on types** (Narrative R5-02, NAR009: every module opens with a docstring)
- A (rec): every top-level type has a javadoc of at least one sentence, about what the type is for.
  The javadoc of a class with `main` (a dev tool) also has usage and exit codes.
- B: only `public` types that another package uses.
- C: no javadoc requirement on types. Methods follow P34.

**✓ F4. FIXME** (Narrative NAR010: a FIXME in reachable code blocks the merge)
- A (rec): a FIXME is a finding, exit 1. A mod has no `main`, so every method counts as reachable.
  Under `--since`, only a FIXME on a line added in the diff is reported.
- B: a FIXME is printed as a warning, exit 0. In the PlanNH review checklist, FIXME and TODO markers are welcome.

## Translations of Python rules

| # | Python rule (ids) | Java proposal | check |
|---|---|---|---|
| ✓ P01 | mixedCase functions, snake_case variables (pylint naming) | standard Java: camelCase methods, fields, locals and parameters. PascalCase types. UPPER_SNAKE constants | CS naming checks |
| ✓ P02 | `main()` first, caller before callee, types last (Q10, R2-10, R3a-03) | in a class: constants, fields, constructors, the entry point (public API or lifecycle handler), then methods in first-call order, nested types last | jc: a method above its first caller |
| ✓ P03 | >3 positional params one per line, keyword-only params do not count (R2b-B1, R5-06) | line breaks are a spotless setting. Java has no keyword arguments, so a call with more than 3 positional values, or with a `null` for a skipped argument, is replaced by a builder (`@Builder(toBuilder = true)` where Lombok is present) or a parameter record. `@Override` methods are exempt | CS ParameterNumber, jc: two or more `null` literal arguments |
| ✓ P04 | implicit concatenation, never `"""` for data (Q03) | in user-facing text, never `+`. Put `%s` placeholders in the format string, `%s%s` where two values are joined, and pass the values to the localization call (S15). Outside user-facing text, a long one-line string may use `+`. A text block only for multi-line data. The incidental indent is removed at compile time, but the value still depends on the position of the closing `"""` | jc: `+` on a string passed to a localization or chat call |
| ✓ P05 | py311 floor, vermin (R7-E07-floor) | Java 25 syntax on `jvmDowngrader` or `modern` repos only. No preview features. A JDK API only where GTNHLib has a stub for it | verify exits 2 on any other setting |
| ✓ P06 | nested comprehension → explicit loop (Q07) | one level of `filter` and `map` in a stream. Where a stream lambda would have another stream inside it, write a loop. No streams in a per-frame or draw method | jc |
| ✓ P07 | a name is clear without its module, two functions do not share a name (R9-03, R7-B06) | a static method's name is clear without its class. Overloads only for one operation over different argument types. Interface implementations are exempt | review |
| ✓ P08 | import the class, keep the verb qualified (R3a-08), plus upstream review "no fully-qualified names" | no fully-qualified name in code. Import the type. Call a static method through its class where the call is unclear without the class name (`Math.max`, `Objects.requireNonNull`). Static-import test assertions, and members used on most lines of a file | jc: a qualified name outside the imports |
| ✓ P09 | implementation detail inside the function, tunable at module level (R3a-12) | a primitive or `String` constant that is an implementation detail is a local `final` in the method, in UPPER_SNAKE. It is a compile-time constant, so there is no per-call cost. An object constant such as a `Pattern` is `private static final`, directly above its only method. A value that players or pack makers tune is a field of the Config class | CS LocalFinalVariableName widened to allow UPPER_SNAKE |
| ✓ P10 | annotate everything, an explicit `Any` is visible (R2-11) | no raw types. `Object` in a signature is the visible `Any`. `var` only where the right-hand side names the type | javac `-Xlint:rawtypes,unchecked` |
| ✓ P11 | annotate the true requirement, `Iterable` (Q13) | the narrowest interface the method uses. Never `ArrayList` or `HashMap` in a signature. `SortedMap` where the order matters | PMD LooseCoupling |
| ✓ P12 | `NewType` for domain primitives (Q15) | a one-component record, `record ScanId(int value)`, at boundaries and in code that runs rarely. A named primitive in per-frame code, where each wrapper is an allocation | review |
| ✓ P13 | `X \| None` in the annotation (R2-11, R9-01) | `@Nullable` from the annotation package the file already imports (PlanNH: javax JSR-305), with `@ParametersAreNonnullByDefault` in each `package-info.java`. `Optional` only as a return type | review |
| ✓ P14 | a path is a `Path` from the boundary inward (R3a-10, R10-path-type) | a path is a `java.nio.file.Path` object, never a `String` built with `+` or `/`. Forge returns `java.io.File` (`FMLPreInitializationEvent.getModConfigurationDirectory()`), so call `toPath()` on the `File` as soon as Forge returns it. Use `Files` methods for file operations, not `File` methods: `File.delete()`, `renameTo()` and `mkdirs()` return `false` on failure and `File.listFiles()` returns `null`, while `Files.delete()`, `Files.move()` and `Files.createDirectories()` throw an `IOException` with the cause | jc: a `File` operation call (heuristic) |
| ✓ P15 | money is exact (R10-money-cents, R10-money-decimal) | amounts are exact: `long` for item, fluid and EU counts, never `float` or `double`. `Math.addExact` and `Math.multiplyExact` where overflow is reachable. A rate may be a `double` | review |
| ✓ P16 | pendulum for dates (R10-pendulum, R10-pendulum-boundary) | `java.time` only. Game time is a `long` named `…Ticks`, at 20 ticks per second | review |
| ✓ P17 | `Enum` for closed sets, `.value` at boundaries, no `Literal` or `StrEnum` (R2-08) | `enum` for closed sets. Never write `ordinal()` to NBT, a packet or JSON. Serialise `name()` or an explicit code field | jc: `ordinal()` in NBT, packet or Gson code |
| ✓ P18 | `Protocol`, never `ABC`, composition over inheritance (R2-01) | an `interface` for a seam with two real implementations. No `abstract class` in project code. `extends` only for a class the platform requires, such as Forge `Block`, `Item` and `TileEntity`, MUI2 widgets and GT bases | jc: `abstract class` |
| ✓ P19 | exhaustive `match` with no fallback arm (Q18, R3a-07, R4-03, R7-A06), plus upstream review: put behaviour that differs between types on the type | for an `enum` or `sealed` type, write a `switch` expression with no `default` arm. A missing constant is then a compile error. A `switch` statement over an enum has no exhaustiveness check, so rewrite it as a `switch` expression that returns a value. `EnumMap.get()` returns `null` for a missing key, so an `EnumMap` is not a substitute. Where the behaviour is a property of the constant, such as the amount format of a resource type, write it on the constant, as an abstract method or a constructor argument. Where only one caller needs a mapping, such as a log level for each outcome, the `switch` is in that caller | jc: `default` in a switch over a project enum or sealed type |
| ✓ P20 | parse at one gate into a frozen dataclass (Q02, Q14, Q17) | parse at one gate into a `record`. GTNH gates: `readFromNBT`, packet decode, Gson, config load | review |
| ✓ P21 | `frozen=True` is the default (R8-D11), plus upstream review "a data class is the record" | `record` for data. In other classes, a field is `final` unless code reassigns it | PMD ImmutableField |
| ✓ P22 | a mutable field is a smell, tuple over list | the compact constructor copies a collection component (`List.copyOf`, or Guava `ImmutableList.copyOf`). Never an array component: a record's `equals` and `hashCode` compare arrays by identity | jc: an array component |
| ✓ P23 | the exception class name ends in `Error` (ruff N818) | the name of an exception class ends in `Exception`: `PlanException`, not `PlanError` or `PlanFailure`. Never `Error`, because a `java.lang.Error` subclass means the JVM is unusable. The rule is about the class name, not a variable name | jc |
| ✓ P24 | narrow handling, one `except (A, B)` for one outcome (Q19, R8-D24) | no `catch (Exception)` or `catch (Throwable)`. Multi-catch for one outcome. The exception is `catch (NoClassDefFoundError)` at the optional-mod boundary (A04) | PMD AvoidCatchingGenericException, AvoidCatchingThrowable |
| ✓ P25 | degrade and report, exit nonzero (Q24) | process every item, then log the tally at WARN. The exception from a bad item is caught in the loop, so the game does not crash | review |
| ✓ P26 | the config gate raises on the first bad entry (R8-D25) | a hand-written config gate rejects the first bad entry. Where an out-of-range value is reset and logged by the GTNHLib or Forge config loader, keep that | review |
| ✓ P27 | `global` declared on mutation, NAR001 (R2b-G1, V-03) | a mutable static field (non-`final`, or a `static final` mutable collection) has a comment with the reason, or is an instance field of the object with the same lifetime. Exempt: fields Forge requires (`@Mod.Instance`, `@SidedProxy`, config fields) and loggers | jc |
| ✓ P28 | one stable event name plus structured fields (Q08) | Log4j parameters: `LOG.warn("merge.rejected rejected={} total={}", rejected, total)`. Never `+` or `String.format` in a log call | jc |
| ✓ P29 | `logging.getLogger(__name__)` (R10-nullhandler) | one logger per mod, `LogManager.getLogger(MODID)`. This is the GTNH convention, and the mod name is then on each `latest.log` line | review |
| ✓ P30 | config file, CLI, environment, constants (R3a-02, R2-06) | a value that players or pack makers tune is a field of the mod's Config class (Forge or GTNHLib `@Config`). Where several implementations of a feature trade time for quality, all of them read one setting. For example, the budget of each solver is multiplied by one `solverEffort` setting, with the levels High, Medium and Low. There is no `greedyStepBudget` setting beside an `lpIterationBudget` setting. Third-party log noise is off globally, with a debug setting to turn it on. No environment variables or system properties for behaviour | review |
| ✓ P31 | (rejected) asyncio for I/O (R2-04) | no new threads. Load work early during the mod-loading phases. World and GUI state only on the server or client thread that uses it | jc: `new Thread`, `Executors.` |
| ✓ P31b | asyncio for I/O (R2-04), as the user restated it | run file I/O, a solve, or other work that takes a noticeable time on a worker thread, and pass the result back to the client thread. The client thread never waits for that work | review |
| ✓ P32 | property-based tests (R2-12), plus upstream review "a test of the implementation's output tests nothing" | jqwik where the project already has it, else JUnit 5 `@ParameterizedTest`. Assert a rule. Never re-implement production math in a test | review |
| ✓ P33 | `testSomething` names | tests are found by the `@Test` annotation, so no `test` prefix is needed. The method name is the rule: `runningMachineNeverDisplaysZero` | review |
| ✓ P34 | `Raises:` in the docstring (NAR004, R8-D28) | `@throws` for every exception absent from the `throws` clause. `@param` and `@return` only for a fact absent from the signature. A javadoc is required on a method with more than 3 parameters or more than 20 lines, as in Python | jc |
| ✓ P35 | `# noqa: NARxxx` | `// noqa: NARxxx`, the same syntax in both skills, for a finding from any tool | verify |

## Architecture translations

| # | Python rule (ids) | Java proposal |
|---|---|---|
| ✓ A01 | module, cycle is a wrong cut (R7-A02) | a package. A cycle between packages is a wrong cut. References in both directions between classes of one package are allowed |
| ✓ A02 | underscore-private names (R7-B08) | `private` or `public` only, no package-private (upstream review). Test classes and test methods are exempt: JUnit 5 convention is package-private, and PlanNH follows it |
| ✓ A03 | `__main__.py` lists the modules (R7-A05-entry, R7-B01-map) | the lifecycle handlers of the `@Mod` class call the registration method of each subsystem and contain no other logic |
| ✓ A04 | one module imports a library (R7-D03) | every reference to an optional mod is in one class, called only behind an `isModLoaded` guard, with the mod `compileOnly`, and `NoClassDefFoundError` caught at that boundary only. Common code never references a client-only class (`@SideOnly`, proxies). A mixin only where no API exists, accessor mixins first |
| ✓ A05 | prefer stdlib at equal ergonomics (R7-D02, R7-D02-stdlib) | prefer the JDK and the libraries the pack already ships (Guava, Gson, commons-lang3) to a new library. Reuse library API, and take display conventions from the pack, read in the sources jars under `~/.gradle/caches/modules-2` |
| ✓ A06 | push over poll (R7-E07) | subscribe to a Forge event instead of polling every tick |
| ✓ A07 | one exhaustive `match`, not registration decorators (R7-A06) | the same, through P19. Forge registries are framework registration and exempt |

## Rules from the PlanNH review checklist and from the user

These have no Python counterpart. The PlanNH-only parts of the PlanNH review checklist are for PlanNH memory.

| # | Rule | check |
|---|---|---|
| ✓ S01 | deterministic order is a property of the field: declare `SortedMap`, build a `TreeMap`, never sort where the map is read. Gson rebuilds a `SortedMap` field as a `TreeMap`, and a plain non-`String`-keyed `Map` as an insertion-ordered `LinkedTreeMap`. A comparator that defines a canonical key is allowed | review |
| ✓ S02 | a draw or render method writes no serialized state | review |
| ✓ S03 | no allocation in a per-frame or draw method. Reuse buffers and primitive containers. On a wrap or measure path, an identity-keyed cache (`if (source == wrappedFor) return;`) with a dirty flag at the source | jc: `new` inside `draw*` or `render*` (heuristic) |
| ✓ S04 | optional instrumentation is called through an interface. The implementation for "off" is a no-op that allocates nothing | review |
| ✓ S05 | a point query is answered without a scan of the whole collection. First look for an invariant that removes the query, and add an index only if the query is still needed | review |
| ✓ S06 | a simple behaviour plus an invariant, in place of a clever prioritisation policy | review |
| ✓ S07 | reuse a type the codebase already has for the same thing, instead of a new type with the same fields | review |
| ✓ S08 | no hardcoded fix in your mod for a bug in another mod. Report the bug to that mod | review |
| ✓ S09 | keybinds are configurable. Register them through NEI where NEI has an API for it | review |
| ✓ S10 | NEI-style lookup and hover only on sprite-like surfaces (item stacks, pins), never on text rows | review |
| ✓ S11 | colours through the colour API of the GUI library (MUI2 `Color`), not bit arithmetic or hex literals | review |
| ✓ S12 | never merge a test that fails. Raise the budget or disable the test explicitly, and say which in the PR | review |
| ✓ S13 | no bootstrap or loader that can be imported only from the test source set. Put the entry point in the main source set, so any source set can import it | review |
| ✓ S14 | (the user's rule) no production change for a test. No test-only field or variable in a production class. A test reads private state through reflection, not through a new accessor, unless the accessor is worth adding for other code | review |
| ✓ S15 | (the user's rule) every user-facing string is a key in the lang file (`assets/<modid>/lang/en_US.lang`), read through a localization call: `StatCollector.translateToLocal(key)`, `StatCollector.translateToLocalFormatted(key, values)`, `ChatComponentTranslation`, or MUI2 `IKey.lang(key)`. No literal user-facing text in code, so not `IKey.str("Machines")` and not `new ChatComponentText("Done")` | jc: a string literal with letters passed to `IKey.str`, `ChatComponentText`, `drawString` or a tooltip list (heuristic) |

## ✓ Drops

One answer for the whole list (`D accept`), or name the rows to keep.

- `from __future__`, import order, 120 columns, quote style, collection literal layout: all of
  them are spotless settings
- an enum-valued constant only after its Enum (R4-03): javac rejects an illegal forward reference
- no merge of branches where the merged branch has no type narrowing (R2b-B5): javac rejects the
  merged pattern binding
- restate the type where a name shadows an import (R8-B06-Q11): Java imports types, not modules
- attributes set only in `__init__`, `hasattr` (Q04): Java requires a declaration for every field
- DB-API `NamedTuple` rows, Pydantic, output validation, ORMs (R10-namedtuple-rows, R8-D10,
  R10-pydantic, R10-orm-validation): a mod has no database or web framework
- JSONL logs, the field formatter, NullHandler (R5-03, R5-09, R8-D23): the log format is set by
  Minecraft, not by the mod
- `asyncio.TaskGroup`, `except TimeoutError` (R10-taskgroup-scope, R3a-06): replaced by P31b
- tests in a separate module: `src/test/java` already
- `__all__` and `__init__.py`, `__main__.py`, one lock file per repo, a logs module (R7-B05,
  R7-B09, R7-D06, R7-E02): no Java counterpart
- the column-0 docstring trick for `ruff format` (NAR011): replaced by the result of the spotless
  spike on `<pre>` samples

## Unchanged rules (no answer needed)

The two principles. Constants grouped by concern. Blank-line rules. `reject*()` helpers. Version
comments on runtime guards. Guard clauses and the positive skip guard. Extraction, 5+ parameters
as a missing owner, and collapsing duplicated code. Parentheses in mixed `&&`/`||`. Spelled-out
names, verb-first names, no restated domain types, informative names for generic types, `raw`
prefixes. Named magic numbers. The annotation-complexity count (NAR005). A record has only what the
input had. The schemaless remainder. `throw new XException(message, cause)` and log it. Expected
form in error messages, one log per raise site, aggregate logs in degrade loops, levels by operator
action, LBYL. Real dependencies in tests. Every docstring rule except P34 and F3. Every comment rule
(R10-*), with Java examples. Every architecture rule not in A01 to A07.
