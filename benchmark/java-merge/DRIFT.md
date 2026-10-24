# Drift between the shared sections of narrative-python and narrative-java

The narrative-python text of five sections is now in `core/rules/`: **Comments**, **Procedures**
(the introduction), **Writing a comment**, **Prose review** and **Published prose**. narrative-java
has a copy of each section, now in `lang/java/rules/` (`comments.md`, `procedures.md`,
`writing-a-comment.md`, `prose-review.md` and `published-prose.md`).
Every difference between the two copies is listed below. Before narrative-java builds from `core/`,
each difference gets a ruling from you: core, leaf, or drop. Until then, `skills.toml` builds
narrative-java from the Java copies.

- **core**: the text goes into `core/rules/`, for every language
- **leaf**: the text stays in the one language, in `lang/<language>/rules/`
- **drop**: the text leaves both skills

On 2026-10-24 you ruled on A1 and B1 to B7, and handed the rest to the recommendations. Those rows
say **as recommended, delegated**.

The tools have no drift. Both skills now build from one copy in `core/tools/`.

## A. Examples and words of the language

Most of the drift is the same rule with Java examples: `#` against `//`, function against method,
docstring against javadoc, `None` against `null`, `match` against `switch`, and Minecraft examples in
place of billing examples. About 200 of the 292 changed lines of **Comments** are of this kind.

Proposal: the rule text is written once in `core/rules/`. Each example becomes a slot, such as
`<!-- example: source-fact -->`. `lang/python/examples/` and `lang/java/examples/` have one file per
slot, and `build_skills.py` puts the language's file in place of the slot. A slot with no file for
a language fails the build. For narrative-python, the built SKILL.md stays byte for byte the same as
today.

| | Recommendation | Decision |
|---|---|---|
| A1. Examples per language | Slots, before the skills became composable | **Neutral examples in core.** `nar:core` is one skill for every language, so an inline example in core has no `#` or `//` and comes from a domain any language fits. A code-block example moves to the language skill, under the name of the rule |

## B. Rules in narrative-java only

| | id | Section | Rule | Recommendation | Decision |
|---|---|---|---|---|---|
| B1 | J1-F11 | Comments, rewrite step 3 | When a fact is false and the correct answer to the same question is at the same source, keep the correct answer in place of the false fact | **core.** Nothing in the rule is about Java | **core** |
| B2 | J1-F12 | Comments, Source kind | A fact about a value from outside the code (a library, a framework, an old save) is a Source fact, written only above the code for the value. A Source comment is allowed only above code that depends on the fact | **core**, with a Python example in a slot, such as a column missing from old databases | **core**, with a neutral example |
| B3 | J1-F10 | Comments, Every term | An identifier as a link (`{@link}` in javadoc), so the reader can jump to the identifier and a rename in the IDE updates the identifier. The Python form is backticks | **leaf.** The rule of a pointer the reader can jump to is in core already. `{@link}` is the Java form, in a slot | **leaf** (Java) |
| B4 | (no id) | Comments | In a PR to another project, leave the comments that exist on the base branch as they are, even the ones the diff moves | **core, with a new decision record.** The rule fits `--since` in both languages, but a rule with no id does not ship | **core**, with the new decision `J1-pr-base-comments` |
| B5 | J1-F4 | Comments, kinds | `FIXME:` is a warning (code 119, exit 0), because a mod has no `main` and every method counts as reachable. In Python, `NAR010` blocks the merge in reachable code | **leaf.** The reason is particular to a mod | **leaf** (Java) |
| B6 | J1-verbs-literal | Comments, Sentence form | `draws` is an agent verb for a widget whose drawing is not the point | **leaf**, as a Java example. The test of the rule, whether the subject can perform the verb, is in core already | **leaf** (Java) |
| B7 | J1-P35 | Comments, findings | A `// noqa` covers the whole comment block and the next code line, because spotless moves a trailing noqa | **leaf.** The reason is spotless | **leaf** (Java) |
| B8 | J1-F14 | Prose review | The scope of the review adds lang entries (Minecraft localisation files) and command help text | **core, reworded** as every text a user reads: error messages, help text and localisation files. Lang entries become the Java example | as recommended, delegated |
| B9 | J1-F15 | Published prose | A page named beside Java sources gets the same checks, in the same list of findings | **leaf.** The sentence is about the Java `verify.py` | as recommended, delegated |

