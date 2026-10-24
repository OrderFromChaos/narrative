### Javadoc rules

**Most members get no javadoc.** A top-level type (`NAR118`) and a method over the contract
threshold (`NAR116`) need one. Any other field, constant or method gets a javadoc only for a fact
that the name, type, value and signature do not show. A javadoc whose facts are already in the
declaration only costs the reader time. Cut such a javadoc whole, not sentence by sentence. The Java
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
- **Its negation would be a bug, an absurdity, or an implementation nobody would ship.** Negate the
  sentence and read it back. **Assume the reader expects competent code, and document only the
  departures.**
- **It is a language feature, explained.**
- **It goes stale and nothing checks it**, unless it is a sample you accept that cost for.

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
- **where the leftover, default and failure cases go**
- a **sample** of concrete text the class reads or writes
- a **constraint from outside the program**: `Forge drops a tile entity whose readFromNBT() throws`
- a **guarantee a caller needs**: `The call writes no file, sends no packet, and changes no world`

- **A method gets a javadoc when its contract is complex**, meaning the method takes more than three
  parameters, or the method's body exceeds 20 lines. Below both, the contract goes in `//` comments.
  `NAR116` flags a method over that threshold with no javadoc. (J1-P34, Q05, R8-D18-resolved)

- **`@throws` for every exception absent from the `throws` clause**, for a method over that
  threshold. A checked exception is in the signature already. `NAR117` flags a `throw new X` with no
  `@throws X` line. `@param` and `@return` only for a fact absent from the signature: an ordering, a
  nullability, a unit, or a count whose meaning is not obvious. (J1-P34, R8-D28-resolved)

- Write nothing in a javadoc that the code does not do, and no consequence that an earlier sentence
  already implies. (Q05)

- **A javadoc is about its class alone.** Do not assert what another class does, do not claim to be
  the only place something happens, and do not count callers. Name another class only where a reader
  of *this* file needs the name to use this file. (R9-02)

- Where semantics vary by implementation (file moves, copies, path manipulation), **show a concrete
  before and after example**, not prose. (R3a-11)

