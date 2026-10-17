# Narrative Python, lite: architecture

`SKILL.md` applies to each file. This document applies to several. Read this document when the
program spans more than one module or imports a third-party package, and not for a single-file
program.

## The measure

**Name the change before you make it. The name must be enough for you to know the one file to
open.** Say the change in a colleague's words: "the vendor revised the frame format", "the
retention window moved to 90 days". A design passes when each such sentence has one destination,
known before reading the program. It fails when the answer is "it depends" or "three places".

**Measure what a person must know to make an edit, not the file count.** At the same file count, a
diff that writes a module name twice is easier to review than a diff that writes a wire format into
the entry point.

**The exchange rate**, dearest first:

1. a parameter threaded through functions that do not use it
2. one more file
3. one more named type. A named type is free when its field belongs to the thing it is about

Spend a named type or a file to delete a threaded parameter. Never the reverse.

## Fact placement

**Ask whose property the fact is, and put the fact in the module of that thing.** A per-vendor retry
cap belongs with the vendor, not in a generic backoff module. A retention window is a property of
the data, not of the scheduler.

- **Do not make a caller pass what the callee can compute from its arguments and imports.** A store
  module may import a config module, so that no caller has to pass it a lookup. This outranks
  dependency direction.
- **An exception type belongs in the shared vocabulary**, not in the module that raises it, because
  an exception can be caught in any module.
- **Centralise a type once it appears in a signature.** A shape built and consumed inside one
  function is a step, not a type. Every type in a signature that other modules use goes in the
  shared vocabulary, even when only one other module reads it. A module of types alone has no
  `### vocabulary` divider.
- **A log field set belongs to the module that emits the record**, not to the formatter. A flat
  shared list is fine while one module produces the records, and a smell once two producers use
  different keys.
- **Name a one-line body when the expression encodes a domain decision**, and not when the
  expression is a plain language or stdlib operation. No tool checks this.

  ```python
  # No. A dict lookup with a default is not a concept.
  def canonicaliseRegion(region: RegionName, reconcile_rules: ReconcileRules) -> RegionName:
      return reconcile_rules.region_aliases.get(region, region)

  # Yes. The pattern and the fold are the PEP 503 rule. A reader learns that from the name.
  def normalizeName(name: PackageName) -> PackageName:
      return _NAME_SEPARATORS.sub('-', name.strip().lower())
  ```

**Code on both sides of a byte layout imports the layout from one shared module.** Two copies drift
apart, and the drift passes every type checker and linter.

## Which module imports which

There is no layer table and no directory rule. This is review judgement. `io/reader.py` importing
`io/checksum.py` is correct, because a checksum is below a reader whatever the directory layout.

**A cycle is a wrong cut, not an import problem.** Break it with a shared vocabulary module. Do not
reach for `if TYPE_CHECKING`, and do not dissolve the shared type into primitives. When a callee
takes primitives, every caller has to destructure the shared type.

**Call a first-party module by name**: `from collector import store`, then `store.insertReading`.
The function name follows the naming rules of `SKILL.md` without the qualifier.

## Where the cuts go

**Give each coherent concern a module, whatever its line count.** A 28-line concern gets a separate
file, and a 340-line file with six concerns becomes six modules.

**The test is whether you can name the module without saying "and".** A `protocol.py` that also has
`crc32Of` is "the wire format **and** checksums", so the checksum moves to a separate module.

**Split.** Six modules of 40 to 90 lines are better than one file of 340. Do not wait for a second
program to use the code.

**There is no fixed split axis.** Cut by technical role when the program has one of everything. Cut
by subject when it has several vendors, formats or sites. Cut on the axis where each expected change
touches fewer modules.

**Shared code inside one system starts as one `common.py`** in that system's directory. Split it
when it grows: definitions first, then implementation. Never a project-wide `utils.py`.

## Package surface

**Prefix every internal module-level name with an underscore**: functions, constants, classes and
type aliases. A module filename has none. Decide by the callers the name has today. When a later
change uses the name elsewhere, drop the underscore in that change. Names in `__main__.py` stay
bare.

