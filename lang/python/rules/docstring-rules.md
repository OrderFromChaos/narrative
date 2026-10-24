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

