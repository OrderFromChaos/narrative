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

