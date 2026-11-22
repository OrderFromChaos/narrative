# Rules 2 to 16 from the Claudish inbox: drafts, version 4

Status, 2026-11-21: rules 2, 3, 6, 7, 10, 12 and 13 are in `core/` and `lang/`, by your choice after the batch test.
Rule 13 is in without its last sentence, on the review list of `verify.py`: the list isn't built yet. Rules 4, 5, 8
and 9 are held for rework. Rules 11, 14, 15 and 16 have no test yet.

Each rule below has a placement, the text to insert and a decision id. Version 3 has your answers of 2026-11-21 to
the open questions, and version 4 has your corrections of the same day. The findings behind those answers are in `benchmark/round12/findings_open_questions.md`.

The examples of a rule are from other domains, so no example is a sentence of the dataset. A Fence example is the
exception: by your choice, the Fence examples are quotes of comments by human authors in the Python standard library.

The dataset is 98 units. Their labels were fixed before any run.

| rule | units | source |
|---|---|---|
| 1 | 13 | the rule 1 units (one confidential, not sent) |
| 2 | 21 | inbox pub 47–62, priv 0–4 |
| 3 | 7 | inbox pub 0, 2, 4–8 |
| 4 | 8 | inbox test units pub 27, 30–32, 38, 39, 42, 43 |
| 5 | 7 | inbox pub 12, and test units pub 28, 29, 40, 42–44 |
| 6 | 6 | inbox pub 10, 48, 51, 53, 58, 59 |
| 7 | 16 | your labels of 2026-11-21, rows 1–17 |
| 8 | 7 | inbox pub 63–69 |
| 9 | 4 | inbox pub 73, and your labels, rows 18–20 |
| 10 | 2 | inbox test units pub 33 and 34 |
| 12 | 6 | inbox test units pub 22–26, and f78a9a96 |
| 13 | 5 | inbox pub 0, 54, 58, 61, and the flagged draft sentence of rule 2a |
| keep | 8 | gold keep units, to count false fixes |

The 20 test units of rules 4, 5, 10 and 12 are out of the final held-out score. Some units have two rules, such as
pub 48 (rules 2 and 6). Rule 11 is a change to a check, and the held-out set of rule 11 is a separate file. Rules 14, 15
and 16 have no units yet, so they get no score in the batch.

## Rule 2a: no changelog in a comment

Placement: `core/rules/comments.md`, **Never**. The text replaces the item `changelog: an earlier state of the code, or
a fixed bug with nothing left of the bug`.

```
- changelog: an earlier state of the code, the story of a bug, or a report from a user. Cut the
  sentence:
  - `a cache of 64 entries once evicted the hot keys under load` → no comment
  A story of a bug in the present tense is still a changelog. Look for the past tense and for
  `once` in a sentence about the code or the users. When the code depends on a fact behind the
  bug, write the fact as a Fence. The form of a Fence is in **Sentence form**. Keep a Source fact
  about old data: `databases written before 2025/04/03 lack the account_id column`. (R10-Q04,
  R10-Q08, R10-Q52, R12-no-changelog, `NAR015`)
```

## Rule 2b: no changelog tests

Placement: a new item of `lang/python/rules/testing.md` and of `lang/java/rules/testing.md`.

```
- **No test only because a bug was fixed.** Write a regression test when the code under test is
  likely to break the same way again, or when the test checks an invariant of the program. Write the
  case and the expected result in the name and the docstring of the test. Use the present tense.
  (R12-no-changelog-tests)
```

Conflict: `lang/python/rules/testing.md` has `Example-based tests cover specific regressions on top`. Under rule 2b
that sentence needs the same condition. The change goes to you in the de-poisoning pass.

You flagged the sentence on the commit message on 2026-11-21, so version 3 drops the sentence and the example of the
sentence.

## Rule 3: to fix NAR017, name the actor

Placement: after `Write named in the report.` in the paragraph on `NAR017` of `core/rules/comments.md`.

```
To fix a `NAR017` finding, make the subject the person or the program that does the act, and keep
the verb: `the invoice tells the customer the due date` → `billing service prints the due date on
the invoice`. Don't turn the verb into a noun, such as `the payment's arrival` or `first
receipt`. Don't swap in a verb of little content, such as `gets`, `is`, `becomes`, `stays` or
`fills`, and don't give a time as `X is the moment of Y` or `X is when Y`:
- `the due date is the moment of the invoice's issue` → `issueInvoice() sets the due date to the
  issue date plus 30 days`
- `the late fee stays on the invoice` → `applyLateFee() adds the late fee to the invoice`
(R12-name-the-actor)
```