**`__all__` declares a package's exports.** A library's `__init__.py` is a re-export façade with
`__all__`, no state and no constants. An application package's `__init__.py` is empty.

**`main` is in `__main__.py`**, so users type `python3 -m collector`. Split the workflow out only
when `main` grows long.

**The entry point has the list of modules and nothing about any of them.** Two files is the floor
for adding a new subject: the new module, and the one line with its name. The docstring of
`__main__.py` is the program's purpose, then the modules in reading order. It is the only docstring
with other modules' names in it.

**`main()`-first generalises to a library.** The public entry takes the position of `main()`,
callees follow in first-call order, and types come last under the divider.

## Classes, Protocols and bundles

**Give values a class when they could differ between instances.** Two connections can coexist, so a
store is a class. A frame format is the same everywhere, so the parser is a module.

**One coordinator, not a chain.** Stages that are not reused separately do not each call the next.
One function calls them in turn, with the intermediates in its local variables.

**Write a pure core when the code has enough decisions for one.** Four routing rules and three
effects are enough. Compute a plan, then apply it. One f-string is not enough.

**Every case of a closed set is in one module, in an exhaustive `match`.** A decorator that
registers each handler at import reverses the import arrows, and mypy cannot check the dispatch
table.

**Centralise a type before anything shares it. Do not generalise behaviour before you need it.**
Moving a type later is a mechanical edit that the type checker verifies. Removing a wrongly general
dispatch is not.

## Resources, state and config

**Open a resource at the scope whose lifetime it matches**, at the top of that scope. The deciding
factor is the cost of the handle on the far side, not idle time. A network connection, a device
socket or a licensed SDK seat has a timeout, a limit or a seat count.

**A module-level singleton is fine for anything never closed**, such as a logger. A connection is
not. **The config object is one such singleton.** Parse it once at import into a frozen record, and
import that name where it is needed. Every module imports the one config, with no per-module slices.
It is assigned once and never rebound. A hardcoded default invented in a module is not allowed. A
default belongs in the config file.

**Leaf modules import the constants they need** when those constants exist at import time. Thread
the config object when the program resolves it at run time. No tool checks this.

**Pass a flag no further down than the function that branches on it.** A flag may go further inside
a named config.

**The clock goes inside the function that reads it.** Test through the real clock, and assert on
ordering and bounds, not on an instant. Inject the clock only for a measured speedup on a hot loop.

## Third-party code

**Take the dependency when it is simpler at the call site.** At equal ergonomics, use the standard
library. `json`, `struct`, `sqlite3`, `pathlib` and `dataclasses` already read well.

**Then contain it.** One module imports the library, and everything downstream gets a domain type.
**Contain handles, not values.** A handle is a thing that must be closed: a connection, a client, a
socket, an open file. `datetime`, `Decimal` and an array cross freely.

**Depend rather than vendor or reimplement**, weighted by adoption: downloads, age, dependents.
Reimplement when you must change the thing wholesale. Vendor only when one frozen version fits with
no changes.

**A pin is a property of the deployment, never of the library.** A library has a version floor. The
repository pins the exact set in one lock file.

## Service, library, monorepo

**One shared logger from one logs module.** The formatter then emits `module`, `lineno` and
`funcName` to locate the record, because `record.name` is constant.

**Shared code goes in the shared library**, not in the first program that used it.

**The source pushes and the service follows**, when the source has notifications, such as a
socket, a queue, a filesystem watch or a webhook. For a source with no notifications, such as an
HTTP endpoint you do not control, poll. A service has no rounds, so its degrade-and-report unit is
a time window.

**Degrade and report across modules.** The module doing the work collects per-item failures, and
the module above logs the aggregate.

A program may contain the name of a rule it implements, such as `NAR006` in `checks.py`. A name from
the same program is not a decision citation.

Four faults are checkable in principle, and no checker for them exists, so they are review
judgement: import cycles, a cross-module import of an underscore-prefixed name, an `__all__` with an
undefined name, and a handle type in a signature outside its owning module.
