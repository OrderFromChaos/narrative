---
name: core
description: The Narrative rules for comments, docstrings, javadoc, error messages, help text and published pages such as a README, in every language. Load with nar:python or nar:gtnh whenever code is written or reviewed, and alone to write or review a page.
---

# Narrative: comments and prose

These rules cover comments, docstrings, javadoc, error messages, help text and published pages, in
every language of Narrative. Load this skill together with the skill of the language, such as
`nar:python` or `nar:gtnh`. The checks run through the `verify.py` of the language skill.

In these rules, a docstring is the doc comment of the language, such as a javadoc in Java, and a
function is a function or a method. `nar:<language>` names the skill of the language of the file.
For Python the skill is `nar:python`, and for Java in a GTNH mod the skill is `nar:gtnh`.

## Comments

**Test: what information is in this comment and not in the code?** (R10-Q25)

These rules cover every text a user reads too: docstrings, error messages, help text and
localisation files. `verify.py` lists comments and docstrings only, so read messages, help text and
localisation files by hand. (R10-docstrings, R10-message-scope)

**Comments are not thinking traces.** While writing, you reasoned through edge cases, alternatives
and spec gaps. That reasoning is a thinking trace. It belongs in your report to the user, not in
the code. (R10-stance)

**Cut a comment whose content a smart reader would get from the code below the comment (including
variable names), no matter how the comment is phrased or what rule category the comment seems to
fit.** (R10-restatement-gate)

Before writing or rewording a comment, follow **Writing a comment** under **Procedures**.

**When shortening an existing comment, rewrite the sentence. Do not delete words from it until it
fits.** (R10-cleanup-rewrite)

**When you replace an existing comment, rewrite it from the code.** (R11-rewrite-from-code)

1. List the facts in the existing comment.
2. Check each fact against its source where you can: the code for a fact about the code, and the
   documentation of the language or the library, a spec or a vendor's documentation for a fact from
   outside the code. Some facts have no source you can check, such as a business decision. Keep
   those.
3. Drop a fact only when you find the fact false. When you find the fact false, and at the same
   source you find the correct answer to the same question, keep the correct answer in place of the
   false fact. For `the config is read once, at startup`, where the code reads the config on each
   request, keep `the config is read on each request`. (J1-F11)
4. Write a new comment from the facts you kept, by the steps of **Writing a comment**.

Reordering or trimming the existing comment's sentences is not a rewrite. The existing comment's
terms, framing and sentence order are not reference material.

**Every term passes one of two tests:**

1. **The domain's word:** the word a practitioner of the domain uses for the thing. In a billing
   tool, the word an accountant uses: an invoice, a refund, a billing period.
2. **An identifier, in backticks:** the name in the code that the reader can jump to, used as a
   pointer, such as `QuotaLedger` or `readManifest()`. Name an identifier in backticks even when its
   name is unclear. The reader can search for the name and read the code.

A term that passes neither test gets a plainer word or a definition at the term's first use.
(R11-rewrite-from-code, R11-pointer-wording)

**A descriptive word in a term is a claim.** (R11-modifier-claim)

Some words in a term are descriptive: an adjective such as `parsed` in `the parsed config`, or a
noun for a kind of thing, such as `helpers` in `the read helpers`. Each descriptive word is a claim.
`parsed` is a claim that the config is parsed, and `helpers` with `read` is a claim that the helpers
only read. Check each descriptive word against its source by step 2 of the rewrite. Keep the word
only when the word is true of everything the term names. `parsed` is false for the defaults:
`loadConfig()` returns them without parsing. When a word is false, use the domain's word or an
identifier instead. Don't add words to cover the other cases: `parsed or default config` is neither
the domain's word nor an identifier.

