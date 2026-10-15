# Narrative
## Before

```python
def nearest_enchant_dungeon(row):
    """Closest Roguelike dungeon whose generated layout contains an enchantment table, with the
    table's exact position. Requires rows from a sweep new enough to emit enchant_tables (probe >=
    555df65b); older rows yield None everywhere, which reads as "no data", not "no dungeon"."""
    sx, _, sz = row["spawn"]
    best = None
    for d in row.get("dungeons") or []:
        for p in d.get("enchant_tables") or []:
            # Distance to the TABLE BLOCK, not to its dungeon's trigger chunk. A dungeon sprawls, so
            # the two differ by up to ~70 blocks: one seed reported "350 blocks" beside a tp for a
            # table that is actually 279 away. The prefilter's own enchant gate measures table
            # position, so ranking on the trigger also disagreed with which seeds the sweep had
            # kept.
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
            # a table can be up to ~70 blocks from its dungeon's trigger chunk. Measure to the table
            distance = dist(spawn_x, spawn_z, x, z)
            tables.append(EnchantTable(distance, x, y, z, dungeon.get("tower")))
    return min(tables, key=lambda table: table.horizontal_distance_blocks, default=None)


### vocabulary #########################################################################


# json.dump() rejects a dataclass, and a NamedTuple is written as a JSON list.
# Field order is part of the summary file's format.
class EnchantTable(NamedTuple):
    horizontal_distance_blocks: float
    x: int
    y: int
    z: int
    tower: str | None
```

