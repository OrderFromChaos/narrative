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