When the reader needs a fact about a library, and you can't read the library's source or find the
fact in the library's documentation, write what your code does at the call. Not `the SDK retries on
timeout`, but `fetchInvoice() calls the SDK once and catches a timeout`. Don't add `with no
retry` or a similar phrase at the end. `with no retry` makes the same claim about the SDK.

**Don't describe what a function's callers do.** (R11-callers)

A developer who changes a caller has no reason to read this comment, so a sentence about what the
callers do becomes false when they change. When the reader needs the reason for a requirement, state
a fact about what the function returns or changes. Not `Return a frozen mapping. The pricing
functions call this on each request`, but `Return a frozen mapping: the rates don't change while the
process runs`. That docstring is on a method that subclasses override, and the developer of each
override reads the docstring to learn what to return. Don't write a docstring for a function that
only returns a constant. A requirement on the callers is part of the function's contract, such as
`Call only from the main thread`. A fact about a function that this function calls is allowed. That
call should be in the code below the comment.

**Don't describe what a function's callers do** is about the code of the callers. A fact about a
value from outside the code, such as a value from a library, a framework, another program or data
that an earlier version saved, is a **Source** fact, even when a caller passes the value to the
function. Write such a fact only above the code for the value. The examples are under **Source
facts** in **Comments in <language>**, in the skill `nar:<language>`.
(J1-F12)

**In a PR to another project, leave the comments that exist on the project's base branch as they
are**, even the ones the diff moves. `verify.py --since` reports only the lines the diff adds or
changes. (J1-pr-base-comments)

**Comment kinds:** (R10-topic-lists, R10-fp-fn, R10-kinds)

- **Source**: a fact or requirement from outside the code. Test: it would still be true if the code
  were deleted, a smart reader wouldn't already know the fact, and the code below the comment
  depends on the fact. (R10-Q10, R10-Q14, R10-Q23, R10-Q34, R10-Q43, R10-Q48, R10-Q51,
  R10-business-case, R10-audience, J1-F12)
  - `vendor closes idle sockets at 60 s`
  - `finance signs off each team's bill separately, so one file per team`
  - `databases written before 2025/04/03 lack the account_id column`
  - `calibration spec CAL-7, section 3`, on a threshold constant
  - `handles millions of rows`, at the top of the function
- **Fence**: code that looks unusual, where the obvious simplification silently breaks the code.
  Test: name the simplification a smart, experienced developer would make, and the defect the
  simplification causes: a wrong result, a crash, a security hole or a performance collapse. A
  cosmetic difference doesn't count, and neither does adding a feature. Name the step the code takes
  because of the fact. (R10-Q20, R10-Q42, R10-Q44, R10-Q45, R10-Q50, R10-Q53, R10-Q55,
  R10-fence-consequence)
  - `the API returns 200 with an error body for a bad key. Check the body too`, not `the API returns
    200 with an error body for a bad key`
  - `constant-time comparison to avoid timing attacks`
  - `we want to make sure deleting an item doesn't shift the unvisited indices. Therefore, walk
    backwards`
  - `migrate before load. load reads the account_id column`
  - not `file can change between calls, so not cached`. A cache is a feature, not a simplification
- **Decoding aid**: a line a smart reader would need docs or a worked example to read. Test: you'd
  look it up. State the intent, not the mechanism. A decoding aid is about a construct of the
  code, so the examples are under **Decoding aids** in **Comments in <language>**, in the skill
  `nar:<language>`. (R10-Q42, R10-Q46)
  - a regex gets a string the regex matches, and one the regex rejects where the boundary is
    unclear. Put each literal in backticks, one per line, so the match boundary is visible and a
    developer can paste the literal into regex101. A description such as `any single character`
    stays plain. (R10-regex-sample, R10-regex-literals)
- **Marker**: no test needed. (R10-candor, R10-Q03, R10-Q05, R10-Q36, R10-Q38, R6-12, R8-block-comments)
  - `FIXME:` incorrect behaviour, or behaviour that breaks soon after deploy. The finding of
    `verify.py` for a `FIXME:` is under **FIXME** in **Comments in <language>**, in the skill
    `nar:<language>`.
  - `TODO:` tech debt, future improvement
  - a stated assumption: `vendor documents no encoding, UTF-8 assumed`
  - a label on a block of at least 4 lines, ideally 6 or more: `parse data` (R10-block-label-size)
  - a rule a developer must enforce, with capitals scaled to the cost of breaking the rule:
    `read-only: NEVER write to the audited readings`

