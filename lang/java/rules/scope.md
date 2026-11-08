## Scope

narrative-gtnh checks GTNHGradle projects at three Java levels. `verify.py` takes the level from
`enableModernJavaSyntax` in `gradle.properties`, with the values of GTNHGradle, and prints the level
on the `level` line of each run. (J1-levels)

| level | `enableModernJavaSyntax` | toolchain | syntax | library |
|---|---|---|---|---|
| Java 25 | `jvmDowngrader`, `modern` | 25 | Java 25 | Java 25, where the GTNHLib stubs of jvmDowngrader cover the API |
| jabel | `jabel`, `true` | 17 | Java 17, with `@Desugar` on a record, and no sealed types | Java 8, with `--release 8` |
| Java 8 | `false`, or no value | 8 | Java 8 | Java 8 |

`true` and `false` match with any case. On any other value, `verify.py` exits 2, and also on
`forceToolchainVersion` other than `-1` or the toolchain of the level. javac runs on the toolchain of
the project, so a call to a method that the library of the level does not have is a compile error.
Checkstyle and PMD run on a JDK 25 at every level.

- No preview features.
- On a guard for a runtime newer than the floor, the comment has the version:
  `// on Java 21 and later, Thread.ofVirtual() is available`. (R10-version-guard)

### Rules by level

Every rule and every check applies at every level, except these. Where a rule below has a record,
`List.copyOf` or a `switch` expression, use the form of the level.

- **A record.** Java 25: a record. jabel: a record with `@Desugar`
  (`com.github.bsideup.jabel.Desugar`). The Jabel of GTNH compiles that record for Java 8, and a record
  with no `@Desugar` does not compile. Java 8: a final class with private final fields, one constructor
  and `getName()` getters, with `equals()` and `hashCode()` when code compares two instances. `NAR108`
  can fire only on a record. (J1-P21-levels)
- **`List.copyOf`.** jabel and Java 8: Guava `ImmutableList.copyOf`, and `ImmutableSet.copyOf` or
  `ImmutableMap.copyOf` for the other collections. (J1-P21-levels)
- **A `switch` over an enum.** Java 25 and jabel: a `switch` expression with no `default` arm. javac
  rejects a missing constant at both levels. Java 8 has no `switch` expression. Put the behaviour on
  the constant, where javac checks every constant. Where only one caller needs a mapping, write a
  `switch` statement with a case for every constant, no `default` arm, and a throw after the switch.
  `NAR107` flags a `default` arm at every level. (J1-P19-java8)
- **A sealed type.** Java 25 only. So the `sealed abstract class` exception of `NAR106` and the sealed
  types of `NAR107` are Java 25 only. (J1-levels)
- **A pattern in a `switch`, and a record pattern.** Java 25 only. jabel: an `instanceof` pattern in
  an `if` chain. Java 8: `instanceof` and a cast. (J1-levels)
- **`var`, a text block and an `instanceof` pattern.** Java 25 and jabel only. (J1-levels)