Placement of a second part: a new last sentence of step 1 of `core/rules/prose-review.md`.

```
If the subject can't perform the verb, name the person or the program that does the act. The
details are in the `NAR017` rule of **Comments**.
```

## Rule 4: one fact in one place

Placement: a new step of `core/rules/writing-a-comment.md`, between **Guarantee it in code** and **Match a kind**. The
later steps are renumbered.

```
3. **Read the comments nearby.** Before you write a comment or a docstring, read the docstring
   of the class or the module, and the comments of the fields and functions next to the new text.
   Don't write a fact a second time. When the comment on the field `nextRow` has `the first row
   not yet exported in this pass`, don't repeat the fact in a comment in `exportSlice()`. A
   guarantee for the callers of a public function, such as thread safety, may be in the docstring
   of the class and in the docstring of the function. In an IDE, a reader of the call sees the
   docstring of the function. (R12-one-place)
```

Version 3 has a new example and a sentence on guarantees for a caller, by your flag of 2026-11-21: "Duplicating this
kind of public developer consumer guarantee is ok".

Placement of a second part: a new sentence of the **Never** item on guarantees in `core/rules/comments.md`.

```
A sentence about a later part of the same function is a guarantee too: `the totals below skip a
closed account` → a comment above the line that skips the account, or no comment.
```

## Rule 5: in a Fence, name the technique and a defect you saw

Placement: the **Fence** kind of **Comment kinds** in `core/rules/comments.md`, after `Name the step the code takes
because of the fact.`

```
Name the technique with the term that practitioners use, such as `debounce`, `double buffering` or
`optimistic locking`. Write a Fence only for a defect that you checked: in the code, in the output
of a test or a run, or in the documentation of a library. Write that defect. Don't write a test only
to show a defect that is plain in the code. Don't write a reason that you guessed. (R12-fence-technique)
```

You flagged the version 3 wording on 2026-11-21: `a defect that you saw with the guard removed`. An agent doesn't
see, and by that wording an agent writes a test of a defect that is plain in the code. The new wording asks for a checked source,
and allows the code as the source.

Version 3 drops the example `debounce the autosave. …`. The example had the two-sentence form that you rejected, and
the Fence examples of rule 14 are human comments.

## Rule 6: a condition is a clause

Placement: a new item of **Sentence form** in `core/rules/comments.md`.

```
- a condition as a clause after `when` or `if`. The clause has a subject and a verb. Don't write
  the condition as a phrase after `at`, `with`, `beside`, `against`, `on` or `for` at the start of
  a sentence:
  - `with a full disk, export() deletes the partial file` → `when the disk is full, export()
    deletes the partial file`
  - `with an expired token, the retry fails` → `when the token has expired, the retry fails`
  Keep an opener with a platform or a version, such as `On Windows,` or `In Python 3.11,`.
  (R12-no-prep-opener)
```

You labelled four platform openers of the standard library G on 2026-11-21.

## Rule 7: no `X, not Y`

Placement: a new item of **Sentence form** in `core/rules/comments.md`. Your labels of 2026-11-21 mark every `, not Y`
of the 17 rows, so the draft has no exception for a Y in the code.

```
- no contrast with `X, not Y` or `not merely`. State X. When the reader needs a fact about Y, write
  the fact in a separate sentence:
  - `amounts are in cents, not dollars` → `amounts are in cents`
  - `Inclusive, not exclusive: the end date is billed` → `end date is billed`
  - `retry on a timeout, not on a refusal` → `retry on a timeout. Raise ConnectionError when the
    server refuses the connection`
  (R12-not-contrast)
```

Conflict: examples of the skill have the form. You flagged the Fence example `the vendor rounds tax per line, not
per invoice` on 2026-11-21. The others go to you in the de-poisoning pass.

## Rule 8: text for players

Placement: a new item of `lang/java/rules/gtnh.md`.

