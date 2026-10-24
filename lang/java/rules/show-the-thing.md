### Show the thing, do not describe it

**Where a class reads or writes concrete text, paste a real sample of that text** in a `<pre>`
block: a tooltip, a chat line, a lang entry, an NEI line, a converted value. **Delete the prose the
sample replaces** rather than keeping both. (R9-08)

**Never invent a sample.** Run the code and paste what it printed. A format that appears nowhere in
the program is a lie in the shape of documentation. **Do not state what you did not observe.**

**Show one line of each shape, not the whole output.** A sample goes stale and no tool checks the
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

