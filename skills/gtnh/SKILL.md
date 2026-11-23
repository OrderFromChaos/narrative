---
name: gtnh
description: Write or review Java in the Narrative house style for GTNH (GregTech New Horizons) Minecraft 1.7.10 mods, on Java 25 with jvmDowngrader, on jabel and on Java 8. Covers caller-before-callee order, records for data, an exhaustive switch with no default arm, checked exceptions at boundaries, localized user-facing text, no allocation per frame, the comment and javadoc rules of nar:core with their NLP checks, and a verified spotless/javac/Checkstyle/PMD toolchain with a --since mode for upstream PRs. Also multi-package architecture and optional-mod containment. Use for any Java written in or for a GTNH mod, when planning a change, and when reviewing a Java diff against this style. For Python files in the same repository, load nar:python too, or load nar:code in place of both. Always load nar:core with this skill: nar:core has the rules for comments, javadoc and error messages.
---
**Before you write or review anything, load the skills `nar:core` and `nar:repo` with the Skill
tool**, unless they are loaded already. `nar:core` has the rules for comments, javadoc, error messages,
and pages, and the steps of **Writing a comment** and **Prose review** that **Procedures** names.
`nar:repo` has the scope of a change in a code repository.


# Narrative Java

**0% of reader effort on rote diffing, 100% on design.** (R2b-P0) Every rule below is a case of
that, or of the second principle, to prefer what the type checker and IDE can follow.

Four near-identical lines that differ in one token make the reader compare them token by token, and
every comparison is a chance to miss the difference. One parameterised call removes the comparison.

This is the root of DRY, of one-name-for-one-thing, of consistent ordering, and of the ban on
gratuitous variation. When two rules conflict, follow the rule under which the reader diffs less.

Second principle, for representation choices: **prefer what the type checker and IDE can follow**,
even when a looser form is more flexible. The type checker here is javac. (R3-P2-rank)

**The steps, in short. The details are in Procedures, the last section.** (R11-steps-summary)
1. Load `nar:core` and this skill before you plan a change, not only before you edit.
2. Make a batch of edits, then run `verify.py` once for the batch.
3. Read the findings and the review lists of that run. Do not filter the output with `grep`, `head`, or
   `tail`.
4. Fix every finding and answer every list entry from that one run, then run `verify.py` once more.
5. In the report, say how many entries of each list you read, such as `read 212 of 212 sentences`.

**This document applies to every file, however many there are.** `architecture.md` adds what happens
**between** packages: which package may use which, where a shared type belongs, when one class
becomes several, and how a mod contains an optional mod. Read it when the change spans more than one
package or touches another mod. `tooling.md` has the job of each tool and the defaults that break a
rule here. Read it before you change a config.

The reason for each rule is in the rule's text, so read the rule and not the id after the rule. The
ids are provenance. They resolve in `benchmark/decisions.jsonl` in the source repository,
`github.com/OrderFromChaos/narrative`. That repository does not ship with the skill. **A rule without an id or a check behind the rule does not belong here.**

## Scope

narrative-gtnh checks GTNHGradle projects at three Java levels. `verify.py` takes the level from
`enableModernJavaSyntax` in `gradle.properties`, with the values of GTNHGradle, and prints the level
on the `level` line of each run. (J1-levels)

| level | `enableModernJavaSyntax` | toolchain | syntax | library |
|---|---|---|---|---|
| Java 25 | `jvmDowngrader`, `modern` | 25 | Java 25 | Java 25, where the GTNHLib stubs of jvmDowngrader cover the API |
| jabel | `jabel`, `true` | 17 | Java 17, with `@Desugar` on a record, and no sealed types | Java 8, with `--release 8` |
| Java 8 | `false`, or no value | 8 | Java 8 | Java 8 |

`true` and `false` match with any case. `verify.py` exits 2 on any other value, and on a
`forceToolchainVersion` other than `-1` or the toolchain of the level. javac runs on the toolchain of
the project, so a call to a method that the library of the level does not have is a compile error.
Checkstyle and PMD run on a JDK 25 at every level.

- Don't use preview features.
- A comment on a guard for a runtime newer than the floor names the version:
  `// on Java 21 and later, Thread.ofVirtual() is available`. (R10-version-guard)

### Rules by level

Every rule and every check applies at every level, except these. Where a rule below has a record,
`List.copyOf`, or a `switch` expression, use the form of the level.

- **A record.** In a Java 25 build, write a record. In a jabel build, write a record with `@Desugar`
  (`com.github.bsideup.jabel.Desugar`). The Jabel of GTNH compiles that record for Java 8, and a record
  with no `@Desugar` does not compile. In a Java 8 build, write a final class with private final fields, one constructor
  and `getName()` getters, with `equals()` and `hashCode()` when code compares two instances. `NAR108`
  can fire only on a record. (J1-P21-levels)
- **`List.copyOf`.** In a jabel or Java 8 build, write Guava `ImmutableList.copyOf`, and `ImmutableSet.copyOf` or
  `ImmutableMap.copyOf` for the other collections. (J1-P21-levels)
- **A `switch` over an enum.** In a Java 25 or jabel build, write a `switch` expression without a `default` arm. javac
  rejects a missing constant at both levels. Java 8 doesn't have a `switch` expression. Put the behaviour on
  the constant, where javac checks every constant. Where only one caller needs a mapping, write a
  `switch` statement with a case for every constant, no `default` arm, and a throw after the switch.
  `NAR107` flags a `default` arm at every level. (J1-P19-java8)
- **A sealed type.** Java 25 only. So the `sealed abstract class` exception of `NAR106` and the sealed
  types of `NAR107` are Java 25 only. (J1-levels)
- **A pattern in a `switch`, and a record pattern.** Java 25 only. jabel: an `instanceof` pattern in
  an `if` chain. Java 8: `instanceof` and a cast. (J1-levels)
