---
name: core
description: The Narrative rules for comments, docstrings, javadoc, error messages, help text and published pages such as a README, in every language. Load with nar:python or nar:gtnh whenever code is written or reviewed, and alone to write or review a page.
---

# Narrative comments and prose

These rules cover comments, docstrings, javadoc, error messages, help text and published pages, in
every language of Narrative. Load this skill together with the skill of the language, such as
`nar:python` or `nar:gtnh`. The checks run through the `verify.py` of the language skill.

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

## Comments

**Before you keep a comment, ask what information is in the comment and not in the code.** (R10-Q25)

These rules cover each text a user reads too:

- docstrings
- error messages
- help text
- localisation files

 `verify.py` lists comments and docstrings only, so read messages, help text and
localisation files by hand. (R10-docstrings, R10-message-scope)

**Comments are not thinking traces.** While writing, you reasoned through edge cases, alternatives,
and spec gaps. That reasoning is a thinking trace. Put the reasoning in your report to the user, and leave the
reasoning out of the code. (R10-stance)

**Cut a comment whose content a smart reader would get from the code below the comment (including
variable names), no matter how the comment is phrased or what rule category the comment seems to
fit.** (R10-restatement-gate)

Before writing or rewording a comment, follow **Writing a comment** under **Procedures**.

**When shortening an existing comment, rewrite the sentence. Do not delete words from it until it
fits.** (R10-cleanup-rewrite)

**When you replace an existing comment, rewrite it from the code.** (R11-rewrite-from-code)

1. List the facts in the existing comment.
2. Check each fact against its source where you can: the code for a fact about the code, and the
   documentation of the language or the library, a spec, or a vendor's documentation for a fact from
   outside the code. You can't check the source of some facts, such as a business decision. Keep
   those facts.
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

An adjective is a descriptive word, such as `parsed` in `the parsed config`. A noun for a kind of
thing is a descriptive word too, such as `helpers` in `the read helpers`. Each descriptive word is a claim.
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

A developer who changes a caller doesn't have a reason to read this comment, so a sentence about what the
callers do becomes false when they change. When the reader needs the reason for a requirement, state
a fact about what the function returns or changes. Not `Return a frozen mapping. The pricing
functions call this on each request`, but `Return a frozen mapping: the rates don't change while the
process runs`. That docstring is on a method that subclasses override, and the developer of each
override reads the docstring to learn what to return. Don't write a docstring for a function of
one line. `NAR023` flags a docstring or a javadoc on a function of one line (R12-one-line-function). A requirement on the callers is part of the function's contract, such as
`Call only from the main thread`. A fact about a function that this function calls is allowed. That
call should be in the code below the comment.

**Don't describe what a function's callers do** is about the code of the callers. A fact about a
value from outside the code, such as a value from a library, a framework, another program, or data
that an earlier version saved, is a **Source** fact, even when a caller passes the value to the
function. Write such a fact only above the code for the value. The examples are under **Source
facts** in **Comments in <language>**, in the skill `nar:<language>`.
(J1-F12)

**In a PR to another project, leave the comments that exist on the project's base branch as they
are**, even the ones the diff moves. `verify.py --since` reports only the lines the diff adds or
changes. (J1-pr-base-comments)

**Comment kinds:** (R10-topic-lists, R10-fp-fn, R10-kinds)

- **Source** is a fact or a requirement from outside the code. A Source comment passes when the
  three are true:
  - the fact would still be true if the code were deleted
  - a smart reader wouldn't already know the fact
  - the code below the comment depends on the fact

  (R10-Q10, R10-Q14, R10-Q23, R10-Q34, R10-Q43, R10-Q48, R10-Q51,
  R10-business-case, R10-audience, J1-F12)
  - `vendor closes idle sockets at 60 s`
  - `finance signs off each team's bill separately, so one file per team`
  - `databases written before 2025/04/03 lack the account_id column`
  - `calibration spec CAL-7, section 3`, on a threshold constant
  - `handles millions of rows`, at the top of the function
