
# Narrative comments and prose

These rules cover comments, docstrings, javadoc, error messages, help text and published pages, in
every language of Narrative. For code, load this skill together with `nar:repo` and the skill of the
language, such as `nar:python` or `nar:gtnh`. For a page outside a code repository, load this skill
together with `nar:page`. The checks run through the `verify.py` of the language skill or of
`nar:page`. For a language without a Narrative skill, such as C, C++, JavaScript, or Verilog, load
this skill together with `nar:repo`, and run the `verify.py` of this skill:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" . --since origin/main
```

**The steps, in short. The details are in Procedures, the last section of `nar:<language>`.**
(R11-steps-summary)
1. Load this skill and `nar:<language>` before you plan a change, not only before you edit.
2. Make a batch of edits, then run `verify.py` once for the batch.
3. Read the findings and the review lists of that run. Do not filter the output with `grep`, `head`, or
   `tail`.
4. Fix every finding and answer every list entry from that one run, then run `verify.py` once more.
5. In the report, say how many entries of each list you read, such as `read 212 of 212 sentences`.

In these rules, a docstring is the doc comment of the language, such as a javadoc in Java, and a
function is a function or a method. `nar:<language>` names the skill of the language of the file.
For Python the skill is `nar:python`, and for Java in a GTNH mod the skill is `nar:gtnh`.

