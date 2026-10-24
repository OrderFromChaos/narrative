---
name: python
description: Write or review Python in the Narrative house style, with mixedCase functions, main() first with types last, parse-at-the-boundary dataclasses, no ORM that re-validates what the database checks, explicit global on mutation, exhaustive match without a fallback arm, and a verified ruff/pylint/mypy toolchain. Covers multi-module architecture too. Which module may import which, when one file becomes several, what goes in a package __init__.py, where a shared type belongs, and when to take or contain a third-party dependency. Use for any Python written in or for this codebase, when laying out modules or packages, and when reviewing a diff against this style. Always load nar:core with this skill: nar:core has the rules for comments, docstrings and error messages.
---
**Before you write or review anything, load the skill `nar:core` with the Skill tool**, unless
`nar:core` is loaded already. `nar:core` has the rules for comments, docstrings, error messages and
published pages, and the steps of **Writing a comment** and **Prose review** that **Procedures**
names.


# Narrative Python

**0% of reader effort on rote diffing, 100% on design.** (R2b-P0) Every rule below is a case of
that, or of the second principle, to prefer what the type checker and IDE can follow.

Four near-identical lines that differ in one token make the reader compare them token by token, and
every comparison is a chance to miss the difference. One parameterised call removes the comparison.

This is the root of DRY, of one-name-for-one-thing, of consistent ordering, and of the ban on
gratuitous variation. When two rules conflict, follow the rule under which the reader diffs less.

Second principle, for representation choices: **prefer what the type checker and IDE can follow**,
even when a looser form is more flexible. State in a `dict[str, Any]` passes `mypy --strict` only
with a `cast()` or a key lookup at every use. Typed attributes pass with neither. (R3-P2-rank)

**The steps to run while writing and before you finish are in Procedures, the last section.**

**This document applies to every file, however many there are.** Naming, layout, types, errors and
docstrings apply to each module of a package exactly as they apply to a single-file program.

`architecture.md` adds what happens **between** files: which module may import which, where a shared
type belongs, when one file becomes several, and which modules may import a third-party dependency.
Read it when the program spans more than one module or imports a third-party package. Skip it for a
single-file program, where none of `architecture.md` applies.

The reason for each rule is in the rule's text, so read the text and not the id after the rule. The
ids are provenance. They resolve in `benchmark/decisions.jsonl` in the source repository,
`github.com/OrderFromChaos/narrative`. That repository does not ship with the skill. **A rule
with no id and no linter behind the rule does not belong here.**

## File layout

```python
from __future__ import annotations   # required for types-last

import struct                        # plain imports, alphabetised
import sys
from pathlib import Path             # then `from` imports, alphabetised
from typing import NewType
                                     # TWO blank lines
                                     
LOG_PATH = Path('jsonl_logs/app.jsonl')     # tunable constants, grouped BY CONCERN
DEFAULT_DB_PATH = Path('app.db')
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
                                     # one blank line
LOG = logging.getLogger(__name__)    # globals baked into the design sit apart


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

- `main()` returns an exit code. Call it as `sys.exit(main())`. All executable code is in
  `main()`. (Q10)

- Caller before callee throughout. At module level, do not *call or subclass* anything defined
  further down. Watch for a constant whose **value** references an Enum member or class. Annotations
  are safe, because the future import makes them lazy. (R2-10, R3a-03)

- That is an **ordering** rule, not a placement ban. A constant whose value is an Enum member is
  legal in `### vocabulary` immediately after that Enum, and that is the constant's only legal
  module-level position. Do not contort around it. (R4-03)

- Order constants by concern. Constants a dev would look for at the same moment go together. All the `_S`
  durations adjacent, then non-duration limits, then hosts, then wire literals. Type usually
  correlates, and concern decides. No blank lines inside the block. (R3a-16, R3a-15)

- 120 columns. Absolute imports only. Single quotes (docstrings and multiline: double).

- Separate logically self-contained blocks inside a function with **one blank line**. That is its
  only meaning here. Short guards written as a group stay grouped, and two adjacent two-line
  `if ...: raise` checks belong together. No blank line after a docstring. (R3a-01)

  **No tool checks this.**
  Place a blank line by these five rules: (`R8-NAR008`, `R8-NAR008-rule`)

  - a body of **8 lines or under takes no internal blanks at all**
  - blanks **recur into nested blocks**, and one loop body can take four
  - **a multi-line statement and the statement that consumes the result are
    one step**, so `executemany` then `commit`, and a constructor then the `return` of the
    constructor's result, stay adjacent
  - a blank precedes a `return` when the phase before the `return` is unrelated, and not when the
    returned value was just built
  - **length is not the trigger**, in either direction. A long statement earns no blank after the
    statement, and a short group of statements still earns one before the next group

- If a guard grows to three lines because it logs before raising, move the log call into a
  `reject*()` helper that logs and returns the exception. The guards are two lines again and group,
  and the raise-site rule still applies. (R4-05)

