"""Record the decisions of a Plan in a SQLite database.

A run is keyed on (now in UTC, resolved snapshot directory, timezone, the four keep counts). A
decision row is keyed on (run, file), so a repeat run adds no rows. A file that appears between two
runs with the same key gets a row in the second.

Rows of the decisions table, as sqlite3 returns them:

    (1, 'db-20281105T073000Z.tar.zst', 'keep', '2028-11-05T02:30:00-05:00', 'hourly daily weekly monthly newest')
    (1, 'db-20281105T053000Z.tar.zst', 'delete', '2028-11-05T01:30:00-04:00', None)
    (1, 'db-20281131T000000Z.tar.zst', 'unparseable', None, None)
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path
from typing import NamedTuple

from snapshot_pruner.vocabulary import HistoryError, Plan


_LOG = logging.getLogger(__name__)


def recordDecisions(database_path: Path, plan: Plan) -> int:
    """Add one row per snapshot of `plan` to the database at `database_path`, creating it when absent.

    Returns:
        The number of decision rows this call added. A repeat run adds 0.

    Raises:
        HistoryError: the database cannot be opened or written.
    """
    SCHEMA = (
        'CREATE TABLE IF NOT EXISTS runs ('
        ' run_id INTEGER PRIMARY KEY,'
        ' now TEXT NOT NULL,'
        ' snapshot_dir TEXT NOT NULL,'
        ' timezone TEXT NOT NULL,'
        ' keep_hourly INTEGER NOT NULL,'
        ' keep_daily INTEGER NOT NULL,'
        ' keep_weekly INTEGER NOT NULL,'
        ' keep_monthly INTEGER NOT NULL,'
        ' UNIQUE (now, snapshot_dir, timezone, keep_hourly, keep_daily, keep_weekly, keep_monthly));'
        'CREATE TABLE IF NOT EXISTS decisions ('
        ' run_id INTEGER NOT NULL REFERENCES runs (run_id),'
        ' file TEXT NOT NULL,'
        " decision TEXT NOT NULL CHECK (decision IN ('keep', 'delete', 'unparseable', 'future')),"
        ' local TEXT,'
        ' rules TEXT,'
        ' PRIMARY KEY (run_id, file));'
    )
    RUN_COLUMNS = 'now, snapshot_dir, timezone, keep_hourly, keep_daily, keep_weekly, keep_monthly'
    RUN_MATCH = ' AND '.join(f'{column} = ?' for column in RUN_COLUMNS.split(', '))

    keep = plan.policy.keep
    run_key = (
        plan.now.isoformat(),
        str(Path(plan.snapshot_dir).resolve()),
        plan.policy.timezone.name,
        keep.hourly,
        keep.daily,
        keep.weekly,
        keep.monthly,
    )
    try:
        with closing(sqlite3.connect(database_path)) as connection, connection:
            connection.executescript(SCHEMA)
            connection.execute(f'INSERT OR IGNORE INTO runs ({RUN_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?)', run_key)
            (run_id,) = connection.execute(f'SELECT run_id FROM runs WHERE {RUN_MATCH}', run_key).fetchone()
            changes_before = connection.total_changes
            connection.executemany('INSERT OR IGNORE INTO decisions VALUES (?, ?, ?, ?, ?)', _buildRows(run_id, plan))
            added = connection.total_changes - changes_before
    except sqlite3.Error as exc:
        _LOG.error('history.failed', extra={'database': str(database_path), 'detail': str(exc)})
        raise HistoryError(f'{database_path}: {exc}') from exc

    _LOG.info('history.recorded', extra={'database': str(database_path), 'run_id': run_id, 'added': added})
    return added


def _buildRows(run_id: int, plan: Plan) -> Iterator[_DecisionRow]:
    for kept in plan.keep:
        yield _DecisionRow(run_id, kept.file, 'keep', kept.local.isoformat(), ' '.join(kept.rules))
    for deleted in plan.delete:
        yield _DecisionRow(run_id, deleted.file, 'delete', deleted.local.isoformat(), None)
    for problem in plan.problems:
        yield _DecisionRow(run_id, problem.file, problem.kind.value, None, None)


### vocabulary #########################################################################


# sqlite3.Cursor.executemany() rejects dataclass rows. A NamedTuple is used instead
class _DecisionRow(NamedTuple):
    run_id: int
    file: str
    decision: str
    local: str | None
    rules: str | None  # space-separated
