# Does /narrative-python raise Opus 5.5 High's SWE-rebench score?

## Why

With the comment-rewrite steps of `SKILL.md`, the model checks each fact of a comment against the
code. During that check, real bugs have turned up that nobody asked about. The question here is
whether the skill also raises the resolved rate on a standard benchmark that Opus 5.5 High has not
saturated.

SWE-rebench has real GitHub issues from Python repositories, each with the fix PR's hidden tests and
a prebuilt Docker image. On the leaderboard's window from 15 May to 1 July 2026, the top model
resolves 64.5%, and Opus 5 [high] resolves 63.4% ([swe-rebench.com](https://swe-rebench.com)). There
is no published score for Opus 5.5.

## Control

Two arms. Same Claude Code binary, model `claude-opus-5-5`, `--effort high`, prompt, tools and
container limits. In the skill arm, the skills `python` and `core` of `skills/` are loaded as the
session plugin `nar`, and the prompt starts with `/nar:python`. The pilot below ran the earlier
single skill as `/narrative-python:narrative-python`. Each result file has the model named in the session's
init event, the models billed, and the input tokens of the first API call. The skill arm's first
call is larger by the size of SKILL.md, about 25,000 tokens.

## Isolation

The task code is third-party: the repository, the repository's test hooks such as `conftest.py`,
the image's packages, and the issue text. No credential is in the same place as that code.

- Claude Code runs on the host in a copy of the task's /testbed, under a login in a dedicated
  config directory. `--restricted` and `--tools` leave only the file tools, Skill, Task and
  ToolSearch. The shell, WebFetch and WebSearch are off, and the file tools are confined to the copy.
- Commands go through `container_tool.py`, an MCP server with one tool, `run`. `run` executes bash
  in the task's container: `--network none`, the host user's uid, the copy at /testbed, and no
  credential or login file mounted.
- `claude` gets an environment built from nothing but HOME, PATH, LANG and the config directory.
- `claude` runs inside bubblewrap. The filesystem is read-only except the copy, the config directory,
  a private /tmp and the Docker socket, so a write anywhere else fails in the kernel.

`run.py sandbox` checks the bubblewrap and container layers with no model call. `run.py hostile`
asks a session for the same escapes. In both runs of `hostile`, the requests were refused, so
`hostile` can't test the file tools.

The tasks are the 860 tasks of the SWE-rebench-leaderboard test split, created from January 2025 to
May 2026. Opus 5.5's training cutoff is June 2026, so some fixes may be in Opus 5.5's training
data. The tasks are the same in both arms, so a fix in the training data raises both arms. The
pilot checks that the base arm is well below 100% before any larger run.

The pilot is a seeded random 30 of the 860, listed in `sample.json`.

## Usage

Convert the published parquet file once:

```bash
mkdir -p ~/.cache/narrative-bugfind
```

```bash
curl -sL -o ~/.cache/narrative-bugfind/test.parquet https://huggingface.co/api/datasets/nebius/SWE-rebench-leaderboard/parquet/default/test/0.parquet
```

```bash
uv run --no-project --with pyarrow python -c "import json, pyarrow.parquet as pq; open('$HOME/.cache/narrative-bugfind/tasks.jsonl', 'w').writelines(json.dumps(row, default=str) + '\n' for row in pq.read_table('$HOME/.cache/narrative-bugfind/test.parquet').to_pylist())"
```

Log in once to the dedicated config directory: start `claude` with
`CLAUDE_CONFIG_DIR=~/.config/narrative-bugfind/claude-config`, then `/login`, then `/exit`. Runs use
the plan of that login. `/logout` in the same directory ends the login.

```bash
uv run experiment/bugfind/run.py gold --tasks ~/.cache/narrative-bugfind/tasks.jsonl --limit 2
```

```bash
uv run experiment/bugfind/run.py sandbox --tasks ~/.cache/narrative-bugfind/tasks.jsonl
```

```bash
uv run experiment/bugfind/run.py run --tasks ~/.cache/narrative-bugfind/tasks.jsonl --limit 1 --jobs 1
```

Each image is 1.3 GB to 2.5 GB over a shared 2.1 GB base. An image is removed when its task is done,
so disk use stays near the base plus --jobs images.

## Pilot results

Run 1, 18 and 19 October 2026, skill at commit `ce50800`. `measure.py` builds `RESULTS.json` from the
result files.

| arm | resolved | new tests passed | old tests broken | cost at list rates | agent time |
|---|---|---|---|---|---|
| base | 16 of 28 (57%) | 42 of 71 | 4 | $10.06 | 82 min |
| skill | 16 of 28 (57%) | 43 of 71 | 1 | $21.49 | 92 min |

- Resolved rate is the same. The arms disagree on 4 tasks: base alone resolved
  `python-pillow__Pillow-9023` and `ucfopen__canvasapi-716`, and skill alone resolved
  `sqlfluff__sqlfluff-7617` and `marcosschroh__dataclasses-avroschema-835`. The exact McNemar p is
  1.0.
- New tests are FAIL_TO_PASS tests, a secondary partial-credit measure. Old tests broken are
  PASS_TO_PASS tests that fail after the patch. 1 against 4 is 5 events, too few to read.
- The skill arm costs 2.1 times as much. The first API call of a skill-arm session has 35,267 to
  44,396 input tokens, against 11,031 to 15,580 in the base arm, because SKILL.md is in the prompt.
- Base resolves 57%, so SWE-rebench isn't saturated for Opus 5.5 High. No session fell back to
  another model.
- With 28 tasks, only a large effect is visible. The pilot rules out a large gain or loss in
  resolved rate, and a small one could still exist.

### Excluded tasks

- `NeurodataWithoutBorders__pynwb-2056`: the same tests fail with the gold patch and without the
  gold patch, so the task can't be graded here. Grading runs with no network, and that may be the
  cause. Not checked.
- `pyccel__pyccel-2512`: the base arm hit the 45-minute limit while the machine's load average was
  about 20 on 16 cores, from other jobs. The diff of that arm has 3,007 files. One is a source file.
  The other 3,006 are written to the repository by pyccel's tests. The skill arm was stopped by hand.

### Grading bugs found during the pilot

Each bug was in grading, not in the model runs. Every result was graded again from its saved diff
by `run.py regrade`, and only `collective__icalendar-880` was run again.

1. `runHost()` stripped the last newline from each diff, and `git apply` rejected 11 of 44 patches.
   Diffs are now kept verbatim.
2. The /testbed of some images has local changes, such as an edited pyproject.toml in
   `mlte-team__mlte-809`. Those changes are in a diff taken against HEAD too, so `git apply` rejects
   the diff in a fresh container. Each file of the diff is now reset to HEAD before the apply.
3. A test patch that creates a file failed to apply when the agent had created a file at the same
   path (`collective__icalendar-880`). Each file of the test patch is now reset to HEAD, or deleted,
   first. The diff of that run was written after grading and was lost, so both arms ran again.
4. The skill-loaded check looked for the skill's text in the log, and a stream-json log doesn't have
   the prompt. The result files now have the input tokens of the first API call.
5. One Docker Hub timeout stopped `optuna__optuna-6428` before any model call. The task ran again.

### Limits

- Both runs of `run.py hostile` ended in a refusal, so `hostile` tested nothing about the file tools.
  `run.py sandbox` tests the bubblewrap layer with no model.
- The two arms of a task run at different times, under different machine load. In a larger run,
  start both arms of a task together, and record the load average.
- Files written to the repository by a test suite go into the diff. pyccel is an example. With
  `git diff --binary`, `git apply` accepts such a diff. Check by hand a diff with more than a few
  hundred files.
- For 43 of the 49 tasks with an interface, the interface is in the issue text, and the prompt has a
  second copy. Both arms get the same prompt. Fix before a larger run.
- In SWE-rebench, the bug is given in the issue. So the effect behind this experiment, a bug found
  during a comment check with nobody asking, isn't visible in this metric. The bug-discovery check
  in the plan is for that effect.