- A `def` with >3 **positional** arguments puts each on a separate line with a trailing comma, even
  under 120 columns. **Calls are exempt.** A signature is read once and a call site is read
  everywhere, so the same rule applied to calls costs lines without buying clarity. (R2b-B1)

- **Keyword-only parameters do not count**, so a function may take any number of them. That is also
  the escape hatch at exactly four. Put `*` before the optional ones and they stop counting, and
  they read as optional in the signature anyway. Note `NAR004` counts *every* parameter, because
  each one is part of the contract even when the caller may omit the parameter. (R5-06)

- Long strings: implicit concatenation in parens. Never `"""` for data, because its whitespace
  becomes part of the value. (Q03)

## Python 3.11 floor

`ruff` targets `py311`. Check with `vermin -t=3.11- --violations`. (R7-E07-floor)

Run tasks that should fail together in an `asyncio.TaskGroup`. Hand-rolled cancellation fails
silently. Give independent handlers, such as one per client connection, a task each. A `TaskGroup`
cancels every task when one raises. (R7-E07-floor, R10-taskgroup-scope)

- **`except TimeoutError` is correct** around `asyncio.wait_for`. At 3.11 `asyncio.TimeoutError`
  *is* the builtin, so the two are one class. (R3a-06)

- Anything added in 3.12 or later is out, including the `type` statement and PEP 695 generics.

- On a guard for a runtime newer than the floor, the comment has the version: `# on 3.12.1 and
  later, wait_closed() waits for open connections`. (R10-version-guard)

## Structure inside a function

- Guard clauses and early return over nesting. (Q06)

- **Write a skip guard as the negation of what a valid item is.** `if not (name_match and
  entry.is_file() and not entry.is_symlink()):`, not `if name_match is None or entry.is_symlink()
  or not entry.is_file():`. (R10-positive-guard)

- Comprehensions may have any number of `if` clauses at a single level. Any **nesting** becomes an
  explicit loop. (Q07)

- **Extract a block when you can foresee reusing or testing it separately**, not merely because it
  has a name. `computeChecksum` extracts because many places could call it. The two halves of
  `openDatabase` do not extract, even though each is nameable. A one-line helper called once is
  residue. (R2-09, R2b-E1, R2b-E2)

- If an extracted function would take 5+ parameters, that is a **missing owner**, not a reason to
  leave the code inline. Find where the values belong. That owner is a **class** when two of it can
  exist at once, and a **module** otherwise. A frozen record is the answer only when nothing has
  behaviour over the values. If a general name for the group is hard to pick, the values are not
  a real group. (R7-C05-resolved, R7-C05-naming)

- Always collapse duplicated-but-drifting code, even when the shared version takes an extra
  parameter. To localise the difference is the whole point. (R2b-E4)

- Mixed `and`/`or` parenthesises each group explicitly. Never `A and B or C and D`. Ruff cannot
  produce this form, so `SIM114` is disabled and `NAR007` enforces the form. (R2b-B4)

- Merge branches that share a body **only where the type checker narrows the merged branch the same
  way.** If you merge two `isinstance` branches, even with parentheses, mypy widens the subject back
  to a union and loses the narrowing. Two explicit branches are better than one clever condition.
  (R2b-B5)

- Collection literals get one item per line **wherever `ruff format` explodes them**. That is any
  literal it cannot fit on one line. This is the output of `ruff format`, not a further rule. A
  short literal it leaves packed is already correct. A word-list-shaped literal may use a
  `# fmt: off` / `# fmt: on` fence to stay packed. (R2b-B2)

## Naming

- Module filenames `snake_case`. Functions and methods `mixedCase`. Classes and types
  `PascalCase`. Variables and arguments `snake_case`. Module constants `ALL_CAPS`. **In a
  `snake_case` codebase that you did not write, match local convention.** Detect before you write.

- Spell names out. No `img_arr`, `cfg`, `idx`. (Q11)

- **A function name starts with a verb, and the verb's object is what the function returns.**
  `parsePolicy`, `readManifest`, `extractPackagesFromLockfileText`, `computeDeletionCutoff`. Not
  `policyIn`, not `cutoffFor`. A name built from a preposition is about the input instead.
  (R9-03)

- **A name is clear without its module**, and the module qualifier does not count toward the name. A
  reader who has never opened the module must understand the name. `requirements_lock.packagesIn` is
  clear at the call site and unclear at the definition, and nothing stops a second module declaring
  a second `packagesIn`. **Two functions in one package do not share a name.** (R9-03, R7-B06)

  **Length is not the defect.** Where the clear name is the longer one, write the longer one.

- Predicates are bare adjectives, and take no verb: `readyForScan`, not `isReadyForScan`, and
  `belowMinimum`, not `checkBelowMinimum`. A predicate returns the answer to a question. (Q12)
  Dunder and protocol methods are named by the language.

- **Do not restate a domain type in a parameter name**: `config: RebinConfig`, not
  `rebin_config: RebinConfig`. The prefix duplicates the type and adds nothing. (Q11)

