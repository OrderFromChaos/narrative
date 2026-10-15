"""Decide which snapshots of a directory to keep and which to delete, as of an instant.

The newest snapshot is kept under every policy. A problem, such as a snapshot from the future, is in
neither `keep` nor `delete`.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pendulum import DateTime

from snapshot_pruner import policy, retention, snapshot_directory
from snapshot_pruner.vocabulary import DeletedSnapshot, InstantError, KeptSnapshot, Plan


_LOG = logging.getLogger(__name__)


def buildPlan(raw_snapshot_dir: str, policy_json_path: Path, now: DateTime) -> Plan:
    """Read the policy, list the directory and construct the Plan as of `now`.

    The call writes no file, deletes nothing and records nothing. `Plan.applied` is False.

    Args:
        raw_snapshot_dir: Echoed in `Plan.snapshot_dir` as passed.
        now: An instant with a UTC offset. Snapshots later than `now` are problems.

    Raises:
        InstantError: `now` has no UTC offset.
        PolicyError: the policy file is unreadable or malformed, or its timezone is unknown.
        SnapshotDirectoryError: `raw_snapshot_dir` is not a directory, or cannot be listed.
    """
    if now.tzinfo is None:
        raise _rejectInstant(now)

    utc_now = now.in_timezone('UTC')
    retention_policy = policy.parsePolicy(policy_json_path)
    listing = snapshot_directory.listSnapshotDirectory(Path(raw_snapshot_dir), utc_now)
    keeping_periods = retention.computeKeepingPeriods(listing.snapshots, retention_policy)
    newest = max(listing.snapshots, key=lambda snapshot: snapshot.at, default=None)

    keep: list[KeptSnapshot] = []
    delete: list[DeletedSnapshot] = []
    for snapshot in sorted(listing.snapshots, key=lambda snapshot: snapshot.at, reverse=True):
        local = snapshot.at.in_timezone(retention_policy.timezone)
        periods = keeping_periods[snapshot.file]
        is_newest = snapshot == newest
        if periods or is_newest:
            keep.append(KeptSnapshot(snapshot.file, local, periods, is_newest))
        else:
            delete.append(DeletedSnapshot(snapshot.file, local))

    _LOG.info('plan.built', extra={'keep': len(keep), 'delete': len(delete), 'problems': len(listing.problems)})
    return Plan(
        now=utc_now,
        snapshot_dir=raw_snapshot_dir,
        policy=retention_policy,
        applied=False,
        keep=tuple(keep),
        delete=tuple(delete),
        problems=listing.problems,
        ignored=listing.ignored,
    )


def _rejectInstant(now: DateTime) -> InstantError:
    _LOG.error('plan.naive_now', extra={'now': now.isoformat()})
    return InstantError(f'now {now.isoformat()!r} has no UTC offset (expected e.g. "2028-11-05T08:00:00Z")')