## C. Text in narrative-python only

These are in `core/rules/` today, and narrative-java has no copy of them. The ruling for each is
whether narrative-java is to have the text. **core** means both skills, and **leaf** means Python only.

| | Section | Text | Recommendation | Decision |
|---|---|---|---|---|
| C1 | Procedures | **Setup** happens once per project too, not only once per machine. In Python, Setup merges `pyproject.toml` into the project | **leaf.** In Java, Setup is once per machine only | as recommended, delegated |
| C2 | Writing a comment, step 2 | `An index lookup doesn't sort its input.` and `Name the step, or use the obvious construct`, with the `setdefault()` example | **core**, with the example in a slot | as recommended, delegated |
| C3 | Writing a comment, step 3 | The keep-content example (`# without the lock, …` → `# two writers can interleave lines …`) | **core**, in a slot | as recommended, delegated |
| C4 | Prose review, step 1 | `Most pairs are in the second list. A subject that is misread in the parse is not in the list.` | **core.** Both skills print the same list | as recommended, delegated |
| C5 | Prose review | The worked example `# an expired item is removed on lookup` | **core**, in a slot | as recommended, delegated |
| C6 | Published prose | If the rest of a page is clearly written by an LLM, suggest cleaning the rest, and do not change the rest unasked | **core.** The rule came after narrative-java copied the section | as recommended, delegated |
| C7 | Published prose | `Only the wording checks and agentverbs.py run on a page.` and `Take the steps of Prose review for each sentence you wrote` | **core** for the second sentence. The first is about the Python `verify.py`, so **leaf** | as recommended, delegated |
| C8 | Comments, Never | `Put a module's guarantee in the project's architecture document` | **core** | as recommended, delegated |
| C9 | Comments, Never | The example for usage placement (`member order is the order plan.json lists …`) | **core**, in a slot | as recommended, delegated |
| C10 | Comments, Sentence form | The examples for nominal chains, worked examples, the `Alternatively,` marker, and intensifiers (`exactly two decimal places`) | **core**, in slots | as recommended, delegated |
| C11 | Comments, Sentence form | `Cut a clause about an internal check, structure or attribute unless the reader needs the clause to act.` | **core** | as recommended, delegated |
| C12 | Comments, wording checks | The note that `NAR015` flags changelog wording about data too, and how to reword such a sentence | **core.** The check is shared | as recommended, delegated |
| C13 | Comments, agent verbs | `Documents get no exception. Write named in the report.` and `It comes from agentverbs.py, the seventh check in verify.py` | **core** for the first. The second counts the checks of the Python `verify.py`, so **leaf** | as recommended, delegated |
| C14 | Comments, agent verbs | The paragraphs on `NAR020`, `NAR021` and `NAR022`. narrative-java has the same checks | **core** | as recommended, delegated |

## D. Codes

narrative-java numbers its Java checks from 100 up (`NAR1xx`, such as 104, 119, 120, 130 and 142),
and the codes of the shared prose checks are `NAR012` to `NAR022`. Code 119 is the Java form of
`NAR010`, and code 120 is the Java form of `NAR019`. With one decision log, one code per rule and a
leaf form for each language is possible. The numbering can also stay as it is.

| | Recommendation | Decision |
|---|---|---|
| D1. Keep the numbering, or one code per rule across languages | **Keep.** With a new code, every `noqa` with a code of today stops working, in the PRs already merged upstream | **Keep the codes of today.** A new rule of one language gets a code with the language as a suffix, such as `NARxxx-java` (revised on 2026-10-24) |