- **With a generic type, the parameter name is the only place the thing is named.** `Path`, `str`,
  `int`, `bytes`, `dict` and `object` constrain only a value's shape. Write
  `policy_json_path: Path`, not `path: Path`, and `manifest_text: str`, not `text: str`. The rule
  above bans a redundant prefix, not an informative one.

- **Raw and parsed forms get different names.** Prefix the raw form with `raw_`: `raw_at: str` from
  the file, `at: DateTime` once parsed. Never `at` beside `parsed.at`. (R10-raw-names)

- **Restate the type where the bare name would shadow an import.** A program that imports a
  first-party module by name burns that identifier at module scope, so the local becomes
  `results_store: Store`. (R8-B06-Q11)

- `from pathlib import Path`, not `pathlib.Path`. Avoid fully qualified names, but keep the module
  where it adds meaning (`struct.unpack`, `json.loads`, `asyncio.wait_for`). Import the class,
  keep the verb qualified. (R3a-08)

## Constant placement

Name every magic number. (Q09) Then place it by this test:

> Could someone change this value safely knowing only what the program **does**, or would they need
> to understand how the function **works**?

The latter is an implementation detail and belongs **inside** the function, still `ALL_CAPS`. Put
`MAGIC`, `HEADER_FORMAT`, a padding byte, a derived size, a checksum mask, and the SQL of a single
function inside. A log path, an archive directory, a glob, exit codes and operator-tunable timeouts
stay at module level. (R3a-12)

*No tool checks this. This is review judgement.*

## Types

- Annotate every parameter and return. `mypy strict = true`, `disallow_any_explicit` left **off**
  so a written `Any` is visible and greppable. (R2-11)

- Annotate the true requirement. A function that only iterates should use `Iterable`, not `list`.
  (Q13)

- `NewType` for domain primitives (`ScanId`, `SampleRef`), so a bare `int` is a type error. (Q15)

- **A file path is a `Path`** from the boundary inward. A `str` path only where an outside API
  requires one, or for an argument echoed exactly as typed, named `raw_…`: `raw_input_dir`.
  (R3a-10, R10-path-type)

- **Money is exact.** Parse an amount with `Decimal(raw)` from the string, never through `float`.
  `Decimal(0.1)` keeps the float's error. Round once, with the mode explicit:
  `cents = int((Decimal(raw) * 100).to_integral_value(ROUND_HALF_UP))`. Without an explicit mode,
  `Decimal` rounds half to even. A computation that yields fractions of a cent, such as
  rate × minutes × multiplier, stays in `Decimal`, integers or `Fraction` until that one rounding.
  Store and serialise integer cents, named `…_cents`. `json` and `sqlite3` reject a `Decimal`.
  (R10-money-cents, R10-money-decimal)

- **Dates and times use `pendulum`**, unless `datetime` is tightly integrated with the repository,
  so that removing `datetime` would be hard. Replace a small `datetime` use with `pendulum`. A
  library that returns `datetime` values, such as `tomllib`, `sqlite3` or a JSON decoder, is a
  boundary. Convert each value to pendulum where the value enters. (R10-pendulum,
  R10-pendulum-boundary)

- `Enum` for closed sets, `.value` at serialisation boundaries. Not `Literal`, not `StrEnum`. (R2-08)

- `Protocol` for a seam with more than one real implementation. Never `ABC`, because that is
  inheritance. (R2-01)

- **An annotation you cannot say out loud needs a name.** The test is conversational. Could you
  refer to this type in a normal discussion with another programmer? `park(car: Car)` reads and
  discusses. `park(car: dict[str, list[tuple[float, float]]])` does neither. (NAR005, R8-D27-resolved)

  **The measure is how many names it contains, below the outermost.** `Car` contains none.
  `dict[str, list[tuple[float, float]]]` contains five, and above four, give the annotation a name.
  A callable becomes a `Protocol`. Anything else becomes a dataclass. (`NAR005`, `R8-D27`)

  **The DB-API is the standing exception.** `sqlite3.executemany` takes a sequence per row and
  raises `ProgrammingError: parameters are of unsupported type` on a dataclass. Instead, use a
  `NamedTuple` for rows. It is a tuple, so `executemany` takes a `NamedTuple`. Its fields have
  names. Use `?` placeholders, and say why in a comment. (`R8-D27`, `R10-namedtuple-rows`)

  ```python
  # sqlite3.Cursor.executemany() rejects dataclass rows. A NamedTuple is used instead
  class FindingRow(NamedTuple):
      path: str
      line: int
      code: str
      detail: str


  def storeFindings(connection: sqlite3.Connection, rows: list[FindingRow]) -> None:
      connection.executemany('INSERT INTO findings VALUES (?, ?, ?, ?)', rows)
      connection.commit()
  ```

  The reason is a shared name, not type safety. Only `NewType` makes swapped coordinates a type
  error (Q15).

- Composition over inheritance, always.

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

