# The literary sentence shape: names, measurements, a draft rule

Your flag of 2026-11-21:

```
The mob spawn overlay quads, in one GL display list for each chunk column of the box of a {@link MobOverlayScan}.
```

## Names

The sentence has three features, and each has a name in grammar or stylistics.

1. **A free modifier**: a phrase without a verb that follows a comma and adds to the sentence. In the flagged sentence
   the free modifier is `, in one GL display list for each chunk column`. A sentence of a base and free modifiers is a **cumulative sentence**. Francis Christensen named
   both terms in "A Generative Rhetoric of the Sentence" (1963), and found the form typical of published literary
   prose. This feature is the closest match to "literary prose".
2. **Nominal style**: nouns and prepositions in place of verbs. Rulon Wells contrasted nominal style with verbal style
   in "Nominal and Verbal Style" (1960). The Swedish readability measure **nominal ratio** (nominalkvot, NQ) divides the
   count of nouns, prepositions and participles by the count of verbs, adverbs and pronouns. The flagged sentence has an NQ of
   14. In the example of Språkbanken, a simple sentence has 0.33.
3. **A verbless sentence** (a minor sentence): a noun phrase with no finite verb, the form of a caption or of an
   advertising line.

The chain `of the box of a MobOverlayScan` adds to feature 2.

## Measurements

The comparison has three groups of sentences, each of 4 or more words:

- the Claudish inbox: the dev units, plus the flagged sentence. 69 sentences.
- human GTNH comments: javadoc and `//` comments of 20 GTNH repositories. Each repository is at its last commit before
  2023-01-01. 1,523 sentences.
- Claude's comments: the first 600 round10 dev units of kind comment or docstring. 678 sentences.

| feature | Claudish inbox | human GTNH | Claude round10 |
|---|---|---|---|
| a free modifier (a comma phrase with no verb, opening with a preposition, a participle or a number) | 10.1% | 1.1% | 4.9% |
| NQ 4 or more in a sentence of 8 or more words | 33% | 17% | 18% |
| a chain of 3 or more prepositional phrases | 5.8% | 1.1% | 1.0% |
| no finite verb | 12% | 19% | 11% |
| `The` as the first word | 17% | 4% | 15% |

- The free modifier separates the groups best: 9 times the human rate, and 1 human sentence in 90.
- NQ separates the groups too, but 1 human sentence in 6 has an NQ of 4 or more, such as `The number of item (output)
  slots available for this machine`. A check on NQ would flag too many good sentences.
- A verbless sentence is common in human comments, such as `Meant for notifications that are being send to an
  admin/op`. Feature 3 alone isn't a fault.
- `The` as the first word is a Claude habit. Both Claude groups have 15% or more, and human comments have 4%.

Free modifiers in the Claudish inbox, each in its sentence:

- `…splits each milestone already reached, at the IGT of the milestone's first reach.`
- `A curve down to the ground makes a wall: 80 blocks, measured, for a cylinder of 10 off a tower.`
- `…over a hundred blocks for one stroke, away from the shape, with nothing placed under the cylinder.`
- `State what is true of the code now, in the present tense.` (Claude's draft of rule 2a)

Free modifiers in Claude's round10 comments: `One row per finding, in the column order of the INSERT.`, `as typed, for
the report's input_dir`, `The event and its total are printed once, against the first of its examples.` You flagged
the `as X, for Y` form on 2026-10-24, and rated the form acceptable then.

Limits: the inbox group is 69 sentences, and has pages and changelog text as well as comments. The human sample is
1,424 comments from 20 repositories. 4 of the 20 are forks of GT5-Unofficial with one history before 2023, so the
sentences were deduplicated by text. The scripts and the human sample are in
`~/.local/share/narrative/eval-private/runs/claudish-rules/shape/`.

## Rule 13, draft

Placement: after the connective item in **Sentence form** of `core/rules/comments.md`. The reason is the reason of the connective
item: the reader can attach the phrase to the wrong noun.

```
- no free modifier. A free modifier is a phrase without a verb that follows a comma: `, in one
  list for each tenant`, `, measured,` or `, with the row number in the error`. The reader can
  attach a free modifier to the wrong noun. Write the phrase as a clause with a
  subject and a verb, or as a separate sentence, or cut the phrase:
  - `The retry jobs, in one list for each tenant of the scheduler` → `` `RetryQueue` has one list
    of jobs per tenant ``
  - `export() stops at the first bad row, with the row number in the error` → `export() stops at
    the first bad row. The row number is in the error message`
  The fourth review list of `verify.py` has every sentence with a free modifier. (R12-no-free-modifier)
```

The second example has `The` as the first word of a sentence in the middle of a comment. Rule 12 covers only the first
word of a comment, so the example passes rule 12.

## Check, draft

A new list from `agentverbs.py`. List each sentence with a comma-delimited segment that comes after the first segment,
has no verb other than a past participle, opens with a preposition, a past participle or a number, and has 2 or more
words. Leave out a segment that opens with `and`, `or`, `but`, `so` or `then`, and a segment in a list of numbers, such
as `24, 32 and 40`.

The check flags 1.1% of the human sentences, such as `Lookup inheritance information from multiple sources, in
order.` and `Represents a collection of MethodSlices, mapped by ID.` On 2026-11-21 you judged that most human uses are
faults too, so the human rate is mostly true positives. You chose a review list: `verify.py` writes a fourth list with
each sentence that has a free modifier. The agent answers each entry by **Prose review**. The list of agent verbs works
the same way.

## Sources

- [Språkbanken: nominal ratio in Sparv](https://spraakbanken.gu.se/en/node/4488), the formula of NQ
- Wells, "Nominal and Verbal Style", in Sebeok (ed.), *Aspects of Style* (1960), pp. 197–200: a bibliography record
  and a summary in a 1963 paper, found by search ([Benjamins, CILT 42](https://benjamins.com/catalog/cilt.42),
  [Deep Blue](https://deepblue.lib.umich.edu/bitstream/handle/2027.42/32240/0000302.pdf)). I haven't read the chapter.
- [Christensen, "A Generative Rhetoric of the Sentence" (1963), discussed in the Journal of Teaching Writing](https://jtw.iupui.edu/index.php/teachingwriting/article/download/18656/18652/26489)
