# Task P16 — GPX activity statistics

Read a directory of GPS track exports, compute distance, moving time, elevation gain and the fastest
kilometre for each activity, and keep a record of the activities in a database. Run as
`python3 -m <package> INPUT_DIR [--settings PATH] [--out DIR]`. Use the standard library only.

## Inputs

- `*.gpx` files in `INPUT_DIR`, read in basename order; other files are ignored. One file is one
  activity. A file must be GPX 1.1: its root element is `gpx` in the namespace
  `http://www.topografix.com/GPX/1/1`. Its `trkpt` elements are under `trk/trkseg`, a `trk` may hold
  several `trkseg`, and a file may hold several `trk`; all segments are taken in document order. A
  `trkpt` has attributes `lat` and `lon` in decimal degrees (`-90..90`, `-180..180`), an optional
  `ele` child in metres and an optional `time` child of the form `2026-06-14T22:40:00Z` (UTC, whole
  seconds). Other elements, including `metadata/time`, are not points and are ignored.
- A settings file, `settings.json` in `INPUT_DIR` unless `--settings` names another path:
  `{"timezone": "Europe/Oslo"}`. `timezone` is mandatory and is an IANA zone name. A missing
  input directory, or a settings file that is unreadable, malformed or has an unknown zone, stops the
  run with exit code 2.

## What it does

1. A file whose root is not the GPX 1.1 `gpx` element (a GPX 1.0 file included) is a problem
   `unsupported version`. A file that is not well-formed XML, or has a `trkpt` with a missing or
   out-of-range `lat`/`lon`, a `time` not in the form above, or an `ele` that is not a number, is a
   problem `malformed`. A problem file is not an activity.
2. Within each segment, in document order, a point is **dropped** when it has no `time`, or when its
   time is not later than the time of the previous kept point in the same segment (a repeated fix).
   A file with fewer than two kept points is a problem `too few points`.
3. **Distance** is the sum, within each segment, of the distances between consecutive kept points.
   Nothing is added between the last point of one segment and the first point of the next. The
   distance between two points is the haversine distance with Earth radius R = 6371008.8 m:
   `a = sin²(Δφ/2) + cos φ1 · cos φ2 · sin²(Δλ/2)`, `d = 2R · asin(√a)`, with φ the latitude and λ
   the longitude in radians.
4. **Time.** `elapsed_s` is the time from the first kept point to the last. An interval between
   consecutive kept points of one segment is **moving** when its distance is at least 0.5 m per
   second of its duration (`d >= 0.5 * dt`). `moving_s` is the sum of the moving intervals.
   `stopped_s` is `elapsed_s - moving_s`, so it holds the stopped intervals and every gap between
   segments.
5. **Elevation gain** uses every kept point that has an `ele`, in order, across segments, with a
   hysteresis of H = 5.0 m. Start with `ref` = the first elevation, `climbing` = false, gain 0. For
   each next elevation `e`: if `e > ref` and (`climbing` or `e - ref >= H`), add `e - ref` to the
   gain, set `ref = e`, `climbing` = true; if `e < ref` and (not `climbing` or `ref - e >= H`), set
   `ref = e`, `climbing` = false; otherwise change nothing.
6. **Fastest kilometre.** Lay the kept points end to end with their cumulative distance (which does
   not grow across a segment gap) and their time. For each whole kilometre k = 1, 2, ... up to the
   total distance, the time at which the cumulative distance first reaches k × 1000 m is linearly
   interpolated within the interval where it is reached; the time at 0 m is the first point's time.
   Split k is the time at k km minus the time at k − 1 km. The fastest split is the smallest, the
   lowest k on a tie. An activity shorter than 1000 m has none.
7. The start is the first kept point's time. `start_local_date` is its date in the settings zone.
8. Write the report below, and store each activity in a SQLite table keyed by `start_utc`. Running
   again over the same inputs adds no rows; a changed file updates its activity's row.

## The outputs

`activities.json` in `--out` (default: the current directory), written with
`json.dumps(report, indent=2, ensure_ascii=False) + '\n'`, keys in this order:

```json
{
  "generated_at": "2026-06-21T08:00:00+00:00",
  "input_dir": "fixture",
  "timezone": "Europe/Oslo",
  "activities": [
    {"file": "lakeside.gpx", "start_utc": "2026-06-01T05:10:00Z", "start_local_date": "2026-06-01",
     "distance_m": 5230.4, "elapsed_s": 1900, "moving_s": 1720, "stopped_s": 180,
     "elevation_gain_m": 41.5, "fastest_km": {"km": 3, "seconds": 301.7},
     "points_used": 190, "points_dropped": 1}
  ],
  "problems": [{"file": "broken.gpx", "problem": "malformed"}],
  "totals": {"activities": 1, "distance_m": 5230.4, "moving_s": 1720, "problems": 1}
}
```

The numbers above are an example of the shape only. `activities` is sorted by `start_utc`,
`problems` by `file`. `distance_m`, `elevation_gain_m` and `seconds` are rounded with
`round(x, 1)`; the three `_s` times are integers. `fastest_km` is `null` when there is none. The
totals' `distance_m` is the sum of the reported distances, rounded with `round(x, 1)`. `input_dir`
is the argument as typed.

A summary on stdout: one line per activity, then the problems and the totals. Exit codes: 0 when
there are no problems, 1 when there is at least one problem, 2 when the run could not start.

The statistics must also be importable: another program calls one function with the input directory
and an optional settings path, and gets the activities and problems back without any file or
database being written.

## What is left to you

The package and module layout, the database schema and location, the summary layout, logging, and
any behaviour this specification does not fix.

## The fixture

`fixture/` has three GPX files, `settings.json` and a text file. Its cases: a run that starts just
after local midnight with a recording pause between two segments, a point without a time, a repeated
fix, a short stop, elevation noise, a metadata time that is not the start, a hike that crosses the
180° meridian with one point missing its elevation, and a GPX 1.0 export.