**A `case _: raise RuntimeError(...)`
one-liner looks equivalent and is not. It type-checks clean and silently accepts the missing
case.** No helper, no `assert_never`. (Q18, R3a-07)

Limitation: this works only when the match returns a value. A side-effecting `-> None` dispatch
gets no protection. Restructure it to return something.

**Keep the `match` even when a mapping looks more natural.** Only a `match` fails mypy when a new
member goes unhandled. A `dict` lookup and an `IntEnum` both type-check clean and fail at run time
with `KeyError`.

Speed does not change this. The difference between the forms is below run-to-run noise. (R4-03)

`IntEnum` is not a substitute. It makes `json.dumps({'level': LogLevel.INFO})` silently emit `20`
where a plain `Enum` raises `TypeError`, and the `str()` of an `IntEnum` changed across releases.
**`StrEnum` is available at the 3.11 floor and is not a substitute either**, for the same reason. It
serialises silently where a plain `Enum` makes the boundary explicit. Keep the plain `Enum` and the
exhaustive `match`. (R4-03, R7-E07-floor)

## Data at boundaries

- Parse untrusted input into a **frozen dataclass at one boundary gate**, then never validate
  again. The objection to Pydantic/ORMs is *pervasive runtime validation*, not a single gate.
  (Q02, Q14, Q17)

- **A parsed record contains only what its input contained.** Where one input format has a field and
  another does not, the field is optional on the shared record, and the check that reads the field
  skips an absent value. **Never substitute a plausible default**, because the output then contains
  a fact that the file does not. (R9-01)

  A lockfile of `name==version` lines has no source. Give the record `source: SourceName | None`
  and let the source check pass on `None`. Do not stamp `'pypi'` on every package. Under a policy
  that allows only `internal`, an invented source turns every line of every lockfile into a finding
  that the manifest never justified.

- **Pydantic can be used for standardizing user input, at the boundary gate, and nowhere else.**
  `TID251` bans the import, so declare `# ruff: noqa: TID251` in the gate module, and name the gate
  function in the gate module docstring. A second suppression in one program means validation is no
  longer at one gate. (R8-D10, R10-pydantic)

- **No framework should validate output.** FastAPI makes a route's return annotation the route's
  response model, so every response is validated at run time. Pass `response_model=None` in the
  route decorator, and keep the annotation for mypy. (R10-pydantic)

- **`frozen=True` is the default for every dataclass.** It has nothing to do with boundaries. A
  record built and consumed inside one function is frozen for the same reason a parsed one is.
  (R8-D11-resolved)

- Drop to mutable only when a **field's value is mutable**, and treat that as a smell rather than
  a decision. Reach for a `tuple` where you would write a `list`. A frozen wrapper around mutable
  contents is a half-guarantee. `dataclasses` will not stop you writing through it, so the bug grows
  quietly and surfaces at run time with nothing to catch the bug. The standing exception is the
  schemaless remainder below, where a `Mapping` field is the prescribed shape.

- **Genuinely schemaless input**: promote the fields the program computes on to typed
  attributes, and put the remainder in one `Mapping[str, object]` field. To flatten it to a JSON
  string costs a second `json.loads` downstream, makes the remainder unaddressable by `jq`, and
  forces the reader back through `Any`. (R4-04)

  A remainder field has two traps:

  - **Never splat the remainder into an output record.** `{'source': path, **entry.extra}` lets an
    untrusted log line with a `source` key **forge the log line's provenance in your report**.
    Nest it: `{'source': path, 'extra': dict(entry.extra)}`.

  - `frozen=True` plus a mapping field is **not hashable**. `set(entries)` raises `TypeError` at
    run time with no linter warning. The code works until someone dedupes.

- **An ORM is fine where it makes database work easier, as long as the ORM adds no run-time
  validation that the database already does.** The cost is per row and per request, and worst on a
  hot path, such as an endpoint that returns database values. SQLAlchemy, peewee, Piccolo and Django
  models run no validation on write or on read. `TID251` bans the ORMs that do: SQLModel, ormar,
  Tortoise, Pony and SQLObject. A migration, a healing script or a one-off backfill can still use
  one: declare `# ruff: noqa: TID251` in that module. There is no `per-file-ignores` list. An
  exception is a property of the module, not of a glob that drifts from the tree the glob matches.
  Do not explain a suppression that follows this rule. Leave the suppression without a comment.
  (Q17, R6-03, R6-07, R7-D04, R7-D04-generalised, R10-orm-validation)

## Errors

- Custom exception types subclassing `RuntimeError`, not `Exception`. (Q20)
- **The name ends in `Error`.** Ruff `N818` enforces this and rejects `SourceRejected`. Use
  `RejectedSourceError`.

- Handle each failure mode narrowly and separately. Never one `try` around the whole operation with
  a tuple of unrelated exception types. (Q19)

