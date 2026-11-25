# Audit

The operations auditor checks each month that the depot ran each scheduled duty with a licensed driver and a bus that
had passed the daily check.

## Monthly check

1. Export the month from the board: **Export → Month → CSV**.
2. Compare the `duty_id` column with the schedule of the month. Each scheduled duty has one row.
3. Filter the rows with `licence_ok = false`. Each such row needs a signed note from the duty manager.
4. Filter the rows with `bus_check = missing`. Each such row needs the paper check sheet of that bus and that day.

## Retention

The board keeps 24 months of assignments. Export each month before the 5th of the next month.
