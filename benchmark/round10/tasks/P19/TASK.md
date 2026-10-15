# Task P19 — semantic versions and a dependency resolver

A library that parses and orders Semantic Versioning 2.0.0 versions, tests them against npm-style
ranges, and picks one version per package for a small dependency graph read from a registry.

A library only, with no command line. Use the standard library only. Include tests.

## The functions

- `compareVersions(a: str, b: str) -> int`: -1 when `a` has lower precedence than `b`, 0 when equal,
  1 when higher.
- `satisfies(version: str, versionRange: str) -> bool`.
- `maxSatisfying(versions: list[str], versionRange: str) -> str | None`: the satisfying version with
  the highest precedence, as written in the list; the first of several with equal precedence; `None`
  when no version satisfies the range.
- `resolve(registry: dict, requirements: dict[str, str]) -> dict[str, str]`, and the exception
  `ResolutionError` that it raises.

An invalid version or range raises `ValueError` in every function.

## Versions

- A version is `MAJOR.MINOR.PATCH`, then optionally `-` and a prerelease, then optionally `+` and
  build metadata. The three parts are numbers without leading zeros (`0` itself is allowed). The
  prerelease and the build are dot-separated non-empty identifiers of `[0-9A-Za-z-]`. A prerelease
  identifier of digits only is numeric and must not have a leading zero; a build identifier may.
- Precedence compares major, minor and patch as numbers. With those equal, a version with a
  prerelease is lower than one without. Two prereleases are compared identifier by identifier: two
  numeric identifiers as numbers, a numeric one is lower than an alphanumeric one, and two
  alphanumeric ones by ASCII order. When all compared identifiers are equal, the longer prerelease is
  higher. Build metadata never affects precedence.

## Ranges

- A range is one or more **sets** joined by `||`. A version satisfies the range when it satisfies at
  least one set. Whitespace around the range is ignored. An empty range is one set with no items. An
  empty set between two `||`, or after a trailing `||`, raises `ValueError`.
- A set is items separated by spaces. Each item expands to zero, one or two comparators (`=`, `<`,
  `<=`, `>`, `>=` and a full version). A version satisfies a set when it satisfies every comparator
  and the prerelease rule below. An operator is followed directly by its version, with no space.
- A **partial version** has one to three dot-separated parts, each a number or a wildcard `x`, `X`
  or `*`. A part after a wildcard must be a wildcard; missing parts count as wildcards. A prerelease
  or build is allowed only after three numbers. Build metadata in a range is ignored.
- Below, `L` is the partial version with every wildcard set to 0, keeping its prerelease. `next(p)`
  adds 1 to part `p`, sets the parts after it to 0, and gives prerelease `0`: `next(minor)` of `1.2`
  is `1.3.0-0`. A `-0` prerelease is the lowest possible, so `<1.3.0-0` excludes `1.3.0` and every
  prerelease of it.

| item | expands to |
|---|---|
| a full version, with `=`, `<`, `<=`, `>`, `>=` or no operator | that comparator (no operator is `=`) |
| `*`, `x`, `X`, `~*`, `^*` | no comparator |
| `1.2`, `=1.2`, `1.2.x` | `>=L <next(last number)`: `>=1.2.0 <1.3.0-0` |
| `>1.2`, `>=1.2`, `<1.2`, `<=1.2` | `>=1.3.0` (`next(last number)` with no prerelease), `>=L`, `<1.2.0-0` (`L` with prerelease `0`), `<next(last number)` |
| `~1.2.3`, `~1.2`, `~1` | `>=L <next(minor)` when the minor is a number, else `>=L <next(major)` |
| `^…` | `>=L <next(p)`, `p` the first part that is a non-zero number, or the last number when all are 0 |
| `A - B`, with a space each side of `-` | `>=L(A)`, then `<=B` when `B` is a full version, else `<next(last number of B)` |

So `^1.2.3-beta.2` is `>=1.2.3-beta.2 <2.0.0-0`. In a hyphen range, a side that is only a wildcard
adds no comparator. A hyphen side with an operator, `~` or `^`, and an operator before a
wildcard-only version (`>=*`), raise `ValueError`.

**The prerelease rule.** A version with a prerelease satisfies a set only when some comparator of
that same set has a prerelease and the same major, minor and patch as the version: `1.4.0-rc.1`
satisfies `>=1.4.0-beta <1.5.0` but not `>=1.3.0 <1.5.0`. This holds per set.

## The resolver

`registry` is the parsed JSON of a file shaped `{"name": {"version": {"dependency": "range"}}}`, and
`requirements` maps package names to ranges. Any invalid version or range in either raises `ValueError`.

1. Keep a list of pending requirements, starting with `requirements` in its key order, and an empty
   map of chosen versions.
2. Remove the first pending requirement. If its package is already chosen, the chosen version must
   satisfy the range, or this branch fails; continue with the rest of the list.
3. Otherwise, try each registry version of the package that satisfies the range, highest precedence
   first: choose it, append its dependencies to the end of the list in their key order, and continue.
   When no version leads to a result, this branch fails. A package missing from the registry has no
   versions.
4. When the list is empty, the chosen map is the result: each package reached, mapped to its version
   string as written in the registry, keys sorted by name. When every branch fails, raise
   `ResolutionError`. The result must equal what this search finds; skipping branches that cannot
   succeed is fine.

## What is left to you

The package and module layout, how a parsed version is represented, error messages, which versions
of one package win when two have equal precedence in the registry, and any behaviour this
specification does not fix.

## The fixture

`fixture/cases.json` has `compare`, `satisfies`, `maxSatisfying` and `resolve` cases with the
expected `result`, or `"raises"` and the exception name; the `resolve` cases use
`fixture/registry.json`. Its cases: numeric and alphanumeric prerelease identifiers, prereleases of
different lengths, uppercase identifiers, leading zeros, build metadata, carets on `0.x` and `0.0.x`,
tildes, x-ranges with operators, hyphen ranges with a partial side, prereleases with and without a
prerelease comparator in the same set, a prerelease as a package's highest version, a resolution that
needs backtracking, an impossible one, a dependency cycle and a missing package.
