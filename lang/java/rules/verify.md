### Verify

Run `verify.py` from the root of the mod. Do not call the tools by hand.

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py"
python3 "${CLAUDE_SKILL_DIR}/verify.py" --since origin/dev
```

**In a PR to another project, pass `--since` with the base branch.** Upstream code already breaks
some of these rules, and a finding on a line the diff does not touch is not the PR's to fix. Only the
lines that the diff against `merge-base(HEAD, base)` adds or changes are reported, and every line of
an untracked file.

**Ask the user before you name something by an upstream convention that `NAR130` rejects.** For
example, GT5's `MultiblockTooltipBuilder` has about 40 `TT_*` fields, such as `TT_machineType`. A new
`TT_parallels` field beside those fields breaks the Java naming convention. With approval, mark the field
`// noqa: NAR130`. (J1-F06)

`verify.py` runs one Gradle invocation with the init script `narrative.init.gradle`: `spotlessApply`
(or `spotlessCheck` with `--no-fix`), `compileJava` with the raw-type and unchecked warnings of
javac, then Checkstyle and PMD with the configs beside `verify.py`. `javachecks.py` then reads the
comments, runs the prose checks, and merges the three reports into one list with NAR codes. A run
with exit 0 or 1 ends with three lists, the input to **Prose review**: every sentence of every
comment, javadoc and named page, every verb whose subject cannot act, and every sentence with a
pronoun. On a run with exit 1, `verify.py` prints the lists after the findings, and the count of
findings last. When Gradle fails, such as on code that does not compile, `verify.py` prints no
lists, because `javachecks.py` has not read the comments yet. With `--since`, the lists cover only
the changed lines. Without `--since`, each list stops after 1000 entries, with the command for the
next 1000. (J1-F01, J1-F09, J1-F14, J1-F15, J1-F16, R11-same-workflow)

| exit | meaning |
|---|---|
| 0 | every check passed. Warnings may be printed |
| 1 | at least one finding, or the code does not compile or is not formatted |
| 2 | the toolchain, `gradle.properties`, `gradlew` or a report is missing, the project is not Java 25, `--since` names no commit, or the diff changes no line |

Pass `--max-workers 1` on a busy machine. The job of each tool, the code table and the tool defaults
that break rules of this skill are in `tooling.md`. Read it before you change a config.

Before the report, for each test that you wrote or changed, name the rule under test and the source
of the test's cases: a generator, the boundary values or both. Where the answer is not both, fix the
test. (J1-P36)

