# Depot Board

Depot Board is the dispatch board of the Northgate bus depot. Dispatchers use it to assign a bus and a driver to each
duty of the day, to handle swaps and sick calls, and to see at a glance which duties are still open. The board checks
each driver's licence and each bus's daily check before it accepts an assignment.

## Why we built Depot Board

Before Depot Board, the depot ran on a whiteboard in the dispatch office and a shared spreadsheet. The whiteboard was
the real record, and the spreadsheet was typed up from a photo of the whiteboard at the end of each shift. Twice in
2024, a driver with an expired licence took a duty because nobody checked the spreadsheet against the licence list. The
operations manager asked for a tool that would make that impossible. We piloted a first version with the early shift in
the autumn of 2024, rewrote the assignment screen after the pilot, and moved the whole depot over in March 2025.

## Install

Depot Board runs on the depot server. Open `http://board.northgate.local` in Chrome or Edge on a dispatch PC, and sign
in with your depot account. The board doesn't run on the tablets in the yard.

### Server install

The board is a Docker Compose stack of three containers: `board-web`, `board-api` and `postgres`. Copy
`deploy/compose.yml` and `deploy/board.env.example` to `/srv/depot-board/` on the depot server, rename the env file to
`board.env`, and fill in `DUTY_SYSTEM_URL`, `DUTY_SYSTEM_TOKEN` and `LICENCE_FEED_URL`. Run
`docker compose up -d` in that folder. The API listens on port 8080 and the web container on port 80. Back up the
`pgdata` volume each night; the board doesn't back itself up.

## Morning assignment

1. At 04:30, open the board. The duties of the day are in the left column, sorted by start time.
2. Drag a bus from the **Buses** column onto each duty. A bus without a daily check shows a grey badge, and the board
   refuses it.
3. Drag a driver from the **Drivers** column onto each duty. The board refuses a driver whose licence has expired, and
   shows an amber badge on a licence that expires within 14 days.
4. When each duty has a bus and a driver, press **Publish**. The drivers get the duty on the driver app.

The current version syncs the duties with the duty system every 30 seconds, so a duty that the planners add at 04:45
shows up without a reload.

## Swaps and sick calls

To swap two drivers, drag one driver card onto the other. Since this version, a swap needs a reason code from the list:
`SICK`, `LATE`, `TRAINING`, `VEHICLE` or `OTHER`.

When a driver calls in sick, press **Sick call** on the driver's card, and enter the time of the call. The board frees
the driver's duties of the day, and shows them in red at the top of the left column. Sick calls from earlier versions
have no caller and no call time.

## Board colours

| Colour | Meaning | What to do |
|---|---|---|
| Green | Bus and driver assigned, published | Nothing |
| Blue | Bus and driver assigned, not published | Press **Publish** |
| Amber | Licence expires within 14 days | Tell the duty manager |
| Red | Duty without a driver, or a sick call | Assign a driver |
| Grey | Bus without a daily check | Ask the yard for the check sheet |

To sum up the table: green means the duty is ready and published, blue means it is ready but not published yet, amber
is a licence warning, red is an open duty or a sick call, and grey is a bus that hasn't had its daily check.

## What Depot Board records

| Area | Recorded |
|---|---|
| Assignments | Each bus and driver put on a duty or taken off, with the dispatcher and the time. |
| Publishing | Each press of **Publish**, with the duties published. |
| Swaps | Each swap, with both drivers, the reason code and the dispatcher. |
| Sick calls | Each sick call, with the caller, the time of the call and the duties freed. |
| Licence checks | Each refused driver, with the licence number and the expiry date. |
| Bus checks | Each refused bus, with the fleet number and the date of the last check. |
| Sync | Each sync with the duty system, with the count of duties added, changed and removed. |

## Export format

**Export → Day**, **Export → Week** and **Export → Month** write a CSV file with one row per duty. The columns are:

- `duty_id`: the id of the duty in the duty system, such as `N-0412`. The id is unique within a day, and the same id
  can come back on another day.
- `duty_date`: the date of the duty, as `YYYY-MM-DD`.
- `start`: the start time of the duty, in ISO 8601 with the offset, such as `2026-04-13T05:40:00+01:00`. Earlier
  versions wrote local times without an offset.
- `end`: the end time of the duty, in the same format as `start`.
- `route`: the route number, such as `12`.
- `route_variant`: the variant of the route, such as `12A`. Exports before this version have no `route_variant`
  column.
- `duty_split`: `true` for the first half of a split shift, and `false` otherwise. The second half has its own row.
- `fleet_no`: the fleet number of the bus, such as `3141`. Empty when no bus was assigned.
- `bus_check`: `passed`, `missing` or `failed`, from the daily check of the bus on that day.
- `driver_id`: the staff number of the driver. Empty when no driver was assigned.
- `licence_ok`: `true` when the licence was valid at the time of the assignment.
- `licence_expiry`: the expiry date of the licence, as `YYYY-MM-DD`.
- `assigned_by`: the depot account of the dispatcher who assigned the driver.
- `assigned_at`: the time of the assignment, in the same format as `start`.
- `published_at`: the time of the publish. Empty for a duty that was never published.
- `swap_reason`: the reason code of the last swap on the duty, or empty.
- `sick_call_at`: the time of the sick call that freed the duty, or empty.
- `late_reason`: the reason the duty started late, from the driver app, or empty.

The file is UTF-8 with a header row, a comma as the separator, and `\r\n` line ends. A field with a comma is in double
quotes. The export of a month with 3,000 duties is about 600 KB.

The API has the same data as JSON at `GET /api/v1/duties?from=YYYY-MM-DD&to=YYYY-MM-DD`, with the field names of the
CSV columns. The API needs a token from `board.env`, in the header `Authorization: Bearer <token>`. A request for more
than 31 days returns `400`.

## Timing

Each record has two times: the time on the depot server, and the time of the duty system at the last sync. The two
can differ by up to the sync interval. The board shows the depot server time.

## Known limits

- The board refuses a driver only on the licence. The board doesn't check working-time rules, so check the rest break
  of a driver who worked a late duty yesterday.
- A bus with a failed daily check is refused, but the yard can mark the check as passed after a repair, and the board
  then accepts the bus.
- In older builds, the departure reminder fired 10 minutes early.
- In older builds, the board refreshed only when a dispatcher pressed F5.
- `assigned_at` is the time of the drop on the board, not the time of the publish.
- `duty_split` rows share a `duty_id`, so count split shifts by `duty_id` and `duty_split = true`.
- A duty that the planners delete after the publish stays on the board in red until the next sync.
- The export of a week or a month takes up to a minute, and the board doesn't respond to other dispatchers while the
  export runs.

## FAQ

**How do I open the board?** Open `http://board.northgate.local` in Chrome or Edge, and sign in with your depot account.

**Can I swap two drivers?** Yes. Drag one driver card onto the other, and pick a reason code.

**What does amber mean?** The driver's licence expires within 14 days.

## Development

Depot Board is a TypeScript app: `web/` is the React front end and `api/` is the Node API. Run `npm ci` in each
folder, then `npm run dev` in `api/` and in `web/`. The dev API uses the fixture duties in `api/fixtures/` instead of
the duty system.

Run the tests with `npm test` in each folder. The API tests need a Postgres on port 5432; `docker compose -f
deploy/compose.test.yml up -d` starts one.

## Performance

Load test of the API on the depot server, 2026-08-04, median of 5 runs:

| Dispatchers | Duties | Drag to saved | Publish | Month export |
|---|---|---|---|---|
| 2 | 300 | 40 ms | 0.6 s | 9 s |
| 4 | 300 | 55 ms | 0.7 s | 11 s |
| 8 | 600 | 90 ms | 1.4 s | 38 s |
