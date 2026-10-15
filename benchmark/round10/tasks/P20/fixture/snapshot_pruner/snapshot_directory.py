"""List a snapshot directory and construct a DirectoryListing.

    db-20281105T073000Z.tar.zst   ->  snapshot at 2028-11-05T07:30:00+00:00
    db-20281131T000000Z.tar.zst   ->  problem, unparseable
    db-20281105T090000Z.tar.zst   ->  problem, future when now is 2028-11-05T08:00:00Z
    db-latest.tar.zst             ->  ignored

A snapshot is a regular file. A subdirectory or a symbolic link is ignored whatever its name, and
the listing does not recurse.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pendulum
from pendulum import DateTime

from snapshot_pruner.vocabulary import DirectoryListing, Problem, ProblemKind, Snapshot, SnapshotDirectoryError


# matches:
# `db-20281105T073000Z.tar.zst`
# `db-20281131T000000Z.tar.zst`
# rejects:
# `db-20281105T0730Z.tar.zst`
# `db-latest.tar.zst`
_SNAPSHOT_NAME = re.compile(r'db-(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z\.tar\.zst', re.ASCII)

_LOG = logging.getLogger(__name__)


def listSnapshotDirectory(snapshot_dir: Path, now: DateTime) -> DirectoryListing:
    """Sort every entry of `snapshot_dir` into snapshots, problems and ignored names.

    Raises:
        SnapshotDirectoryError: `snapshot_dir` is not a directory, or cannot be listed.
    """
    if not snapshot_dir.is_dir():
        raise _rejectDirectory(snapshot_dir, 'not a directory')

    try:
        entries = sorted(snapshot_dir.iterdir())
    except OSError as exc:
        raise _rejectDirectory(snapshot_dir, f'cannot be listed: {exc.strerror}') from exc

    snapshots: list[Snapshot] = []
    problems: list[Problem] = []
    ignored: list[str] = []

    for entry in entries:
        name_match = _SNAPSHOT_NAME.fullmatch(entry.name)
        if not (name_match and entry.is_file() and not entry.is_symlink()):
            ignored.append(entry.name)
            continue

        at = _parseSnapshotInstant(name_match)
        if at is None:
            problems.append(Problem(entry.name, ProblemKind.UNPARSEABLE))
        elif at > now:
            problems.append(Problem(entry.name, ProblemKind.FUTURE))
        else:
            snapshots.append(Snapshot(entry.name, at))

    _LOG.info(
        'snapshot_directory.listed',
        extra={'snapshots': len(snapshots), 'problems': len(problems), 'ignored': len(ignored)},
    )
    return DirectoryListing(snapshots=tuple(snapshots), problems=tuple(problems), ignored=tuple(ignored))


def _parseSnapshotInstant(name_match: re.Match[str]) -> DateTime | None:
    """Return the UTC instant of a snapshot name, or None for an impossible timestamp such as November 31."""
    year, month, day, hour, minute, second = (int(group) for group in name_match.groups())
    try:
        return pendulum.datetime(year, month, day, hour, minute, second, tz='UTC')
    except ValueError:
        return None


def _rejectDirectory(snapshot_dir: Path, detail: str) -> SnapshotDirectoryError:
    _LOG.error('snapshot_directory.rejected', extra={'snapshot_dir': str(snapshot_dir), 'detail': detail})
    return SnapshotDirectoryError(f'{snapshot_dir}: {detail}')
