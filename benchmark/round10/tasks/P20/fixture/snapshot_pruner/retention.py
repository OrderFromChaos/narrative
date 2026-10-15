"""Apply the periodic rules of a retention policy to a set of snapshots.

Under a rule with a count of N, the newest snapshot of each of the N most recent periods that have a
snapshot is kept. Periods follow the local wall clock in the policy's timezone:

    hourly   (year, month, day, hour)
    daily    (year, month, day)
    weekly   (ISO year, ISO week)
    monthly  (year, month)

When an hour occurs twice at the end of daylight saving time, both copies are one hourly period. The
rules are independent of one another.
"""

from __future__ import annotations

from collections.abc import Sequence

from pendulum import DateTime

from snapshot_pruner.vocabulary import KeepCounts, Period, Policy, Snapshot


def computeKeepingPeriods(snapshots: Sequence[Snapshot], policy: Policy) -> dict[str, tuple[Period, ...]]:
    """Map each snapshot's file name to the periods it is kept under, in `Period` member order.

    Returns:
        An entry for every snapshot. The tuple is empty for a snapshot kept under no rule.
    """
    keeping_periods: dict[str, list[Period]] = {snapshot.file: [] for snapshot in snapshots}
    for period in Period:
        for snapshot in _selectNewestOfRecentPeriods(snapshots, policy, period):
            keeping_periods[snapshot.file].append(period)

    return {file: tuple(periods) for file, periods in keeping_periods.items()}


def _selectNewestOfRecentPeriods(snapshots: Sequence[Snapshot], policy: Policy, period: Period) -> list[Snapshot]:
    newest_by_period: dict[_PeriodKey, Snapshot] = {}
    for snapshot in snapshots:
        key = _computePeriodKey(snapshot.at.in_timezone(policy.timezone), period)
        incumbent = newest_by_period.get(key)
        if incumbent is None or snapshot.at > incumbent.at:
            newest_by_period[key] = snapshot

    recent_keys = sorted(newest_by_period, reverse=True)[: _countKeptPeriods(policy.keep, period)]
    return [newest_by_period[key] for key in recent_keys]


def _computePeriodKey(local: DateTime, period: Period) -> _PeriodKey:
    match period:
        case Period.HOURLY:
            return (local.year, local.month, local.day, local.hour)
        case Period.DAILY:
            return (local.year, local.month, local.day)
        case Period.WEEKLY:
            iso_date = local.isocalendar()
            return (iso_date.year, iso_date.week)
        case Period.MONTHLY:
            return (local.year, local.month)


def _countKeptPeriods(keep: KeepCounts, period: Period) -> int:
    match period:
        case Period.HOURLY:
            return keep.hourly
        case Period.DAILY:
            return keep.daily
        case Period.WEEKLY:
            return keep.weekly
        case Period.MONTHLY:
            return keep.monthly


### vocabulary #########################################################################

# fields run from the largest unit to the smallest, so the keys of one period sort chronologically
_PeriodKey = tuple[int, ...]
