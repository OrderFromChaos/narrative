---
name: proposal
description: Write or review a proposal in the Narrative house style: a page that recommends a course of action to a decision-maker, such as a refund policy for a finance director. Suggestions, not decisions or prohibitions, no mechanism the rule works without, schedules as guidelines, a weaknesses section, and an order by the reader's role. Loads nar:page and nar:core.
---
**Before you write or review the page, load the skills `nar:core` and `nar:page` with the Skill
tool**, unless they are loaded already. `nar:core` has the sentence rules, and `nar:page` has the
rules for each page. This skill adds the rules for one kind of page.

# Narrative: proposals

A proposal is a page with a recommendation to a decision-maker, such as a refund policy for a
finance director. The decision-maker may adopt the page as a written procedure, and an auditor
checks the team against a written procedure.

**Write suggestions, and leave the decisions and the prohibitions to the reader.** (R13-suggestions)
The decision-maker decides, so write the page as a recommendation. Leave out negotiation tactics and
fallback positions, such as a section on what to do `if a second manager must sign each refund`.

**Describe a practice in use today, and don't prohibit the practice.** (R13-describe-practice) A
rule such as `Don't let the refund limit depend only on the customer tier in the CRM` contradicts a
process where the limit does depend on that field.

**State the rule, and leave out a mechanism the rule works without.** (R13-no-mechanism) Each
mechanism on the page is one more step to follow each time. Leave out a second signature on each
refund, a form version on each request, and a fixed deadline without a reason. Offer a mechanism as
an option in the conversation, and keep the mechanism off the page.

**Word a fixed schedule as a guideline.** (R13-schedule-guideline) A missed interval then isn't a
departure from the procedure. `Review refunds about monthly`, so a holiday doesn't break the
procedure.

**Add a weaknesses section.** (R13-weaknesses) Compare the approach with the alternatives the reader
is looking at, such as the refund features of the shop's payment provider, so the reader sees the
trade-offs.

**Order the page by the reader's role.** (R13-proposal-order) For a finance reader, put the steps,
the forms and the legal basis first, and the technical detail last, after a divider.

## Verify the page

For a cleanup, take steps 1 to 4 of **To clean up a page** in `nar:page` before you run `verify.py`.

Run the `verify.py` of `nar:page` on the page, with the command under **Verify a page** in
`nar:page`. The folder of this skill doesn't have a `verify.py`. Take **Prose review** of `nar:core`
on the lists of the run. Then read the page against the checklist of `nar:page`, and against each
rule of this skill, one rule at a time.
