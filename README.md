# Narrative
## Before

```python
def nearest_enchant_dungeon(row):
    """Closest Roguelike dungeon whose generated layout contains an enchantment table,
    with the table's exact position. Requires rows from a sweep new enough to emit
    enchant_tables (probe >= 555df65b); older rows yield None everywhere, which reads as
    "no data", not "no dungeon"."""
    sx, _, sz = row["spawn"]
    best = None
    for d in row.get("dungeons") or []:
        for p in d.get("enchant_tables") or []:
            # Distance to the TABLE BLOCK, not to its dungeon's trigger chunk. A dungeon
            # sprawls, so the two differ by up to ~70 blocks: one seed reported "350
            # blocks" beside a tp for a table that is actually 279 away. The prefilter's
            # own enchant gate measures table position, so ranking on the trigger also
            # disagreed with which seeds the sweep had kept.
            dd = dist(sx, sz, p[0], p[2])
            if best is None or dd < best[0]:
                best = (dd, p[0], p[1], p[2], d.get("tower"))
    return best
```

## After

```python
def findNearestEnchantTable(sweep_row: Mapping[str, Any]) -> EnchantTable | None:
    """Find the enchant table nearest to spawn, in any Roguelike dungeon of the sweep row.

    For a row from a probe before 555df65b, None means no data, not that no table exists.
    """
    spawn_x, _, spawn_z = sweep_row["spawn"]
    tables = []
    for dungeon in sweep_row.get("dungeons") or []:
        for x, y, z in dungeon.get("enchant_tables") or []:
            # a table can be up to ~70 blocks from its dungeon's trigger chunk.
            # Measure to the table
            distance = dist(spawn_x, spawn_z, x, z)
            tables.append(EnchantTable(distance, x, y, z, dungeon.get("tower")))
    return min(tables, key=lambda table: table.horizontal_distance_blocks, default=None)

# Field order is part of the summary file's format.
class EnchantTable(NamedTuple):
    horizontal_distance_blocks: float
    x: int
    y: int
    z: int
    tower: str | None
```

