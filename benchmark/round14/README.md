# Round 14: page cleanups

Round 14 has the rules of `nar:page` for the cleanup of a page that exists, and rules for the design of an HTML page.
The rules come from the user's feedback of 2026-11-24: a prompt from the gtnh-speedrun-audit repository on the
cleanups of README.md and VERIFIERS.md, and two old artifacts that the user reviewed after a cleanup with the drafts.
`decisions.jsonl` has one `R14-*` decision per rule.

In a cleanup, the agent labels each section `keep`, `move` or `cut` for the named reader, makes the moves and the cuts,
dates each relative time, and only then runs `verify.py --cleanup`, so the cuts come before the sentence fixes. For
the cleanup, `verify.py` lists each section with the section's words, flags a release named by the release's place in
the history (`NAR028`), and prints the words of the page against HEAD.

The fresh-agent tests of `.claude/skills/new-narrative-rule` are still to do. The test inputs are:

| Input | Reader | Units | Location |
|---|---|---|---|
| README.md of gtnh-speedrun-audit at `467f885` | runners | 15 sections | private, `~/.local/share/narrative/eval-private/page-triage/readme/` |
| VERIFIERS.md of gtnh-speedrun-audit at `00ff77f` | moderators | 77 sections, 25 dates | private, `~/.local/share/narrative/eval-private/page-triage/verifiers/` |
| `depot-board/README.md` | dispatchers | 25 sections, 5 dates | this directory |

`labels.jsonl` has a label for each unit of the depot page. Claude wrote the labels, and the labels haven't been checked,
so the labels are bronze. For the private inputs, the labels are silver: Claude took the labels from the user's cleanups in
commit `00ff77f` (README.md) and commit `d5fda33` (VERIFIERS.md).
