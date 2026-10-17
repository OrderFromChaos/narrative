---
name: narrative-lite description: Lite version of the Narrative house style for Python, with
mixedCase functions, main() first with types last, parse-at-the-boundary frozen dataclasses,
explicit global on mutation, exhaustive match without a fallback arm, strict comment and docstring
rules, and a verified ruff/pylint/mypy toolchain. Multi-module layout is in architecture.md. Use for
any Python written in or for this codebase, and when reviewing a diff against this style. ---

# Narrative Python, lite

**0% of reader effort on rote diffing, 100% on design.** Four near-identical lines that differ in
one token make the reader compare them token by token, and every comparison is a chance to miss the
difference. One parameterised call removes the comparison. This is the root of DRY, of one name for
one thing, of consistent ordering, and of the ban on gratuitous variation. When two rules conflict,
follow the rule under which the reader diffs less.

**For representation choices, prefer what the type checker and IDE can follow**, even when a looser
form is more flexible. State in a `dict[str, Any]` passes `mypy --strict` only with a `cast()` or a
key lookup at every use. Typed attributes pass with neither.

These rules apply to each module of a package as they apply to a single-file program. Read
`architecture.md` when the program spans more than one module or imports a third-party package.
Read the matching section of `domains.md` for a program with money, dates, asyncio, SQLite rows, a
web framework or a logging setup. The steps to run while writing and before you finish are in
**Procedures**. The reason and decision id behind each rule are in the full `narrative` skill.

## File layout

```python
from __future__ import annotations   # required for types-last

import logging                       # plain imports, alphabetised
import sys
from pathlib import Path             # then `from` imports, alphabetised
from typing import NewType
                                     # TWO blank lines

LOG_PATH = Path('jsonl_logs/app.jsonl')     # tunable constants, grouped BY CONCERN
DEFAULT_DB_PATH = Path('app.db')
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
                                     # one blank line
LOG = logging.getLogger(__name__)    # design-level globals, in a separate group


def main() -> int:                   # FIRST. A reader starts here
    ...


def stepOne(...) -> ...:             # workflow, in first-call order
def stepTwo(...) -> ...:
def leafHelper(...) -> ...:


### vocabulary #########################################################################

ScanId = NewType('ScanId', int)      # types LAST. A reader needs what main() passes
class Outcome(Enum): ...             # around only after the high-level design
class ConfigError(RuntimeError): ...
@dataclass(frozen=True)
class ScanHeader: ...
```

- `main()` returns an exit code. Call it as `sys.exit(main())`. All executable code is in `main()`.
- Caller before callee throughout. At module level, do not call or subclass anything before its
  definition. Annotations are safe, because the future import makes them lazy. A constant whose
  value is an Enum member goes in `### vocabulary` directly after that Enum. Do not restructure
  code to avoid this placement.
- Order constants by concern. Constants a developer looks for at the same moment go together: all
  the `_S` durations, then other limits, then hosts, then wire literals. Operator-tunable values
  come before developer-only bindings. No blank lines inside the block.
- 120 columns. Absolute imports only. Single quotes, and double quotes for docstrings and multiline
  strings.
- Long strings use implicit concatenation in parens. Never `"""` for data, because its whitespace
  becomes part of the value.
- In a `def` with more than 3 positional parameters, put each on a separate line with a trailing
  comma, even under 120 columns (`NAR003`). Keyword-only parameters do not count, so a `*` before
  the optional parameters is the escape hatch. Calls are exempt.
- Separate logically self-contained blocks inside a function with one blank line, and use a blank
  line for nothing else. No tool checks this:
  - a body of 8 lines or under has no internal blanks
  - blanks recur into nested blocks
  - a multi-line statement and the statement that consumes its value are one step: `executemany`
    then `commit`, a constructor then the `return` of it
  - a blank precedes a `return` when the phase before it is unrelated, and not when the returned
    value was just built
  - length is not the trigger, in either direction
  - short guards written as a group stay grouped. No blank line after a docstring

## Python 3.11 floor

