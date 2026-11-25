---
name: page
description: The base Narrative rules for each page that people read, such as a report, a proposal or a README. The rules cover the target audience, the scope and the structure of a page, executive summaries, titles and headings as noun phrases, plain wording without marketing copy or rhetorical setups, coined and overloaded terms, and charts and diagrams. Load with nar:core to write or review a page. A category skill such as nar:proposal, nar:brief or nar:runbook loads this skill and adds the rules for one kind of page.
---
**Before you write or review a page, load the skill `nar:core` with the Skill tool**, unless
`nar:core` is loaded already. `nar:core` has the sentence rules, the agent-verb rules and the steps
of **Prose review**. This skill adds the base rules for each page, and a category skill adds the
rules for one kind of page.

# Narrative: pages

These rules cover a page that people read, such as:
- an HTML report
- a findings page
- a proposal
- a runbook
- a README

`nar:core` covers each sentence. This skill covers the reader, the scope, the structure, the titles,
the register, the terms, and the charts and diagrams of the page. A category skill, such as
`nar:proposal`, `nar:brief` or `nar:runbook`, loads this skill and adds the rules for one kind of
page.

In these rules, the reader is the target audience of the page, named before you write (**Reader**),
never a generic reader.

**Load `nar:core`, this skill and the category skill of the page before you plan the page.** (R13-steps)

**To write a new page, name the reader and the question, write the page, and run `verify.py` once.** (R13-steps) Fix
each finding, take **Prose review** of `nar:core`, and check the page against the checklist at the end of this skill.

**To clean up a page, cut before you change a sentence.** (R14-cleanup-steps)
1. Name the reader and the question of the page.
2. Label each section `keep`, `move` or `cut` (R14-triage).
3. Make the moves and the cuts, and check that each moved fact is on the destination page.
4. Date each relative time (R14-dated).
5. Run `verify.py --cleanup`, fix each finding, and take **Prose review**.

## Reader

**Name the people of the target audience before you write.** (R13-name-reader) A job title is too
broad. A finance director, a supplier's sales team and a bus mechanic each need a different page.
When you don't know who reads the page, ask the user.

**Leave out what the reader knows already, and detail the reader can't use.** (R13-reader-knows) The
sales team of a seed supplier knows the germination rate of each seed the supplier sells, and
doesn't learn anything from a slide with that number. A finance director knows the approval steps of
a purchase order. A sales team can't use the folder layout on a customer's file server. A term in
common use in the reader's field stays without a gloss. EBITDA stays EBITDA for a finance team.

**Use the reader's term for a thing, and name the unit or the kind.** (R13-reader-terms)
- `timetable`
- `wheelchair-accessible`
- `on board`
- `depot`
- `12 kg of flour` in place of `12 kg`
- `sourdough starter` in place of `the bubbly jar`

**Use the real name of a thing, and the same name in each place.** (R13-real-name) Write the name of
the fare type, and give the code as a pointer: `fare type: concession (fare_code = 6)`. A reader
takes a bare `fare_code 6` for the sixth fare.

## Scope

**A reader can follow the page without another file.** (R13-standalone) Don't refer to material off
the page, such as another file like the supplier comparison, `the surveyed shops`, `the note above
the boxes` on a page without such a note, or `the manager's check` in a process without such a step.
Don't refer to the session of the page, such as `as before` or `the previous candidate`.

**Keep to the question of the page.** (R13-on-question) Delete or narrow a section without an answer
to the question. A comparison with a rival bakery's prices doesn't belong on a page about the
delivery routes. Cite a text only for a claim in the text. A food-labelling rule for packaged bread
doesn't require a label on each delivery crate. Leave out a case with a cause outside the question.
When a page is about the delays from road works, leave out the one late delivery of 42 that followed
an urgent phone call to the driver.

**Check each claim.** (R13-check-claims) Don't copy a value from an earlier document without
checking the value. Label a claim without data as a hypothesis, or delete the claim. Name an
assumption as an assumption. A spike at 08:30 may be the school run and unrelated to the timetable
change.

**Replace each relative time with a release or a date from the history of the project.** (R14-dated) `Exports before
this version don't have a route column` → `Exports before 1.1.0 don't have a route column`. Do the same for `older bundles`,
`recently`, `(current)` and `found later`.