- **`var`, a text block and an `instanceof` pattern.** Java 25 and jabel only. (J1-levels)
## Class layout

```java
package com.example.planner.data;

import java.nio.file.Path;                           // import order and groups are a spotless setting
import java.util.List;

/** Read plan files from the config directory of the mod. */
public final class PlanFiles {

    public static final String PLAN_SUFFIX = ".plan";   // constants first, grouped BY CONCERN
    public static final int MAX_PLANS = 64;

    private final Path planDir;                       // then fields, then constructors

    public PlanFiles(Path planDir) {
        this.planDir = planDir;
    }

    public List<Plan> readAll() throws PlanException {  // the entry point, then callees in
        ...                                           // first-call order
    }

    private Plan readOne(Path planPath) throws PlanException { ... }

    /** One plan file, parsed. */
    public record Plan(String name, int machineCount) {}  // nested types LAST
}
```

- **Caller before callee.** A method this class calls goes below the method's first caller. The
  entry point of the class is first: the public API, or the lifecycle handler. Nested types are
  last. `NAR101` flags a method above the method's first caller in the class. (J1-P02, Q10, R2-10)

- Order constants by concern. Constants a developer would look for at the same moment go together.
  No blank lines inside the block. (R3a-16, R3a-15)

- Layout is a spotless setting. Lines are broken at 120 columns by the GTNH Eclipse formatter, with
  each call of a chain after the first on a separate line. Do not fight it. (J1-D01)

- **Re-wrap with `verify.py`.** Spotless splits a comment line over 120 columns but never joins
  short lines, so after an edit the line breaks of the first draft remain: `The product is` / `a` /
  `float, …`. Before Gradle runs, `verify.py` fills each paragraph of the javadoc and the whole-line
  `//` comments up to column 120 of the line, so spotless doesn't split a line. When `--no-fix` is
  given, `NAR125` flags each paragraph that the re-wrap would change, and `javachecks.py --rewrap` on the file
  re-wraps each such paragraph. (R11-rewrap-fill)

- Separate logically self-contained blocks inside a method with **one blank line**. That is its only
  meaning here. Short guards written as a group stay grouped. (R3a-01)

  **The tools don't check this.** Place a blank line by these five rules: (`R8-NAR008`, `R8-NAR008-rule`)

  - a body of **8 lines or under doesn't take an internal blank**
  - blanks **recur into nested blocks**, and one loop body can take four
  - **a multi-line statement and the statement that consumes the result are
    one step**, so a builder chain then the `return` of the chain stay adjacent
  - a blank precedes a `return` when the phase before the `return` is unrelated, and not when the
    returned value was just built
  - **length is not the trigger**, in either direction

- If a guard grows to three lines because it logs before throwing, move the log call into a
  `reject*()` helper that logs and returns the exception. The guards are two lines again and group:
  `throw rejectLine(raw_line, "no machine count");` (R4-05)

- **Java doesn't have keyword arguments.** A call with more than 3 positional values, or with a `null` for
  a skipped argument, is replaced by a builder, or by a parameter record. Where Lombok is present,
  use `@Builder(toBuilder = true)`. An `@Override` has the signature of the platform. `NAR131`
  flags a method with more than 3 parameters, and `NAR102` a call with two or more `null` arguments.
  (J1-P03, R2b-B1, R5-06)

- **Long strings.** In user-facing text, never `+` (J1-P04). Outside it, `+` joins a long one-line
  string. A text block is for multi-line data only. The incidental indent of a text block is removed
  at compile time, but the value still depends on the position of the closing `"""`. (J1-P04, Q03)

## Structure inside a method

- Guard clauses and early return over nesting. (Q06)

- **Write a skip guard as the negation of what a valid item is.**
  `if (!nameMatches || Files.isSymbolicLink(path) || !Files.isRegularFile(path)) continue;` →
  `if (!(nameMatches && Files.isRegularFile(path) && !Files.isSymbolicLink(path))) continue;`
  (R10-positive-guard)

- **One level of `filter` and `map` in a stream.** Where a stream lambda would have another stream
  inside the lambda, write a loop. No stream in a per-frame or draw method. `NAR103` flags a stream
  inside a stream lambda. (J1-P06, Q07)

- **Extract a block when you can foresee reusing or testing it separately.** A name for the block
  isn't a reason to extract the block. A one-line helper called once is residue. (R2-09, R2b-E1, R2b-E2)

- If an extracted method would take 5 or more values, that is a **missing owner**. Don't leave
  the code inline. That owner is a **class** when two of it can exist at once, and a final
  utility class with a private constructor and static methods otherwise. A record fits only a group
  of values without methods. If a general name for the group is hard to pick, the
  values are not a real group. (R7-C05-resolved, R7-C05-naming)

- Always collapse duplicated-but-drifting code, even when the shared version takes an extra
  parameter. To localise the difference is the whole point. (R2b-E4)

- Mixed `&&` and `||` parenthesise each group explicitly. Never `a && b || c && d`. `NAR123`
  enforces it. (R2b-B4)

## Naming

- Use the standard Java case:
  - camelCase for methods, fields, locals, and parameters
  - PascalCase for types
  - UPPER_SNAKE for constants

  A local compile-time constant may be UPPER_SNAKE too (under **Constants**). `NAR130`
  enforces it with Checkstyle, and allows the SRG and MCP names of Minecraft (`func_…`, `field_…`,
  `p_…`) of an override. (J1-P01)

- Spell names out. No `cfg`, `idx`, `tmp`. (Q11)

- **A method name starts with a verb, and the verb's object is what the method returns.**
  `parsePlan`, `readManifest`, `computeDeletionCutoff`. `planFrom` and `cutoffFor` break the rule. Record
  accessors and `@Override` methods of the platform are exempt. (R9-03)

- **A static method's name is clear without the method's class**, to a reader who has never opened
  the class. Overloads only for one operation over different argument types. Interface
  implementations are exempt. (J1-P07, R9-03, R7-B06)

  **Length is not the defect.** Where the clear name is the longer one, write the longer one.