- **Related means the handling is the same, not that the classes share a base.** Where two failures
  produce one outcome, one `except (A, B)` arm is correct and two identical arms are the
  rote diffing banned by the top principle. But check the premise first. Two arms that look
  identical usually should not be. A timeout and an unreachable host are different facts and deserve
  different words, and writing the same string twice is how that gets lost. (R8-D24-resolved)

- `raise NewError(...) from exc`, **and** log it. Both. (Q21)

- **An error message for malformed input includes the expected form.** `bad --now value '2028-11-05'
  (expected "2028-11-05T08:00:00Z")`. An example in the docstring also works. (R10-expected-form)

- **Log the generic fact once at the raise site, however you factor that.** A parser with six
  raise sites does not get six log statements. Route them through a helper that logs and returns
  the exception, then `raise rejectLine(...) from exc`. The helper emits the same records as six
  inline log calls and costs fewer lines. (Q23, R4-02)

- **At the handle site, log what the failure meant there, but in a degrade-and-report loop log the
  aggregate, not the item.** This is the rule that matters. Per-item handle-site logging on a file
  of 10,000 bad lines writes a record per line and megabytes of output. Log the item at DEBUG and a
  per-file tally at WARNING. That is tens of records and kilobytes, and every item still appears
  under `--verbose`. (R4-02)

- **Level follows from what an operator can act on.** A per-item failure is DEBUG, the tally is
  WARNING. An operator cannot act on line 4,812 of one file. An operator can act on "4,812 of
  10,000 lines rejected". (R4-02)

- LBYL over EAFP. You know your invariants, you do not know every exception an implementation
  can raise. (Q22)

- Degrade and report: process the whole batch, collect failures, log a summary, exit nonzero. Never
  abort on the first bad item. (Q24)

- **The config gate is the exception.** (R8-D25-resolved) `Q24` governs the batch a program
  processes, not the configuration of what to process. With a half-valid config, what the
  program was asked to do is unknown, so the gate raises on the first malformed entry and the
  program exits. Degrading there would run the job the operator did not ask for.

## Module state

- **`global` marks a side effect, not a dependency.** Declare it when a function *mutates* module
  state. A read is exempt. (R2b-G1)

- Python already forces `global` to rebind. Python does not police in-place mutation, and it passes
  every linter: `CONFIG.clear()`, `CONFIG['k'] = v`, `CONFIG.attr = v`. That is `NAR001`.

- `NAR001` also counts a call to a method whose name starts with a configuration verb, such as
  `set`, `add`, `register` or `close`. So a function that calls `LOG.addHandler(...)` declares
  `global LOG` even though the function never rebinds `LOG`. (V-03)

- Every attribute declared in `__init__`. `hasattr(self, ...)` is a red flag. (Q04)

## Logging

One stable event name plus structured `extra={...}` fields, never an f-string of prose. The
message is a queryable key. (Q08)

**Get each module's logger with `logging.getLogger(__name__)`.** In a package used as a library, add
`logging.NullHandler()` to the package logger once, in the package's top-level `__init__.py`.
Without it, the last-resort handler prints the package's warnings to stderr in a program that
configures no logging.
In a program, configure logging once, in `main()`, and add no NullHandler. (R10-nullhandler)

**JSONL output is for machine reading. For terminal output, don't use JSONL.** (R5-03,
R8-D23-resolved)

- **A service, or any program whose logs are collected**: JSONL. Always import JSONL logging from a
  shared module. Don't vendor it.

- **A single-file tool run by hand**: the short field formatter below.

**Do not use `basicConfig(format='%(levelname)s %(message)s')`.** The standard formatter discards
everything in `extra`. `LOG.warning('merge.rejected', extra={'rejected': 4812, 'total': 10000})`
then prints `WARNING merge.rejected`, and the operator never sees the number that the tally rule
exists to give them. Follow the event-name rule with that formatter and the logs are worse than an
f-string. (R5-09)

```python
_STANDARD = frozenset(logging.LogRecord('', 0, '', 0, '', None, None).__dict__) | {'message', 'asctime'}
_LOCATION = ('module', 'lineno', 'funcName')


class FieldFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extra = {k: v for k, v in record.__dict__.items() if k not in _STANDARD}
        located = {key: getattr(record, key) for key in _LOCATION}
        fields = ' '.join(f'{k}={v}' for k, v in sorted({**located, **extra}.items()))
        return f'{record.levelname} {record.getMessage()} {fields}'
```

That prints `WARNING merge.rejected funcName=merge lineno=88 module=loader rejected=4812
total=10000`. It has the tally an operator acts on and the location of the call site.

## Configuration

Most explicit first:

1. **A config file tracked in the repo**, parsed into a frozen dataclass. This is the default for
   any deployment setting. Infrastructure becomes code-defined and diffable. (R3a-02)

2. **CLI arguments** for the inputs of a batch tool invoked by hand. `argparse`.

3. **Environment** for secrets and DB URLs, via `python-decouple`, not `os.environ`. (R2-06)

4. **`ALL_CAPS` constants** for tuning knobs that do not vary by deployment.

## Concurrency

