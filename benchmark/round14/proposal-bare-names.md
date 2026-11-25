# Proposal: read a javadoc link as the bare name

Applied on 2026-11-24 to `{@link}`, `{@linkplain}` and `{@code}`, at the user's choice (R14-bare-name). The rule
text is in `core/rules/prose-review.md`.

## Problem

`agentverbs.py` treats a name in a javadoc link as code. When the verb is a verb that code does, such as `take`, `read`
or `return`, and the sentence has a direct object, the pair counts as an operation of code, and the pair isn't on the
review list. In PlanNH, `{@link #lang} and {@link #translate} take the last part of a key` passed that way. The bare
form, `lang and translate take the last part of a key`, doesn't name the argument or the result of a call.

## Measurement

Pairs that the operation-of-code test skips with a link or a code span as the subject:

| Corpus | Sentences | Skipped pairs |
|---|---|---|
| GT5-Unofficial `gregtech/api/logic`, branch `processingspec/5-eye-of-harmony` | 325 | 15 |
| PlanNH `src/main/java`, commit `52a71d6` | 1,510 | 4 |
| Narrative `core/tools` and `lang/python/tools` (Python, backticks) | 1,097 | 50 |

Most of the Python pairs have a literal token as the subject, such as `a / opens a regex`, and are right to skip. I
propose the change for `{@link}` and `{@linkplain}` only.

## Rule text, `core/rules/prose-review.md`, after `the spec reads` isn't

> A name in a javadoc link isn't code for this test. Read the sentence with the bare name: `{@link #stop} and
> {@link #route} take the last part of an id` reads as `stop and route take the last part of an id`. The bare sentence
> doesn't name the argument or the result of a call. Write the call and the result: `stop("12")` returns `north.12`.
> (R14-bare-name)

## Check change

`codeprose.py` of Java marks the span of a `{@link}` or `{@linkplain}` tag apart from a `{@code}` span. `reviewPairs()`
of `agentverbs.py` skips a pair with a link as the subject only by the other rules, so the review list has the pair
`stop take`. The pair shows the bare name. The review list grows by about one entry per 20 sentences of javadoc.
