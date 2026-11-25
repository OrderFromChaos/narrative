# Changelog

## 2.1.0 (2026-09-21)

- The board syncs with the duty system every 30 seconds. The sync ran every 2 minutes before.
- The export has a `late_reason` column.

## 2.0.0 (2026-04-13)

- A licence that expires within 14 days shows an amber badge on the driver's card.
- The export uses ISO 8601 times with the offset, such as `2026-04-13T05:40:00+01:00`. Earlier exports had local times
  without an offset.
- Swaps need a reason code.

## 1.2.0 (2025-10-06)

- The departure reminder fires 5 minutes before the duty starts. It fired 10 minutes early before, because of a time
  zone bug.
- The export has a `duty_split` column for split shifts.

## 1.1.0 (2025-06-16)

- The export has a `route_variant` column, such as `12A`.
- Sick calls log the caller and the time of the call.

## 1.0.0 (2025-03-03)

- First release: the board, morning assignment, swaps, the licence check on each assignment, the CSV export, and the
  board refresh every 2 minutes without a reload.
