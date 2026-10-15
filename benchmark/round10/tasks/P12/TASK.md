# Task P12 — incremental build planner

Decide which packages of a monorepo must be rebuilt since the last build, put them in parallel build
stages, and report every dependency cycle and every dependency on a package that does not exist.

Run as `python3 -m buildplan <root> [--state PATH]`. Use the standard library only (Python 3.11 or
later, for `tomllib`).

## Inputs

- **Manifests.** Every file named `package.toml` anywhere under `<root>` declares one package. The
  package's directory is the directory holding the manifest. Keys: `name` (string, mandatory, unique
  across the repository), `dependencies` (array of package names, default empty), `sources` (array
  of glob patterns, default empty). A dependency listed twice counts once.
- **Sources.** A file belongs to the package whose directory is its nearest ancestor holding a
  `package.toml`. A file is a source of that package when its path relative to the package directory
  matches one of the package's patterns. A pattern never claims a file inside a nested package's
  directory, even when the pattern's text matches it.
- **Patterns.** `/` separates segments; matching is case-sensitive and compares the whole path. A
  segment that is exactly `**` matches zero or more directory segments. Elsewhere `*` matches any
  run of characters within one segment and `?` one character within a segment. No other character is
  special, and a leading `.` is not special.
- **Last build.** `<root>/last-build.json`, or the path given with `--state`:

```json
{"packages": {"core": {"src/core/store.py": "9f2c…"}, "config": {}}}
```

  Each package built last time maps its source paths (relative to its directory, `/` separators) to
  the lowercase hex SHA-256 of the file's bytes at that build. A package with no sources is recorded
  with an empty object.

## What it does

1. Read every manifest and the last-build file.
2. A dependency on a name that no manifest declares is a **missing** dependency.
3. A **cycle** is a closed path along dependency edges that visits no package twice; a package that
   depends on itself is a cycle of one. Report every such cycle exactly once, rotated so that its
   smallest name comes first, then in dependency order: each package depends on the next, and the
   last depends on the first. Names compare by Unicode code point.
4. A package is **blocked** when it is on a cycle, has a missing dependency, or depends directly or
   transitively on a blocked package. Blocked packages are neither stale nor staged.
5. For each other package, hash the bytes of each current source file as stored on disk, with no
   newline or encoding conversion. Its **own sources changed** when the package is absent from the
   last-build file (reason `new`), or when the current path-to-hash map differs from the recorded
   one: a source added, removed, or with different bytes (reason `sources changed`).
6. A package is **stale** when its own sources changed, or when any of its dependencies is stale
   (reason `dependency rebuilt`). Own sources take precedence over a stale dependency for the reason.
7. Stage the stale packages: a stale package with no stale dependency is in stage 1; any other is in
   the stage after the highest stage among its stale dependencies. Each package appears once. Within
   a stage, names are sorted by code point.

## The output

The plan on stdout, written with `sys.stdout.write(json.dumps(plan, indent=2) + '\n')`, keys in this
order:

```json
{
  "stale": [{"package": "core", "reason": "sources changed", "files": ["src/core/store.py"]}],
  "stages": [["core"], ["api", "ui"]],
  "cycles": [["fmt", "lint"]],
  "missing": [{"package": "report", "dependency": "charts"}],
  "blocked": ["fmt", "lint", "report"]
}
```

The values above show the shape only. `stale` is sorted by `package`. `files` lists, sorted by code
point, the paths added, removed or changed for `sources changed`, every current source for `new`,
and nothing for `dependency rebuilt`. `cycles` is sorted by comparing the lists element by element;
`missing` by `package`, then `dependency`; `blocked` by name. Errors go to stderr.

Exit codes: 0 when there is no cycle and no missing dependency, 1 when there is at least one (the
plan is still written), 2 when the run could not start (missing root, unreadable or malformed
manifest or last-build file, a manifest without `name`, two manifests with the same `name`).

The planning must also be importable: another program calls one function with the root directory and
an optional last-build path, and gets the plan back without anything being printed.

## What is left to you

The package and module layout, error messages, logging, and any behaviour this specification does
not fix.

## The fixture

`fixture/` is a repository root with 18 package manifests, their source files and a `last-build.json`.
Its cases: a diamond dependency below an edited package, two independent cycles of different
lengths, a self-dependency, a dependency on an undeclared package with a package depending on it, a
package nested inside another package's directory and matched by the outer package's pattern, a
source file whose bytes differ only in line endings, a package with no sources, and a recorded source
file that has been deleted.
