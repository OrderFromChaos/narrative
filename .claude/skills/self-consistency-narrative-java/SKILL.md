---
name: self-consistency-narrative-java
description: Check the narrative-java skill's own files against its own rules, so no violation reaches agents that load it. Covers the prose of lang/java/rules/*.md, the Java documents and README, the Java code examples in those files, the Python scripts and the fixtures. Use when the user asks for a self-consistency pass, a self-evaluation, or to re-apply the rules to the skill.
---

# Self-consistency of narrative-java

Agents copy the wording and the examples of `lang/java/rules/*.md`, so a violation there is copied into
new code. Run every step from the repository root. Edit `lang/java/`, then run `python3 build_skills.py`,
because `skills/` is generated. Change nothing that a rule does not require, and commit
nothing.

1. **New rules since the last pass.** `git log -1 --format=%cs -- lang/java core` gives the date. Read every
   record of `benchmark/decisions.jsonl` from that date on, and look for examples that a new rule
   makes wrong.

2. **Prose of the docs.** The wording checks one code at a time, without NAR012, because the docs
   cite decision ids as provenance:

   ```bash
   for code in NAR013 NAR014 NAR015 NAR016 NAR018; do python3 skills/python/checks.py --select $code lang/java/rules/*.md lang/java/architecture.md lang/java/tooling.md lang/java/README.md; done
   ~/.local/share/narrative/lintenv/bin/python skills/java/agentverbs.py lang/java/rules/*.md lang/java/architecture.md lang/java/tooling.md lang/java/README.md
   ~/.local/share/narrative/lintenv/bin/python skills/java/agentverbs.py --review lang/java/rules/*.md lang/java/architecture.md lang/java/tooling.md lang/java/README.md
   ```

   Known and accepted: in the rule modules, the NAR014, NAR016 and NAR018 hits on the lines with the banned
   words as examples, the NAR017 misparses `value knowing` and `Comments thinking`, which the Python skill
   has too, the NAR017 misparse `each flagged` (`re-wraps each flagged javadoc paragraph`), and the
   NAR022 hit `its state` in the quoted Forge log message. In `lang/java/README.md`, the NAR014 hit on the list
   of findings. Take the steps of **Prose review** in `lang/java/rules/prose-review.md` for each pair of the review list.

3. **Java examples.** Write each fenced `java` block of `lang/java/rules/*.md` and `lang/java/*.md` to a `.java` file in the
   scratchpad, and run `javachecks.py` on them for the comment checks:

   ```bash
   ~/.local/share/narrative/lintenv/bin/python skills/java/javachecks.py <scratch>/examples/
   ```

   The blocks are fragments, so NAR118 on them is expected. Every other finding is a fault in an
   example. An inline example in backticks, such as `` `// the vendor closes idle sockets at 60 s` ``,
   is not covered. Read those by hand.

4. **Python scripts**, with the toolchain of the Python skill, from a scratch directory whose
   `pyproject.toml` is `lang/python/tools/pyproject-snippet.toml`:

   ```bash
   cd <scratch> && PATH=<repo>/.lintenv/bin:$PATH <repo>/.lintenv/bin/python <repo>/skills/python/verify.py --venv <repo>/.lintenv <repo>/lang/java/tools/javachecks.py <repo>/lang/java/tools/codeprose.py <repo>/lang/java/tools/verify.py <repo>/lang/java/tests/run_fixtures.py <repo>/lang/java/tests/run_rewrap.py
   ```

   All 7 checks must pass.

5. **Fixtures**: `python3 lang/java/tests/run_fixtures.py --gradle <gradle>` reports 0 files with the wrong
   codes. One Gradle run at a time, at `nice -n 19`. `~/.local/share/narrative/lintenv/bin/python
   lang/java/tests/run_rewrap.py` reports 0 cases wrong.

6. **Records and build**: `python3 verify_docs.py` reports 0 problems.

7. **Fix and report.** Fix a clear violation in place. A change to a rule goes to the user first.
   Run the steps again. After the user commits, `./install.sh java` updates the installed copy.