`ruff` targets `py311`, and `vermin -t=3.11- --violations` checks the floor. Anything added in 3.12
or later is out, including the `type` statement and PEP 695 generics. For asyncio, read
`domains.md`.

## Structure inside a function

- Guard clauses and early return over nesting.
- Write a skip guard as the negation of what a valid item is: `if not (name_match and
  entry.is_file() and not entry.is_symlink()):`, not `if name_match is None or entry.is_symlink() or
  not entry.is_file():`.
- Comprehensions may have any number of `if` clauses at one level. Any nesting becomes an explicit
  loop.
- Extract a block when you can foresee reusing or testing it separately, not because it has a name.
  A one-line helper called once is residue.
- If an extracted function would take 5+ parameters, find where the values belong: a class when
  there can be two instances at once, a module otherwise, and a frozen record only when nothing has
  behaviour over the values. If a general name for the group is hard to pick, the group is not real.
- Collapse duplicated-but-drifting code, even when the shared version takes an extra parameter.
- Mixed `and`/`or` parenthesises each group. Never `A and B or C and D` (`NAR007`).
- Merge branches that share a body only where mypy narrows the merged branch the same way. After a
  merge of two `isinstance` branches, the type of the subject is a union again.
- At the end of a long function, name the returned value, so the reader does not scroll to the
  signature. Early returns and guard exits are exempt.

## Naming

- Module files `snake_case`. Functions and methods `mixedCase`. Classes and types `PascalCase`.
  Variables and arguments `snake_case`. Module constants `ALL_CAPS`. In a `snake_case` codebase
  that you did not write, match local convention.
- Spell names out. No `img_arr`, `cfg`, `idx`.
- A function name starts with a verb, and the verb's object is what the function returns:
  `parsePolicy`, `computeDeletionCutoff`. Not `policyIn`, not `cutoffFor`.
- A name is clear without its module qualifier, to a reader who has never opened the module.
  `store.insertReading` reads well because `insertReading` reads well alone. Two functions in one
  package do not share a name. Where the clear name is the longer one, write the longer one.
- Predicates are bare adjectives: `readyForScan`, not `isReadyForScan` or `checkReadyForScan`.
  Dunder and protocol methods are named by the language.
- Do not restate a domain type in a parameter name: `config: RebinConfig`. With a generic type such
  as `Path`, `str`, `int`, `bytes`, `dict` or `object`, the parameter name is the only place the
  thing is named: `policy_json_path: Path`, not `path: Path`.
- Raw and parsed forms get different names: `raw_at: str` from the file, `at: DateTime` once parsed.
- Where the bare name would shadow an imported first-party module, restate the type:
  `results_store: Store`.
- `from pathlib import Path`, not `pathlib.Path`. Import the class, and keep the verb qualified:
  `struct.unpack`, `json.loads`, `asyncio.wait_for`.

## Constant placement

Name every magic number, then ask: could someone change this value safely knowing only what the
program **does**, or would they need to understand how the function **works**? An implementation
detail goes **inside** the function, still `ALL_CAPS`: the magic bytes of a file format, a struct
format, a padding byte, a derived size, a checksum mask, the SQL of one function. A log path, an
archive directory, a glob, exit codes and operator-tunable timeouts stay at module level. No tool
checks this.

## Types

- Annotate every parameter and return. `mypy --strict`, with `disallow_any_explicit` off, so a
  written `Any` is visible and greppable.
- Annotate the true requirement. A function that only iterates takes `Iterable`, not `list`.
- `NewType` for domain primitives (`ScanId`, `SampleRef`), so a bare `int` is a type error.
- A file path is a `Path` from the boundary inward. A `str` path only where an outside API requires
  one, or for an argument echoed as typed, named `raw_…`: `raw_input_dir`.
- `Enum` for closed sets, `.value` at serialisation boundaries. Not `Literal`, `IntEnum` or
  `StrEnum`. `json.dumps` writes an `IntEnum` or a `StrEnum` silently and raises `TypeError` on a
  plain `Enum`, so `.value` must be explicit at each serialisation boundary of a plain `Enum`.
