# Task P20 — change request: a yearly rule, pinned snapshots, a deletion limit

`fixture/snapshot_pruner/` is a working snapshot pruner, written to `fixture/ORIGINAL_TASK.md`.
Make the three changes below in that package. Keep everything the original specification requires:
a run on a directory without `pins.txt`, with a policy without `yearly` and without `--max-delete`,
gives the same plan.json, summary and exit code as before.

`pendulum` may be used, as the package already does. Nothing else outside the standard library.

## 1. A yearly rule

`keep` may have a fifth rule, `"yearly"`, a non-negative integer like the other four. It is
optional: a policy without it has `yearly` 0, so every policy file the original program accepted is
still valid. Any other key in `keep` is still malformed.

A `yearly` period is a calendar year on the local wall clock in the policy's timezone: not the
snapshot's UTC year, and not its ISO week-numbering year. The rule works like the other four: under
`yearly: N`, the newest snapshot of each of the N most recent years that contain a snapshot is
kept. It is independent of the other rules.

The database records the `yearly` count with each run, so two runs that differ only in `yearly` are
different runs.

## 2. Pinned snapshots

The snapshot directory may have a file `pins.txt`, which lists snapshots that are always kept. It is
UTF-8, with or without a byte order mark, with `\n` or `\r\n` line endings. Each line is read so:

1. Everything from the first `#` to the end of the line is a comment and is removed.
2. Leading and trailing whitespace is removed.
3. A line that is then empty is skipped. Every other line is a pin: the file name of one snapshot,
   without a directory. A name listed more than once is one pin.

A pin that names a snapshot keeps it, under the rule `pinned`. Pins do not change the other rules:
a pinned snapshot takes part in each rule as before, and each rule picks the same snapshots as
without pins. A pin that names an unparseable snapshot or a snapshot from the future changes
nothing: that file stays a problem of its kind and is in neither `keep` nor `delete`.

A pin that names no regular file of the snapshot shape in the directory (a missing file, another
name, a subdirectory, a symbolic link, a path) is a problem, `"bad-pin"`, with the pin as `file`:

```json
{"file": "db-20250301T000000Z.tar.zst", "problem": "bad-pin"}
```

It counts toward exit code 1 like the other problems. `pins.txt` itself is not a snapshot, so it is
ignored like any other entry that is not one. Without `pins.txt`, nothing is pinned. A `pins.txt`
that cannot be read, or is not UTF-8, stops the run with exit code 2.

`rules` now lists in the order `hourly`, `daily`, `weekly`, `monthly`, `yearly`, `pinned`,
`newest`. `problems` is still sorted by `file`. The importable function reads `pins.txt` too, and its
arguments do not change.

## 3. A deletion limit

`--max-delete N`, with N a non-negative integer, limits an `--apply` run. When the plan's `delete`
list has more than N snapshots, nothing is deleted; exactly N is allowed. A refused run otherwise
goes as a dry run: the decisions are recorded, plan.json is written with `"applied": false`, and the
summary is printed. The summary also states that the deletion was refused, with the number of
snapshots to delete and N. The exit code of a refused run is 3, whatever the problems.

Without `--apply`, `--max-delete` changes nothing. A value of N that is not a non-negative integer
stops the run with exit code 2.

The exit codes are now: 0 when there are no problems, 1 when there is at least one problem, 2 when
the run could not start or `--apply` failed to delete a file, 3 when `--max-delete` refused an
`--apply` run.

## The summary

Each kept snapshot's line shows all of its rules, `yearly` and `pinned` included, and each bad pin
has a problem line like any other problem.

## What is left to you

Where the changes go in the package, the summary layout, how the database records pins and bad pins,
whether a database written by the original program stays usable, and any behaviour this
specification does not fix.

## The fixture

`fixture/snapshots/` and `fixture/policy.json` are the original fixture, run with
`--now 2028-11-05T08:00:00Z`. That directory has no `pins.txt` and that policy has no `yearly`.

`fixture/archive/` and `fixture/policy-yearly.json` are new, run with `--now 2030-02-15T12:00:00Z`.
Their cases: a snapshot whose local year differs from its UTC year, a snapshot whose local year
differs from its ISO week-numbering year, and a `pins.txt` with a byte order mark, `\r\n` line
endings, a full-line comment, a comment after a name, blank lines, a repeated name, a pin of a
snapshot that a rule already keeps, and pins naming a missing file, a symbolic link and a snapshot
from the future.

`--apply` deletes fixture files. Run it on a copy of the fixture.
