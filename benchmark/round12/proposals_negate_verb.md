# Rule 1 (R12-negate-verb): examples that break the rule

A scan of `core/rules/`, `lang/*/rules/` and `lang/*/*.md` found 144 sentences with `no`, `nothing`, `none` or
`nobody` on a subject, an object or after `is`. The scan is a spaCy parse, and the script and the list are in
`~/.local/share/narrative/eval-private/runs/claudish-rules/rule1/`.

This file has the 13 examples of a comment, docstring, javadoc or message. Agents copy these. Each change waits for
your approval.

## A. Examples to rewrite

| # | file:line | now | proposed |
|---|---|---|---|
| A1 | core/rules/comments.md:209 | trade terms over paraphrase: `has no side effects` | trade terms over paraphrase: `doesn't have side effects` |
| A2 | core/rules/comments.md:125 | Marker: `vendor documents no encoding, UTF-8 assumed` | `vendor doesn't document an encoding, UTF-8 assumed` |
| A3 | core/rules/prose-review.md:20 | bad claim: `the log has no stop event, so the server never stopped` | `the log doesn't have a stop event, so the server didn't stop` |
| A4 | lang/java/rules/comments-java.md:27 | `// worlds saved before 1.2.0 have no "tier" tag` | `// worlds saved before 1.2.0 don't have a "tier" tag` |
| A5 | lang/java/rules/comments-java.md:62 | `// The vendor API returns at most 100 rows per page and no total count.` | `// The vendor API returns at most 100 rows per page, and doesn't return a total count.` |
| A6 | lang/python/rules/comments-python.md:52 | the same sentence as A5, with `#` | the same rewrite as A5 |
| A7 | lang/java/rules/javadoc-rules.md:58 | `The call writes no file, sends no packet, and changes no world` | `The call doesn't write a file, send a packet or change a world` |
| A8 | lang/python/rules/docstring-rules.md:43 | `The call writes no file, prints nothing, and records nothing` | `The call doesn't write a file, print output or log an event` |
| A9 | lang/python/rules/docstring-rules.md:37 | `host is null when the entry's report has no host` | `host is null when the entry's report doesn't have a host` |
| A10 | lang/python/rules/docstring-rules.md:9 | sentence to cut: `An empty line holds nothing` | `An empty line doesn't have a value` |
| A11 | lang/python/rules/docstring-rules.md:71 | bad claim: `nothing outside this module imports sqlite3` | `only this module imports sqlite3` |
| A12 | lang/python/rules/show-the-thing.md:47 | module docstring: `the bytes that no team owns` | `the unassigned bytes` |
| A13 | lang/java/tools/javachecks.py:641, shown in lang/java/README.md:34 | NAR118 message: `Planted has no javadoc.` | `Planted doesn't have a javadoc.` |

Notes:
- A1: the item is about the trade term `side effects`. The rewrite keeps the term and moves the negation onto the
  verb. Another option is a trade term without a negation, such as `idempotent`.
- A3, A10 and A11 are bad examples of other rules. The rewrite keeps each example's fault for the other rule and
  removes only the negated noun.
- A8 drops `records nothing`, because `records` with `the call` as the subject is a NAR017 form.
- A11 changes the negation to `only`. The claim is the same, and `do not claim to be the only place` is the rule
  beside the example.

## B. Examples outside the rule, left as they are

- `no` in a phrase, after `with` or another preposition: `a machine with no rate`, `a number with no suffix`,
  `Don't add with no retry`. The rule doesn't cover this form (probe 2a9f881a).
- labels without a verb: `// no default arm`, `# no case _`, `no policy.json in fixture/`, `No preview features.`
- the Python value `None`: `| None`, `response_model=None`, `Such a field holds None`, `Car contains none`.

## C. The prose of the rules, about 120 sentences

Examples: `write no comment` (3 times in writing-a-comment.md), `No tool checks this.` (8 times), `There is no layer
table`, `has nothing to do with`, `costs nothing`, `None of it applies`.

These wait for the de-poisoning pass after the rule 1 check is in `core/tools/agentverbs.py`. The check then gives the
list, and the same check confirms each fix.