- `Protocol` for a seam with more than one real implementation. Never `ABC`. Composition over
  inheritance, always.
- Name an annotation that you cannot say out loud. Count the names below the outermost:
  `dict[str, list[tuple[float, float]]]` has five, and above four, name the annotation (`NAR005`). A
  callable becomes a `Protocol`, and anything else a dataclass. The reason is a shared name, not
  type safety. For DB-API rows, read `domains.md`.

### Exhaustive dispatch with no fallback arm

```python
def severityFor(outcome: Outcome) -> LogLevel:
    match outcome:
        case Outcome.INGESTED:
            return LogLevel.INFO
        case Outcome.REJECTED:
            return LogLevel.WARNING
        # no `case _`. Adding a member then fails mypy with: error: Missing return statement
```

No `case _: raise ...` and no `assert_never`. With a fallback arm, the code type-checks clean, and a
missing case gets no mypy error. The protection works only when the match returns a value,
so restructure a `-> None` dispatch to return something. Keep the `match` even where a `dict` lookup
looks more natural. A lookup type-checks clean and fails at run time with `KeyError`.

## Data at boundaries

- Parse untrusted input into a **frozen dataclass at one boundary gate**, then never validate again.
  The objection to Pydantic and ORMs is pervasive run-time validation, not a single gate.
- **A parsed record contains only what its input contained.** Where one input format has a field
  and another does not, the field is optional on the shared record, and the check that reads it
  skips `None`. Never substitute a plausible default. A lockfile line with no source gets
  `source: None`, not `'pypi'`.
- Pydantic only at the boundary gate. `TID251` bans the import, so declare `# ruff: noqa: TID251`
  in the gate module, and name the gate function in its module docstring. If a program has a second
  suppression, validation is at two gates, not one.
- An ORM is fine where it adds no run-time validation that the database already does: SQLAlchemy,
  peewee, Piccolo, Django models. `TID251` bans SQLModel, ormar, Tortoise, Pony and SQLObject. A
  migration or a one-off backfill may use a banned ORM, with `# ruff: noqa: TID251` in that module
  and no comment. No `per-file-ignores` list.
- `frozen=True` on every dataclass, including a record built and consumed inside one function. A
  mutable field value is a smell: write a `tuple` where you would write a `list`. A frozen wrapper
  around mutable contents is a half-guarantee that nothing enforces.
- For schemaless input, promote the fields the program computes on to typed attributes, and put the
  remainder in one `Mapping[str, object]` field, not a JSON string. Two traps:
  - never splat the remainder into an output record. With `{'source': path, **entry.extra}`, the
    provenance in your report is overwritten by any `source` key in an untrusted log line. Nest it:
    `{'source': path, 'extra': dict(entry.extra)}`
  - a frozen dataclass with a mapping field is not hashable. `set(entries)` raises `TypeError` with
    no linter warning

## Errors

- Custom exceptions subclass `RuntimeError`, and the name ends in `Error` (`N818`):
  `RejectedSourceError`.
- Handle each failure mode narrowly and separately. Never one `try` around the whole operation. One
  `except (A, B)` arm is right only where the handling is the same. First check whether the same
  handling is right for both failures. A timeout and an unreachable host are different facts and get
  different messages.
- `raise NewError(...) from exc`, **and** log it.
- An error message for malformed input includes the expected form: `bad --now value '2028-11-05'
  (expected "2028-11-05T08:00:00Z")`.
- Log the generic fact once at the raise site. With several raise sites, route them through a
  `reject*()` helper that logs and returns the exception: `raise rejectLine(...) from exc`. Each
  guard is then two lines, and adjacent two-line guards group.
- At the handle site, log what the failure meant there. In a degrade-and-report loop, log each item
  at DEBUG and a per-file tally at WARNING. An operator cannot act on line 4,812 of one file, and
  can act on "4,812 of 10,000 lines rejected".
- LBYL over EAFP. You know your invariants, and you do not know every exception an implementation
  can raise.