asyncio is the default for I/O-bound work. (R2-04)

## Testing

- **Real dependencies**: a real socket on loopback, a real temp SQLite file, a real temp directory.
  A test double is a last resort for something you cannot run. Flag each one as a known
  gap. With a fake transport, tests pass while production fails. (R2-02, Q16)

- **Property-based tests (hypothesis) wherever there is an invariant**: round-trips, ordering,
  conservation, numeric range. Example-based tests cover specific regressions on top. A very slow
  stateful property test may be opt-in rather than run in CI. (R2-12)

- **Test functions are `testSomethingDescriptive`**, in camelCase with a `test` prefix. The
  conventional `test_parse_header_roundtrips` fails the `mixedCase` gate this style mandates. The
  camelCase spelling passes pylint, *and* the pytest default `python_functions = test*` still
  collects the test function.

- Tests are in a separate module, not in the program file. A `from hypothesis import given` at
  module scope makes the program raise `ModuleNotFoundError` before the program reaches `main()` on
  any machine without the test library.

  Where a single file is required, put the tests behind `### tests` before the
  `### vocabulary` divider and import hypothesis lazily.

## The module docstring

**Every module opens with a docstring. Anything runnable has a usage example.** A reader meets it
first, before `main()`, so it is about what the program is *for*, not how the program works.
(R5-02, NAR009)

**Write for a professional developer who has the file open.** That reader knows the language and the
vocabulary of the trade, so `API`, `idempotent` and `tuple` are the right words and a plain-English
circumlocution around them is worse. One idea per sentence. **One word for one thing, and the word
is the identifier the code uses.** With `unassigned` in a docstring where the code has
`unattributed`, a reader greps for something that is not there. (R9-09)

The prose rules for comments and docstrings are in **Comments**.

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

Required:

- what it does
- an example invocation per meaningful mode
- exit codes when there are more than two
- the shape of input and output where the shape is not obvious from the arguments

`NAR009` enforces the docstring. For a module with a `__main__` block, `NAR009` also enforces the
example.

### Show the thing, do not describe it

**Where a module reads or writes concrete text, paste a real sample of that text.** A rendered
table, a log line, a report, a converted value, an input format. **Delete the prose the sample
replaces** rather than keeping both. (R9-08)

**Never invent a sample.** Run the program and paste what it printed, or paste the `repr` of what
the function returned. A format that appears nowhere in the program is a lie in the shape of
documentation, and is worse than the prose the format replaced, because a reader cannot tell an
invented sample from a real one. This is the docstring case of the boundary rule above. **Do not
state what you did not observe.** A module that computes records rather than rendering text pastes
the records.

**Show one line of each shape, not the whole output.** One team row, one over-quota line, one file
outcome, and no repeats. The reader needs every shape the module can emit and needs no volume.

**A sample goes stale and no tool checks the sample.** Keep it small, and re-paste the sample when
the output changes.

**Expect it to cost lines.** The sample is there for exactness, not brevity. A reader learns
the column order, the units and the alignment from three rows of a table and cannot learn them from
a sentence about the table having columns.

```python
"""Format the result of a reconciliation as a table for a terminal.

    TEAM              USED     QUOTA   OVERAGE
    platform        550.0G    500.0G     50.0G
    archive         120.0G    100.0G     20.0G
    search            1.2T      2.0T         -

Teams over quota come first, worst first. A team within its quota has `-` as its overage.
"""
```

**Keep at least one line of the body at column 0**, as the last line above does. `ruff format`
strips the common leading indent from a docstring body, so a docstring whose body is *entirely*
indented gets flattened and the sample loses alignment. With one unindented line, the indent
is kept. The check is listed in `tooling.md`.

Avoid the same table as prose:

```python
"""Format the result of a reconciliation as a table for a terminal.

The table has one row for each team, then the largest paths of each team above its quota, then
the bytes that no team owns, then the outcome of every file. Every size carries a unit suffix.
"""
```

A conversion takes a table of cases rather than a sentence per case:

```python
"""Convert a size with a unit suffix to a count of bytes, and back.

    4096   ->          4096
    12K    ->         12288
    1.5G   ->    1610612736
    2T     -> 2199023255552

A unit is a power of 1024. A number with no suffix is a count of bytes.
"""
```

### Docstring rules

The summary line is mandatory. **A body is not, and usually does not earn its place.** (R9-09)

**Cut a sentence when any of these is true:**

- **It is visible in the file.** `frozen=True` is on the line above. `| None` is in the signature.
  A reader who has the file open does not need either restated.
- **Its negation would be a bug, an absurdity, or an implementation nobody would ship.** Negate the
  sentence and read it back. `it never holds a value that the file did not state` negates to a bug.
  `An empty line holds nothing` negates to an absurdity. `Other files are skipped, so the quota file
  can share the directory` negates to a scanner that dies on a stray file. Nobody would ship that scanner.
  All three are free sentences and all three go. **Assume the reader expects competent code, and
  document only the departures.**