- **Fence** is code that looks unusual. The obvious simplification of the code silently breaks the
  code. To test a Fence, name the simplification that a smart, experienced developer would make, and
  the defect that the simplification causes, such as a wrong result, a crash, a security hole, or a
  performance collapse. A
  cosmetic difference doesn't count, and neither does adding a feature. Name the step the code takes
  because of the fact. (R10-Q20, R10-Q42, R10-Q44, R10-Q45, R10-Q50, R10-Q53, R10-Q55,
  R10-fence-consequence)
  - `the API returns 200 with an error body for a bad key` → `the API returns 200 with an error
    body for a bad key. Check the body too`
  - `constant-time comparison to avoid timing attacks`
  - `we want to make sure deleting an item doesn't shift the unvisited indices. Therefore, walk
    backwards`
  - `migrate before load. load reads the account_id column`
  - `file can change between calls, so not cached` isn't a Fence. A cache is a feature, and the
    test of a Fence is about a simplification
- **Decoding aid** is a line that a smart reader would need docs or a worked example to read. A line
  passes the test when you would read the docs for the line. State the intent, and leave out the mechanism. A decoding aid is about a construct of the
  code, so the examples are under **Decoding aids** in **Comments in <language>**, in the skill
  `nar:<language>`. (R10-Q42, R10-Q46)
  - a regex gets a string the regex matches, and one the regex rejects where the boundary is
    unclear. Put each literal in backticks, one per line, so the match boundary is visible and a
    developer can paste the literal into regex101. A description such as `any single character`
    stays plain. (R10-regex-sample, R10-regex-literals)
- A **Marker** is exempt from the tests. (R10-candor, R10-Q03, R10-Q05, R10-Q36, R10-Q38, R6-12, R8-block-comments)
  - `FIXME:` incorrect behaviour, or behaviour that breaks soon after deploy. The finding of
    `verify.py` for a `FIXME:` is under **FIXME** in **Comments in <language>**, in the skill
    `nar:<language>`.
  - `TODO:` tech debt, future improvement
  - a stated assumption: `vendor doesn't document an encoding, UTF-8 assumed`
  - a label on a block of at least 4 lines, ideally 6 or more: `parse data` (R10-block-label-size)
  - a rule a developer must enforce, with capitals scaled to the cost of breaking the rule:
    `NEVER write to the audited readings`

**Never, even when a kind's test passes:**
- what the next line or a single call does (R10-Q01, R10-Q06, R10-Q39, R10-Q47, R10-Q54)
- standard library or language behaviour the reader knows: `<=`, case sensitivity, the null value (R10-Q19, R10-Q21, R10-Q26, R10-Q49)
- why the file follows this style guide: `so this is a class and not a module` (R9-02, R10-Q01)
- decision ids such as `(Q08)` (R7-D04-comments, `NAR012`)
- changelog: an earlier state of the code, the story of a bug, or a report from a user. Cut the
  sentence:
  - `a cache of 64 entries once evicted the hot keys under load` → no comment
  A story of a bug in the present tense is still a changelog. Search for the past tense and for
  `once` in a sentence about the code or the users. When the code depends on a fact behind the
  bug, write the fact as a Fence. The form of a Fence is in **Sentence form**. Keep a Source fact
  about old data: `databases written before 2025/04/03 lack the account_id column`. (R10-Q04,
  R10-Q08, R10-Q52, R12-no-changelog, `NAR015`)
- the value of a constant. The value is in the declaration of the constant, and a comment with the
  value is wrong once the constant changes. Write what the value means, or nothing:
  - `# retry every 30 s` above `RETRY_DELAY_SECONDS = 30` → no comment
  - `# the vendor accepts 1 to 100` beside `MIN_PAGE_SIZE` and `MAX_PAGE_SIZE` → `# page sizes the
    vendor API accepts`
  The item is about config comments too, because a config comment is code text. Help text for
  players in the lang file is outside the item. A tooltip may have `Range 8-64 blocks`. `NAR027` flags a
  number in a comment that is the value of a constant the comment names, or of a constant just below
  (R12-no-constant-values)
