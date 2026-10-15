# Task P11 — access log analyser

Count a web server's requests per local hour from its rotated access logs, with status classes, size
percentiles and the most requested paths, and report every line that could not be read.

## Inputs

Run as `python3 -m <package> LOG_DIR --config PATH [--out PATH]`. Use the standard library only.

- `LOG_DIR` holds the log files, named `access.log`, `access.log.N` or `access.log.N.gz`, where `N`
  is a positive integer without leading zeros; a `.gz` file is gzip compressed. Other files are
  ignored. Rotated files can overlap: the end of one file can be repeated at the start of the next.
- `--config PATH`, a JSON file: `{"timezone": "Europe/Berlin", "top_paths": 3}`. Both keys are
  mandatory. `timezone` is an IANA zone name; `top_paths` is a positive integer.
- `--out PATH`, the report file, default `report.json` in the current directory.

A log file holds bytes, not text. A line is the bytes up to each `\n`, with a trailing `\r` removed;
the empty piece after the final `\n` is not a line. Lines are numbered from 1 in each file, in the
decompressed content. Lines are in the combined log format, each time with its own UTC offset:

```
192.0.2.10 - - [24/Oct/2026:22:40:05 +0000] "GET /index.html?x=1 HTTP/1.1" 200 5120 "-" "Mozilla/5.0"
```

## What it does

1. Read every log file. Each check below states what a valid line meets; a line that fails one is
   **malformed**, and its problem is the name of the first check it fails:
   - `syntax`: the line's bytes match, with `re.fullmatch`, the bytes pattern
     `(\S+) (\S+) (\S+) \[([^\]]*)\] "([^"]*)" ([1-5][0-9][0-9]) ([0-9]+|-) "([^"]*)" "([^"]*)"`.
     The groups are host, ident, user, time, request, status, size, referer, user agent. The referer
     and user agent can hold any bytes, including bytes that are not UTF-8; they are not checked.
   - `bad time`: the time is `DD/Mon/YYYY:HH:MM:SS +HHMM` (or `-HHMM`), with `Mon` one of the English
     abbreviations `Jan` to `Dec`, and is a real date and time.
   - `bad request`: the request splits on single spaces into exactly three parts: a method of
     uppercase ASCII letters, a target, and a protocol `HTTP/D.D` with `D` a digit.
   - `bad path`: the target starts with `/` and holds only bytes 0x21 to 0x7E. The **path** is the
     target before its first `?`. Each `%` in the path is followed by two hex digits, in either case;
     the path is decoded by replacing each `%XX` with the byte it names, and the decoded bytes are
     valid UTF-8. No other change is made to the path.
2. Overlapping files repeat lines, and a server can log two identical requests in the same second.
   Valid lines with equal bytes are identical; such a line counts as many requests as the most times
   it occurs in any one file, and its other occurrences are **duplicates**. Malformed lines never are.
3. Each request belongs to the local hour, in the configured zone, that contains its instant. When
   daylight saving time ends, each copy of the repeated hour is a separate hour with its own offset.
4. Per hour: the number of requests; the number per status class (`1xx` to `5xx`, from the first
   digit of the status); and the 50th and 95th percentiles of the response sizes. A size of `-`
   means no body was sent: the request counts, but takes no part in the percentiles. The `p`th
   percentile of `n` sizes sorted ascending is the size at 1-based rank `ceil(p × n / 100)`, computed
   exactly (nearest rank, no interpolation). With no sizes in the hour, a percentile is `null`.
5. Across all requests, the `top_paths` paths with the most requests, by count descending, then by
   path in code point order.

## The outputs

The report, written to `--out` with `json.dumps(report, indent=2, ensure_ascii=False) + '\n'`, keys
in this order:

```json
{
  "timezone": "Europe/Berlin",
  "files": ["access.log", "access.log.1"],
  "hours": [
    {"hour": "2026-03-29T03:00:00+02:00", "requests": 7,
     "status": {"1xx": 0, "2xx": 5, "3xx": 0, "4xx": 2, "5xx": 0},
     "size_p50": 810, "size_p95": 4096}
  ],
  "top_paths": [{"path": "/über-uns", "requests": 12}],
  "malformed": [{"file": "access.log.1", "line": 14, "problem": "bad path"}],
  "totals": {"lines": 120, "requests": 101, "duplicates": 6, "malformed": 13}
}
```

The values above are an example of the shape only. `files` lists the log files read, sorted by name.
`hours` holds only hours with at least one request, sorted by instant; `hour` is the local start of
the hour in ISO 8601 with its offset, and `status` always has all five keys. `malformed` is sorted
by `file`, then `line`, and `problem` is `syntax`, `bad time`, `bad request` or `bad path`.
`totals.lines` counts every line read, so it equals `requests + duplicates + malformed`. A summary
table on stdout: one row per hour, then the top paths and the totals.

Exit codes: 0 when no line is malformed, 1 when at least one is, 2 when the run could not start
(missing log directory, unreadable or malformed config, unknown time zone, a log file that cannot
be read or decompressed). A directory with no log files gives a report with empty lists, exit 0.

The analysis must also be importable: another program calls one function with the log directory and
the config path, and gets the report back as a dict shaped like the JSON above, writing no file.

## What is left to you

The package and module layout, the table layout, error messages, logging, and any behaviour this
specification does not fix.

## The fixture

`fixture/` has `config.json` and `logs/` with `access.log`, `access.log.1`, `access.log.2.gz` and
`error.log`. Its cases: offsets `-0400`, `+0000`, `+0200` and `+0530` in one local hour, the repeated
hour on the night of 2026-10-25, one path written three ways with escapes and a query string, a
request line with a space in its target, an invalid escape, an escape that is not UTF-8, `-` sizes,
lines repeated across rotated files, two identical requests in one file, a gzip file, a user agent
that is not UTF-8, a German month name and a file that is not a log.
