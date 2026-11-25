## Rhetorical setups

A rhetorical setup is a common LLM tell. To test a sentence, delete the setup, and write the fact
that is left as the sentence.

**Leave out a denied strawman.** (R13-strawman) `Not just X, but Y`, `This isn't X. It's Y`, or `X, not Y` when
a reader didn't think X. Write Y. `NAR024` flags `X, not Y` and `not merely`, and this rule covers
the other forms too. When a reader is likely to assume X, write the fact about X in a separate
sentence, with the reason X is wrong.
- `The oven isn't the bottleneck, the proofing is` → `The oven waits on the proofing. Each tray is
  proofed before the oven is free.`

**Leave out a setup question before an answer.** (R13-question-setup) `The result?`, `Why does this
matter?` and `The catch?` are such questions. Write the answer. A question belongs on a page only as
a question without an answer yet.

**Write a sentence in place of a label and a colon in running prose.** (R13-label-colon) A colon or
a dash splits the sentence into a label without a verb and the rest, with the short part on either
side. A short tail is a reveal, such as `The fix: one line.` or `Here's the catch: …`. A short head
is a label on an explanation, such as `AUC 0.9: a cut on rainfall separates …`, `Evidence: …` or
`The user's point: …`. People don't speak this way. Write one ordinary sentence with a subject and a
verb: `The north depot's delay is the only delay on each day of the week.` A label with a colon is
fine in a bullet, a table cell, a caption, a glossary entry, and before a list.

**Leave out a kicker at the end of a section.** (R13-kicker) `In short, …`, `The bottom line: …`,
`That's the whole story.`, `Nothing else.` End a section on the last fact.

**Leave out signposts.** (R13-signposts) `Here's what you need to know`, `Let's break it down`,
`It's worth noting that`, `Importantly,`, `This is where X comes in.` Delete the signpost and keep
the rest.

**Leave out fragment runs and triplets.** (R13-fragments) `Simple. Fast. Reliable.`, or `faster,
simpler and safer` without a fact behind each word. List only items with a fact on the page, and
give the fact.

**Leave out dramatic punctuation.** (R13-punctuation) An em dash for a pause or a reveal, an
exclamation mark, a one-word paragraph. Use a comma, a period or parentheses. Keep a dash for an
aside only.

**Leave out before and after framing without a change for the reader.** (R13-before-after) `No more
waiting`, `Gone are the days`. Say what happens, with the number.

