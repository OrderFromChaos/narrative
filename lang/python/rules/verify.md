### Verify

Run `verify.py`. Do not call the tools by hand.

```
python3 "${CLAUDE_SKILL_DIR}/verify.py" .
python3 "${CLAUDE_SKILL_DIR}/verify.py" . --since origin/main
```

Pass `verify.py` any path. Every Python file below that path is checked. Run `verify.py` from the
project root, because the default `--config` is `./pyproject.toml`. `verify.py` rewrites files with
`checks.py --rewrap`, `ruff check --fix` and `ruff format`, unless you pass `--no-fix`. For each
tool that fails, `verify.py` prints that tool's output. With `--cache-dir DIR`,
`.narrative_cache` is in DIR, such as a directory outside a checkout that the agent may not write. A path of `-` is a
page read from stdin, such as a draft that is not in a file yet.

**To check only what changed, pass `--since` with the commit before your edits**, in any repository: `--since HEAD`
for uncommitted edits, or `--since main` on a branch. In a repository with no commits, name the changed files as
paths, and do not filter the output. In a stacked PR, pass `--since` with the branch that you created the PR's branch
from, such as the branch of PR 2 for PR 3. (R11-since-any)

**In a PR to another project, pass `--since` with the base branch.** Upstream code already breaks
some of these rules, and a finding on a line the diff does not touch is not the PR's to fix. Only
the lines that the diff against `merge-base(HEAD, base)` adds or changes are reported, and every
line of an untracked file. A finding on a `def` or `class` line counts for every line of the
definition, and a finding in a comment or docstring counts for every line of the passage. Under
`--since`, `verify.py` applies a fix of `ruff check` only when the fix edits a changed line, and
`ruff format` formats only the changed lines. When the project's `pyproject.toml` is not a Narrative
config, pass `--config` with a copy of `pyproject-snippet.toml` named `pyproject.toml`, outside the
project. List each finding that was already on the base branch under `upstream findings kept`, and ask the user once
whether to fix those findings. (R11-upstream-ask) (R11-since, R11-same-workflow)

`verify.py` resolves every tool to an absolute path. It exits 2 when a tool is missing or
`pyproject.toml` is absent. **Do not replace it with a loop that greps tool output for findings.**
With such a loop, a missing binary or config produces empty output, and empty output reads as a pass.

`verify.py` runs these tools, in the order that converges: `checks.py --rewrap`,
`ruff check --fix`, `ruff format`, `pylint`, `mypy --strict`, `checks.py`, `vermin`, `agentverbs.py`.
A run with exit 0 or 1 writes three lists to `.narrative_cache/review-lists.txt`, the input to **Prose
review**: every sentence of every comment, docstring and named page, every verb whose subject cannot
act, and every sentence with a pronoun. The file and the number of entries in each list are
on the last line of the output. With `--since`, the lists cover only the changed lines of the code and the
pages. Without `--since`, each list stops after 1000 entries, with the command for the next 1000.
`verify.py` keeps the spaCy results of each comment in `.narrative_cache/` in the current
directory, so a run after a small change parses only the changed comments. (R11-lists-on-failure,
R11-page-inventory, R11-list-pages, R11-prose-cache)

| exit | meaning |
|---|---|
| 0 | every tool passed |
| 1 | at least one tool had a finding |
| 2 | the toolchain or the config is missing, so nothing was checked, or the review lists could not be written |

The job of each layer, and the tool defaults that break rules of this skill, are in `tooling.md`. For
example, `ruff check --fix` collapses blank lines after imports, and the `SIM114` fix merges branches
and loses type narrowing. Read `tooling.md` before you change config.