```
- **Text for players: the lang file, config comments, help text and the changelog.**
  (R12-player-text)
  - Address the player as `you`. Use the player's word for a setting or a control: the label on
    the screen, or the word a player uses. `Fade` → `Transparency`.
  - When an option gets a sibling option, name in each label what differs: `Speed` → `Walk speed`
    and `Fly speed`.
  - Leave a list of values and a range out of the comment string of a config option in the code.
    A developer who adds a value then has one place to change. Help text for players in the lang
    file is outside this bullet.
  - Describe only what this mod does in help text and the changelog. Leave out vanilla behaviour,
    such as `press T to open chat`, limits that players don't reach, and a formula that a player works
    out from the numbers on the screen.
```

Version 3 changes the third bullet. Version 2 allowed a list that string formatting builds from the code. In pub 33,
Claude built the list of styles from `MobSpawnOverlayStyle.formatAllNames()`, and you rejected the list: "Should not
duplicate values here. This force compels all future devs adding modes to update multiple locations".

## Rule 9: the domain's word for a thing

Placement: after the item `possessives and noun compounds over relative clauses` in **Sentence form** of
`core/rules/comments.md`.

```
- the domain's word for a thing. For each `that`, `which` or `who` clause, ask whether a
  practitioner has one word or a short term for the thing, and use the word in place of the clause:
  - `the invoices that no customer has paid` → `unpaid invoices`
  - `the accounts that don't have an owner` → `unowned accounts`
  (R12-domain-word)
```

## Rule 10: no constant values in comments

From the entry of 2026-11-07 in `benchmark/INBOX.md`. Placement: a new item of **Never** in `core/rules/comments.md`.

```
- the value of a constant. The value is in the declaration of the constant, and a comment with the
  value is wrong once the constant changes. Write what the value means, or nothing:
  - `# retry every 30 s` above `RETRY_DELAY_SECONDS = 30` → no comment
  - `# the vendor accepts 1 to 100` beside `MIN_PAGE_SIZE` and `MAX_PAGE_SIZE` → `# page sizes the
    vendor API accepts`
  The item is about config comments too, because a config comment is code text. Help text for
  players in the lang file is outside the item. A tooltip may have `Range 8-64 blocks`.
  (R12-no-constant-values)
```

Version 3 changes the last sentence. Version 2 put all text that a user reads outside the item. pub 33 and 34 are
config comments, and you rejected the values in both.

Check: the inbox entry has a draft of a check. Flag a number in a comment when the number is the value of a constant
that the comment names, or of a constant declared on the lines below the comment.

## Rule 11: `NAR116` becomes a review list

From the entry of 2026-11-21 in `benchmark/INBOX.md`. Placement: three places in `lang/java/rules/javadoc-rules.md`,
and the row of `NAR116` in the table of `lang/java/tooling.md`.

The item that opens with `A method gets a javadoc when its contract is complex` becomes:

```
- **A method gets a javadoc when a reader can't learn from the name of the method and the comments
  of the body what the method does.** Answer one question for each method in the `NAR116` review
  list of `verify.py`:
  - without a javadoc: can a reader learn from the name of the method and the comments of the body
    what the method does? If not, write a javadoc.
  - with a javadoc: what does a reader learn from the javadoc, and not from the name of the method
    or the comments of the body? If nothing, cut the javadoc.
  (J1-P34, Q05, R8-D18-resolved, R12-nar116-review)
```

In the first paragraph, `A top-level type (NAR118) and a method over the contract threshold (NAR116) need one.`
becomes:

```
Write one for a top-level type (`NAR118`), and for a method by the `NAR116` review list.
```

In the item on `@throws`, `for a method over that threshold` becomes `in the javadoc of a method`. The number 20 is
then only in the row of `NAR116` in `lang/java/tooling.md`.

The row of `NAR116` in `lang/java/tooling.md`:

```
| `NAR116` | a review list of each method over 20 body lines. The list has methods with a javadoc too (J1-P34, R12-nar116-review) | PMD, then `javachecks.py` |
```

The tool change: the PMD rule of `NAR116` drops the parameter count, and `javachecks.py` writes each hit to the review
list in place of a finding.

Your labels of 24 methods over the current threshold are the evidence. The labels are in `label_open_questions.md`
and `label_nar116_heldout.md`. Y is your label for a method that should have a javadoc.

- 8 methods are over the threshold only by the number of parameters. You labelled none of the 8 Y.
- All 7 methods that you labelled Y have more than 20 body lines. You labelled half of the methods over 20 lines N.
- A trigger by the name of the method fit the first 14 labels, and failed on the held-out 10.
- You labelled no method of one line Y.
- You chose a review list that covers a method with a javadoc too, because an agent may have written a poor javadoc
  earlier.

## Rule 12: no noun phrase for the identifier

From your flag of 2026-11-21 on the class javadoc of `MobOverlayDisplayList` (inbox unit f78a9a96), and your Q4
labels. Placement: a new item of **Sentence form** in `core/rules/comments.md`.

```
- don't make the first sentence of a docstring a noun phrase for the identifier. Write a sentence
  with a verb about what the reader can't get from the name, or cut the docstring:
  - `The size of this stratum (number of lines)` on the field `size` → no javadoc, and the name
    `lineCount`
  - `A GL display list of the mob spawn overlay.` on the class `MobOverlayDisplayList` →
    `` `MobOverlayDisplayList` compiles the overlay quads of each chunk column into one GL display
    list. ``
  (R12-no-name-phrase)
