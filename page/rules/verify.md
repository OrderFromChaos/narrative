## Verify a page

**Check the whole page in each turn with a change to the page.** (R13-whole-page) Run `verify.py` on
the whole page without `--since`, and apply the rules of this skill to the whole page once, after
the batch of edits. A reader reads the whole page, and the whole page has to read well. Only the
wording checks and `agentverbs.py` run on a page, and a Python project's config isn't needed.

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" docs/report.html --no-fix
```

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
   exclamation mark, or before and after framing.
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
