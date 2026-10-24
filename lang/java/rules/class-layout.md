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

- **Re-wrapping is a tool's job.** Spotless splits a comment line over 120 columns but never joins
  short lines, so after an edit the line breaks of the first draft remain: `The product is` / `a` /
  `float, …`. `NAR125` flags a javadoc line with room for the first word of the next line. Before the
  checks, `verify.py` re-wraps each flagged javadoc paragraph and splits each whole-line `//` comment
  over 120 columns. With `--no-fix`, run `javachecks.py --rewrap` on the file. The re-wrap moves line
  breaks only, never words. (J1-F02, J1-F08)

- Separate logically self-contained blocks inside a method with **one blank line**. That is its only
  meaning here. Short guards written as a group stay grouped. (R3a-01)

  **No tool checks this.** Place a blank line by these five rules: (`R8-NAR008`, `R8-NAR008-rule`)

  - a body of **8 lines or under takes no internal blanks at all**
  - blanks **recur into nested blocks**, and one loop body can take four
  - **a multi-line statement and the statement that consumes the result are
    one step**, so a builder chain then the `return` of the chain stay adjacent
  - a blank precedes a `return` when the phase before the `return` is unrelated, and not when the
    returned value was just built
  - **length is not the trigger**, in either direction

- If a guard grows to three lines because it logs before throwing, move the log call into a
  `reject*()` helper that logs and returns the exception. The guards are two lines again and group:
  `throw rejectLine(raw_line, "no machine count");` (R4-05)

- **Java has no keyword arguments.** A call with more than 3 positional values, or with a `null` for
  a skipped argument, is replaced by a builder, or by a parameter record. Where Lombok is present,
  use `@Builder(toBuilder = true)`. An `@Override` has the signature of the platform. `NAR131`
  flags a method with more than 3 parameters, and `NAR102` a call with two or more `null` arguments.
  (J1-P03, R2b-B1, R5-06)

- **Long strings.** In user-facing text, never `+` (J1-P04). Outside it, `+` joins a long one-line
  string. A text block is for multi-line data only. The incidental indent of a text block is removed
  at compile time, but the value still depends on the position of the closing `"""`. (J1-P04, Q03)