- **It is a language feature, explained.** `Such a field holds None` repeats what optional means.
- **It goes stale and nothing checks it**, unless it is a sample you accept that cost for.

**Compress what survives:**

- **Name the property, do not explain it.** `Rows are keyed on team, total and quota, so runs are
  idempotent` replaces three sentences about idempotence.
- **State an ordering as its sort key.** In prose, a multi-level sort is ambiguous between one
  composite key and two separate sorts. `Teams sort by (-over, -used, team). The paths inside a team
  sort by (-size, path)` settles that, and the tie-break on `team` is visibly ascending while the
  numbers run descending. In prose, the same information is longer than the key.
- **In the summary line, use the real name of what the code produces.** `Read the quota file, and
  construct a QuotaPolicy accordingly` beats `Read the quota file, and answer what it states about a
  team and about a path`, a paraphrase of a type that already has a name.
- **Stop at the fact.** `The first malformed field stops the read.` is the rule. A following
  sentence on why stopping is right is not functionality. This is `R9-02` one step further in. The
  ban is not only on style-guide justification but on justifying the design at all. Where a reason
  has to survive, it is a `#` comment at the line the reason concerns.

**A body earns its place for these, and in practice for nothing else:**

- an **ordering or tie-break**, invisible without reading a sort key
- a **unit, a nullability or a provenance** absent from the annotation — `Sizes are plain byte
  counts`, `host is null when the entry's report has no host`
- **where the leftover, default and failure cases go**. Most awkward docstrings are awkward because
  they circle an unstated default.
- a **sample** of concrete text the module reads or writes
- a **constraint from outside the program** — `the standard formatter of logging discards extra`
- a **guarantee a caller needs** — `The call writes no file, prints nothing, and records nothing`

- **A function gets a docstring when the function's contract is complex**, meaning the function
  takes more than three parameters, or exceeds 20 lines. Below both, the contract goes in `#`
  comments. Raising is not a trigger, because the style routes raise sites through a `reject*()`
  helper and every two-line guard that calls one contains a `raise`. (Q05, R2-03, R2-05, R5-05,
  R8-D18-resolved)

  The trigger is contract complexity, not length alone, so the parameter count sits beside the line
  count. A bare line threshold is easy to get around by fragmentation. Splitting a 21-line
  function into two 12-line ones deletes the obligation without simplifying either contract.

- **The docstring has a summary and a `Raises:` section. It has `Args:` and `Returns:` only where
  they give a fact absent from the signature.** `NAR004` enforces `Raises:`, because an exception is
  the one part of a contract absent from every annotation. (R8-D28-resolved)

  Write `Returns:` for an ordering, a nullability, a unit, or a count whose meaning is not obvious:
  `The number of rows this call added. A repeat run adds 0.` Do not write `The parsed policy`
  above `-> Policy`. Write an `Args:` entry for a parameter the body does not consume in the obvious
  way: `manifest: Where the text came from, for the rejection message.` Do not write
  `path: The file to read.`

  A section that duplicates the module docstring is worse than an absent one. When the exit codes
  are already in the module docstring, leave them out of the docstring of `main()`.

- Write nothing in a docstring that the code does not do, and no consequence that an earlier
  sentence already implies. (Q05)

- **A docstring is about its file alone.** Do not assert what another module does, do not claim to
  be the only place something happens, and do not count callers. `nothing outside this module
  imports sqlite3` and `this is the one place that builds it` are claims that no tool checks and
  that the next commit can make false. Name another module only where a reader of *this* file needs
  the name in order to use this file. (R9-02)

- Where semantics vary by implementation (file moves, copies, path manipulation), **show a
  concrete before/after example**, not prose. (R3a-11)

## Comments in Python

These rules add to **Comments** in `nar:core`. Each heading below is the name that `nar:core` uses
for the rule.

### Library facts

For a fact about the Python standard library, read the source or the Python documentation and check
the fact. (R11-rewrite-from-code)

### Source facts

A fact about a value from outside the code goes above the code for the value (J1-F12):

```python
# databases written before 2025/04/03 lack the account_id column
account_id = row['account_id'] if 'account_id' in row.keys() else None
```

### Decoding aids

- `SIZE_PATTERN = re.compile(...)  # number, then an optional binary unit suffix`
- `# fsum() for accurate floating point math`
- a regex, with a string the regex matches and one the regex rejects:
  ```python
  # matches:
  # `search_v2`
  # `db-host`
  # rejects:
  # `x.y`
  BARE_KEY = re.compile(r'[A-Za-z0-9_-]+')
  ```

(R10-Q42, R10-Q46, R10-regex-sample, R10-regex-literals)

### Fence

- `# bool subclasses Python int. Reject it too`, not `# bool subclasses Python int`
- `# isdigit() admits non-ASCII digits such as '²'. Check isascii() too`
- the `X would` form in full:
  ```python
  # Here read_bytes() is used. The alternative, read_text(), would turn \r\n and \r into \n, even
  # inside a quoted CSV field.
  csv_bytes = csv_path.read_bytes()
  ```