- **Predicates take `is`, `has`, or `can`:** `isReady()`, `hasPower()`, `canExtract()`. Forge,
  Minecraft, GT, and Lombok `@Getter` use these names, so a call site reads the same as the library
  calls beside the call site. (J1-F1)

- **Do not restate a domain type in a parameter name:** `RebinConfig rebinConfig` →
  `RebinConfig config`. (Q11)

- **When the type is generic, the parameter name is the only place the thing is named.** `Path`,
  `String`, `int`, and `Object` constrain only a value's shape. `Path path` → `Path policyJsonPath`,
  and `String text` → `String manifestText`.

- **Raw and parsed forms get different names.** Prefix the raw form with `raw`: `String rawAt` from
  the file, `Instant at` once parsed. Never `at` beside `parsed.at()`. (R10-raw-names)

- **No fully-qualified name in code.** Import the type. Call a static method through its class
  where the call is unclear without the class name: `Math.max`, `Objects.requireNonNull`.
  Static-import test assertions, and members used on most lines of a file. `NAR104` flags a
  qualified name outside the imports. Where two types with one simple name are used in one file,
  import the more frequent type, and write the full name of the other type. A qualified name that clashes with an import or
  with a type declared in the file is not a `NAR104` finding. (J1-P08, R3a-08, J1-no-noqa)

## Constants

Name every magic number. (Q09) Then place it by this test:

> Could someone change this value safely knowing only what the program **does**, or would they need
> to understand how the method **works**?

- **An implementation detail is inside the method.** A primitive or `String` constant is a local
  `final`, in UPPER_SNAKE. It is a compile-time constant, so javac inlines the value at each use. An object
  constant, such as a `Pattern`, is `private static final`, directly above the constant's only
  method. (J1-P09, R3a-12)
- **A value that players or pack makers tune is a field of the Config class** (under
  **Configuration**). (J1-P09)
- Constants that a developer changes, and that are not implementation details, stay at the top of
  the class.

*`verify.py` doesn't check where a constant is. This is review judgement.*

## Types

- **No raw types.** `Object` in a signature is the visible form of "any type", so `Object` is
  visible and greppable. `var` only where the right-hand side names the type:
  `var plans = new ArrayList<Plan>()`. `NAR121` reports the raw-type and unchecked warnings of
  javac. (J1-P10, R2-11)

- **Annotate the true requirement.** A parameter has the narrowest interface the method uses:
  - `Iterable`
  - `Collection`
  - `List`
  - `Map`

  Never `ArrayList` or `HashMap` in a signature. `SortedMap`
  where the order matters (under **GTNH**). `NAR140` flags a concrete collection type in a signature,
  a field, or a local. `EnumMap` and `EnumSet` keep their types: `new EnumMap<>(map)` and
  `EnumSet.copyOf(set)` throw on an empty argument of another type. (J1-P11, Q13, J1-F03)

- **Domain primitives.** A one-component record, `record ScanId(int value)`, at boundaries and in
  code that runs rarely, so a bare `int` is a type error. In per-frame code each wrapper is an
  allocation, so there the name of the primitive is the type: `int scanId`. (J1-P12, Q15)

- **Nullability.** `@Nullable` from the annotation package the file already imports (PlanNH: javax
  JSR-305), with `@ParametersAreNonnullByDefault` in each `package-info.java`. `Optional` only as a
  return type. (J1-P13, R9-01)

- **A path is a `java.nio.file.Path` object**, never a `String` built with `+` or `/`. Forge returns
  `java.io.File`, as from `FMLPreInitializationEvent.getModConfigurationDirectory()`, so call
  `toPath()` on the `File` as soon as Forge returns the `File`. Use `Files` methods for file
  operations. `File.delete()`, `renameTo()`, and `mkdirs()` return `false` on
  failure, and `File.listFiles()` returns `null`. `Files.delete()`, `Files.move()`, and
  `Files.createDirectories()` throw an `IOException` with the cause. `NAR115` flags a `File`
  operation. (J1-P14, R3a-10)

- **Amounts are exact.** `long` for item, fluid, and EU counts, never `float` or `double`.
  `Math.addExact` and `Math.multiplyExact` where overflow is reachable. A rate may be a `double`.
  (J1-P15)

- **Time.** `java.time` only. Game time is a `long` named `…Ticks`, at 20 ticks per second.
  (J1-P16)

- **`enum` for closed sets.** Never write `ordinal()` to NBT, a packet or JSON: reordering the
  constants changes every saved world. Serialise `name()`, or an explicit code field. `NAR105` flags
  `ordinal()` in NBT, packet, or Gson code. (J1-P17, R2-08)

- **Composition over inheritance.** An `interface` for a seam with two real implementations. No
  `abstract class` in project code. `extends` only for a class the platform requires: Forge `Block`,
  `Item` and `TileEntity`, MUI2 widgets, GT bases. A `sealed abstract class` is allowed when its
  permitted subclasses share fields: the fields are declared once, in the class. Only Java 25 has
  sealed types. `NAR106` flags every other abstract class. (J1-P18, R2-01, J1-F05, J1-levels)

- **Give a name to a type you cannot say out loud.** Could you refer to this type in a normal
  discussion with another programmer? `Map<String, List<Pair<Float, Float>>>` has five names below
  the outermost one, and above four, give it a name: a record, or a functional interface for a
  callable. `NAR122` counts the names. (NAR005, R8-D27-resolved)

### Exhaustive dispatch with no default arm

```java
private static Level levelOf(Outcome outcome) {
    return switch (outcome) {
        case INGESTED -> Level.INFO;
        case REJECTED -> Level.WARN;
        // no default arm. A new constant of Outcome is then a compile error
    };
}
```

