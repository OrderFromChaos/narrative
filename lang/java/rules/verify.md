### Verify

Run `verify.py` from the root of the mod. Do not call the tools by hand.

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py"
python3 "${CLAUDE_SKILL_DIR}/verify.py" --since origin/dev
```

**To check only what changed, pass `--since` with the commit before your edits**, in any repository: `--since HEAD`
for uncommitted edits, or `--since main` on a branch. In a repository with no commits, name the changed files as
paths, and do not filter the output. In a stacked PR, pass `--since` with the branch that you created the PR's branch
from, such as the branch of PR 2 for PR 3. (R11-since-any)

**In a PR to another project, pass `--since` with the base branch.** Upstream code already breaks
some of these rules, and a finding on a line the diff does not touch is not the PR's to fix. Only the
lines that the diff against `merge-base(HEAD, base)` adds or changes are reported, and every line of
an untracked file. List each finding that was already on the base branch under `upstream findings kept`, and ask the user once
whether to fix those findings. (R11-upstream-ask)

**Ask the user before you name something by an upstream convention that `NAR130` rejects.** For
example, GT5's `MultiblockTooltipBuilder` has about 40 `TT_*` fields, such as `TT_machineType`. A new
`TT_parallels` field beside those fields breaks the Java naming convention. With approval, mark the field
`// noqa: NAR130`. (J1-F06)

`verify.py` runs one Gradle invocation with the init script `narrative.init.gradle`: `spotlessApply`
(or `spotlessCheck` with `--no-fix`), `compileJava` with the raw-type and unchecked warnings of
javac, then Checkstyle and PMD with the configs beside `verify.py`. `javachecks.py` then reads the
comments, runs the prose checks, and merges the three reports into one list with NAR codes. A run
with exit 0 or 1 writes three lists to `.narrative_cache/review-lists.txt`, the input to **Prose
review**: every sentence of every comment, javadoc and named page, every verb whose subject cannot
act, and every sentence with a pronoun. The file and the number of entries in each list are
on the last line of the output. When Gradle fails, such as on code that does not compile, `verify.py` writes
no lists, because `javachecks.py` has not read the comments yet. With `--since`, the lists cover only
the changed lines of the code and the pages. Without `--since`, each list stops after 1000
entries, with the command for the next 1000. (J1-F01, J1-F09, J1-F14, J1-F15, J1-F16, R11-same-workflow)

| exit | meaning |
|---|---|
| 0 | every check passed. Warnings may be printed |
| 1 | at least one finding, or the code does not compile or is not formatted |
| 2 | the toolchain, `gradle.properties`, `gradlew` or a report is missing, the project is not Java 25, `--since` names no commit, the diff changes no line, or the review lists could not be written |

Pass `--max-workers 1` on a busy machine. The job of each tool, the code table and the tool defaults
that break rules of this skill are in `tooling.md`. Read it before you change a config.

**After an edit of comments or pages only, pass `--prose-only`.** Gradle does not run, so the run
takes seconds: the re-wrap, the prose checks and the review lists. Spotless, javac, Checkstyle and
PMD run only without `--prose-only`, so the last run before the report is a run without
`--prose-only`.

With `--project DIR`, `verify.py` checks the mod in DIR. With `--cache-dir DIR`, `.narrative_cache`
is in DIR, such as a directory outside a checkout that the agent may not write. A path of `-` is a
page read from stdin, such as a draft that is not in a file yet.

Before the report, for each test that you wrote or changed, name the rule under test and the source
of the test's cases: a generator, the boundary values or both. Where the answer is not both, fix the
test. (J1-P36)

