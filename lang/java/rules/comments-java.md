## Comments in Java

These rules add to **Comments** in `nar:core`. Each heading below is the name that `nar:core` uses
for the rule. A docstring there is a javadoc here, and a localisation file there is a lang file of
the mod here.

### Identifiers

An identifier in javadoc is a link: `{@link #getMachineModes}` or `{@link ExtendedBlockStorage}`.
In an IDE, the reader can jump from the link to the target. When someone renames the target in the
IDE, the link changes with the name. `{@link}` takes a class, a field, a method or a package. Put a
parameter, a local variable or a value such as `null` in `{@code}`. In a `//` comment, put the name
in backticks. Link to an identifier even when its name is unclear. From the link, the reader can
jump to the code and see what the name stands for. (R11-pointer-wording, J1-F10)

### Library facts

For a fact about vanilla Minecraft or Forge, read the source and check the fact.
(R11-rewrite-from-code)

### Source facts

A fact about a value from vanilla Minecraft, Forge, another mod or an old save, such as a `null`
field or a missing NBT tag, goes above the code for the value (J1-F12):

```java
// worlds saved before 1.2.0 have no "tier" tag
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
// The vendor API returns at most 100 rows per page and no total count.
// Keep requesting until a page comes back short.
while ((page = fetchPage(cursor)).size() == PAGE_SIZE) {
```

(R10-depth-example)

### FIXME

`verify.py` prints each `FIXME:` as a warning, `NAR119`, and still exits 0. A mod has no `main`, so
every method counts as reachable. (J1-F4)

### Return contracts

`NAR120` flags a `// returns …` comment at the top of a method. (R10-return-contract)

### Agent verbs

`draws` is an agent verb for a widget whose drawing is not the point. (J1-verbs-literal)

### noqa

The exceptions to **Never add a `noqa` yourself** are the three `noqa` uses prescribed in this
skill: `NAR104` for two types of one name, `NAR142` in a degrade-and-report loop, and `NAR130` once
the user approves an upstream name. (R11-findings)

A `// noqa: NARxxx` covers every line of the comment block, and the code line after a whole-line
block, because spotless wraps a `//` comment over 120 columns and moves a trailing noqa to the next
line. The same syntax silences a finding from any tool. (J1-P35)

### Pages

Name each page to `verify.py`, which then runs the prose checks only, with no Gradle project:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" README.md docs/report.html
```

A page named beside Java sources gets the same checks, in the same list of findings.
(R10-published-prose, J1-F15)