(R10-fence-form, R10-fence-fact, R10-fence-alternative)

### Depth

```python
# The vendor API returns at most 100 rows per page and no total count.
# Keep requesting until a page comes back short.
while len(page := fetchPage(cursor)) == PAGE_SIZE:
```

(R10-depth-example)

### Placement

A comment on an argument goes above the call that passes the argument, such as above
`pendulum.parse(raw_at, tz=None)`, not below the `try` block. (R10-argument-placement)

### FIXME

In reachable code a `FIXME:` blocks the merge (`NAR010`). In code nothing calls, the `FIXME:` is a
warning to whoever wires that code in. Every function of a module with no `main` and no `__main__`
block counts as reachable. (R8-D02)

### noqa

The exceptions to **Never add a `noqa` yourself** are the `# ruff: noqa: TID251` lines prescribed
in **Data at boundaries**. (R11-findings)

### Pages

`agentverbs.py` is the seventh check of `verify.py`. Name each page to `verify.py`:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" README.md docs/report.html
```

## Procedures

Take these in order. **Setup** happens once per machine and once per project. **Writing a comment**
applies to each comment as you write the comment. **Verify** and **Prose review** follow once the
code is written. **Published prose** applies to each page you write, such as a README.
(R10-procedures) **Writing a comment**, **Prose review** and **Published prose** are in
`nar:core`.

### Setup

Once per machine, make one lint venv and reuse the venv for every project. A venv per project means
a separate install of about 430 MB in each. (R10-setup)

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

When an update of the skill changes `requirements-lock.txt`, run the `uv pip install` line again.
`install.sh` and a plugin update copy the new lock file but install nothing.
`verify.py` uses this venv by default, and when the venv is missing `verify.py` prints these two
commands for the current machine. Pass `--venv` for a venv at another path. On Windows, run the
scripts with `py` or `python` wherever `python3` appears in this document.

Once per project, merge `pyproject-snippet.toml` into the project's `pyproject.toml`, or copy
`pyproject-snippet.toml` as the `pyproject.toml` of a new project. The file must be named
`pyproject.toml`. Ruff reads a config file with any other name as a `ruff.toml`, and `verify.py`
exits 2.

### Verify

Run `verify.py`. Do not call the tools by hand.

```
python3 "${CLAUDE_SKILL_DIR}/verify.py" .
python3 "${CLAUDE_SKILL_DIR}/verify.py" . --since origin/main
```

Pass `verify.py` any path. Every Python file below that path is checked. Run `verify.py` from the
project root, because the default `--config` is `./pyproject.toml`. `verify.py` rewrites files with
`ruff check --fix` and `ruff format`, unless you pass `--no-fix`. For each tool that fails,
`verify.py` prints that tool's output.

**In a PR to another project, pass `--since` with the base branch.** Upstream code already breaks
some of these rules, and a finding on a line the diff does not touch is not the PR's to fix. Only
the lines that the diff against `merge-base(HEAD, base)` adds or changes are reported, and every
line of an untracked file. A finding on a `def` or `class` line counts for every line of the
definition, and a finding in a comment or docstring counts for every line of the passage. Under
`--since`, `verify.py` applies a fix of `ruff check` only when the fix edits a changed line, and
`ruff format` formats only the changed lines. When the project's `pyproject.toml` is not a Narrative
config, pass `--config` with a copy of `pyproject-snippet.toml` named `pyproject.toml`, outside the
project. (R11-since, R11-same-workflow)

`verify.py` resolves every tool to an absolute path. It exits 2 when a tool is missing or
`pyproject.toml` is absent. **Do not replace it with a loop that greps tool output for findings.**
With such a loop, a missing binary or config produces empty output, and empty output reads as a pass.

`verify.py` runs these tools, in the order that converges: `ruff check --fix`, `ruff format`,
`pylint`, `mypy --strict`, `checks.py`, `vermin`, `agentverbs.py`. A run with exit 0 or 1 ends
with three lists, the input to **Prose review**: every sentence of every comment, docstring and
named page, every verb whose subject cannot act, and every sentence with a pronoun. On a run with
exit 1, `verify.py` prints the lists after the findings. With `--since`, the lists cover only the
changed lines. Without `--since`, each list stops after 1000 entries, with the command for the next
1000. `verify.py` keeps the spaCy results of each comment in `.narrative_cache/` in the current
directory, so a run after a small change parses only the changed comments. (R11-lists-on-failure,
R11-page-inventory, R11-list-pages, R11-prose-cache)

| exit | meaning |
|---|---|
| 0 | every tool passed |
| 1 | at least one tool had a finding |
| 2 | the toolchain or the config is missing, so nothing was checked |

The job of each layer, and the tool defaults that break rules of this skill, are in `tooling.md`. For
example, `ruff check --fix` collapses blank lines after imports, and the `SIM114` fix merges branches
and loses type narrowing. Read `tooling.md` before you change config.

