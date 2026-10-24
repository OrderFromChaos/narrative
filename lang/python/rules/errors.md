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