- Degrade and report: process the whole batch, collect failures, log a summary, exit nonzero. The
  config gate is the exception. It raises on the first malformed entry and the program exits,
  because when the config is half valid, the job the operator asked for is unknown.

## Module state

- Declare `global` when a function **mutates** module state. A read is exempt. `NAR001` counts
  in-place mutation (`CONFIG.clear()`, `CONFIG['k'] = v`, `CONFIG.attr = v`) and a call to a method
  whose name starts with a configuration verb such as `set`, `add`, `register` or `close`. So
  `global LOG` goes in any function that calls `LOG.addHandler(...)`.
- Declare every attribute in `__init__`. `hasattr(self, ...)` is a red flag.

## Logging

- One stable event name plus structured `extra={...}` fields, never an f-string of prose. Get each
  module's logger with `logging.getLogger(__name__)`. A program configures logging once, in
  `main()`.
- A service, or any program whose logs are collected, writes JSONL through a shared module. A
  single-file tool run by hand prints through the `FieldFormatter` in `domains.md`.
- Never `basicConfig(format='%(levelname)s %(message)s')`. The standard formatter discards
  everything in `extra`, and the tally is lost.

## Configuration, concurrency

Most explicit first:

1. a config file tracked in the repo, parsed into a frozen dataclass, for any deployment setting
2. CLI arguments with `argparse`, for the inputs of a batch tool run by hand
3. the environment through `python-decouple`, not `os.environ`, for secrets and DB URLs
4. `ALL_CAPS` constants for tuning knobs that do not vary by deployment

asyncio is the default for I/O-bound work.

## Testing

- Real dependencies: a real socket on loopback, a real temp SQLite file, a real temp directory. A
  test double is a last resort. Flag each test double as a known gap.
- Hypothesis property tests wherever there is an invariant: round-trips, ordering, conservation,
  numeric range. Example tests cover specific regressions on top. A very slow stateful property test
  may be opt-in, outside CI.
- Test functions are `testSomethingDescriptive`. The pytest default `python_functions = test*`
  collects them.
- Tests go in a separate module, so the program does not import hypothesis. Where one file is
  required, put the tests behind `### tests` before `### vocabulary`, and import hypothesis lazily.

## The module docstring

**Every module opens with a docstring, and anything runnable has a usage example** (`NAR009`). The
module docstring is about what the program is *for*, not how it works. Write for a professional
developer who has the file open, so `API`, `idempotent` and `tuple` are the right words. One idea
per sentence. One word for one thing, and the word is the identifier the code uses.

Required: what it does, an example invocation per meaningful mode, exit codes when there are more
than two, and the shape of input and output where the arguments do not make it obvious.

```python
"""Load a CSV file into a SQLite table.

Each column is typed from its values as INTEGER, REAL or TEXT. A row that does not fit the
inferred types is skipped and reported. The program does not modify an existing table.

Usage:
    $ python3 load_csv.py readings.csv readings.db measurements
    $ python3 load_csv.py readings.csv readings.db measurements --sample-rows 200

Exit codes:
    0  every row loaded
    1  one or more rows skipped
    2  the file, the database or the arguments were unusable
"""
```

**Show the thing.** Where a module reads or writes concrete text, such as a table, a log line, a
report or an input format, paste a real sample and delete the prose it replaces. **Never invent a
sample.** Run the program and paste what it printed, or the `repr` of what the function returned.
For a module that computes records, not text, paste the records. Show one line of each shape, and no
repeats. Expect the sample to cost lines. Keep it small, and re-paste it when the output changes,
because no tool checks it. Where behaviour varies by case, such as a file move or a path
manipulation, show a before/after example.

```python
"""Format the result of a reconciliation as a table for a terminal.

    TEAM              USED     QUOTA   OVERAGE
    platform        550.0G    500.0G     50.0G
    search            1.2T      2.0T         -

Teams over quota come first, worst first. A team within its quota has `-` as its overage.
"""
```

Keep at least one line of the body at column 0, as the last line above does. Otherwise
`ruff format` strips the indent and the sample loses its alignment (`NAR011`).

## Docstring rules

The summary line is mandatory. A body is usually unnecessary.

