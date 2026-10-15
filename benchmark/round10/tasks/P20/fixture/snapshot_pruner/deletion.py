"""Delete the snapshots in the delete list of a Plan.

A failed deletion does not stop the others.
"""

from __future__ import annotations

import logging
from pathlib import Path

from snapshot_pruner.vocabulary import DeletionFailure, Plan


_LOG = logging.getLogger(__name__)


def deleteSnapshots(plan: Plan) -> list[DeletionFailure]:
    snapshot_dir = Path(plan.snapshot_dir)
    failures: list[DeletionFailure] = []
    for deleted in plan.delete:
        try:
            (snapshot_dir / deleted.file).unlink()
        except OSError as exc:
            _LOG.debug('deletion.failed', extra={'file': deleted.file, 'reason': exc.strerror})
            failures.append(DeletionFailure(deleted.file, exc.strerror or type(exc).__name__))

    if failures:
        _LOG.error('deletion.failures', extra={'failed': len(failures), 'attempted': len(plan.delete)})
    return failures