For an `enum` or `sealed` type, write a `switch` expression without a `default` arm. javac then rejects
a missing constant. **A `default ->` arm compiles clean and accepts the missing case.** `NAR107`
flags a `default` arm in a switch over an enum or a sealed type of the project.
(J1-P19, Q18, R3a-07) Java 8 doesn't have a `switch` expression, and the form there is in **Rules by level**
in **Scope**. (J1-P19-java8)

- javac doesn't check that a `switch` **statement** over an enum covers every constant. Rewrite it as a `switch`
  expression that returns a value.
- **Keep the `switch` even where an `EnumMap` looks natural.** `EnumMap.get()` returns `null` for a
  missing key, at run time.
- In a jvmDowngrader build, the synthetic default of an exhaustive `switch` throws a stub
  `MatchException`, and in a jabel build an `IncompatibleClassChangeError`. It is reachable only when a
  newer enum class is loaded than the one compiled against.
- **Where the behaviour is a property of the constant**, such as the amount format of a resource
  type, write the behaviour on the constant, as an abstract method or a constructor argument. javac
  then requires it of every constant, and call sites don't branch on the constant. **Where only one caller needs
  a mapping**, such as a log level for each outcome, the `switch` is in that caller. (J1-P19)
- A type-pattern switch over a type that is not sealed, such as an NEI handler object, needs a
  `default` arm.

## Data at boundaries

- Parse untrusted input into a **record at one boundary gate**, then never validate again. GTNH
  gates: `readFromNBT`, packet decode, Gson, config load. (J1-P20, Q02, Q14)

- **A parsed record contains only what its input contained.** Where one input format has a field and
  another does not, the component is `@Nullable` on the shared record, and the check that reads the
  component skips an absent value. **Never substitute a plausible default**, because the output then
  contains a fact that the file does not. (R9-01)

- **A record is the default for data.** A class that is just data is the record. Don't wrap a
  nested record in a class. In a jabel or Java 8 build, the record has the form of **Rules by level** in
  **Scope**. In other classes, a field is `final` unless code reassigns the field.
  `NAR141` flags a field that could be final. (J1-P21, R8-D11-resolved)

- **A record is shallowly immutable.** The compact constructor copies a collection component with
  `List.copyOf`, or Guava `ImmutableList.copyOf`, which is the only one on jabel and Java 8. **Never
  an array component:** `equals()` and `hashCode()` of a record compare arrays by identity, so two
  equal plans compare unequal. `NAR108` flags an array component. (J1-P22)

- **Genuinely schemaless input.** Promote the fields the program computes on to typed components,
  and put the remainder in one `JsonObject` or `Map<String, JsonElement>` component. **Never merge
  the remainder into an output object.** An untrusted key with the name of an output field would
  replace that field. Nest the remainder instead. (R4-04)

## Errors

- **Checked for boundary and I/O failures, unchecked for everything else.** A parse error of a file,
  a packet or NBT `extends Exception`, so a call site without a `try` or a `throws` clause doesn't
  compile. A broken invariant `extends RuntimeException`. (J1-F2, Q20)

  A checked exception cannot leave a lambda for a JDK functional interface, or an override of a
  Minecraft or Forge method. Catch it there:

  ```java
  @Override
  public void readFromNBT(NBTTagCompound compound) {
      super.readFromNBT(compound);
      try {
          plan = parsePlan(compound.getString("plan"));
      } catch (PlanException exception) {
          plan = null;
      }
  }
  ```

  An exception that leaves `readFromNBT()` is caught by Forge, which logs "its state cannot be
  restored" and drops the tile entity. A `@Mod.EventHandler` or `@SubscribeEvent` method is not an
  override, so a `throws` clause on the method compiles.

- **The name of an exception class ends in `Exception`:** `PlanError` or `PlanFailure` →
  `PlanException`. Never `Error`, because a `java.lang.Error` subclass means the JVM is unusable.
  `NAR109` enforces both. (J1-P23)

- **Handle each failure mode narrowly and separately.** No `catch (Exception)`,
  `catch (RuntimeException)`, `catch (NullPointerException)`, `catch (Throwable)`, or `catch (Error)`.
  `NAR142` flags them. There are two exceptions. One is `catch (NoClassDefFoundError)` at the
  optional-mod boundary, described in `architecture.md`. The other is `catch (RuntimeException)` in
  a degrade-and-report loop over code from another mod, whose exceptions you cannot list. Write the
  reason in a comment in the catch block, and ask the user whether to keep the finding (the rule
  is under **noqa**):

  ```java
  for (MTEMultiBlockBase machine : machines) {
      try {
          checkConformance(machine);
      } catch (RuntimeException exception) {
          // GT machines throw undeclared unchecked exceptions. Record the failure and check the next machine
          failures.add(machine.getLocalName() + ": " + exception);
      }
  }
  ```

  (J1-P24, Q19, J1-F04, J1-no-noqa)

- **Related means the handling is the same.** A shared base class doesn't make two failures related. Where two failures
  produce one outcome, one multi-catch `catch (A | B exception)` is correct. But check the premise
  first. A timeout and an unreachable host are different facts and deserve different words.
  (R8-D24-resolved)

- `throw new XException(message, cause)`, **and** log it. Both. `NAR144` flags a rethrow that drops
  the cause. (Q21)

- **An error message for malformed input includes the expected form.** `bad count 'twelve' in
  plan.txt (expected a whole number such as 12)`. (R10-expected-form)

- **Log the generic fact once at the raise site, however you factor that.** Route several raise
  sites through a `reject*()` helper that logs and returns the exception. (Q23, R4-02)

- **Where a failure is handled, log what the failure meant there. In a degrade-and-report loop, log
  the aggregate.** Log the item at DEBUG and the tally at WARN. (R4-02)

- **Level follows from what an operator can act on.** A pack maker cannot act on recipe 4,812. A
  pack maker can act on "4,812 of 10,000 recipes rejected". (R4-02)

- LBYL over EAFP. You know your invariants, you do not know every exception an implementation can
  throw. (Q22)