**Cut a sentence when:**

- it is visible in the file: `frozen=True` on the line above, `| None` in the signature
- its negation is a bug, an absurdity, or code nobody would ship. Assume the reader expects
  competent code, and document only the departures
- it is a language feature, explained
- it is false of the code, or is a consequence of an earlier sentence
- it goes stale and nothing checks it, unless it is a sample

**Compress what survives:**

- name the property: `Rows are keyed on team, total and quota, so runs are idempotent`
- state an ordering as its sort key: `Teams sort by (-over, -used, team)`
- in the summary line, call what the code produces by its real name: `construct a QuotaPolicy`
- stop at the fact. No sentence on why the design is right. A reason that has to survive is a `#`
  comment at the line it concerns

**Write a body only for:**

- an ordering or a tie-break
- a unit, a nullability or a provenance absent from the annotation
- where the leftover, default and failure cases go
- a sample of concrete text the module reads or writes
- a constraint from outside the program
- a guarantee a caller needs: `The call writes no file, prints nothing, and records nothing`

A function gets a docstring when it takes more than three parameters or exceeds 20 lines
(`NAR004`). Below both, the contract goes in `#` comments. The docstring has a summary and a
`Raises:` section. It has `Args:` and `Returns:` only for a fact absent from the signature. Write
`Returns: The number of rows this call added. A repeat run adds 0.`, not `The parsed policy` above
`-> Policy`. An `Args:` entry is for a parameter the body does not consume in the obvious way. Leave
out a fact already in the module docstring, such as the exit codes on `main()`.

## Comments

These rules cover docstring prose, error messages and `--help` text too.

**Test: what information is in this comment and not in the code?**

**Comments are not thinking traces.** Your reasoning through edge cases, <!-- noqa: NAR017 -->
alternatives and spec gaps belongs in your report to the user, not in the code.

**Cut a comment whose content a smart reader would get from the code below it, including the
variable names**, whatever its wording or kind.

When shortening a comment, rewrite the sentence. Do not cut words from the sentence until the
comment fits.

Before writing or rewording a comment, in order:

1. **Rename first.** If the information fits in a name or a type, rename and write no comment:
   `over_quota: ByteCount`, `total_cents`, `rollingMeanSignedError`.
2. **Guarantee it in code.** Establish a cheap precondition, such as sorted input, upstream in the
   call flow, not in the function that depends on it. If a code change removes a trap, make the
   change and write no comment. If explaining how the code works takes more than one plain clause,
   rewrite the code. Name the step, or use the obvious construct.
3. **Match a kind** below, pass its test, and stay off the **Never** list. Deleting is a valid
   outcome. When only the wording breaks a rule, rewrite the wording and keep the content.
4. **Set the depth and sentence form** by the rules below.

**Kinds:**

- **Source**: a fact or requirement from outside the code. Test: it would still be true if the code
  were deleted, and a smart reader would not already know it.
  - `# vendor closes idle sockets at 60 s`
  - `# databases written before 2025/04/03 lack the account_id column`
  - `WARN_THRESHOLD = 1.6  # calibration spec CAL-7, section 3`
- **Fence**: code that looks unusual, where the obvious simplification silently breaks it. Test:
  name the simplification a smart, experienced developer would make, and the defect it causes: a
  wrong result, a crash, a security hole or a performance collapse. A cosmetic difference does not
  count, and neither does a feature. Write the fact the code depends on, then the step the code
  takes because of that fact.
  - `# bool subclasses Python int. Reject it too`, not `# bool subclasses Python int`
  - `# migrate before load. load reads the account_id column`
  - not `# file can change between calls, so not cached`. A cache is a feature, not a
    simplification

  Write `X would` only when X is an alternative the code does not use. When the code under the
  comment does X, state the problem X is there for: `# the endpoint drops the first request after
  idle time. Retry once`.

  ```python
  # Here read_bytes() is used. The alternative, read_text(), would turn \r\n and \r into \n, even
  # inside a quoted CSV field.
  csv_bytes = csv_path.read_bytes()
  ```