```

Version 3 replaces the ban on `The` as the first word. Your Q4 labels have three G later sentences that open with
`The`, and three G javadocs that open with `The` or `A`. Five of the six B javadocs are a noun phrase for the
identifier. The two examples in the rule are from the Q4 items, so they aren't from another domain. Both are quoted as
faults.

Check: none yet. A check could look for a first sentence without a finite verb whose head noun is part of the
identifier, such as `size` in `The size of this stratum`.

## Rule 13: no free modifier

The draft, the measurements and the sources are in `benchmark/round12/proposal_literary_sentence.md`. You chose on
2026-11-21 to make the check a fourth review list of `verify.py`.

Open: `, such as X` is a phrase without a verb after a comma, and the skill has the form in many places. On 2026-11-21
you answered that the form is a question for more research, and that the three fixes I offered are poor: only in the middle of a
sentence, every use, or none. Until then, rule 13 and the check leave `, such as X` out. The detector skips the form
already, because `such` isn't a preposition, a participle or a number.

## Rule 14: the Fence form

From your rejection of the two-sentence Fence form on 2026-11-21, and your Q1 labels. Placement: the text replaces
the item of **Sentence form** in `core/rules/comments.md` that opens with `a Fence is the fact the code depends on,
then the step the code takes`.

```
- write a Fence as one sentence in the names of the code. The sentence has the step that the code takes
  and the failure that the code avoids by the step. `so that`, `to avoid` or `because` joins the
  two. Two sentences, a fact and then the step, repeat the code. A sentence with `would` alone has
  the danger without the step. Two Fences by human authors in the Python standard library:
  - `Pause early so that "ssl_protocol.data_received()" doesn't have a chance to get called
    before "ssl_protocol.connection_made()".` (asyncio/base_events.py)
  - `bpo-35726: make copy of record to avoid affecting other handlers in the chain.`
    (logging/handlers.py)
  (R12-fence-one-sentence)
```

Both comments are in Python 3.10, which is from 2021. You rated the first "excellent". The Fence examples of the skill, such as
`the endpoint drops the first request after idle time. Retry once`, go to you in the de-poisoning pass.

## Rule 15: no docstring on a one-line function

From your notes on Q3 items 7 and 10, and on Q4 item 7. Placement: the sentence `Don't write a docstring for a
function that only returns a constant` in `core/rules/comments.md` becomes:

```
Don't write a docstring for a function of one line. (R12-one-line-function)
```

You asked on 2026-11-21 whether the rule is redundant. Version 3 had the same rule for Java in rule 11, `A method of
one line gets no javadoc`. Version 4 drops that sentence from rule 11, so rule 15 is the one place of the rule.

Your note on Q3 item 10: "one line function rule >> labeling obfuscated names". So the rule covers a one-line function
that calls an obfuscated name.

## Rule 16: a design comment goes by the constant

From your note on Q1 item 1. Placement: the item of **Sentence form** in `core/rules/comments.md` that opens with
`directly above the statement it concerns`, a new sentence:

```
When a comment about the design behind a constant passes the test of a comment kind, put the comment
above the declaration of the constant, or in the docstring of the function. (R12-design-comment-place)
```

Version 3 of 2026-11-21 opened with `Write a comment about the design`, which reads as an instruction to write the
comment, and had the free modifier `, such as a read in chunks of chunk_size,`. You flagged both.
