## Structure inside a method

- Guard clauses and early return over nesting. (Q06)

- **Write a skip guard as the negation of what a valid item is.**
  `if (!(nameMatches && Files.isRegularFile(path) && !Files.isSymbolicLink(path))) continue;`, not
  `if (!nameMatches || Files.isSymbolicLink(path) || !Files.isRegularFile(path)) continue;`
  (R10-positive-guard)

- **One level of `filter` and `map` in a stream.** Where a stream lambda would have another stream
  inside the lambda, write a loop. No stream in a per-frame or draw method. `NAR103` flags a stream
  inside a stream lambda. (J1-P06, Q07)

- **Extract a block when you can foresee reusing or testing it separately**, not merely because it
  has a name. A one-line helper called once is residue. (R2-09, R2b-E1, R2b-E2)

- If an extracted method would take 5 or more values, that is a **missing owner**, not a reason to
  leave the code inline. That owner is a **class** when two of it can exist at once, and a final
  utility class with a private constructor and static methods otherwise. A record is the answer only
  when nothing has behaviour over the values. If a general name for the group is hard to pick, the
  values are not a real group. (R7-C05-resolved, R7-C05-naming)

- Always collapse duplicated-but-drifting code, even when the shared version takes an extra
  parameter. To localise the difference is the whole point. (R2b-E4)

- Mixed `&&` and `||` parenthesise each group explicitly. Never `a && b || c && d`. `NAR123`
  enforces it. (R2b-B4)

