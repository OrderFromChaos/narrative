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