- **Decoding aid**: a line a smart reader would need docs or a worked example to read. Test: you
  would look it up. State the intent, not the mechanism.
  - `SIZE_PATTERN = re.compile(...)  # number, then an optional binary unit suffix`
  - give a regex a string it matches and, where the boundary is unclear, a string it rejects. Put
    each string in backticks on a separate line:
    ```python
    # matches:
    # `search_v2`
    # rejects:
    # `x.y`
    BARE_KEY = re.compile(r'[A-Za-z0-9_-]+')
    ```
- **Marker**: no test needed.
  - `FIXME:` incorrect behaviour, or behaviour that breaks soon after deploy. In reachable code, a
    `FIXME` fails `verify.py` (`NAR010`)
  - `TODO:` tech debt, future improvement
  - a stated assumption: `# vendor documents no encoding, UTF-8 assumed`
  - a label on a block of at least 4 lines, ideally 6 or more: `# parse data`
  - a rule a developer must enforce, with capitals scaled to the cost of breaking it:
    `# read-only: NEVER write to the audited readings`

**Never, even when a kind's test passes:**

- what the next line or a single call does
- standard library or language behaviour the reader knows: `<=`, case sensitivity, `None`
- why the file follows this style guide: `so this is a class and not a module`
- decision ids such as `(Q08)` (`NAR012`)
- changelog: an earlier state of the code, or a fixed bug with nothing left of it (`NAR015`)
- alternatives never in the code (`rather than`, `instead of`), except in architecture discussion
- risks far outside the task's scale, and decisions too inconsequential for a later reader to
  reconsider
- future needs nobody has documented or planned
- reassurance that a weakness is fine, such as `deliberately` or `on purpose` (`NAR014`)
- guarantees about other modules or functions, in a comment or a docstring. A docstring is about its
  file alone. Put a module's guarantee in the project's architecture document. Where the check is
  cheap, check it in the code: `while self.items and …`, not `# store() rejects an oversized item,
  so the cache is never empty`
- how one function uses a type, written on the type
- illustrations of a decision just discussed in the session
- a function's return contract. State it in the docstring, and only if the return type does not
  make it obvious (`NAR019`)

**Depth:** in proportion to the idea's difficulty for the reader. `# signed error` on a rolling
mean, more on a novel method. A one-line comment stays one clause, or two short sentences. When the
reader needs the consequence or the action as well as the fact, write a block of full sentences:

```python
# The vendor API returns at most 100 rows per page and no total count.
# Keep requesting until a page comes back short.
while len(page := fetchPage(cursor)) == PAGE_SIZE:
```

**Sentence form:**

- a one-line `#` comment has a lowercase start and no final period. Several lines, and every
  docstring, are sentences
- no semicolon, no dash between clauses, and no second clause on a connective such as `which` or
  `since`, where the reader may attach it to the wrong noun. Write two sentences:
  `# migrate before load. load reads the account_id column` (`NAR013`)
- terse. Drop articles where nothing is lost, never the subject or the verb
- every clause has a subject and a verb. A label is fine: `# least recently used first`. A predicate
  with its subject cut is not: `Bound to one machine` → `The modifier is bound to one machine`.
  `NAR020` flags only the `Named, so …` form
- every noun phrase refers to one real thing, at the moment the sentence is about. Name the
  variable, function, file or value it refers to. Rewrite when the thing does not exist yet, when
  the property belongs to another object, or when two things fit: `# open() creates a missing log
  file` → `# open() creates the log file if it doesn't exist`. Repeat the noun. Do not write a
  stand-in such as `it`, `that` or `the one`
- the concrete thing, not `what the X does to the Y`
- a claim is true in every case that reaches it. Otherwise, name the case. List the paths that
  reach the sentence: `# an expired item is removed on lookup` → `# an expired item is removed on
  lookup, or before any eviction`. Count the unit the code counts. In an error message, advise only
  steps the program has not taken: `no policy.json in fixture/. Pass --policy to use another file`