**Never, even when a kind's test passes:**
- what the next line or a single call does (R10-Q01, R10-Q06, R10-Q39, R10-Q47, R10-Q54)
- standard library or language behaviour the reader knows: `<=`, case sensitivity, the null value (R10-Q19, R10-Q21, R10-Q26, R10-Q49)
- why the file follows this style guide: `so this is a class and not a module` (R9-02, R10-Q01)
- decision ids such as `(Q08)` (R7-D04-comments, `NAR012`)
- changelog: an earlier state of the code, or a fixed bug with nothing left of the bug (R10-Q04,
  R10-Q08, R10-Q52, `NAR015`)
- alternatives never in the code (`rather than`, `instead of`), except in architecture discussion (R10-Q07, R10-rather-than)
- risks far outside the task's scale, and decisions too inconsequential for a later reader to reconsider (R10-Q13, R10-rating)
- future needs nobody has documented or planned (R10-Q15)
- reassurance that a weakness is fine, such as `deliberately` or `on purpose` (R10-candor, R10-Q20, `NAR014`)
- guarantees about other modules or functions. Put a module's guarantee in the project's
  architecture document. Where the code depends on another function's guarantee and the check is
  cheap, check the guarantee in the code: test for an empty cache in the loop condition, not
  `store() rejects an oversized item, so the cache is never empty` (R10-Q24, R10-Q11, R10-other-modules,
  R10-check-invariant)
- how one function uses a type, written on the type: `member order is the order plan.json lists a
  snapshot's rules` belongs with the function that writes plan.json, or nowhere if the order is
  already plain in that function (R10-usage-placement)
- illustrations of a decision just discussed in the session (R10-Q21)
- a function's return contract. State it in the docstring, and only if the return type doesn't make
  the contract obvious. (R10-return-contract, `NAR019`)

**Depth:** in proportion to the idea's difficulty for the reader. `signed error` on a rolling
mean, more on a novel method. When the reader needs the consequence or the action as well as the
fact, write a second sentence, as a block of full sentences. The example is under **Depth** in
**Comments in <language>**, in the skill `nar:<language>`.
A one-line comment stays one clause, or two short sentences. (R10-Q16, R10-seed-2, R10-depth-sentences,
R10-depth-example, R10-period-join)

**Sentence form:**
- a one-line comment has a lowercase start and no final period. Several lines, and every docstring, are sentences. (R10-Q26, R10-Q35, R10-docstrings)
- two sentences over a connective such as `which`, `since`, `as` or `, where`. With a connective,
  the reader may attach the second clause to the wrong noun. `migrate before load, which reads the
  account_id column` → `migrate before load. load reads the account_id column`. A comparison with
  `as` to other code states no fact: `a float, as in the parser` → `the parser computes in float
  too`. `NAR021` flags `as in`, a sentence that opens with `As` and has no verb, `as the X verbs
  it`, and `, where` (R10-period-join, R11-connective-as-where)
- terse. Drop articles where nothing is lost, never the subject or the verb (R10-seed-10, R10-terse-narrow)
- every clause has a subject and a verb. A label for the thing is fine: `least recently used
  first`, `Exact, case-sensitive comparison.` A predicate with the subject cut is not:
  `Bound to one machine` → `The modifier is bound to one machine`, and
  `named, so a recreated container gets it back` → `named volumes persist when a container is
  recreated (e.g. docker compose down && docker compose up)`. (R10-subject-verb, `NAR020`)
