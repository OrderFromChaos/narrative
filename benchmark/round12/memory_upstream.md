# Prose rules from the memories of Claude

Each prose pattern below is in a memory of Claude on this machine, and not in the skill. After you approve the
drafts, the rules go into the skill with a record in `decisions.jsonl`, and I remove the patterns from the
memories.

Each draft is de-poisoned by step 5 of the skill `new-narrative-rule`:

- the prose checks: `NAR012`–`NAR018`, `NAR017`, `NAR020`–`NAR022`, `NAR024`–`NAR026`, and the lists for review
- the text after each arrow, checked as a comment
- a read against your Claudish patterns and against the other drafts

The text after each arrow doesn't have an entry on a review list. An agent copies the example of a rule word for
word, so each example shows the fix that fits most often.

## Patterns that are already rules

| memory | pattern | rule |
|---|---|---|
| `claudish-patterns` | `what the X of the Y` | `R10-nominal-chain` |
| `claudish-patterns` | a stand-in pronoun | `R10-stand-in`, `NAR022` |
| `claudish-patterns` | a condition after `with` at the start | `R12-no-prep-opener`, `NAR026` |
| `claudish-patterns` | `X, not Y` and `not merely` | `R12-not-contrast`, `NAR024` |
| `claudish-patterns` | `as X, for Y` | `R12-no-free-modifier` |
| `claudish-patterns` | a statement too obvious to need a comment | `R10-restatement-gate` |
| `claudish-patterns` | a long clause for a thing with a domain word | `R11-rewrite-from-code` |
| `claudish-patterns` | `Every X, at Y` | `R12-every` |
| `no-personified-abstractions` | an abstract noun as the subject of an act, such as `the parser owns the retry` | `NAR017` |
| `no-personified-abstractions` | a metaphor on a verb, such as `one comment anchors the block` | `NAR017`, or the list of pairs |
| `no-personified-abstractions` | a container verb | `NAR016` |
| `no-personified-abstractions` | a vague `it` | `NAR022` |
| `no-personified-abstractions` | a paraphrase where a trade term exists | `R10-seed-3` |

## Drafts

`core/rules/comments.md`, **Sentence form**:

1. ~~`R10-tool-subjects`: the input as the subject of `passes` or `fails`.~~ Dropped: `pylint flags a mixedCase local`
   is fine, and `NAR017` flags `mypy sees node.name`, the one sentence of this form in the units.
2. ~~`R10-owner-term`: `belongs in` for the place of code.~~ Dropped: `NAR017` flags `the parser owns the retry`.
3. ~~Metaphors.~~ Dropped: `NAR017` or the list of pairs has a metaphor on a verb, such as `one comment anchors the
   block`.
4. A new intensifier, `only`. `only` is in the current first sentence of the item, so that sentence is reworded:
   ```
   - no intensifiers. Drop a word that adds stress and doesn't add a fact, such as `exactly`,
     `always`, `every`, `only`, `precisely`, or `simply`.
   ```
5. A scenario, in place of the item `the general case` (`R10-Q40`) that you flagged on 2026-11-22:
   ```
   - Write the behaviour for any input, and leave out a scenario and a sample count: `records two
     and three are separated by a blank line` → `records are separated by blank lines`, and `A file
     with 10,000 bad rows emits one record at the default level` → `emit one status record per file`
   ```
6. ~~`The` at the start.~~ Dropped: `The vendor API` is fine. In `The scan version changes on a block change`,
   the fault is `scan version`, a term that is neither the domain's word nor an identifier. The two tests for a term
   in **Comments** are about that fault.
7. A colon. Item 3 of `benchmark/OPEN_WORK.md` has this rule as open:
   ```
   - Write two sentences in place of a clause joined by a colon, or of an `X: Y` opening. When the
     half after the colon is a definition of the word before the colon, cut the definition:
     `# idempotent: a second run changes nothing` → `# idempotent`. A colon is fine before a code
     example or a bulleted list (draft 12)
   ```

`core/rules/published-prose.md`:

8. The history of a page:
   ```
   State the current fact and the condition of the fact. Don't write the history of the page, such
   as an earlier figure or a change of mind: `far smaller than it first looked` → `9% less
   code on a spec with fixed outputs`
   ```
9. Headings:
   ```
   A heading is the name of the topic: `What goes in a body, and what does not` → `Docstring body`
   ```
10. A README:
    ```
    Open a README with the benefit to the reader. Give a number for the benefit when you have one.
    Then put a cost of adoption in a short caveat, and then an example. Put evidence and process in
    other documents, and link to those documents from the README.
    ```
11. Instructions for an agent, such as a skill or a prompt:
    ```
    In instructions for an agent, don't use a verb of perception such as `see`, `look`, or `notice`.
    Name the act: `see the list` → `read the list`
    ```

`core/rules/comments.md`, **Sentence form**, a separate rule:

12. A bulleted list. You flagged `General term: example 1, example 2, …, and example 8.` on 2026-11-22:
    ```
    - a list of more than two items after a colon in bullets. Put a sentence about the list above
      the bullets. A list of two items may be inline:
      `Retried errors: a timeout, a refused connection, a reset connection, and an HTTP 503.` →
      Retry on these errors:
      - a timeout
      - a refused connection
      - a reset connection
      - an HTTP 503
    ```

13. The Oxford comma:
    ```
    - use the Oxford comma
    ```

## Conflicts with the skill

- **Draft 12.** Ten sentences of the skill have a colon and then a list of three or more items in backticks, such as
  `` A parameter has the narrowest interface the method uses: `Iterable`, `Collection`, `List`, `Map`. `` in
  `lang/java/rules/types.md`. The others are in `core/rules/comments.md` (4), `lang/java/rules/gtnh.md` (2),
  `lang/python/rules/module-state.md`, `lang/python/rules/verify.md`, and `lang/python/tooling.md`. Proposed: a bulleted
  list for each.
- **Draft 12, the scope.** The draft is about a list after a colon, the form that you flagged. A list of three items
  in a sentence, such as `a timeout, a refusal, or a reset`, stays inline.

- **Draft 13.** I ran a probe with spaCy over the rule files and the Java and Python docs. The probe has 103 hits, each
  a list without the Oxford comma. Proposed: I add each comma in the de-poisoning pass after
  your approval. I turn the probe into a check if the probe is precise on human code.

## The memories after the change

- `claudish-patterns`, `no-personified-abstractions`, `docs-state-facts-not-revisions`, and `readme-pitch-style` are
  removed.
- `agent-verbs-flag-vagueness` has the rulings of your 2026-10-13 review on `NAR017`. An example: `the table shows`
  is fine, and `the summary shows` isn't. The rulings go into the `NAR017` paragraph of `core/rules/comments.md`, and
  the memory is removed.
- The memories about the work, such as `never-commit-or-push` and `complex-questions-in-files`, stay. They aren't
  prose rules.
