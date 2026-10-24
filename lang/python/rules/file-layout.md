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