- every noun phrase refers to one real thing, at the moment the sentence is about. Name the object in
  the program each noun phrase refers to, and rewrite when:
  - the thing does not exist yet, or does not have its property yet: `openLog() creates a missing
    log file` → `openLog() creates the log file if the file doesn't exist`
  - the property belongs to another object: `in the snapshot's timezone` → `in the policy's
    timezone`. A snapshot name is in UTC, and the timezone comes from the policy
  - the referent is gone or ambiguous: `the parser leaves TOML local times without one` → `without a
    UTC offset`. A pronoun at the start of a sentence can refer to the subject of either sentence
    before the pronoun, so repeat the noun
  - a stand-in such as `the one`, `it` or `that` takes the place of a noun that fits: `follow the
    one under which the reader diffs less` → `follow the rule under which the reader diffs less`.
    Repeat the noun (R10-stand-in)
  - `it` or `its` after two or more singular nouns in one sentence. A reader can take the pronoun
    for either noun, even when only one of the nouns makes sense. Repeat the noun the pronoun stands
    for, or split the sentence: `QuotaLedger extends Store, and it caches every read` → `QuotaLedger
    extends Store, and Store caches every read`. `NAR022` flags this form (R11-pronoun-grammar)
  (R10-referent)
- the concrete thing, not `what the X does to the Y`: `Say what the fact requires of the code` →
  `Name the step the code takes because of the fact` (R10-nominal-chain)
- a claim is true in every case that reaches the claim. Otherwise, name the case in the sentence.
  List the paths that reach the sentence:
  - `an expired item is removed on lookup` → `an expired item is removed on lookup, or before any
    eviction`
  - `Returns the cached copy.` → `Returns the cached copy when one exists, otherwise the downloaded
    one.`
  - count the unit the code counts: `every file is counted` → `the lines of every file are
    counted`
  - in an error message, advise only steps the program has not taken: `no policy file found.
    Check the input directory` → `no policy.json in fixture/. Pass --policy to use another file`
  (R10-case-coverage)
- when a comment moves from one approach to another, mark the switch with `Alternatively,`:
  `opening the file for writing would empty the file before the write. Alternatively, write a
  temporary file and rename the temporary file over the original`. Without the marker, the second
  sentence reads as more about the first approach (R10-alternative-marker)
- possessives and noun compounds over relative clauses: `the archive's collections`, `in read order` (R10-seed-1, R10-seed-9, R10-Q32)
- trade terms over paraphrase: `has no side effects`. Modifiers before the noun: `JSONL logs`. (R10-seed-3, R10-seed-4)
- the conclusion, not the derivation. State what the code means, not how the code gets there.
  `empty when malformed`, not `empty when a malformed line names no customer as a string`. Cut a
  clause about an internal check, structure or attribute unless the reader needs the clause to act.
  (R10-conclusion)
- no intensifiers. Drop a word that only stresses, such as `exactly`, `always`, `precisely` or
  `simply`. Keep it when the sentence means something else without the word: `exactly two decimal
  places`. (R10-intensifiers)
- the full term when a short form is ambiguous: `timezone`, not `zone` (R10-clipped-terms)
- contractions and the imperative (R10-Q28, R10-Q29, R10-we)
- callables as `name()`, and no article before an identifier (R10-Q30, R10-Q35)
- only names the reader can resolve from the comment's position (R10-Q22, R10-Q21)
- with code or an abstract noun as the subject, only verbs for what code literally does: `returns`,
  `raises`, `reads`, `writes`, `calls`, `skips`. Never agency or containment: `finds`, `knows`,
  `holds`, `carries`, `keeps its`, `costs`. Write `a module has one function`, not
  `a module holding one function`. These words are examples. The test is whether the subject can
  perform the verb. (R10-Q31, R10-Q39, R10-seed-1, R10-seed-6, R10-seed-15, R10-skill-gaps)
- no `is what`, no `its own` (R10-Q40, R10-Q41, `NAR018`)
- the general case: `records are separated by blank lines`, not `two records` (R10-Q40)
- a worked example matches what the code does for every case in the example: not `with a->b and
  b->c, a and c compare unequal` when a and b also compare unequal (R10-worked-example)
