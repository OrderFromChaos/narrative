## Types

- **No raw types.** `Object` in a signature is the visible form of "any type", so `Object` is
  visible and greppable. `var` only where the right-hand side names the type:
  `var plans = new ArrayList<Plan>()`. `NAR121` reports the raw-type and unchecked warnings of
  javac. (J1-P10, R2-11)

- **Annotate the true requirement.** A parameter has the narrowest interface the method uses:
  `Iterable`, `Collection`, `List`, `Map`. Never `ArrayList` or `HashMap` in a signature. `SortedMap`
  where the order matters (see **GTNH**). `NAR140` flags a concrete collection type in a signature,
  a field or a local. `EnumMap` and `EnumSet` keep their types: `new EnumMap<>(map)` and
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
  operations, not `File` methods. `File.delete()`, `renameTo()` and `mkdirs()` return `false` on
  failure, and `File.listFiles()` returns `null`. `Files.delete()`, `Files.move()` and
  `Files.createDirectories()` throw an `IOException` with the cause. `NAR115` flags a `File`
  operation. (J1-P14, R3a-10)

- **Amounts are exact.** `long` for item, fluid and EU counts, never `float` or `double`.
  `Math.addExact` and `Math.multiplyExact` where overflow is reachable. A rate may be a `double`.
  (J1-P15)

- **Time.** `java.time` only. Game time is a `long` named `…Ticks`, at 20 ticks per second.
  (J1-P16)

- **`enum` for closed sets.** Never write `ordinal()` to NBT, a packet or JSON: reordering the
  constants changes every saved world. Serialise `name()`, or an explicit code field. `NAR105` flags
  `ordinal()` in NBT, packet or Gson code. (J1-P17, R2-08)

- **Composition over inheritance.** An `interface` for a seam with two real implementations. No
  `abstract class` in project code. `extends` only for a class the platform requires: Forge `Block`,
  `Item` and `TileEntity`, MUI2 widgets, GT bases. A `sealed abstract class` is allowed when its
  permitted subclasses share fields: the fields are declared once, in the class. `NAR106` flags every other
  abstract class. (J1-P18, R2-01, J1-F05)

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

For an `enum` or `sealed` type, write a `switch` expression with no `default` arm. javac then rejects
a missing constant. **A `default ->` arm compiles clean and accepts the missing case.** `NAR107`
flags a `default` arm in a switch over an enum or a sealed type of the project.
(J1-P19, Q18, R3a-07)

- A `switch` **statement** over an enum has no exhaustiveness check. Rewrite it as a `switch`
  expression that returns a value.
- **Keep the `switch` even where an `EnumMap` looks natural.** `EnumMap.get()` returns `null` for a
  missing key, at run time.
- Under jvmDowngrader, the synthetic default of an exhaustive `switch` throws a stub
  `MatchException`. It is reachable only when a newer enum class is loaded than the one compiled
  against.
- **Where the behaviour is a property of the constant**, such as the amount format of a resource
  type, write the behaviour on the constant, as an abstract method or a constructor argument. javac
  then requires it of every constant, and call sites get no branches. **Where only one caller needs
  a mapping**, such as a log level for each outcome, the `switch` is in that caller. (J1-P19)
- A type-pattern switch over a type that is not sealed, such as an NEI handler object, needs a
  `default` arm.