- **Degrade and report.** Process every item, then log the tally at WARN. The exception from a bad
  item is caught in the loop, so the game does not crash. (J1-P25, Q24)

- **The config gate is the exception.** A hand-written config gate rejects the first bad entry,
  because with a half-valid config, what to do is unknown. Where an out-of-range value is reset and
  logged by the GTNHLib or Forge config loader, keep that. (J1-P26, R8-D25-resolved)

## Static state

- **A mutable static field has a comment with the reason**, on the line above or after the field on
  the same line, **or the field is an instance field of the object with the same lifetime.** A
  mutable static field is non-`final`, or a `static final` mutable collection. Fields that Forge
  requires (`@Mod.Instance`, `@SidedProxy`, and config fields) and loggers are exempt. `NAR110` flags
  the rest. (J1-P27, R2b-G1)

## Logging

- **One stable event name plus parameters, never a sentence built with `+`.** The message is a
  queryable key: `LOG.warn("merge.rejected rejected={} total={}", rejected, total)`. No `+` and no
  `String.format` in a log call. They also build the string when the level is off. `NAR111` flags
  them. (J1-P28, Q08)

- **One logger per mod**, `LogManager.getLogger(MODID)`. This is the GTNH convention, and the mod name
  is then on each `latest.log` line. The log format comes from Minecraft. (J1-P29)

## Configuration

- **A value that players or pack makers tune is a field of the mod's Config class**, from Forge
  `Configuration` or GTNHLib `@Config`. Don't write the value as a literal, or as a field of another class. (J1-P30)
- **Where several implementations of a feature trade time for quality, all of them read one
  setting.** For example, the budget of each solver is multiplied by one `solverEffort` setting, with
  the levels High, Medium, and Low. Don't add a `greedyStepBudget` setting beside an
  `lpIterationBudget` setting. (J1-P30)
- Third-party log noise is off globally, with a debug setting to turn the noise on. Don't save and
  restore the log level around each call. (J1-P30)
- Don't read an environment variable or a system property for behaviour. (J1-P30, R3a-02)

## Concurrency

**Run file I/O, a solve, or other work that takes a noticeable time on a worker thread, and pass the
result back to the client thread. The client thread never waits for that work.** World and GUI state
change only on the thread that uses them. (J1-P31b)

```java
CompletableFuture.supplyAsync(() -> computePlan(request))
    .thenAccept(plan -> Minecraft.getMinecraft().func_152344_a(() -> showPlan(plan)));
```

`func_152344_a` is the SRG name of the 1.7.10 method that queues a task for the client thread.

## Testing

- **Real dependencies.** Use a real temp directory with `@TempDir` and a real file. Don't use Mockito. A test
  double is a last resort for something you cannot run. Flag each one as a known gap. Keep logic off
  Minecraft types, so the tests run headless. (R2-02, Q16)

- **Property-based tests wherever there is an invariant**: round-trips, ordering, conservation,
  numeric range. jqwik where the project already has jqwik, else JUnit 5 `@ParameterizedTest` over
  generated cases. **Assert a rule.** `assertEquals("3.12", format(3.12))` repeats
  the implementation's output, and a table of such asserts is not a test of anything. Never re-implement production math
  in a test. (J1-P32, R2-12)
  Give such a test both kinds of case: generated cases, and the boundary values of the invariant, so
  the boundary values are in every run. Generate with jqwik, or with `java.util.Random` and a
  constant seed, so a failing case is the same on the next run. (J1-P36)

- **A test method name is the rule.** Tests are found by the `@Test` annotation, so a `test` prefix
  isn't needed: `runningMachineNeverDisplaysZero()`. (J1-P33)

- **Never merge a test that fails.** If a scenario is aspirational, raise the budget or disable the
  test explicitly, and say which in the PR. (J1-S12)

- **No bootstrap or loader that can be imported only from the test source set.** Put the entry
  point in the main source set, so any source set can import the entry point. (J1-S13)

- **No production change for a test.** No test-only field or variable in a production class. A test
  reads private state through reflection. Add an accessor only when other code uses the
  accessor too. (J1-S14)

- **No test only because a bug was fixed.** Write a regression test when the code under test is
  likely to break the same way again, or when the test checks an invariant of the program. Write the
  case and the expected result in the name and the docstring of the test. Use the present tense.
  (R12-no-changelog-tests)
## GTNH

- **Every user-facing string is a key in the lang file** (`assets/<modid>/lang/en_US.lang`), read
  through a localization call:
  - `StatCollector.translateToLocal(key)`
  - `StatCollector.translateToLocalFormatted(key, values)`
  - `ChatComponentTranslation`
  - MUI2 `IKey.lang(key)`
  - a wrapper of the mod around one of these calls, such as `NEIClientUtils.translate`

  A text call takes the text itself, such as `IKey.str`, `new ChatComponentText`, or `drawString`. Don't
  pass literal user-facing text to a text call. `IKey.str("Machines")`,
  `new ChatComponentText("Done")`, and `drawString("Done", x, y, color)` break the rule. `NAR113-gtnh` flags
  literal text in `IKey.str`, `ChatComponentText`, `drawString`, and a tooltip line of
  `addInformation`. (J1-S15, J1-P04-keys)

- **In user-facing text, never `+`.** Put `%s` placeholders in the lang entry, `%s%s` where two values
  are joined, and pass the values to the localization call. `NAR112-gtnh` flags a `+` in a text call,
  in a localization call, and after a localization call. A wrapper is found by the method name:
  - `translate*`
  - `localize*`
  - `trans`
  - `tr`
  - `i18n`

  (J1-P04, J1-P04-keys)

  ```
  plan.machines=%s machines at %s
  ```

  ```java
  StatCollector.translateToLocalFormatted("plan.machines", count, tierName)
  ```