- alternatives never in the code (`rather than`, `instead of`), except in architecture discussion (R10-Q07, R10-rather-than)
- risks far outside the task's scale, and decisions too inconsequential for a later reader to reconsider (R10-Q13, R10-rating)
- a future need that isn't in a document or a plan (R10-Q15)
- reassurance that a weakness is fine, such as `deliberately` or `on purpose` (R10-candor, R10-Q20, `NAR014`)
- guarantees about other modules or functions. Put a module's guarantee in the project's
  architecture document. Where the code depends on another function's guarantee and the check is
  cheap, check the guarantee in the code: `store() rejects an oversized item, so the cache is never empty` →
  test for an empty cache in the loop condition (R10-Q24, R10-Q11, R10-other-modules,
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
- a one-line comment has a lowercase start, and doesn't end with a period. Several lines, and every docstring, are sentences. (R10-Q26, R10-Q35, R10-docstrings)
- two sentences over a connective such as `which`, `since`, `as`, or `, where`. A reader can attach
  the clause after a connective to the wrong noun. `migrate before load, which reads the
  account_id column` → `migrate before load. load reads the account_id column`. A comparison with
  `as` to other code states no fact: `a float, as in the parser` → `the parser computes in float
  too`. `NAR021` flags `as in`, a sentence that opens with `As` and doesn't have a verb, `as the X verbs
  it`, and `, where` (R10-period-join, R11-connective-as-where)
- no free modifier. A free modifier is a phrase without a verb that follows a comma. Each of these
  is a free modifier:
  - `, in one list for each tenant`
  - `, measured,`
  - `, with the row number in the error`

  The reader can attach a free modifier to the wrong noun. Write the phrase as a clause with a
  subject and a verb, or as a separate sentence, or cut the phrase:
  - `The retry jobs, in one list for each tenant of the scheduler` → `` `RetryQueue` has one list
    of jobs per tenant ``
  - `export() stops at the first bad row, with the row number in the error` → `export() stops at
    the first bad row. The row number is in the error message`
  The fourth review list of `verify.py` has every sentence with a free modifier (R12-no-free-modifier)
- terse. Drop an article when the meaning stays the same. Keep the subject and the verb (R10-seed-10,
  R10-terse-narrow)
- every clause has a subject and a verb. A label for the thing is fine: `least recently used
  first`, `Exact, case-sensitive comparison.` A predicate with the subject cut is not:
  `Bound to one machine` → `` `LicenseKey` is bound to one machine ``, and
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
  - a stand-in such as `the one`, `it`, or `that` takes the place of a noun that fits: `follow the
    one under which the reader diffs less` → `follow the rule under which the reader diffs less`.
    Repeat the noun (R10-stand-in)
  - `it` or `its` after two or more singular nouns in one sentence. A reader can take the pronoun
    for either noun, even when only one of the nouns makes sense. Repeat the noun the pronoun stands
    for, or split the sentence: `QuotaLedger extends Store, and it caches every read` → `QuotaLedger extends Store, and Store caches reads`. `NAR022` flags this form (R11-pronoun-grammar)
  (R10-referent)
- the concrete thing. A phrase such as `what the X does to the Y` is abstract: `Say what the fact requires of the code` →
  `Name the step the code takes because of the fact` (R10-nominal-chain)
- a claim is true in every case that reaches the claim. Otherwise, name the case in the sentence.
  List the paths that reach the sentence:
  - `an expired item is removed on lookup` → `an expired item is removed on lookup, or before any
    eviction`
  - `Returns the cached copy.` → `Returns the cached copy when one exists, otherwise the downloaded
    one.`
  - count the unit the code counts: `files are counted` → `lines are counted`
  - in an error message, advise only steps the program has not taken: `no policy file found.
    Check the input directory` → `no policy.json in fixture/. Pass --policy to use another file`
  (R10-case-coverage)
- when a comment moves from one approach to another, mark the switch with `Alternatively,`:
  `opening the file for writing would empty the file before the write. Alternatively, write a
  temporary file and rename the temporary file over the original`. When the marker is missing,
  the second sentence reads as more about the first approach (R10-alternative-marker)
- possessives and noun compounds over relative clauses: `the archive's collections`, `in read order` (R10-seed-1, R10-seed-9, R10-Q32)
- trade terms over paraphrase: `doesn't have side effects`. Modifiers before the noun: `JSONL logs`. (R10-seed-3, R10-seed-4)
- the conclusion. State what the code means, and leave out how the code gets there: `empty when a
  malformed line names no customer as a string` → `empty when malformed`. Cut a
  clause about an internal check, structure, or attribute unless the reader needs the clause to act.
  (R10-conclusion)
- no intensifiers. Drop a word that adds stress and doesn't add a fact, such as `exactly`,
  `always`, `every`, `only`, `precisely`, or `simply`. Keep it when the sentence means something else without the word: `exactly two decimal
  places`. `every` is a guarantee that the claim is true in all cases with no exception, often in
  the code of other functions. `every` is also a word of marketing copy and of reassurance. Write
  `every` only when you are sure of the claim on all paths. When you are even a little unsure, cut
  `every`: `rebuild the index on every save` → `rebuild the index on save` (R10-intensifiers,
  R12-every, R12-only)
- the full term when a short form is ambiguous: `zone` → `timezone` (R10-clipped-terms)
- contractions and the imperative (R10-Q28, R10-Q29, R10-we)
- a negation is on the verb, such as `doesn't`, `isn't`, or `can't`. Don't put `no`, `nothing`, or `none` on
  the subject or the object of a verb, or after `is`:
  - `exportMonth() writes nothing for an empty month` → `exportMonth() doesn't write a file for an
    empty month`
  - `a draft invoice is no proof of payment` → `a draft invoice isn't proof of payment`
  - `no invoice is sent twice` → `an invoice isn't sent twice`
  - `the fields that no parser reads` → `the fields that parseInvoice() doesn't read`
  `NAR025` flags this form (R12-negate-verb)
- a condition as a clause after `when` or `if`. The clause has a subject and a verb. Don't write
  the condition as a phrase after `at`, `with`, `beside`, `against`, `on`, or `for` at the start of
  a sentence:
  - `with a full disk, export() deletes the partial file` → `when the disk is full, export()
    deletes the partial file`
  - `with an expired token, the retry fails` → `when the token has expired, the retry fails`
  Keep an opener with a platform or a version, such as `On Windows,` or `In Python 3.11,`. `NAR026` flags an opener
  after any of these words but `for`, because an opener with `for` is usually a purpose (R12-no-prep-opener)
- no contrast with `X, not Y` or `not merely`. State X. When the reader needs a fact about Y, write
  the fact in a separate sentence:
  - `amounts are in cents, not dollars` → `amounts are in cents`
  - `Inclusive, not exclusive: the end date is billed` → `end date is billed`
  - `retry on a timeout, not on a refusal` → `retry on a timeout. Raise ConnectionError when the
    server refuses the connection`
  `NAR024` flags `, not` and `not merely` (R12-not-contrast)
- don't make the first sentence of a docstring a noun phrase for the identifier. Write a sentence
  with a verb about what the reader can't get from the name, or cut the docstring:
  - `The size of this stratum (number of lines)` on the field `size` → no javadoc, and the name
    `lineCount`
  - `A GL display list of the mob spawn overlay.` on the class `MobOverlayDisplayList` →
    `` `MobOverlayDisplayList` compiles the overlay quads of each chunk column into one GL display
    list. ``
  A label is fine on a constant, an enum constant or a field when the label has a fact that isn't
  in the name, such as the look of a style:
  - `` {@link #addVertices} adds a small square in the middle of the block `` on `SQUARE` →
    `A small square in the middle of an untinted block.`
  When the fact fits in the name, rename the field. (R12-no-name-phrase, R12-label-constant)
- callables as `name()`, and no article before an identifier (R10-Q30, R10-Q35)
- only names the reader can resolve from the comment's position (R10-Q22, R10-Q21)
- only verbs for what code literally does, when the subject is code or an abstract noun. These verbs
  are fine:
  - `returns`
  - `raises`
  - `reads`
  - `writes`
  - `calls`
  - `skips`

  A verb of agency or containment isn't fine:
  - `finds`
  - `knows`
  - `holds`
  - `carries`
  - `keeps its`
  - `costs`

  `a module holding one function` →
  `a module has one function`. These words are examples. The test is whether the subject can
  perform the verb. (R10-Q31, R10-Q39, R10-seed-1, R10-seed-6, R10-seed-15, R10-skill-gaps)
- no `is what`, no `its own` (R10-Q40, R10-Q41, `NAR018`)
- Write the behaviour for any input, and leave out a scenario and a sample count: `records two
  and three are separated by a blank line` → `records are separated by blank lines`, and `A file
  with 10,000 bad rows emits one record at the default level` → `emit one status record per file`
  (R10-Q40, R12-no-scenario)
- a worked example matches what the code does for every case in the example: not `with a->b and
  b->c, a and c compare unequal` when a and b also compare unequal (R10-worked-example)
- no semicolon and no dash. Write two sentences (R10-no-semicolon, `NAR013`)
- Write two sentences in place of a clause joined by a colon, or of an `X: Y` opening. When the
  half after the colon is a definition of the word before the colon, cut the definition:
  `# idempotent: a second run changes nothing` → `# idempotent`. A colon is fine before a code
  example or a bulleted list (R12-colon)
- a list of more than two items after a colon in bullets. Put a sentence about the list above
  the bullets. A list of two items may be inline:
  `Retried errors: a timeout, a refused connection, a reset connection, and an HTTP 503.` →
  ```
  Retry on these errors:
  - a timeout
  - a refused connection
  - a reset connection
  - an HTTP 503
  ```
  (R12-bulleted-list)
- use the Oxford comma (R12-oxford-comma)
- a comment line over the line limit is wrapped onto the next line. Never change the wording to fit (R11-wrap-not-reword)
- **re-wrap with `verify.py`.** Before the checks, `verify.py` fills each paragraph of a
  comment or doc comment up to column 120, in every language, and under `--since` only a paragraph
  with a changed line. The line breaks of a blank comment line, a list item, a block tag, a sample,
  and the strings under `matches:` stay as written. When `--no-fix` is given, `NAR125` flags
  each paragraph that the re-wrap would change. The re-wrap moves line breaks only, never words (R11-rewrap-fill)
- a Fence is the fact the code depends on, then the step the code takes because of that fact:
  `the vendor rounds tax per line. Round each line before the sum`. Write `X would`
  only when X is an alternative the code does not use, such as a read of the whole file into
  memory, when the code below the comment streams the file line by line. When the code under the
  comment does X, state the problem X is there for: `without the retry, the first request after
  idle time fails` → `the endpoint drops the first request after idle time. Retry once`. The
  `X would` form in full is under **Fence** in **Comments in <language>**, in the skill
  `nar:<language>`. (R10-fence-form, R10-fence-fact, R10-fence-alternative)
- a comment on one branch of a `match`, `switch` or `if` chain is about what only that branch does. A reason
  that covers every branch goes above them once. Cut it when a name such as `local` already makes
  the reason obvious (R10-branch-comment)
- directly above the statement it concerns. Above the enclosing block is too far. Put a comment
  inside a try block above the call the comment concerns, and keep the comment off the `try` line.
  Put a comment on an argument above the call that passes the argument. End-of-line for a short note. (R10-Q34, R10-locality, R10-fence-form,
  R10-argument-placement)

`NAR012` to `NAR016` and `NAR018` flag six wording faults in comments and docstrings, and a clean
run isn't evidence about the rest of these lists. Check every comment and docstring you write or
touch against them. A dash after a list-item term is allowed. `NAR015` also flags `no longer` about
data. Such a sentence usually has data as the subject of an agent verb, so reword the sentence.
(R10-lint, R10-skill-gaps, R10-list-dash, R10-nar015-scope,
R10-nar016, R10-nar018)

`NAR017` is an agent verb on a subject that cannot act, meaning a noun that is not a person, with a
verb for something only a person does: thought or speech (`a period ranks`, `the report names it`,
`a policy can judge`), or, with an object, a deliberate act (`the default config sends the job to a
queue`, `the fallback places the file`). The rule is the same for documents. Write `named in the report`. A
table, figure, or example on the page can show what is in the table, figure, or example: `the table
below shows the totals`. A program or an element of a screen doesn't show anything: `the summary
shows the totals` → `the summary has the totals`. A machine in a game or a factory may feed or
receive: `a tower feeding a reactor` is fine. A verb of code is a finding too when the act behind the
verb is vague. Name the change: `Enumerator.resolve() applies it` → `resolve() sets the tier of each
recipe`. (R12-agentverb-rulings)
It comes from `agentverbs.py`, which `verify.py` runs. The check parses each sentence, and
some noun compounds and participles are flagged by mistake. (R10-agentverb-check,
R10-agentverb-agency)

To fix a `NAR017` finding, make the subject the person or the program that does the act, and keep
the verb: `the invoice tells the customer the due date` → `billing service prints the due date on
the invoice`. Don't turn the verb into a noun, such as `the payment's arrival` or `first
receipt`. Don't swap in a verb of little content, such as `gets`, `is`, `becomes`, `stays`, or
`fills`, and don't give a time as `X is the moment of Y` or `X is when Y`:
- `the due date is the moment of the invoice's issue` → `issueInvoice() sets the due date to the
  issue date plus 30 days`
- `the late fee stays on the invoice` → `applyLateFee() adds the late fee to the invoice`
(R12-name-the-actor)

`NAR020`, from the same check, is a clause with no subject before `, so`: `Named, so a recreated
container gets it back`, or a subordinate clause before `, so`: `Whether some terms differ by
mode, so…`. Only that form is flagged. Check every other clause against the subject and
verb rule in **Sentence form** by hand. (R10-subject-verb, R10-nar020, R11-nar020-subordinate)

`NAR021`, from the same check, is a clause that `as` or `, where` joins to a sentence. The
connective rule is in **Sentence form**. (R11-connective-as-where)

`NAR022`, from the same check, is `it` or `its` after two or more singular nouns in one sentence.
The referent rule is in **Sentence form**. (R11-pronoun-grammar)

**A finding is information.** Read the sentence again, then rewrite or delete the sentence, except
in three cases:

1. **A misparse.** The flagged words are not the subject and verb, or not one clause, in what you
   wrote. Leave the sentence.
2. **A quoted example.** The flagged text is an example of the fault, such as a banned word in the
   rule that bans the word. Leave the sentence.
3. **The code's name for the thing.** The flagged words come from an identifier, such as `the worker
   owns the lock` from `ownsLock()`. Leave the sentence, and list the sentence in your report.

Do not drop a finding from the output, with `grep -v` or otherwise. A finding that you take for a
tool error goes in your report with the file and line. When the user decides to keep a finding, keep
only that finding, and only in that pass. (R11-no-filter)

**Never add a `noqa` yourself.** The exceptions are under **noqa** in **Comments in <language>**, in
the skill `nar:<language>`. For a sentence left under case 1, 2 or 3, don't add a `noqa`: leave the
sentence and the finding, and list the sentence in your report. Rewrite a sentence from a review
list only when the sentence fails a step of **Prose review**. (R11-findings, R11-noqa-leave)

### Writing a comment

Take these steps in order before writing or rewording a comment. The kinds, the **Never** list,
**Depth** and **Sentence form** are in **Comments**.

1. **Rename first.** If the information fits in a name or a type, rename, and don't write a comment:
   `ByteCount` as the type of `overQuota`, `totalCents`, `rollingMeanSignedError`. (R10-Q25, R10-Q27, R10-Q16)
2. **Guarantee it in code.** Establish a cheap precondition, such as sorted input, upstream in the
   call flow. Don't establish the precondition in the function that depends on the
   precondition. Don't
   write a comment. An index lookup doesn't sort its input. If a code change removes a trap, make the
   change, and don't write a comment. If explaining how the code works takes more than one plain clause, rewrite the code
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

**Fix every finding of `verify.py` first. Then read the review lists in the file named on the last
line of the output, plus every error message and `--help` string.** You rewrite sentences when you
fix findings, so read the lists from the run after the fixes. The first list has every sentence of every comment and
docstring in the code, and every sentence of each named page. The second has each subject that
cannot act, paired with the subject's verb, for every verb that is neither a `NAR017` finding nor
an operation of code. A verb such as `reads` or `runs` is an operation of code only with a direct
object and code as the verb's subject: `PlanLoader reads the plan file` is one, and `the spec reads` isn't. The
third has every sentence with `it`, `its`, or a standalone `that`, each after the sentence before. The fourth has every
sentence with a free modifier: write the phrase as a clause or a separate sentence, or cut the phrase
(R12-no-free-modifier). The fifth list has each docstring, javadoc, and member comment, and each function over 20 body lines (`NAR116`). Take these steps for each
sentence. (R10-prose-inventory, R10-closing-review, R11-pronoun-list,
R11-literal-review)

1. Name the subject and the verb. Can that subject perform that verb? Most pairs are in the second
   list. A subject that is misread in the parse is not in the list. If the subject can't perform the verb, name the person or the program that does the act. The details are in the `NAR017` rule of **Comments**.
2. For each noun phrase, name the variable, function, file, or value that the phrase refers to. If
   you can't name one, or you can name two, rewrite. Check each descriptive word of the phrase by **A descriptive word
   in a term is a claim**. For each pronoun in the third list, name the noun the pronoun stands for.
   If that noun is in another sentence, repeat the noun. (R10-stand-in)
3. List the code paths that reach the line, such as each branch, each caller, and each failure. Check the claim
   on every path. A missing log entry is not proof that the event never happened. Before you write a
   claim such as `the log doesn't have a stop event, so the server didn't stop`, check that the code logs a
   stop event on every path where the server can stop. (R11-absence-proof)
4. Test the sentence against **Sentence form**, and the comment against the restatement gate.

For `an expired item is removed on lookup`:
- `an expired item` is an `Item` whose `deadline` has passed. `lookup` is `getItem()`.
- Two paths remove an expired item: `getItem()`, and `dropExpired()` before an eviction. The
  comment covers only `getItem()`.
- The rewrite: `an expired item is removed on lookup, or before any eviction`.

Rewrite a sentence from a review list only when the sentence fails a step of **Prose review**. When
the subject can do the verb in the domain's sense, such as a row that gets the default currency, leave the sentence unchanged.
(R11-review-question)

Fix every finding and answer every list entry from one run, then run `verify.py` once more. Do not
run `verify.py` after each single fix. (R11-batch-runs)

**When you ask the user to choose in a report, show the text of each option before and after the
change.** When the report has only an id such as `B3`, or a path to a file, the user can't compare the
options.
(R11-options-inline)

### Published prose

A README, a doc page or an HTML report that you write follows the prose rules of this skill, as a
comment does. When you rewrite part of a page, the rules cover the section you changed. If the
rest of the page is clearly written by an LLM, suggest cleaning the rest, and do not change the
rest unasked. A page that a person wrote and you did not change is left as it is, unless the user
asks for it to be checked. Name each page to the `verify.py` of the language skill. The command is
under **Pages** in **Comments in <language>**, in the skill `nar:<language>`.

Write a page about the current code and data, with no changelog wording such as `now`, `no longer`,
or `was changed to`. Changelog wording belongs only in a changelog file that already exists in the
repository, such as `CHANGELOG.md`. Do not create a changelog file unless the user asks for one.
(R11-page-changelog)

State the current fact and the condition of the fact. Don't write the history of the page, such
as an earlier figure or a change of mind: `far smaller than it first looked` → `9% less code on a
spec with fixed outputs`. (R12-page-history)

A heading is the name of the topic: `What goes in a body, and what does not` → `Docstring body`.
(R12-topic-heading)

Open a README with the benefit to the reader. Give a number for the benefit when you have one.
Then put a cost of adoption in a short caveat, and then an example. Put evidence and process in
other documents, and link to those documents from the README. (R12-readme-order)

In instructions for an agent, such as a skill or a prompt, don't use a verb of perception such as
`see`, `look`, or `notice`. Name the act: `see the list` → `read the list`. (R12-no-perception-verb)

Only the wording checks and `agentverbs.py` run on a page. `verify.py` writes the lists of
**Prose review** for each named page too. When `--since` is given, only the passages of a page with a
changed line are checked and listed. Take the steps of **Prose review** for each sentence you wrote, and
handle each finding by the rule **A finding is information**. (R10-published-prose,
R11-page-inventory)
