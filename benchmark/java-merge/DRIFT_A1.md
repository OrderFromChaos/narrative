# A1: how a shared rule gets the examples of each language

## The problem

The two skills have the same **Fence** rule with different examples:

| | Python skill | Java skill |
|---|---|---|
| short example | `# bool subclasses Python int. Reject it too` | `// Character.isDigit() accepts non-ASCII digits such as '٣'. Check the range '0' to '9' too` |
| full example | a block with `csv_path.read_bytes()` | a block with `Files.readAllBytes()` |

The rule text around the examples is the same in both. Today the rule text is in two files, and the
two copies have drifted. Each option below puts the rule text in one file. Each option has the same
three parts:

- **Files**: the files you edit for this one rule
- **Source**: the text of those files
- **Built**: the text of `skills/python/SKILL.md`, which an agent loads

## What a slot is

Options 1 and 4 use slots. A slot is a marker in a rule file, such as
`<!-- example: fence-full -->`. The marker is only in the source files of this repository. **No
agent ever sees a slot.**

`build_skills.py` writes the SKILL.md of each skill. When the build reaches a marker, the build
reads the example file of that language and puts the file's text in place of the marker. If a
language has no file for a marker, the build fails with the name of the missing file.

## Option 1: a slot for every example

**Files**

```
core/rules/comments.md
lang/python/examples/fence-short.md
lang/python/examples/fence-full.md
lang/java/examples/fence-short.md
lang/java/examples/fence-full.md
```

Comments has 26 inline comment examples and 3 code blocks, so about 30 such pairs, and more for
words such as `None` and `null`.

**Source**

`core/rules/comments.md`:

```markdown
- a Fence is the fact the code depends
  on, then the step the code takes
  because of that fact:
  <!-- example: fence-short -->.
  The `X would` form in full:
  <!-- example: fence-full -->
```

`lang/python/examples/fence-short.md`:

```markdown
`# bool subclasses Python int. Reject
it too`
```

`lang/python/examples/fence-full.md`:

````markdown
```python
# Here read_bytes() is used. The
# alternative, read_text(), would turn
# \r\n and \r into \n.
csv_bytes = csv_path.read_bytes()
```
````

**Built**

````markdown
- a Fence is the fact the code depends
  on, then the step the code takes
  because of that fact: `# bool
  subclasses Python int. Reject it too`.
  The `X would` form in full:
  ```python
  # Here read_bytes() is used. The
  # alternative, read_text(), would turn
  # \r\n and \r into \n.
  csv_bytes = csv_path.read_bytes()
  ```
````

- **Good:** the built Python SKILL.md is exactly today's text.
- **Bad:** 30 to 60 example files per language for Comments. The rule source has a marker in the
  middle of most sentences, so the rule reads as a whole only after a build.

## Option 2: the examples in a separate module per language

**Files**

```
core/rules/comments.md
lang/python/rules/comments-examples.md
lang/java/rules/comments-examples.md
```

**Source**

`core/rules/comments.md`:

```markdown
- a Fence is the fact the code depends
  on, then the step the code takes
  because of that fact. The examples are
  under Fence in Examples of comments.
```

`lang/python/rules/comments-examples.md`:

````markdown
## Examples of comments

**Fence:** `# bool subclasses Python
int. Reject it too`. The `X would` form
in full:
```python
# Here read_bytes() is used. The
# alternative, read_text(), would turn
# \r\n and \r into \n.
csv_bytes = csv_path.read_bytes()
```
````

**Built**

The rule text of the source, then the rest of **Comments**, then **Examples of comments** about 300
lines later, with the examples above.

- **Good:** no markers. Each source file reads as plain text.
- **Bad:** each example is far from its rule. In round 10, agents copied the skill's examples word
  for word (`benchmark/round10/README.md`), so the examples matter. Whether an example far from its
  rule still works is not measured.

## Option 3: the examples of every language in core

**Files**

```
core/rules/comments.md
```

**Source**

`core/rules/comments.md`:

````markdown
- a Fence is the fact the code depends
  on, then the step the code takes
  because of that fact. Python: `# bool
  subclasses Python int. Reject it too`.
  Java: `// Character.isDigit() accepts
  non-ASCII digits such as '٣'. Check
  the range '0' to '9' too`. The
  `X would` form in full:
  ```python
  # Here read_bytes() is used. The
  # alternative, read_text(), would turn
  # \r\n and \r into \n.
  csv_bytes = csv_path.read_bytes()
  ```
  ```java
  // Here Files.readAllBytes() is used.
  // The alternative, Files.readString(),
  // would throw on a byte that is not
  // UTF-8.
  byte[] plan = Files.readAllBytes(path);
  ```
````

**Built**

The same text as the source, in both skills.

- **Good:** one file, and no build step for examples.
- **Bad:** each skill has the examples of every language. Text in backticks is 26% of the words of
  **Comments**, so **Comments** grows by about a quarter for each language. An agent can copy the
  comment syntax of the wrong language.

## Option 4: inline examples with no language, a slot for each code block

**Files**

```
core/rules/comments.md
lang/python/examples/fence-full.md
lang/java/examples/fence-full.md
```

Comments has 3 code blocks, so 3 such pairs.

**Source**

`core/rules/comments.md`:

```markdown
- a Fence is the fact the code depends
  on, then the step the code takes
  because of that fact: `the vendor
  rejects a batch over 500 rows. Send
  500 at a time`. The `X would` form in
  full:
  <!-- example: fence-full -->
```

`lang/python/examples/fence-full.md`:

````markdown
```python
# Here read_bytes() is used. The
# alternative, read_text(), would turn
# \r\n and \r into \n.
csv_bytes = csv_path.read_bytes()
```
````

**Built**

````markdown
- a Fence is the fact the code depends
  on, then the step the code takes
  because of that fact: `the vendor
  rejects a batch over 500 rows. Send
  500 at a time`. The `X would` form in
  full:
  ```python
  # Here read_bytes() is used. The
  # alternative, read_text(), would turn
  # \r\n and \r into \n.
  csv_bytes = csv_path.read_bytes()
  ```
````

- **Good:** the rule source reads as one text, with 3 markers in Comments. Each skill has one
  language.
- **Bad:** an inline example has no `#` or `//`. An example about one language, such as
  `bool subclasses Python int`, becomes a slot or is replaced with an example that fits any
  language. Each replacement changes an example of the Python skill, so each replacement goes to
  you first and is tested with the eval before the replacement ships.

## Recommendation

Option 4: the rule source stays readable, with few markers. Option 1 is the choice if the Python
text is to stay exactly as today.