- no semicolon and no dash. Write two sentences (R10-no-semicolon, `NAR013`)
- a comment line over the line limit is wrapped onto the next line. Never change the wording to fit (R11-wrap-not-reword)
- a Fence is the fact the code depends on, then the step the code takes because of that fact:
  `the vendor rounds tax per line, not per invoice. Round each line before the sum`. Write `X would`
  only when X is an alternative the code does not use, such as a read of the whole file into
  memory, when the code below the comment streams the file line by line. When the code under the
  comment does X, state the problem X is there for: `without the retry, the first request after
  idle time fails` → `the endpoint drops the first request after idle time. Retry once`. The
  `X would` form in full is under **Fence** in **Comments in <language>**, in the skill
  `nar:<language>`. (R10-fence-form, R10-fence-fact, R10-fence-alternative)
- a comment on one branch of a `match`, `switch` or `if` chain is about what only that branch does. A reason
  that covers every branch goes above them once. Cut it when a name such as `local` already makes
  the reason obvious (R10-branch-comment)
- directly above the statement it concerns, not above its enclosing block. Comments inside a try
  block go above the call the comment concerns, not above the `try`. A comment on an argument goes
  above the call that passes the argument, not below the try block. End-of-line for a short note. (R10-Q34, R10-locality, R10-fence-form,
  R10-argument-placement)

`NAR012` to `NAR016` and `NAR018` flag six wording faults in comments and docstrings, and a clean
run is no evidence about the rest of these lists. Check every comment and docstring you write or
touch against them. A dash after a list-item term is allowed. `NAR015` also flags `no longer` about
data. Such a sentence usually has data as the subject of an agent verb, so reword the sentence.
(R10-lint, R10-skill-gaps, R10-list-dash, R10-nar015-scope,
R10-nar016, R10-nar018)

`NAR017` is an agent verb on a subject that cannot act, meaning a noun that is not a person, with a
verb for something only a person does: thought or speech (`a period ranks`, `the report names it`,
`a policy can judge`), or, with an object, a deliberate act (`the default config sends the job to a
queue`, `the fallback places the file`). Documents get no exception. Write `named in the report`. A
table, figure or example on the page can show what is in the table, figure or example: `the table
below shows the totals`.
It comes from `agentverbs.py`, which `verify.py` runs. The check parses each sentence, and
some noun compounds and participles are flagged by mistake. (R10-agentverb-check,
R10-agentverb-agency)

`NAR020`, from the same check, is a clause with no subject before `, so`: `Named, so a recreated
container gets it back`, or a subordinate clause before `, so`: `Whether some terms differ by
mode, so…`. Only that form is flagged. Check every other clause against the subject and
verb rule in **Sentence form** by hand. (R10-subject-verb, R10-nar020, R11-nar020-subordinate)

`NAR021`, from the same check, is a clause that `as` or `, where` joins to a sentence. See the
connective rule in **Sentence form**. (R11-connective-as-where)

`NAR022`, from the same check, is `it` or `its` after two or more singular nouns in one sentence.
See the referent rule in **Sentence form**. (R11-pronoun-grammar)

**A finding is information.** Read the sentence again, then rewrite or delete the sentence, except
in three cases:

1. **A misparse.** The flagged words are not the subject and verb, or not one clause, in what you
   wrote. Leave the sentence.
2. **A quoted example.** The flagged text is an example of the fault, such as a banned word in the
   rule that bans the word. Leave the sentence.