(Taken from a [gtnh-determinism](https://github.com/OrderedSet86/gtnh-determinism/blob/6d12e3e/seedsearch/multi-criteria.py#L102-L117) seed-search helper, at commit [`6d12e3e`](https://github.com/OrderedSet86/gtnh-determinism/commit/6d12e3e). Original function was written with either Fable 5 or Opus 5.)

## How??

I wanted a code skill that would make LLMs write Python like me. Tricks this skill uses:

1. Over a few weekends, I rated hundreds of A/B examples of Python function design and architecture. This led to specific enough rules to lint and fix most code bugbears. (These are tracked in `benchmark/`.)
2. LLMs tend to go wild with anthropomorphizing inanimate things, saying things like "*the manifest knows errors*". What does it mean to "know" an error? For this I use NLP (natural-language processing) to lint for inanimate subject + agency verb. Although this technique sounds less impressive than point (1), **I cannot overstate** how much this deslops LLM comments.
3. Clear good comment metric: facts outside the code, simplification fences, decoding aids, and meta-level markers such as `TODO:`.
4. An explicit double checking step. (There are enough rules here that even frontier models miss a few things on the first pass...)

Some examples of (2):

| Before | After |
|---|---|
| `A malformed row costs its file a place in the report.` | `A file with a malformed row is left out of the report.` |
| `--drop clears the collections the archive carries` | `--drop clears the archive's collections` |
| `the middleware finds the fixture user and signs the request in` | `In development, sign the request in as the fixture user.` |
| `a module holding one function` | `a module has one function` |

## Note

⚠️ This skill has an opinionated unidirectional ordering for code (`main()` first, then the steps it calls in call order, then the types). This does produce readable and pleasing code, but may lead to stylistic differences between your PR and the rest of your codebase. **It will not force migrate the rest of your codebase to this style unless you tell it to.**

## Install

### As a plugin (updates itself)

In Claude Code:

```
/plugin marketplace add OrderFromChaos/narrative-python
/plugin install narrative@narrative-python
```

Then open `/plugin`, go to **Marketplaces**, select `narrative-python` and select **Enable auto-update**.
Each push to this repository then reaches you at your next session. Invoke the skill as
`/narrative:narrative`, or let Claude load it when a task involves Python.

The first time Claude runs the checks, Claude sets up the shared lint venv in
`~/.local/share/narrative/lintenv` (`%LOCALAPPDATA%\narrative\lintenv` on Windows), with `uv`.
After that, every project uses the same venv.

To roll the plugin out to a whole team, a Claude Code admin can add this to managed settings:

```json
{
  "extraKnownMarketplaces": {
    "narrative-python": {
      "source": { "source": "github", "repo": "OrderFromChaos/narrative-python" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "narrative@narrative-python": true }
}
```

### By hand

Clone the repository and run the installer:

```bash
git clone git@github.com:OrderFromChaos/narrative-python.git
cd narrative-python

./install.sh
```

`install.sh` copies the skill's ten files to `~/.claude/skills/narrative`, or to a path you give
it. Invoke the skill as `/narrative`, or let Claude
load it when a task involves Python.

**To update, run `git pull && ./install.sh`.** If you change to the plugin, delete
`~/.claude/skills/narrative`, or Claude loads both copies.

# Details

## Claudish Begone

Values indicate rate per 100 comment blocks, with 95% CIs.

| | Claude, no skill | | /narrative Claude | Human code |
|---|---|---|---|---|
| comment blocks (n=) | 2,962 |  | 201 | 21,977 |
| median words | 22 | → | 12 [10, 13] | 9 |
| p90 words | 79 | → | 20 [18, 27] | 29 |
| more than one sentence (%) | 41.6 | → | 36.8 [30.5, 43.7] | 14.8 |
| `, not` contrast | 7.9 | → | 0.5 [0.1, 2.8] | 0.4 |
| dash | 17.5 | → | 0.0 [0.0, 1.9] | 1.0 |
| `every`, `never`, `whole`, `exactly` | 22.0 | → | 6.0 [3.4, 10.1] | 1.5 |
| `the one` / `one place` | 2.3 | → | 0.0 [0.0, 1.9] | 0.1 |
| `deliberately`, `on purpose`, `by design` | 1.9 | → | 0.0 [0.0, 1.9] | 0.1 |
| `rather than` / `instead of` | 14.0 | → | 0.0 [0.0, 1.9] | 1.1 |
| `, so` between clauses | 24.4 | → | 4.0 [2.0, 7.7] | 2.9 |
| semicolon | 15.7 | → | 0.5 [0.1, 2.8] | 2.3 |
| agent verb: `finds`, `knows`, `wants`, `decides`, `owns` | 2.2 | → | 0.0 [0.0, 1.9] | 0.3 |
| container verb: `holds`, `carries`, `keeps`, `names` | 7.9 | → | 0.0 [0.0, 1.9] | 0.2 |
| intensifier: `genuine`, `actually`, `really`, `truly` | 6.3 | → | 0.0 [0.0, 1.9] | 1.4 |
| article before an identifier: `the foo()` | 2.3 | → | 0.0 [0.0, 1.9] | 0.5 |
| `because` | 7.8 | → | 0.0 [0.0, 1.9] | 2.3 |
| passive voice | 17.3 | → | 7.5 [4.6, 11.9] | 12.5 |
| changelog: `now`, `no longer`, `used to` | 2.7 | → | 0.0 [0.0, 1.9] | 2.4 |
| hedge: `usually`, `probably`, `might` | 0.3 | → | 0.0 [0.0, 1.9] | 2.0 |
| first person: `we`, `our`, `I` | 1.0 | → | 0.0 [0.0, 1.9] | 16.4 |
| `TODO`, `NOTE`, `FIXME` | 0.3 | → | 0.0 [0.0, 1.9] | 3.6 |

- `human code` is the CPython stdlib and the mypy, pylint and astroid sources.
- `/narrative Claude` is based on output from 20 different sample specs.

## The nineteen custom lint rules

| rule | finding |
|---|---|
| `NAR001` | module state changed with no `global`. Ruff and pylint report nothing on this at any setting |
| `NAR002` | `hasattr(self, ...)`, which means an attribute exists only on some paths |
| `NAR003` | more than three positional arguments on one `def` line |
| `NAR004` | no docstring on a complex function (more than three parameters, or a long body), or no `Raises:` on one that raises |
| `NAR005` | an annotation with more than four names below the outermost |
| `NAR006` | an assignment that shadows a module name |
| `NAR007` | `and` inside `or` without parentheses |
| `NAR009` | no module docstring, or a runnable module with no usage example |
| `NAR010` | a `FIXME` in code that runs |
| `NAR011` | a docstring body indented past the docstring's column, which `ruff format` flattens |
| `NAR012` | a decision id in a comment or docstring |
| `NAR013` | a dash or a semicolon between clauses in a comment or docstring |
| `NAR014` | `deliberately`, `on purpose`, `by design` or `intentionally` in a comment or docstring |
| `NAR015` | changelog wording in a comment or docstring: `no longer`, `previously`, `it used to` |
| `NAR016` | `holds`, `carries` and their forms in a comment or docstring |
| `NAR017` | an agent verb on a subject that cannot act: `a period ranks`, `the report names it`, `the default config sends the job` |
| `NAR018` | a possessive `own` in a comment or docstring |
| `NAR019` | a return contract written as a comment at the top of a function body |
| `NAR020` | a clause with its subject cut before `, so`: `Named, so a recreated container gets it back` |
| `NAR021` | a clause joined by `as` or `, where`: `a float, as in the parser` |

`NAR000` is code for a file that could not be read or parsed.

## Measured code effects

The style has four goals. Three of them are measurable with an agent harness.

| goal | result |
|---|---|
| 1. shorter than unguided code | **yes.** 33% fewer SLOC against an ordinary spec, 9% fewer against a detailed output contract |
| 2. more readable than unguided code | **cannot be agent measured.** (But definitely passes my human review...) |
| 3. doesn't create future tech debt | **fewer lines, more files.** A two-step change costs 329 lines against 365, over 14 files against 12. This is an acceptable null result - one of these files is `vocabulary.py` |
| 4. no worse against the spec | **yes, on twenty blind tests.** Both arms pass 20 of 20 |

The test task is a billing reconciler, with two specs in the table below. In V5 the outputs are
named but not specified (a realistic spec). In V6 the report schema, the ordering, the exit codes
and the join are fixed to the byte, so the remaining difference is style.

| | modules | lines | code lines | ruff | format | pylint | mypy | checks |
|---|---|---|---|---|---|---|---|---|
| V5 `base` | 12 | 1317 | 879 | 321 | FAIL | 36 | 0 | 14 |
| V5 **`full`** | 12 | **963** | **590** | **0** | **ok** | **0** | **0** | **0** |
| V6 `base` | 14 | 1380 | 831 | 93 | FAIL | 32 | 2 | 2 |
| V6 **`full`** | 14 | **1316** | **752** | **0** | **ok** | **0** | **0** | **0** |

With the skill, code is **33% shorter** than unguided code on typical specs, and **9% shorter** on unrealistically specific specs. The gap between the two comes from the guided agent choosing a narrower report. In V5, `full`'s report has
three top-level keys and `base`'s has eight, and both are correct readings of the spec. (I would count this as a YAGNI win - not pre-emptively designing unasked features.)

**Bugs.** Both arms pass **20 of 20** tests in a conformance suite written by a blinded agent.

**Tech debt.** Five change requests, each at a different seam, were applied to
each arm by an agent that saw only that arm and that change.

| | `base` files / lines | `full` files / lines |
|---|---|---|
| C1: a 3rd cost format | **5 / 137** | 7 / 234 |
| C5: a 4th cost format | 7 / 228 | **7 / 95** |
| **the cycle** | **12** / 365 | 14 / **329** |
| C2: a fourth finding kind, across every layer | 6 / 115 | **5 / 106** |
| C3: a new rules field | **2 / 48** | 4 / 59 |
| C4: a new column in three outputs | **5 / 90** | 6 / 92 |

At C1 the guided agent extracted a shared parser, which cost more lines at the time. At C5 the
unguided agent reached the same design, because the spec requires identical rejection messages
across formats. Both pay about 95 lines for a fifth format. The guided arm touches more files in
three of the five changes, the same number in one, and fewer in one. In C1, C3 and C5, some of its
files changed only to re-paste a stale docstring sample (required by rule `R9-08`).

## License

Apache-2.0. See `LICENSE`. `skill/words.json` has word lists derived from WordNet 3.0 and VerbNet 3,
under their licenses. The text of both licenses is in the `license` field of `skill/words.json`.
