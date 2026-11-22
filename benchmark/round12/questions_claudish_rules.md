# Open questions on the Claudish-inbox rules

Five questions. Your answers fix the wording of the rules before the approval of the batch.

## Q1. The form of a Fence

You flagged this example of rule 2a on 2026-11-21 (inbox unit 41a5422d):

```
the payment provider charges each new idempotency key. Send the key of the first attempt on each retry
```

The form comes from the skill. The item on the Fence form in **Sentence form** has the text "a Fence is the fact the
code depends on, then the step the code takes because of that fact" (R10-fence-form, R10-fence-fact). Every Fence
example of the skill has the form:

- `the endpoint drops the first request after idle time. Retry once`
- `the API returns 200 with an error body for a bad key. Check the body too`
- `migrate before load. load reads the account_id column`

The second sentence names the step that the code below the comment takes. A reader of the code sees the step, so the
sentence adds little. By a common maxim, a reader learns how from the code and why from the comment. The second
sentence is about how.

Three forms for the flagged example:

| option | rewrite | risk |
|---|---|---|
| A: one sentence with the defect of the simplification | `a new key on each retry would charge the card twice` | a sentence with `would` is about code that isn't there. The existing item allows `X would` only for an alternative that the code doesn't use, and a new key per retry is such an alternative |
| B: the fact alone, directly above the line | `the provider charges once per idempotency key` | when the comment is above a block, the reader may not find the line that depends on the fact |
| C: one sentence with the step and the reason | `reuse the key of the first attempt, because the provider charges once per key` | the sentence is still about how, and `because` joins two clauses |

Option A is also the test of the Fence kind: the simplification a developer would make, and the defect that the
simplification causes. With option A or B, the item on the Fence form changes, and so do the Fence examples of the
skill.

## Q2. The units of rules 10 and 12

Rule 10 (constant values in comments) and rule 12 (`The` as the first word) don't have dev units with the fault. The
evidence of both rules is in the test split. All of it comes from the NEI mob spawn overlay PR:

- rule 10: inbox pub 33 and 34 (`goes stale`)
- rule 12: f78a9a96, and the class javadocs of the form `The X of Y.` (pub 22–26)

Rules 4 and 5 use 12 test units of the same PR, and those 12 are out of the final held-out score. The same choice for
rules 10 and 12 moves 8 more units out. The other choice: rules 10 and 12 get a score only in the final run on the test
split.

## Q3. `NAR116` (rule 11)

`NAR116` flags a method over 3 parameters or 20 body lines without a javadoc. On NEI PR 1146, both flagged methods
are private: `WorldOverlayRenderer.compileChunkFaces()` and `MobOverlayScan.markChunks()`.

| option | change |
|---|---|
| A | `NAR116` flags only public, protected and package methods. A reviewer applies the rule to a private method |
| B | the thresholds go up, such as 5 parameters or 40 body lines |
| C | `NAR116` is removed. A reviewer applies the rule in `javadoc-rules.md` |

## Q4. The scope of rule 12

The draft is about the first word of a comment or a docstring. These are the forms in place of `The`:

- a class or a module: the identifier as the subject. You chose this form B.
- a function: the imperative, such as `Return the invoices of one billing period, oldest first.`
- a one-line comment: no article, such as `vendor sends amounts in cents`

Two questions on the scope:

1. Is the rule about the first word of every sentence of a comment, or of the first sentence only?
2. Are the forms for a function and for a one-line comment right? You chose a form only for a class.

## Q5. Openers with a version or a platform (rule 6)

By rule 6, a condition is a clause after `when` or `if`. The rule replaces a phrase such as `with a full disk,`. Some
openers name a version or a platform, such as `On Linux,` and `In Python 3.11,`. No flag has this form. Should rule 6
cover these openers? The rewrite would be `when the program runs on Linux, the path is ~/.config`.