- when a comment covers a second approach, start that sentence with `Alternatively,`
- possessives and noun compounds over relative clauses: `the archive's collections`. Trade terms
  over paraphrase: `has no side effects`. Modifiers before the noun: `JSONL logs`
- the conclusion, not the derivation: `None when malformed`. Cut a clause about an internal check,
  structure or attribute unless the reader needs it to act
- no intensifiers such as `exactly`, `always` or `simply`, unless the sentence means something else
  without one: `exactly two decimal places`
- the full term when a short form is ambiguous: `timezone`, not `zone`
- contractions and the imperative. Callables as `name()`, and no article before an identifier
- only names the reader can resolve from the comment's position
- the general case: `records are separated by blank lines`, not `two records`
- a worked example matches what the code does for every case in it
- with code or an abstract noun as the subject, only verbs for what code literally does: `returns`,
  `raises`, `reads`, `writes`, `calls`, `skips`. Never agency or containment: `finds`, `knows`,
  `holds`, `carries`, `keeps its`, `costs`. Write `a module has one function`, not `a module holding
  one function`. The test is whether the subject can perform the verb. Documents get no exception:
  write `named in the report`. A table or example on the page can show what is in it (`NAR016`,
  `NAR017`)
- no `is what`, no `its own` (`NAR018`)
- a comment on one branch of a `match` or `if` chain is about that branch alone. A reason that
  covers every branch goes above them once
- directly above the statement it concerns, not above its enclosing block. Inside `try:`, above the
  call, not above `try:`. A comment on an argument goes above the call that passes it. End-of-line
  for a short note

`verify.py` flags some of these faults, and a clean run is no evidence about the rest. Silence a
false positive with `# noqa: NARxxx`.

## Procedures

**Setup** happens once per machine and once per project. **Verify** and **Prose review** follow
once the code is written. **Published prose** applies to each page you write, such as a README.

### Setup

Once per machine, make one lint venv and reuse it for every project.

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

Run the `uv pip install` line again when `requirements-lock.txt` changes. On Windows, use `py` or
`python` wherever `python3` appears.

Once per project, merge `pyproject-snippet.toml` into the project's `pyproject.toml`, or copy it as
the `pyproject.toml` of a new project. With any other file name, `verify.py` exits 2.

### Verify

```
python3 "${CLAUDE_SKILL_DIR}/verify.py" .
```

Run it from the project root, on any path. It rewrites files with `ruff check --fix` and
`ruff format` unless you pass `--no-fix`, then runs `pylint`, `mypy --strict`, `checks.py`, `vermin`
and `agentverbs.py`, and prints the output of each tool that fails. Exit 0 is a pass, 1 is a
finding, and 2 is a missing tool or config, so nothing was checked. Do not call the tools by hand
or grep their output: if a binary is missing, the output is empty, and empty output looks like a
pass. Read `tooling.md` before you change config.

### Prose review

After a passing run, review every comment, docstring, error message and `--help` string that you
wrote or changed in this task. `verify.py` prints two lists: every comment and docstring summary,
and each subject that cannot act paired with its verb. For each sentence in scope:

1. Name the subject and the verb. Can that subject perform that verb? Most pairs are in the second
   list. A subject that is misread in the parse is not in it.
2. For each noun phrase, name the variable, function, file or value it refers to. If none fits, or
   two do, rewrite.
3. List the code paths that reach the line: each branch, each caller, each failure. Check the claim
   on every path.
4. Test the sentence against **Sentence form**, and the comment against the restatement gate.

Fix what fails and run `verify.py` again.

### Published prose

A README, a doc page or an HTML report that you write follows these prose rules. When you rewrite
part of a page, the rules cover the section you changed. A page that a person wrote is left as it
is unless the user asks. If the rest of a page is clearly written by an LLM, suggest cleaning it.
Name each page to `verify.py`, such as `python3 "${CLAUDE_SKILL_DIR}/verify.py" README.md`. Only the
wording checks and `agentverbs.py` run on a page. Take the steps of **Prose review** for each
sentence you wrote. Silence a false positive with `<!-- noqa: NAR017 -->` on its line.