- **A computed lang key starts with its literal prefix**: `translate("chat.mode." + mode)`. In the key
  argument of a localization call, a `+` is allowed when the key starts with a literal that ends in a
  dot, and a literal of the key doesn't have a space. `translate(name + ".enable")` is a finding, and so is a
  `+` in a text call. (J1-P04-keys)

- **Deterministic order is a property of the field.** Declare `SortedMap`, build a `TreeMap`, and
  never sort where the map is read. Gson rebuilds a `SortedMap` field as a `TreeMap` on load, and a
  plain `Map` with keys that are not `String` as an insertion-ordered `LinkedTreeMap`. A comparator
  that defines a canonical key is allowed. (J1-S01)

- **A draw or render method doesn't write serialized state.** (J1-S02)

- **No allocation in a per-frame or draw method.** Reuse buffers and primitive containers. In a wrap
  or measure path, use an identity-keyed cache, `if (source == wrappedFor) return;`, with a dirty flag
  at the source, so a steady frame doesn't recompute. `NAR114-gtnh` flags `new` and `.stream()` in a
  `draw*` or `render*` method. (J1-S03)

- **Optional instrumentation is called through an interface.** The implementation for "off" is a
  no-op that doesn't allocate. (J1-S04)

- **A point query is answered without a scan of the whole collection.** First search for an invariant
  that removes the query, and add an index only if the query is still needed. (J1-S05)

- **A simple behaviour plus an invariant**, in place of a clever prioritisation policy. (J1-S06)

- **Reuse a type the codebase already has for the same thing**, instead of a new type with the same
  fields. (J1-S07)

- **No hardcoded fix in your mod for a bug in another mod.** Report the bug to that mod. (J1-S08)

- **Keybinds are configurable.** Register them through NEI where NEI has a keybind API. (J1-S09)

- **NEI-style lookup and hover only on sprite-like surfaces**, such as item stacks and pins, never
  on text rows. Players expect it on NEI sprites. (J1-S10)

- **Colours through the colour API of the GUI library**, MUI2 `Color`. Don't use bit arithmetic or
  hex literals. (J1-S11)

## Javadoc

**Every top-level type has a javadoc of at least one sentence, about what the type is for.** A reader
meets the javadoc first, so the javadoc is about what the class is *for*. How the class works is in the
code. The javadoc of a
class with `main`, such as a dev tool, also has a usage example and the exit codes. `NAR118` flags a
top-level type without a javadoc. (J1-F3, R5-02)

**Write for a professional developer who has the file open.** That reader knows Java, Forge, and the
vocabulary of the trade, so `API`, `idempotent`, and `NBT` are the right words. One idea per
sentence. **One word for one thing, and the word is the identifier the code uses.** (R9-09)

The prose rules for comments and javadoc are in **Comments**.

### Samples of output

**Where a class reads or writes concrete text, paste a real sample of that text** in a `<pre>`
block: a tooltip, a chat line, a lang entry, an NEI line, a converted value. **Delete the prose the
sample replaces** rather than keeping both. (R9-08)

**Never invent a sample.** Run the code and paste what it printed. A format that appears nowhere in
the program is a lie in the shape of documentation. **Do not state what you did not observe.**

**Show one line of each shape of the output.** A sample goes stale, and `verify.py` doesn't check the
sample. Keep it small, and re-paste the sample when the output changes.

```java
/**
 * Format a machine count for the tooltip of a plan node.
 *
 * <pre>
 *     MACHINE        COUNT    RATE
 *     Electrolyzer      12    3.5/s
 *     Centrifuge         4    0.25/s
 * </pre>
 *
 * A machine with no rate shows {@code -} in the RATE column.
 */
```

A plain `<pre>` table is unchanged by the GTNH spotless config. In `<pre>{@code …}</pre>`, each tag
is moved to a separate line, and the lines between the tags are unchanged.

A conversion takes a table of cases rather than a sentence per case:

```java
/**
 * Convert an amount with a unit suffix to a count, and back.
 *
 * <pre>
 *     4096    ->           4096
 *     12K     ->          12000
 *     1.5M    ->        1500000
 * </pre>
 */
```

### Javadoc rules

**Most members don't get a javadoc.** Write one for a top-level type (`NAR118`), and for a method by the `NAR116` review list. Any other field, constant or method gets a javadoc only for a fact
that the name, type, value, and signature do not show. A javadoc whose facts are already in the
declaration only costs the reader time. Cut such a javadoc whole. Don't cut the javadoc sentence by sentence. The Java
habit of a javadoc on every public member does not apply here. (J1-F07)

**State each fact once**, on the declaration the fact belongs to. Elsewhere, link to that
declaration. (J1-F07)

```java
public static final int ITEM_PIPE_CASING_TIERS = 8;
public static final int PIPE_CASING_TIERS = 4;

/** @param tier from 1 to {@link #PIPE_CASING_TIERS} */
public static ItemList pipeCasing(int tier) {
```

not

```java
/** How many item pipe casings {@link #chainItemPipeCasings} accepts, numbered from 1. */
public static final int ITEM_PIPE_CASING_TIERS = 8;

/** How many pipe casings there are. {@link #pipeCasing} numbers them from 1. */
public static final int PIPE_CASING_TIERS = 4;
```

A javadoc that is kept starts with a summary sentence. **A body is not required, and usually does
not earn its place.** (R9-09)

**Cut a sentence when any of these is true:**

- **It is visible in the file.** `final` is on the line above. `@Nullable` is in the signature.
- **Its negation would be a bug, an absurdity, or an implementation that a developer wouldn't ship.** Negate the
  sentence and read it back. **Assume the reader expects competent code, and document only the
  departures.**
- **It is a language feature, explained.**
- **It goes stale and the tools don't check it**, unless it is a sample you accept that cost for.

**Compress what survives:**

- **Name the property, do not explain it.** `Rows are keyed on team, total and quota, so runs are
  idempotent`.
