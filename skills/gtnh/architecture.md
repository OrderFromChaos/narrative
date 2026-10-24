# Narrative Java architecture

`SKILL.md` applies to one file. This document applies to several, and to the boundary between a mod
and the other mods in the pack.

Read this when the change spans more than one package, or touches another mod. Do not read it for a
change inside one class.

The reason for each rule is in the text of the rule. The ids are provenance. They resolve in
`benchmark/decisions.jsonl` in the source repository, `github.com/OrderFromChaos/narrative`. A rule
that no tool can check is marked as such.

## The measure

**Name the change before you make it. The name must be enough for you to know the one file to
open.** (`R7-M01`)

Say what the change is in the words a colleague would use: "GT renamed the recipe map", "the cache
window moved to 90 ticks", "we added a third recipe source". A design passes when each of those
sentences has exactly one destination, and when you know that destination before you read the
mod. It fails when the answer is "it depends" or "three places".

**Measure what you must know to make an edit, not the number of files in the edit.**
(`R7-A05-measure`)

**The exchange rate**, dearest first (`R7-M02`):

1. a parameter threaded through methods that do not use it
2. one more file
3. one more named type. It costs nothing when the field belongs to the thing the field is about

Spend a named type or a file to delete a threaded parameter. Never the reverse.

## Fact placement

**Ask whose property the fact is, and put the fact in that thing's class.** (`R7-A05-property`)

A per-machine overclock limit is a property of the machine, so the overclock limit belongs with the
machine and not in a generic overclock calculator. A retention window is a property of the data, not
of the task that runs the cleanup.

- **Do not make a caller pass what the callee can compute from its arguments and imports.**
  (`R7-A01-revised`) **This outranks dependency direction.**

- **An exception type belongs in the shared vocabulary, not in the class that throws the
  exception.** (`R7-A04-revised`) It can be caught in any class, so the exception type belongs to no
  one class.

- **A type centralises once it appears in a signature.** (`R7-B07`, `R7-B07-bound`) A shape built
  and consumed inside one method is a step, not a type. **Every type in a signature that other
  packages use goes in the shared vocabulary package**, with no exception for a type that only one
  other package reads. (`R8-D19-resolved`)

- **A log field set belongs to whatever emits the record**, not to a shared list. (`R7-E02-fields`)

- **A one-line body earns its name when the expression encodes a domain decision.** It does not
  when the expression is a plain language or library operation. (`R9-12`)

  ```java
  // No. A map lookup with a default is not a concept.
  private static String canonicalTier(String tier, Map<String, String> aliases) {
      return aliases.getOrDefault(tier, tier);
  }

  // Yes. The tier ladder of GT is a rule of the pack. A reader learns that from the name.
  private static int voltageOfTier(int tier) {
      return 8 << (2 * tier);
  }
  ```

  This is judgement, and no tool checks this.

**Two participants that must agree on a byte layout share one class.** (`R7-A05`) A packet is
encoded and decoded in one `IMessage` class, `toBytes()` beside `fromBytes()`. A copy on each side is
the worst option, because drift between the copies is a bug that no type checker reports.

## Which package uses which

**There is no layer table and no directory rule. This is review judgement, not a check.**
(`R7-A05-levels`)

**A cycle between packages is a wrong cut.** (`R7-A02`, `J1-A01`) Break the cycle with a shared
vocabulary package. Classes inside one package may reference each other in both directions.

**Call a static method through its class, and make the method name clear without the class.**
`PlanFiles.readAll()` reads well because `readAll` reads well without the qualifier. (`R7-B06`,
`R9-03`, `J1-P07`)

## Where the cuts go

**A coherent concern earns a class. Line count is not the criterion**, in either direction.
(`R7-B01-B03-criterion`)

**The test is whether you can name it without saying "and".** (`R8-D12-resolved`) `PlanFiles` is plan
files. A `PacketCodec` that also formats tooltips is "the wire format **and** tooltips", so the
tooltips leave. If the only name for a group has an "and", the group is two groups.

**Split.** (`R7-B01`) Six classes of 40 to 90 lines are better than one of 340. Do not wait for a
second user of the code.

**There is no fixed split axis.** (`R7-B02`) Cut by technical role when the mod has one of
everything. Cut by subject when it has several providers, several formats or several machines. Cut
on the axis the expected changes land in more cleanly.

**Naming a concept and crossing a boundary are two tests, and they can disagree.** (`R7-B04`,
`R8-D39`) Where they disagree, treat the disagreement as a question for review, not a rule.

**Shared code inside one subsystem starts in one package of that subsystem.** (`R7-A05-growth`)
Never a project-wide `Utils` class.

## Package surface

**`private` or `public` only, no package-private.** (`J1-A02`) A member that no other class uses is
`private`. Test classes and test methods are exempt, because JUnit 5 convention is package-private,
and PlanNH follows the convention. `NAR124-gtnh` flags a package-private member in main sources.

