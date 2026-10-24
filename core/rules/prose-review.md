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