- **State an ordering as its sort key.** `Machines sort by (-count, name)`.
- **In the summary, use the real name of what the code produces.**
- **Stop at the fact.** Where a reason has to survive, it is a `//` comment at the line the reason
  concerns.

**A body earns its place for these, and in practice for nothing else:**

- an **ordering or tie-break**, invisible without reading a comparator
- a **unit, a nullability or a provenance** absent from the signature: `Amounts are in litres`
- **where the leftover, default, and failure cases go**
- a **sample** of concrete text the class reads or writes
- a **constraint from outside the program**: `Forge drops a tile entity whose readFromNBT() throws`
- a **guarantee a caller needs**: `` `preview()` doesn't write a file, send a packet, or change a world ``

- **A method gets a javadoc when a reader can't learn from the name of the method and the comments
  of the body what the method does.** Answer one question for each entry of the `NAR116` review
  list of `verify.py`:
  - a method without a javadoc: can a reader learn from the name of the method and the comments of the
    body what the method does? If not, write a javadoc.
  - a javadoc or a comment on a type, a field, an enum constant, or a method: what does a reader learn
    from the javadoc or the comment, and not from the name and the code? If the reader doesn't learn
    more, cut the javadoc or the comment. Keep one sentence on a top-level type (`NAR118`).
  (J1-P34, Q05, R8-D18-resolved, R12-nar116-review)

- **`@throws` for every exception absent from the `throws` clause**, in the javadoc of a method. A checked exception is in the signature already. `NAR117` flags a `throw new X` with no
  `@throws X` line. `@param` and `@return` only for a fact absent from the signature: an ordering, a
  nullability, a unit, or a count whose meaning is not obvious. (J1-P34, R8-D28-resolved)

- Don't write a fact in a javadoc that the code doesn't do, or a consequence that an earlier sentence
  already implies. (Q05)

- **A javadoc is about its class alone.** Do not assert what another class does, do not claim to be
  the only place something happens, and do not count callers. Name another class only where a reader
  of *this* file needs the name to use this file. (R9-02)

- Where semantics vary by implementation (file moves, copies, path manipulation), **show a concrete
  before and after example** in place of prose. (R3a-11)

## Comments in Java

These rules add to **Comments** in `nar:core`. Each heading below is the name that `nar:core` uses
for the rule. A docstring there is a javadoc here, and a localisation file there is a lang file of
the mod here.

### Identifiers

An identifier in javadoc is a link: `{@link #getMachineModes}` or `{@link ExtendedBlockStorage}`.
In an IDE, the reader can jump from the link to the target. When someone renames the target in the
IDE, the link changes with the name. `{@link}` takes a class, a field, a method, or a package. Put a
parameter, a local variable or a value such as `null` in `{@code}`. In a `//` comment, put the name
in backticks. Link to an identifier even when its name is unclear. From the link, the reader can
jump to the code and read what the name stands for. (R11-pointer-wording, J1-F10)

### Library facts

For a fact about vanilla Minecraft or Forge, read the source and check the fact.
(R11-rewrite-from-code)

### Source facts

A fact about a value from vanilla Minecraft, Forge, another mod or an old save, such as a `null`
field or a missing NBT tag, goes above the code for the value (J1-F12):

```java
// worlds saved before 1.2.0 don't have a "tier" tag
final int tier = tag.hasKey("tier") ? tag.getInteger("tier") : 1;
```

### Decoding aids

- `AMOUNT = Pattern.compile(...); // a number, then an optional K, M or G suffix`
- `// Math.fma() for one rounding in a * b + c`
- a regex, with a string the regex matches and one the regex rejects:
  ```java
  // matches:
  // `search_v2`
  // `db-host`
  // rejects:
  // `x.y`
  private static final Pattern BARE_KEY = Pattern.compile("[A-Za-z0-9_-]+");
  ```

(R10-Q42, R10-Q46, R10-regex-sample, R10-regex-literals)

### Fence

- `// Character.isDigit() accepts non-ASCII digits such as '٣'. Check the range '0' to '9' too`
- the `X would` form in full:
  ```java
  // Here Files.readAllBytes() is used. The alternative, Files.readString(), would throw
  // MalformedInputException on a byte that is not UTF-8.
  final byte[] planBytes = Files.readAllBytes(planPath);
  ```

(R10-fence-form, R10-fence-fact, R10-fence-alternative)

### Depth

```java
// The vendor API returns at most 100 rows per page, and doesn't return a total count.
// Keep requesting until a page comes back short.
while ((page = fetchPage(cursor)).size() == PAGE_SIZE) {
```

(R10-depth-example)

### FIXME

`verify.py` prints each `FIXME:` as a warning, `NAR119`, and still exits 0. A mod doesn't have a `main`, so
every method counts as reachable. (J1-F4)

### Return contracts

`NAR120` flags a `// returns …` comment at the top of a method. (R10-return-contract)

### Agent verbs

`draws` is an agent verb for a widget whose drawing is not the point. (J1-verbs-literal)

### noqa

Never write a `noqa` in Java code. This skill is not used upstream, so each `// noqa` in a PR is a
comment that the upstream maintainer must delete.

These cases are exempt from the checks:
- `NAR104` on a qualified name that clashes with an import or with a type declared in the file
- in a Mixin class:
  - `NAR130` on a member with the prefix `modid$`
  - `NAR106` on the abstract Mixin class
  - `NAR131` on an injector method, because the parameter list must match the target method
  - `NAR140` on a `@Shadow`, `@Accessor`, or `@Invoker` member and on an injector signature, because
    each type must be the type in the target class

Keep these findings only when the user approves:
- `NAR142` in a degrade-and-report loop
- `NAR130` on a name in the style of upstream names, such as `TT_parallels`
- `NAR112-gtnh` on a call to a method named `translate*`, `localize*`, `trans`, `tr`, or `i18n` that
  does not localize text

