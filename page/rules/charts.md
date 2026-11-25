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

