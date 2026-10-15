"""Plan the pruning of a directory of backup snapshots under a retention policy.

From another program:

    >>> import pendulum
    >>> from pathlib import Path
    >>> from snapshot_pruner import buildPlan
    >>> plan = buildPlan('fixture/snapshots', Path('fixture/policy.json'), pendulum.parse('2028-11-05T08:00:00Z'))
    >>> plan.keep[0].file, plan.keep[0].rules
    ('db-20281105T073000Z.tar.zst', ('hourly', 'daily', 'weekly', 'monthly', 'newest'))
    >>> plan.problems[0]
    Problem(file='db-20281105T090000Z.tar.zst', kind=<ProblemKind.FUTURE: 'future'>)
"""

from __future__ import annotations

import logging

from snapshot_pruner.plan import buildPlan
from snapshot_pruner.report import formatPlanJson
from snapshot_pruner.vocabulary import (
    DeletedSnapshot,
    InstantError,
    KeepCounts,
    KeptSnapshot,
    Period,
    Plan,
    Policy,
    PolicyError,
    Problem,
    ProblemKind,
    SnapshotDirectoryError,
)


__all__ = [
    'DeletedSnapshot',
    'InstantError',
    'KeepCounts',
    'KeptSnapshot',
    'Period',
    'Plan',
    'Policy',
    'PolicyError',
    'Problem',
    'ProblemKind',
    'SnapshotDirectoryError',
    'buildPlan',
    'formatPlanJson',
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
