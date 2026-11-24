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
`TT_parallels` field beside those fields breaks the Java naming convention. If the user approves, add the finding
to the keep-list (the rule is under **noqa**). (J1-F06, J1-no-noqa)

`verify.py` runs one Gradle invocation with the init script `narrative.init.gradle`, at every
level of **Scope**:

1. `spotlessApply` (or `spotlessCheck` under `--no-fix`)
2. `compileJava` with the raw-type and unchecked warnings of javac
3. Checkstyle and PMD with the configs beside `verify.py`

`javachecks.py` then reads the comments, runs the prose checks, and merges the three reports into
one list with NAR codes. A run with exit 0 or 1 writes six lists to
`.narrative_cache/review-lists.txt`, the input to **Prose review**:

- every sentence of every comment, javadoc, and named page
- every verb whose subject cannot act
- every sentence with a pronoun
- every sentence with a free modifier
- each javadoc and member comment, and each method over 20 body lines (`NAR116`)
- each method and constructor with more than 3 parameters (`NAR131`)

The `NAR116` list comes from the PMD report, and the `NAR131` list from the Checkstyle report, so a
run with `--prose-only` doesn't have these two lists. The file and the number of entries in each list are on the last line of the output. When Gradle fails, such as on code that does not compile, `verify.py` doesn't
write the lists, because `javachecks.py` has not read the comments yet. When `--since` is given, the
lists cover only the changed lines of the code and the pages. Otherwise each list stops after 1000
entries, with the command for the next 1000. (J1-F01, J1-F09, J1-F14, J1-F15, J1-F16, R11-same-workflow)

| exit | meaning |
|---|---|
| 0 | every check passed. Warnings may be printed |
| 1 | at least one finding, or the code does not compile or is not formatted |
| 2 | the toolchain, `gradle.properties`, `gradlew`, or a report is missing, `enableModernJavaSyntax` or `forceToolchainVersion` has a value without a level in **Scope**, `--since` doesn't name a commit, the diff doesn't change a line, `javachecks.py` stopped before the count line of the findings, or the review lists could not be written |

Pass `--max-workers 1` on a busy machine. The job of each tool, the code table, and the tool defaults
that break rules of this skill are in `tooling.md`. Read it before you change a config.

**After an edit of comments or pages only, pass `--prose-only`.** Gradle does not run, so the run
takes seconds: the re-wrap, the prose checks and the review lists. Spotless, javac, Checkstyle, and
PMD run only without `--prose-only`, so the last run before the report is a run without
`--prose-only`.

`--project DIR` makes `verify.py` check the mod in DIR. `--cache-dir DIR` puts `.narrative_cache`
in DIR, such as a directory outside a checkout that the agent may not write. A path of `-` is a
page read from stdin, such as a draft that is not in a file yet.

Before the report, for each test that you wrote or changed, name the rule under test and the source
of the test's cases: a generator, the boundary values or both. Where the answer is not both, fix the
test. (J1-P36)