Ask the user about each finding. If the user approves, add the finding to the keep-list:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" --keep src/main/java/com/example/Scan.java:57:NAR142 --reason 'GT machine code'
```

The keep-list is `.git/info/narrative-keep`. Files in `.git/info` are not part of any commit. A
kept finding is not printed, and is counted as `kept` in the last line of the output. When the line
of the finding changes, the finding is printed again. (R11-findings, J1-no-noqa)

### Pages

Name each page to `verify.py`, which then runs the prose checks only, with no Gradle project:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" README.md docs/report.html
```

A page named beside Java sources gets the same checks, in the same list of findings. A run with
pages only doesn't check a Java source, so for a change to code and a page, name both:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" src/main/java README.md
```
(R10-published-prose, J1-F15)

## Procedures

Take these in order. **Setup** happens once per machine. **Writing a comment** applies to each
comment as you write the comment. **Verify** and **Prose review** follow once the code is written.
**Published prose** applies to each page you write, such as a README. (R10-procedures) **Writing a comment**, **Prose review** and **Published prose** are in
`nar:core`.

### Setup

The Java skill uses the same lint venv as the Python skill, one per machine, and the same prose
checks. (R10-setup)

Linux and macOS:

```bash
uv venv --python 3.11 ~/.local/share/narrative/lintenv
uv pip install --python ~/.local/share/narrative/lintenv/bin/python -r "${CLAUDE_SKILL_DIR}/requirements-lock.txt"
```

Windows (PowerShell):

```powershell
uv venv --python 3.11 $env:LOCALAPPDATA\narrative\lintenv
uv pip install --python $env:LOCALAPPDATA\narrative\lintenv\Scripts\python.exe -r "${CLAUDE_SKILL_DIR}/requirements-lock.txt"
```

The JDK of the level (8, 17, or 25) comes from the Gradle toolchain of the project, and a JDK 25 for
Checkstyle and PMD comes from the Gradle toolchains too. PMD 7.28.0 and Checkstyle 13.5.0 come from
Maven Central on the first run. No project file changes.

### Verify

Run `verify.py` from the root of the mod. Do not call the tools by hand.

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py"
python3 "${CLAUDE_SKILL_DIR}/verify.py" --since origin/dev
```

**To check only what changed, pass `--since` with the commit before your edits**, in any repository: `--since HEAD`
for uncommitted edits, or `--since main` on a branch. In a repository with no commits, name the changed files as
paths, and do not filter the output. In a stacked PR, pass `--since` with the branch that you created the PR's branch
from, such as the branch of PR 2 for PR 3. (R11-since-any)

**In a PR to another project, pass `--since` with the base branch.** Upstream code already breaks
some of these rules, and a finding on a line the diff does not touch is not the PR's to fix. Only the
lines that the diff against `merge-base(HEAD, base)` adds or changes are reported, and every line of
an untracked file. List each finding that was already on the base branch under `upstream findings kept`, and ask the user once
whether to fix those findings. (R11-upstream-ask)

**Ask the user before you name something by an upstream convention that `NAR130` rejects.** For
example, GT5's `MultiblockTooltipBuilder` has about 40 `TT_*` fields, such as `TT_machineType`. A new
`TT_parallels` field beside those fields breaks the Java naming convention. If the user approves, add the finding
to the keep-list (the rule is under **noqa**). (J1-F06, J1-no-noqa)

`verify.py` runs one Gradle invocation with the init script `narrative.init.gradle`, at every
level of **Scope**:

1. `spotlessApply` (or `spotlessCheck` under `--no-fix`)
2. `compileJava` with the raw-type and unchecked warnings of javac
3. Checkstyle and PMD with the configs beside `verify.py`

`javachecks.py` then reads the comments, runs the prose checks, and merges the three reports into
one list with NAR codes. A run with exit 0 or 1 writes five lists to
`.narrative_cache/review-lists.txt`, the input to **Prose review**:

- every sentence of every comment, javadoc, and named page
- every verb whose subject cannot act
- every sentence with a pronoun
- every sentence with a free modifier
- each javadoc and member comment, and each method over 20 body lines (`NAR116`)

The `NAR116` list comes from the PMD report, so a run with `--prose-only` doesn't have the `NAR116`
list. The file and the number of entries in each list are on the last line of the output. When Gradle fails, such as on code that does not compile, `verify.py` doesn't
write the lists, because `javachecks.py` has not read the comments yet. When `--since` is given, the
lists cover only the changed lines of the code and the pages. Otherwise each list stops after 1000
entries, with the command for the next 1000. (J1-F01, J1-F09, J1-F14, J1-F15, J1-F16, R11-same-workflow)

| exit | meaning |
|---|---|
| 0 | every check passed. Warnings may be printed |
| 1 | at least one finding, or the code does not compile or is not formatted |
| 2 | the toolchain, `gradle.properties`, `gradlew`, or a report is missing, `enableModernJavaSyntax` or `forceToolchainVersion` has a value without a level in **Scope**, `--since` doesn't name a commit, the diff doesn't change a line, `javachecks.py` stopped before the count line of the findings, or the review lists could not be written |

Pass `--max-workers 1` on a busy machine. The job of each tool, the code table, and the tool defaults
that break rules of this skill are in `tooling.md`. Read it before you change a config.

**After an edit of comments or pages only, pass `--prose-only`.** Gradle does not run, so the run
takes seconds: the re-wrap, the prose checks and the review lists. Spotless, javac, Checkstyle, and
PMD run only without `--prose-only`, so the last run before the report is a run without
`--prose-only`.

`--project DIR` makes `verify.py` check the mod in DIR. `--cache-dir DIR` puts `.narrative_cache`
in DIR, such as a directory outside a checkout that the agent may not write. A path of `-` is a
page read from stdin, such as a draft that is not in a file yet.

Before the report, for each test that you wrote or changed, name the rule under test and the source
of the test's cases: a generator, the boundary values or both. Where the answer is not both, fix the
test. (J1-P36)

