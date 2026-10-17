# Narrative Python, lite: domain rules

Read only the section for a domain that the program touches. Every other rule is in `SKILL.md`.

## Money

Money is exact. Parse an amount with `Decimal(raw)` from the string, never through `float`.
`Decimal(0.1)` keeps the float's error. Round once, with the mode explicit:
`cents = int((Decimal(raw) * 100).to_integral_value(ROUND_HALF_UP))`. Without an explicit mode,
`Decimal` rounds half to even. A computation that yields fractions of a cent, such as
rate × minutes × multiplier, stays in `Decimal`, integers or `Fraction` until that one rounding.
Store and serialise integer cents, named `…_cents`. `json` and `sqlite3` reject a `Decimal`.

## Dates and times

Use `pendulum`, unless `datetime` is so tightly integrated with the repository that removing it
would be hard. Replace a small `datetime` use with `pendulum`. A library that returns `datetime`
values, such as `tomllib`, `sqlite3` or a JSON decoder, is a boundary. Convert each value to
pendulum where it enters.

## asyncio

- Run tasks that should fail together in an `asyncio.TaskGroup`. Hand-rolled cancellation fails
  silently. A `TaskGroup` cancels every task when one raises, so give independent handlers, such as
  one per client connection, a task each.
- `except TimeoutError` is correct around `asyncio.wait_for`. At 3.11, `asyncio.TimeoutError` is the
  builtin.
- On a guard for a runtime newer than the 3.11 floor, the comment has the version: `# on 3.12.1 and
  later, wait_closed() waits for open connections`.

## SQLite and the DB-API

`sqlite3.executemany` takes a sequence per row and raises `ProgrammingError: parameters are of
unsupported type` on a dataclass. This is the standing exception to naming an annotation with a
dataclass. Use a `NamedTuple` for rows, with `?` placeholders, and say why in a comment:

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

## Web frameworks

No framework should validate output. FastAPI makes a route's return annotation its response model,
so every response is validated at run time. Pass `response_model=None` in the route decorator, and
keep the annotation for mypy.

## Logging setup

In a package used as a library, add `logging.NullHandler()` to the package logger once, in its
top-level `__init__.py`. Without it, the last-resort handler prints the package's warnings to stderr
in a program that configures no logging. A program adds no NullHandler.

A single-file tool run by hand prints through this formatter:

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
total=10000`: the tally an operator acts on, and the location of the call site.