(Taken from a [gtnh-determinism](https://github.com/OrderedSet86/gtnh-determinism/blob/6d12e3e/seedsearch/multi-criteria.py#L102-L117) seed-search helper, at commit [`6d12e3e`](https://github.com/OrderedSet86/gtnh-determinism/commit/6d12e3e). Original function was written with either Fable 5 or Opus 5.)

## Benefits

- **A third less code to review.** Programs Claude writes (based on a realistic spec) with the skill have
  33% fewer executable lines. Against a highly detailed output contract, the savings are 9%.
- **Passes mypy --strict.** Contains an opinionated linting pipeline including ruff, pylint, `mypy --strict`, 17 custom AST checks, and NLP checks for inanimate agent verbs and cut subjects.
- **No loss in spec correctness.** Guided and unguided programs pass the same blind conformance tests.
- **Comments a reviewer wants.** Most of Claude's writing tics fall to the human rate or below, and comments are added for good reasons only.
- **Does not cause catastrophic tech debt problems.** Two consecutive change requests cost 329 changed lines with the
  skill against 365 without it, over 14 files against 12.
- **One command for the whole toolchain.** `verify.py` runs every tool in the right order, and
  exits 2 when a tool is missing, so a missing tool never passes as a clean run.
- **Transferrable to other languages.** The rules and checks are for Python, but the principles carry over. In my
  experience, asking Claude to take the good parts of `/narrative` into another language works
  well.

Rules come from 456 human-selected choices between real working programs.

⚠️ This skill has an opinionated ordering for code (`main()` first, then the steps it calls in call order, then the types). This does produce readable and pleasing code, but may lead to code differences between your PRs and the rest of your codebase. It will not force migrate the rest of your codebase to this style unless you tell it to.

## Claude's comments, with and without the skill

`human code` is the CPython standard library and the mypy, pylint and astroid sources. `Claude, with the skill` is twenty
runs of the shipped skill, one on each of twenty tasks, with 95% CIs. Values indicate rate/100 comment blocks.

| | Claude, no skill | human code | Claude, with the skill |
|---|---|---|---|
| comment blocks (n=) | 2,962 | 21,977 | 201 |
| median words | 22 | 9 | 12 [10, 13] |
| p90 words | 79 | 29 | 20 [18, 27] |
| more than one sentence (%) | 41.6 | 14.8 | 36.8 [30.5, 43.7] |
| `, not` contrast | 7.9 | 0.4 | 0.5 [0.1, 2.8] |
| dash | 17.5 | 1.0 | 0.0 [0.0, 1.9] |
| `every`, `never`, `whole`, `exactly` | 22.0 | 1.5 | 6.0 [3.4, 10.1] |
| `the one` / `one place` | 2.3 | 0.1 | 0.0 [0.0, 1.9] |
| `deliberately`, `on purpose`, `by design` | 1.9 | 0.1 | 0.0 [0.0, 1.9] |
| `rather than` / `instead of` | 14.0 | 1.1 | 0.0 [0.0, 1.9] |
| `, so` between clauses | 24.4 | 2.9 | 4.0 [2.0, 7.7] |
| semicolon | 15.7 | 2.3 | 0.5 [0.1, 2.8] |
| agent verb: `finds`, `knows`, `wants`, `decides`, `owns` | 2.2 | 0.3 | 0.0 [0.0, 1.9] |
| container verb: `holds`, `carries`, `keeps`, `names` | 7.9 | 0.2 | 0.0 [0.0, 1.9] |
| intensifier: `genuine`, `actually`, `really`, `truly` | 6.3 | 1.4 | 0.0 [0.0, 1.9] |
| article before an identifier: `the foo()` | 2.3 | 0.5 | 0.0 [0.0, 1.9] |
| `because` | 7.8 | 2.3 | 0.0 [0.0, 1.9] |
| passive voice | 17.3 | 12.5 | 7.5 [4.6, 11.9] |
| changelog: `now`, `no longer`, `used to` | 2.7 | 2.4 | 0.0 [0.0, 1.9] |
| hedge: `usually`, `probably`, `might` | 0.3 | 2.0 | 0.0 [0.0, 1.9] |
| first person: `we`, `our`, `I` | 1.0 | 16.4 | 0.0 [0.0, 1.9] |
| `TODO`, `NOTE`, `FIXME` | 0.3 | 3.6 | 0.0 [0.0, 1.9] |

The skill brings most rows to the human rate or below.

## Install

Clone the repository and run the installer from its root:

```bash
git clone git@github.com:OrderFromChaos/narrative-python.git
cd narrative-python

./install.sh
```

`install.sh` copies the skill's ten files to `~/.claude/skills/narrative`, or to a path you give
it. Invoke the skill as `/narrative`, or let Claude
load it when a task involves Python.

**To update, run `git pull && ./install.sh`.**

## Dependencies

`checks.py` needs only the standard library, so it runs with any `python3` at 3.11 or later:

```bash
python3 ~/.claude/skills/narrative/checks.py src/
python3 ~/.claude/skills/narrative/checks.py src/ --select NAR001 --select NAR009
```

For the rest of the toolchain, I recommend a single environment so you don't have to recreate it for each project.

Linux and macOS:

```bash
uv venv ~/.local/share/narrative/lintenv --python 3.11
uv pip install --python ~/.local/share/narrative/lintenv/bin/python -r ~/.claude/skills/narrative/requirements-lock.txt
```

Windows (PowerShell):

```powershell
uv venv $env:LOCALAPPDATA\narrative\lintenv --python 3.11
uv pip install --python $env:LOCALAPPDATA\narrative\lintenv\Scripts\python.exe -r $HOME\.claude\skills\narrative\requirements-lock.txt
```

When an update changes requirements-lock.txt, run the `uv pip install` line again. (`install.sh` only copies the new lock file.) On Windows, use `py` or `python` in place of `python3` in the commands below.

| package | version | job |
|---|---|---|
| `ruff` | 0.16.3 | formatting, imports, annotations, bugbear, quotes, banned APIs |
| `pylint` | 4.0.7 | `mixedCase` function names, which no other linter can require |
| `mypy` | 2.3.1 | type correctness under `--strict` |
| `vermin` | 1.8.0 | the Python 3.11 floor |
| `hypothesis` | 6.165.10 | property tests, which the style requires |
| `pendulum` | 3.2.0 | dates and times |
| `spacy`, `en_core_web_md` | 3.8.16, 3.8.0 | the sentence parse behind `agentverbs.py` (`NAR017`) |

Then merge `pyproject-snippet.toml` into your project's `pyproject.toml`, or copy it for a new
project. Several settings differ from the tool defaults, and `tooling.md` gives the reason for each.

```bash
cp ~/.claude/skills/narrative/pyproject-snippet.toml pyproject.toml   # new project
```

## Verify

Run `verify.py` from your project root, and not the tools one by one:

```bash
cd your-project                                          # both defaults are relative
python3 ~/.claude/skills/narrative/verify.py .           # rewrites files: runs --fix and format
python3 ~/.claude/skills/narrative/verify.py . --no-fix  # reports only, changes nothing
```

It checks every Python file below the path. It runs `ruff check --fix`, `ruff format`, `pylint`,
`mypy --strict`, `checks.py`, `vermin` and `agentverbs.py`, in that order, because that order
converges. When a tool fails, it prints that tool's output.

Name a Markdown or HTML file, such as a README Claude wrote, and it gets the prose checks only:

```bash
python3 ~/.claude/skills/narrative/verify.py README.md docs/report.html
```

| exit | meaning |
|---|---|
| 0 | every tool passed |
| 1 | at least one tool reported a finding |
| 2 | the toolchain or the config is missing, so nothing was checked |

## Comments and docstrings

Comments and docstrings are written for a smart, experienced developer with the file open, in the vocabulary of the trade: `idempotent`, `tuple`, `API`.

By default, Claude's comments tend to record the reasoning behind the code: edge cases, alternatives and spec
gaps. `SKILL.md` instead starts with a test: what information does this comment give over
the code itself? Two rules follow. The reasoning belongs in the session user messages, and a comment
that a professional reader would get from the code below it is cut.

After a passing run, `verify.py` prints every comment and docstring summary, so the agent double checks its work.

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

`NAR000` is code for a file that could not be read or parsed.

## What is in this repository

| path | contents |
|---|---|
| `skill/` | the ten files of the skill. `architecture.md` has the multi-module rules |
| `install.sh` | the list of files in the skill, and the installer |
| `verify_docs.py` | checks that every decision id and rule code in the documents exists |
| `benchmark/decisions.jsonl` | all 456 decisions, each with its reasoning and evidence |
| `benchmark/round1/` to `round10/` | the rounds that produced the decisions. `benchmark/README.md` describes each |
| `benchmark/GAPS.md` | gaps found by writing real programs against the skill, and the rule each one became |
| `validation/` | held-out tasks, in three arms each: no guidance, the earlier style doc, the skill |
| `experiment/length/` | whether the style makes code longer: four tasks, two arms |

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