**Don't claim more than the data shows.** (R13-no-overclaim) When a pattern has a simpler cause,
name the cause. A value that only goes down is at the lowest reading on record at each new failure.
A failure at that reading is the expected result of any failure, and isn't evidence about the value.

**Leave out each remark that a stakeholder could read as a dig.** (R13-no-dig) Don't argue against a
phrase that a reader of the page used in passing, such as `the current system is fine`.

**Leave out an unflattering detail that doesn't change the reader's decision.**
(R13-no-unflattering) Leave last year's price rise out of a pitch to a new stockist. The reader's
decision is the same without the detail.

**Keep each finding that the user called important.** (R13-keep-important) Keep the finding as the
conclusion, and leave out the working. Before you delete such a finding, ask the user. In a pruning
pass on a page about late buses, the agent deleted the section on the drivers' break times, which
the user had called very important. The agent restored the section as two sentences in the table of
unanswered questions, and left out the two tables of shifts.

## Structure

**In a cleanup, label each section `keep`, `move` or `cut` before you change a sentence.** (R14-triage) Give each
`keep` the reader's action, each `move` the other reader and the page, and each `cut` the reason. `The reader might
want to know` isn't an action. Put the labels and the share of the page that you cut or moved in the report. A table
of driver shifts on the depot manager's page about late buses is a `move` to the rota planner's page.

**Name the reader's use of each section.** (R13-section-use) Do the same for each paragraph, table,
chart and table row in the section, and delete what the reader can't use, even when the data is
true, measured and hard to get. Delete a paragraph with the values of a chart or a table in words. A
reader skips a paragraph without content, and on a page of such paragraphs, the reader skips the few
with content too.

**Order the sections by the reader's priorities.** (R13-order) Put first the sections the reader
acts on. For a finance director, the budget goes right after the steps. Mark the start of the
technical detail with a divider.

**Put each note on method or provenance in a footnote.** (R13-order, R13-footnotes) This covers file
names, the time zone, the method, the sampling and the source of each reading. Put such a note in
the footnotes at the end of the page. Never put the note at the top, or in small print under a table
or a chart.

**Put numbers in a table or a chart, and keep ranges out of paragraphs.** (R13-tables) A new result
on a question already on the page goes into the table for that question. Write one conclusion for
the table. Rainfall against late arrivals goes into the AUC table, and stays out of the prose under
the table.

**Show the data on one question once.** (R13-one-view) When the data on one question is in two
charts or tables, merge the two into one. When a table duplicates the data of a chart, move each
value of the table that isn't on the chart onto the chart as a label, then delete the table. The
table of late trips on a page about a bus route had the times, delays and rainfall of the daily
chart. Only the driver changes and the detours were new, so the rewrite has those events as labels
on the chart.

**Use bullets for a run of separate statements.** (R13-bullets) Give each glossary entry a line.

**State a fact once, then refer back to the fact.** (R13-once) Before you publish, delete repeated
sections, a subhead with the words of the heading above the subhead (`Now: rented vans` over `vans
on a rental contract`), and instructions with the content of the section headings.

**A summary is an executive summary, and is shorter than a copy of the page.** (R13-summary) In a
section such as `In short` or `Summary`, give the conclusion, the status of the conclusion, and the
decision or the next step, in about three lines or bullets. Leave out the data recap, the list of
findings, and each number other than the number behind the conclusion. After the summary alone, a
reader knows the next action. The evidence stays in the sections. Five paragraphs of `In short` on a
three-page brief is a digest.

**Sort the unanswered questions into solved and unsolved.** (R13-questions)

**Give times in the time zone of the readers, with the zone labelled once.** (R13-time-zone) Convert
UTC log times before they reach the page.

## Titles and headings

**Name a page with the name the team uses for the subject, in two to five words.** (R13-title-name)
`Route 12 Delays`, `Oven Logs`, `Supplier Onboarding`. `What the delay information shows` is a
clause. Put the finding in the first sentence, and the name of the subject in the title.

**Give a page, a section or a card one title.** (R14-one-title) `Bus network · Route audit · v2` over `Route 12
delays` → `Route 12 delays`. Put `v2` in the first sentence.

**When an item has a short name, use the name in each place, and leave out a letter or a code for the item.**
(R14-name-not-letter) `cause B` → `late starts`. Leave a numbered name such as `Bake 2` on a run of a test plan
(R13-test-plan).

**A title or a heading is a noun phrase, with no clause.** (R13-heading-noun, R12-topic-heading)
- `How the queue jams` → `Queue jams`
- `Why the bread sank` → `Collapse cause`
- `What starts a delay` → `Delay triggers`
- `Who calls whom` → `Call paths`

A reduced relative clause counts as a clause: `Rules the drivers follow` → `Driver rules`.

**Name a topic in a heading, and put the finding under the heading.** (R13-heading-topic)
- `Route 12 runs late on Mondays because of the market` → `Monday market delays`
- `Buses run late without traffic` → `Delay without traffic`

Put the finding in the first sentence under the heading, where the finding has room for a status and
a number.

**Write a topic as a heading, and the answer to a question in the first sentence.**
(R13-heading-question) `Is the new route affordable?` → `Cost`.

**Name the subject of the section, and leave out the writer's work on the subject.**
(R13-heading-subject) Leave out each word for reading, finding, checking or collecting data. The
reader assumes the writer read the data.
- `Every ticket checked` → `Ticket records`
- `Every complaint read so far` → `Complaints`
- `The night bus` → `Night bus`

Drop a leading `The` that a reader doesn't need, and sweep words such as `Every`, `All` and
`Everything`.

**Start a dated heading with the date.** (R13-heading-date) `05-02 detour on Main Street`, `Council
reply of 05-09`.

**Use the words a reader types to find the page later.** (R13-heading-search) `what we
found` → `route delays`.

**Don't repeat the parent heading, or the first line under the heading.** (R13-heading-repeat)

## Register

An LLM tends to write marketing copy in technical documentation. A writer who knows the reader can
still write marketing copy. Apply **Reader** and **Scope** to choose the content of the page, and
these rules to choose the wording.

**Report the facts, and leave the persuasion out.** (R13-report) Replace an evaluative word with the
measurement or the fact behind the word, or remove the word.
- `fast` → `arrives within 2 minutes of the timetable`
- `robust` → the failure that the code handles

**Leave out promotional words.** (R13-promo-words) seamless, robust, powerful, cutting-edge,
state-of-the-art, leverages, unlocks, empowers, ensures, effortless, game-changing, world-class,
best-in-class.

**Leave out intensifiers and importance labels.** (R13-importance) critical, key, crucial,
significant, extremely, truly, highly. Give the reason in place of the label: `a critical check` →
`a check that stops the order`. A word in the domain's sense stays, such as an API key, a critical
section, or a statistically significant result.

**Leave out tagline headings.** (R13-tagline) `Built for speed`, `Why it matters`.

**Say what a mechanism does, and leave out the benefit to the reader.** (R13-mechanism)

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

## Terms

Acronyms of the reader's field are usually fine. The fault is a term with several meanings, or a
term packed with information absent from the word, as if the writer made up jargon for the task. A
reader stops to ask `Both what?`, `What is the second check?`, `which boxes?` or `what is replay
mode?`.

**Don't coin a term.** (R13-no-coined) Use the name in the system, the name in the field, or a plain
description. Coin a term only when the thing doesn't have a name and the term recurs on the page,
and define the term in one sentence at first use.
- `Late rule` → `Lateness threshold`
- `Ways around the queue` → `Queue exceptions`
- `The two forms` → `Refund request form`

**Give each term one meaning on the page.** (R13-one-meaning) Don't use one word for two things on
one page, such as `late` for a bus behind the timetable and for the rule of counting first delays.
Don't use two words for one thing (**Reader**).

**Write out a method or a condition in place of a packed modifier.** (R13-packed-modifier) `flagged
trip`, `clean week` and `first-delay AUC` each stand for a procedure, and `clean week` sounds like a
judgement. Write the procedure out, such as `the trip on the first Monday with a detour`, or use a
plain name with a definition.

**A capitalized or quoted label is a coined term**, unless the label is a product, a proper noun or
a defined term. (R13-capitalized-label) A made-up `Delay Window` or a word in scare quotes gets the
treatment of a coined term.

**Name the members of a group again when the members are more than a sentence away.**
(R13-group-label) `the two forms`, `both`, `the boxes`, `these cases`.

**Rewrite a phrase that a reader has to ask about.** (R13-ask-about) `a big order` (how big?), `at
full speed` (of what?), `correct with one cutoff` (which cutoff?), `a small depot van`.

**Gloss a statistic at first use, unless the target audience uses the statistic in their work.**
(R13-gloss-statistic) This covers AUC, p, r and a confidence interval. Judge by the people who read
the page, and leave the job title aside. Write the gloss as an ordinary sentence on what the number
means for the question of the page. Leave out a textbook definition. For example, `With an AUC of
0.9, one rainfall threshold puts the late trip above the trip on time in 90% of pairs.` A page for
several audiences gets the gloss. When you don't know whether the readers use the statistic, ask the
user.

**Use a technical word in the exact sense of the word.** (R13-exact-sense) A moving average doesn't
remove a trend.

## Charts

**A chart stands alone.** (R13-chart-standalone, R13-chart-frame) Give each chart a title, a label
with units on each axis, and a legend inside the chart. Define the marks in the legend, and keep the
caption free of mark definitions. A reader can forward a chart alone, so a label doesn't have `as
before`, `current` or `previous candidate`.

**Draw gridlines.** (R13-gridlines) Draw gridlines on each chart at the ticks of each axis. Draw the
gridlines in a light colour behind the data. When a chart doesn't have gridlines, a reader can't
read a value off a point or a line.

**Title a chart with the quantities and the events plotted, exactly.** (R13-chart-title,
R13-title-window) `Delay vs. rainfall`. Name which events and which time window the chart covers.
`Bus delays before a breakdown` → `Bus delays around the 5 breakdowns on route 12`. When the title
has `a`, the reader can't tell one breakdown from each breakdown, and `before` is wrong for a window
on both sides of each breakdown. Use the subtitle for the scale only, such as `log scale`. Keep
legend labels short, with a qualifier in parentheses, such as `05-14 detour (planned)`.

**Label the axes in physical units.** (R13-chart-units) `GPS field 7` → `Minutes late`.

**Pool the readings of all collections into one series.** (R13-pool) Make a series of each thing the
reader compares, such as route 12 against route 40, or weekdays against weekends. Never make a
series of how or when a reading was taken, such as GPS reads against driver reports, or the March
export against the April export. Put the source of each reading in a footnote. When a chart had a
series for the March export, the reader learned from the dots of that series only that the reads
came from another export.

**Style an HTML page in one dark theme, unless the user asks for a light theme.** (R14-dark-only) Leave out the light
colours and the `prefers-color-scheme` rules, and check the contrast of each colour against the dark background only.

**Highlight the syntax of each code block on an HTML page.** (R14-code-highlight) Name the language of each block,
such as `class="language-java"`, load highlight.js 11.9.0 from cdnjs, and paste `${CLAUDE_SKILL_DIR}/a11y-dark.css`
into the `<style>` of the page. Each colour of the `a11y-dark` theme has a contrast of at least 7:1 on the theme's
background.

**Keep the standard colour of a value, such as green for added lines and red for removed lines of a diff.**
(R14-standard-colour) GitHub and `git diff` show added lines in green and removed lines in red, so a reader expects
those colours on a count of changed lines. Write `+363 −67` with `+363` in green and `−67` in red. A failed test in
red and a passed test in green follow the same rule.

**Give each item of a set one colour, and use that colour for the item in the cards, the tables and the charts of the
page.** (R14-item-colour) Four causes of late buses get four colours, and `late starts` has one colour on the card,
the table and the chart.

**Give each data series a colour of the series' own.** (R13-series-colour) Keep the colour of each
series far in hue from the colour of each other series on the page. Next to red breakdown markers, a
reader takes an orange delay line for part of the same series. A colour for a status, such as red
for an error, can repeat across the page.

**Keep the marks readable.** (R13-chart-marks) Draw each mark clear of the other marks. Use one size
scale across the series. Draw each mark at one size, whatever the number of readings at the mark.
When large dots for busy stops sat over small squares for quiet stops, a correct average looked
wrong. For a summary line, give the reason for the mean over the median.

**Leave out a label for a feature that the chart shows plainly**, such as `where a threshold would
lie`. (R13-chart-obvious) Delete a bare date such as `the 3rd` on a chart. The reader can't tell
which event happened on the date. (R13-annotation)

**Draw an uncertain interval as a shaded region.** (R13-chart-interval) The first day of the new
timetable lies somewhere between the 8th and the 12th, so shade the span on the chart. A reader
takes a line at one date for a known date.

**Drop points that don't bear on the question.** (R13-chart-points) Trips cancelled before departure
come off the delay chart.

**Chart each relevant variable, and include the reference series for a comparison.**
(R13-chart-variables) Chart the delay of each route, and don't chart the busiest route alone. In a
chart of a test or a change, plot the readings from before the test or the change too, so the reader
sees the change against the earlier readings. (R13-before)

**Add new data to each chart on the question.** (R13-update-all) When new data arrives on a
question, add the data to each chart and table on the question, and update the date range in each
title. A reader takes a chart with an older date range for a stale chart.

## Diagrams

**Draw an arrow for a message or a flow only.** (R13-arrow) Write a state or a condition as a note.
An arrow labelled `no orders while the shop is closed` → a note `The till can't take an order while
the shop is closed`.

**Make the sender and the receiver of each arrow clear.** (R13-arrow-owner) Give each receiver
column a colour, repeat the header in a long sequence diagram, and draw the head office as a central
hub in place of long crossing arrows.

**Give a legend for each colour and box shape.** (R13-legend) A reader asked `what do the boxes
mean?` and `why are some arrows dashed?`.

**Draw each path that the argument depends on.** (R13-paths) Draw the path to the archive for the
order files, prices.csv and stock.csv, or a reader can't tell which step writes each file.

**Split or delete a catch-all node**, such as `kitchen, tills, delivery`. (R13-catch-all)

**Draw separate charts for steps with different people, and draw a loop as a loop.**
(R13-split-flow) The order request (shop to warehouse) and the restock request (warehouse to
supplier) get two charts. Pack, check and re-pack is a loop, and a chart of three boxes in a line
doesn't show the loop.

## Tables

**Keep column headers short.** (R13-header) Remove each word of a column header that the reader gets
from the neighbouring column. When the column on the left has the breakdowns, `Cause of the
breakdown` → `Cause`. Put a method detail in a footnote, such as the 5 minutes of grace after the
timetable time before a bus counts as late.

**Align the header of a numeric column with the numbers.** (R13-header-align) Right-align both, and
left-align a text column and the text column's header.

## Verify a page

**Check the whole page in each turn with a change to the page.** (R13-whole-page) Run `verify.py` on
the whole page without `--since`, and apply the rules of this skill to the whole page once, after
the batch of edits. A reader reads the whole page, and the whole page has to read well. Only the
wording checks and `agentverbs.py` run on a page, and a Python project's config isn't needed.

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" docs/report.html --no-fix
```

