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

