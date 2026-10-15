# Task P13 — recurring event expansion

Expand the recurring events of an iCalendar file into the concrete occurrences that start inside a
time window, in UTC and in local time, and report every event that could not be expanded. Use the
standard library only; `pendulum` may be used, but no iCalendar or recurrence-rule library.

## Inputs

- The calendar file, the first argument: UTF-8, lines ending in CRLF or LF. A line that starts with
  a space or tab continues the line before it: first remove the line break and that one character.
  A content line is `NAME;PARAM=VALUE;...:VALUE`; names are case-insensitive, a parameter value may
  be in double quotes (removed), and the first `:` outside double quotes ends the parameters.
- `--start INSTANT`, `--end INSTANT`: ISO 8601 with a UTC offset. An occurrence is in the window
  when it starts at or after `--start` and before `--end`. `--out PATH`: the JSON output file.

The file starts with `BEGIN:VCALENDAR`. Only `VEVENT` components are read; any other, `VTIMEZONE`
included, is skipped whole. `TZID` values are IANA zone names. Only these event properties count:

- `UID`, mandatory. `SUMMARY`, optional; `\\`, `\,`, `\;` and `\n` or `\N` are unescaped.
- `DTSTART`, mandatory: `DTSTART;TZID=Europe/Berlin:20270131T170000` (local time in that zone) or
  `DTSTART:20270320T230000Z` (UTC; its zone for output is `UTC`). Any other form is `bad DTSTART`.
- `RRULE`, optional, parts separated by `;`: `FREQ` (`DAILY`, `WEEKLY` or `MONTHLY`), `INTERVAL`
  (positive, default 1), `COUNT`, `UNTIL` (UTC only, `20270413T000000Z`), `BYDAY` (`MO`..`SU`,
  comma-separated; under `MONTHLY` an item may carry an ordinal, `2TU` or `-1FR`), `BYMONTHDAY`
  (`MONTHLY` only; comma-separated, 1 to 31 or -31 to -1). Any other part or value, `COUNT` with
  `UNTIL`, or `BYDAY` with `BYMONTHDAY`, is an `unsupported rule`.
- `EXDATE`, zero or more, each with comma-separated values in a `DTSTART` form, in any zone.
- `RECURRENCE-ID`, in the `DTSTART` forms: the event is an **override** of one occurrence of the
  **master**, the event with the same `UID` and no `RECURRENCE-ID`.

## What it does

1. Read the events. Reject, first match wins: no `UID` or `DTSTART` as `missing property`; a `TZID`
   that is not an IANA zone, in any property, as `unknown time zone`; then `bad DTSTART`, then
   `unsupported rule`; a second master with a `UID` already used as `duplicate UID`.
2. Expand each master in wall-clock time in its `DTSTART` zone, at the `DTSTART` time of day.
   - `DAILY`: every `INTERVAL`th day from the `DTSTART` date; `BYDAY` keeps only those weekdays.
   - `WEEKLY`: weeks run Monday to Sunday. Every `INTERVAL`th week from the one holding `DTSTART`,
     on each `BYDAY` weekday, or on the `DTSTART` weekday without `BYDAY`.
   - `MONTHLY`: every `INTERVAL`th month from the `DTSTART` month. `BYMONTHDAY` lists days of the
     month, -1 being the last. `BYDAY` gives every such weekday, or with an ordinal the nth such
     weekday of the month, counted from the end when negative. Without either, the `DTSTART` day.
     A day the month does not have (31 in April, `5MO` with four Mondays) is skipped.
   - Days before `DTSTART` are skipped. `DTSTART` is the first occurrence even if the rule omits it,
     and the only one without `RRULE`.
3. Turn each local time, local `EXDATE` and `RECURRENCE-ID` values included, into an instant. A time
   that does not exist (the clock jumps forward) takes the offset in force before the jump, so 02:30
   becomes 03:30 in the new offset. A time that occurs twice (the clock goes back) is the first one.
4. `COUNT` keeps the first N occurrences; `UNTIL` keeps those at or before its instant. Both apply
   before `EXDATE`, so an excluded occurrence still counts toward `COUNT`.
5. Remove each occurrence whose instant equals an `EXDATE` instant. An override then replaces the
   occurrence at its `RECURRENCE-ID` instant: the start becomes the override's `DTSTART`, in its
   zone, and its `SUMMARY`, if any, replaces the master's. An override with no accepted master, or
   whose `RECURRENCE-ID` matches no remaining occurrence, is rejected as `orphan override`.
6. Keep the occurrences whose final start is in the window, and write the outputs.

## The outputs

The `--out` file, written with `json.dumps(result, indent=2, ensure_ascii=False) + '\n'`, keys in
this order:

```json
{
  "calendar": "fixture/team.ics",
  "window": {"start": "2027-03-01T00:00:00Z", "end": "2027-05-01T00:00:00Z"},
  "occurrences": [
    {"uid": "crit@kestrel.test", "summary": "Design crit (moved)",
     "start_utc": "2027-04-16T09:00:00Z", "start_local": "2027-04-16T11:00:00+02:00",
     "timezone": "Europe/Berlin", "moved_from_utc": "2027-04-15T12:00:00Z"}
  ],
  "rejected": [{"line": 47, "uid": "anniversary@kestrel.test", "reason": "unsupported rule"}]
}
```

These entries show the shape only. UTC instants (`start_utc`, `moved_from_utc`, the window) are
`YYYY-MM-DDTHH:MM:SSZ`; `start_local` is the instant in `timezone`, offset as `+HH:MM`.
`moved_from_utc` is the replaced instant for an override, else `null`; `summary` is `""` when none
applies. `line` is the 1-based number of the `BEGIN:VEVENT` line in the file as stored; a missing
`uid` is `null`. `occurrences` is sorted by `start_utc`, then `uid`; `rejected` by `line`;
`calendar` is the argument as typed.

A summary table on stdout: one row per occurrence, then the rejected events. Exit codes: 0 when
nothing is rejected, 1 when at least one event is rejected, 2 when the run could not start (missing
or unreadable file, no `BEGIN:VCALENDAR`, an instant without an offset, `--end` not after
`--start`).

The expansion must also be importable: another program calls one function with the calendar path
and the two instants, and gets the occurrences and rejected events back without writing any file.

## What is left to you

Package and table layout, how far an endless rule is expanded, logging, and anything not fixed here.

## The fixture

`fixture/team.ics`, run with `--start 2027-03-01T00:00:00Z --end 2027-05-01T00:00:00Z`. Its cases: a
daily event at 02:30 New York time across the 2027-03-14 jump forward, with `COUNT` and `EXDATE`; a
two-weekly event at 02:30 Sydney time on 2027-04-04, when the clock goes back; `BYMONTHDAY=31`;
`-1FR` with an `EXDATE` in another zone; `2TU` with a UTC `UNTIL`; overrides that move one
occurrence within and one out of the window; a UTC `DTSTART`; folded lines, one with a tab; a
`VTIMEZONE` block; three events to reject.