For a cleanup, add `--cleanup`. The last review list of the run is the section list. Give each entry of the section
list the reader's action.

A path of `-` is a page read from stdin, such as a draft that is not in a file yet. Take **Prose
review** of `nar:core` on the lists of the run, and handle each finding by **A finding is
information**.

**Look at the page in a browser after a change to the style of a table or a chart**, before you
publish. (R13-look) A cell style can break the columns of a table.

`verify.py` doesn't check the rules of this skill yet. After the prose review, read the page against
this checklist, one item at a time, and fix each failure.

1. The title is two to five words, a noun phrase, without a clause, a question, a finding or a
   process word.
   Each heading follows the same rule.
2. The page doesn't have a promotional word, an intensifier, a tagline heading, a strawman, a
   question setup, a label and colon in running prose, a kicker, a signpost, a fragment run, an
   exclamation mark, before and after framing, or two titles for one item.
3. Each term is the system's name, the field's name or a plain description. A coined term recurs on
   the page and has a definition at first use. Each term has one meaning on the page.
4. The summary, if the page has one, is about three lines with the conclusion, the status and the
   next step.
5. The page doesn't refer to material off the page or to the session.
6. Each section, paragraph, table, chart and table row has a use for the reader. A paragraph doesn't
   have the values of a chart or a table in words, and the data of one question is in one chart or
   table.
7. Each note on method or provenance is in a footnote.
8. Each chart passes **Charts**, and has these parts:
   - a title
   - axis labels with units
   - a legend inside the chart
   - gridlines
   - a colour for each series
   - one mark size
   - the latest data

   Each diagram passes **Diagrams**, and each table passes **Tables**.
9. For a cleanup, the report has the `keep`, `move` or `cut` label of each section, and the share of the page that
   you cut or moved.