**The `@Mod` class is the entry point.** (`J1-A03`, `R7-A05-entry`) The lifecycle handlers of the
`@Mod` class call the registration method of each subsystem and contain no other logic. For a new
subsystem, the change is one new class and one new line in the handler.

**`main()`-first generalises to a library class.** (`R7-E05`) The public entry takes the first
position, callees follow in first-call order, nested types last.

## What earns a class, an interface, a record

**Values that could differ between instances earn a class.** (`R7-C01-C02-revised`) Two plan files
can be open at once, so a plan reader is a class. A packet format is the same everywhere, so the
format's codec is a final class with static methods.

An `interface` is earned once a seam has more than one real implementation (`J1-P18`). A class is
earned once two of it can exist at once. One object, one implementation, and a class is the right
answer.

**One coordinator, not a chain.** (`R7-C03`) Stages with no separate use do not each call the
next. One method calls them in turn, with the intermediates in the method's local variables.

**A pure core earns its place by the number of decisions in the core.** (`R7-C06`, `R7-C07`)
Compute a plan, then apply the plan. In a mod, a pure core has one more benefit: with no Minecraft
type in the core, the core's tests run headless.

**Every case of a closed set is in one class, in an exhaustive `switch`.** (`R7-A06`, `J1-A07`)
Adding a constant must be a compile error at the switch. Forge registries are framework registration
and exempt.

**Centralise a type before anything shares the type. Do not generalise behaviour before you need
it.** (`R7-B07-preemption`)

## Resources, state and config

**A resource is opened at the scope whose lifetime the resource matches**, in try-with-resources,
and the reader finds the open at the top of that scope. (`R7-A03`)

**Idle time is not the variable. What the handle costs on the far side is.** (`R7-A03-idle`)

**A static singleton is fine for anything never closed.** (`R7-E01`) A logger is a static field. A
connection is not.

**One mod-wide Config class reaches every package.** (`R7-E03`) Its fields are static, and
`NAR110` exempts them. A default belongs in the Config class, not in a literal of some other class.

**Leaf classes read the constants they need.** (`R7-A07`) *No tool checks this.*

**Pass a flag no further down than the method that branches on the flag.** (`R7-C04`)

**The clock goes inside the method that reads the clock.** (`R7-E04`) Test through the real clock
and assert on ordering and bounds, not on an instant.

## Third-party code and other mods

**Take a dependency when it is simpler at the call site, and prefer what the pack already ships.**
(`R7-D02`, `R7-D02-stdlib`, `J1-A05`) The JDK, Guava, Gson and commons-lang3 are in every GTNH pack.
A new library is a new jar in the pack. Reuse library API, and take display conventions from the
pack: read them in the sources jars under `~/.gradle/caches/modules-2`.

**Contain an optional mod.** (`R7-D03`, `R7-D01`, `J1-A04`)

- Every reference to the optional mod is in one class, and the mod is `compileOnly`.
- That class is called only behind a guard such as `Loader.isModLoaded("gregtech")`. The JVM loads a
  class at first use, so with the mod absent, the class is never loaded.
- `NoClassDefFoundError` is caught at that boundary only. Everywhere else it is a bug.
- Common code never references a client-only class (`@SideOnly(Side.CLIENT)`, the client proxy).
  A dedicated server crashes on it.
- A mixin only where no API exists, and accessor mixins first.

**Contain handles, not values.** (`R7-D01-D03-containment`, `R7-D01-D03-handle`) An `ItemStack` or a
`FluidStack` crosses freely. A network channel or an open file does not.

**Depend rather than vendor or reimplement**, weighted by adoption. (`R7-D05`, `R7-D05-trust`)

**Subscribe to a Forge event instead of polling every tick.** (`J1-A06`, `R7-E07`)

## Where degrade-and-report splits

**The class doing the work collects per-item failures, and the class above logs the aggregate.**
(`Q24`, `R7-A08`)

## Comments

The comment rules are in `SKILL.md`, **Comments**, including the ban on decision citations
(`NAR012`). The name of a rule that the program **implements** is allowed, such as the NAR code of a
check, in the check. A name from the same program is not a citation.

## Not architecture, learned alongside

**Name the value of the last return.** (`R7-return-naming`) At the end of a long method, the name of
the returned value is enough, and the reader does not scroll to the signature.

**Order constants by who changes the value.** (`R7-A05-ordering`) Pack-tunable values are in the
Config class. Developer-only bindings are last in the block.

## What no tool can check

- **Dependency direction.** (`R7-A05-levels`)
- **Where a fact belongs.** (`R7-A05-property`)
- **The split axis, and whether a concern is coherent.** (`R7-B02`, `R7-B01-B03-criterion`)
- **Whether a bundle is a real thing.** (`R7-C05-naming`)

Two more are checkable in principle and **no checker for them exists**, so they are review
judgement too: a cycle between packages, and a reference to an optional mod outside the mod's class.
