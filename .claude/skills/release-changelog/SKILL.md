---
name: release-changelog
description: Write the Discord changelog of a Narrative release, as messages under 2,000 characters with before-and-after tables in code blocks, built from the git diff and checked with verify.py. Use when the user asks for a changelog, release notes, or a Discord post for a commit or a range of commits.
---

# The Discord changelog of a release

Run each command from the root of the narrative-python checkout that has the release commits, usually master.
`discord_changelog.py` is in the directory of this skill.

1. **Read the range.** The user names a commit or a range. For one commit `SHA`, the range is `SHA^..SHA`.
   - `git log --format='%h %ad %s' --date=short RANGE`
   - `git diff --stat=200 RANGE` and `git diff --numstat RANGE`. Read the full list of files. Don't cut the list
     with `head` or `tail`. A changelog that an agent wrote from a cut list had wrong facts.
   - `git diff RANGE -- benchmark/decisions.jsonl` for the new decisions, and the added lines of
     `eval/units/claudish_inbox.jsonl` for the count of new units.
   - `git diff RANGE` of each rule file and each tool. This diff has the text before and after each change.
2. **Put the changes in sections.** The order of the sections:
   - new prose rules
   - new checks and review lists
   - the fixes of the checks and of the text of the skill

   In each section, put the change with the largest effect on the output of the skill first. Leave out an edit that
   the user made by hand, such as an edit of the README, unless the user asks for the edit.
3. **Write the spec**, a JSON file in the scratchpad. `examples/2b7637d.json` is the spec of commit `2b7637d`.
   - A message has a `lead`, a `table` of a `header` and `rows`, and a `tail`. The table and the tail may be left out.
   - The lead of a message starts with a bold section header, such as `**1. New prose rules**`. The first message
     starts with ``**Changes in Narrative `SHA`** (DATE)``. For a range, the first message starts with
     ``**Changes in Narrative since `SHA`** (DATE to DATE, N commits)``.
   - The header of a table is `Rule | Before | After`, `Case | Before | After`, or `Area | Before | After`.
   - Take each Before and After from the text of a rule, the diff, a fixture, or the output of the skill. Never write
     a rewrite of yours in a cell.
   - A newline in a cell starts a new line in the cell, such as the lines of a bulleted list.
4. **Build the messages.**
   `uv run --no-project python discord_changelog.py SPEC OUT --prose PROSE`

   OUT and PROSE go in the scratchpad. The script prints the length of each message. Exit code 1 means a message has
   more than 2,000 characters. Discord doesn't post a longer message. Move the last rows to a new message with
   the lead `**N. SECTION** (continued)`, and build again.
5. **Check each claim against the diff**, such as each count, each name of a check, and each cell of a table.
6. **Check the prose outside the tables.**
   `python3 skills/python/verify.py PROSE --no-fix --cache-dir SCRATCHPAD/vcache`

   Fix each finding, and answer each entry of `review-lists.txt`. Edit the spec, build again, and check again until
   both checks pass. The tables quote rules and code, so the checks skip the code blocks.
7. **Send OUT to the user.** Don't add OUT to the repository.