3. **The code's name for the thing.** The flagged words come from an identifier, such as `the worker
   owns the lock` from `ownsLock()`. Leave the sentence, and list the sentence in your report.

**Never add a `noqa` yourself.** The exceptions are under **noqa** in **Comments in <language>**, in
the skill `nar:<language>`. (R11-findings)

### Writing a comment

Take these steps in order before writing or rewording a comment. The kinds, the **Never** list,
**Depth** and **Sentence form** are in **Comments**.

1. **Rename first.** If the information fits in a name or a type, rename and write no comment:
   `ByteCount` as the type of `overQuota`, `totalCents`, `rollingMeanSignedError`. (R10-Q25, R10-Q27, R10-Q16)
2. **Guarantee it in code.** Establish a cheap precondition, such as sorted input, upstream in the
   call flow, not in the function that depends on the precondition, and write no comment. An index
   lookup doesn't sort its input. If a code change removes a trap, make the change and write no
   comment. If explaining how the code works takes more than one plain clause, rewrite the code
   instead. Name the step, or use the obvious construct. A `dict` filled with `setdefault()` and
   sliced by insertion order becomes an explicit loop that counts periods. (R10-Q19, R10-footgun,
   R10-hard-comment)
3. **Match a kind.** Write a comment only if it is one of the four **Comment kinds**, passes that
   kind's test, and is not under **Never**. Deleting is a valid outcome of a rewrite when the content
   fails the test. When only the wording breaks a rule, rewrite the wording and keep the content:
   `without the lock, two writers interleave their lines` → `two writers can interleave lines in
   the log. The lock serializes them`. (R10-keep-content)
4. **Set the depth and sentence form** by **Depth** and **Sentence form**.

### Prose review

**Fix every finding of `verify.py` first. Then read the three lists at the end of the output, plus
every error message and `--help` string.** You rewrite sentences when you fix findings, so read the
lists from the run after the fixes. The first list has every sentence of every comment and
docstring in the code, and every sentence of each named page. The second has each subject that
cannot act, paired with the subject's verb, for every verb that is neither a `NAR017` finding nor
an operation of code. A verb such as `reads` or `runs` is an operation of code only with a direct
object and code as the verb's subject: `PlanLoader reads the plan file`, not `the spec reads`. The
third has every sentence with `it`, `its` or a standalone `that`, each after the sentence before.
Take these steps for each sentence. (R10-prose-inventory, R10-closing-review, R11-pronoun-list,
R11-literal-review)

1. Name the subject and the verb. Can that subject perform that verb? Most pairs are in the second
   list. A subject that is misread in the parse is not in the list.
2. For each noun phrase, name the variable, function, file or value that the phrase refers to. If
   none fits, or two do, rewrite. Check each descriptive word of the phrase by **A descriptive word
   in a term is a claim**. For each pronoun in the third list, name the noun the pronoun stands for.
   If that noun is in another sentence, repeat the noun. (R10-stand-in)
3. List the code paths that reach the line: each branch, each caller, each failure. Check the claim
   on every path.
4. Test the sentence against **Sentence form**, and the comment against the restatement gate.

For `an expired item is removed on lookup`:
- `an expired item` is an `Item` whose `deadline` has passed. `lookup` is `getItem()`.
- Two paths remove an expired item: `getItem()`, and `dropExpired()` before an eviction. The
  comment covers only `getItem()`.
- The rewrite: `an expired item is removed on lookup, or before any eviction`.

An entry on a review list is a question, not a finding. When the subject can do the verb in the
domain's sense, such as a row that gets the default currency, leave the sentence unchanged.
(R11-review-question)

Fix what fails and run `verify.py` again.

### Published prose

A README, a doc page or an HTML report that you write follows the prose rules of this skill, as a
comment does. When you rewrite part of a page, the rules cover the section you changed. If the
rest of the page is clearly written by an LLM, suggest cleaning the rest, and do not change the
rest unasked. A page that a person wrote and you did not change is left as it is, unless the user
asks for it to be checked. Name each page to the `verify.py` of the language skill. The command is
under **Pages** in **Comments in <language>**, in the skill `nar:<language>`.

Only the wording checks and `agentverbs.py` run on a page. `verify.py` prints the three lists of
**Prose review** for each named page too. Take the steps of **Prose review** for each sentence you
wrote, and handle each finding by the rule **A finding is information**. (R10-published-prose,
R11-page-inventory)
