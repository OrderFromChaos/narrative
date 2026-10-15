"""Render a Plan as the text of plan.json, and as a summary for a terminal.

An excerpt of plan.json, with one entry of each list:

    {
      "now": "2028-11-05T08:00:00+00:00",
      "snapshot_dir": "fixture/snapshots",
      "applied": false,
      "keep": [
        {
          "file": "db-20281025T120000Z.tar.zst",
          "local": "2028-10-25T08:00:00-04:00",
          "rules": [
            "weekly",
            "monthly"
          ]
        }
      ],
      "delete": [
        {
          "file": "db-20281105T053000Z.tar.zst",
          "local": "2028-11-05T01:30:00-04:00"
        }
      ],
      "problems": [
        {
          "file": "db-20281131T000000Z.tar.zst",
          "problem": "unparseable"
        }
      ]
    }

One summary line of each shape. The last two are the counts of a dry run and of an --apply run:

    keep     db-20281105T073000Z.tar.zst  2028-11-05T02:30:00-05:00  hourly daily weekly monthly newest
    delete   db-20281104T120000Z.tar.zst  2028-11-04T08:00:00-04:00
    delete   db-20281105T053000Z.tar.zst  2028-11-05T01:30:00-04:00  FAILED: Permission denied
    problem  db-20281131T000000Z.tar.zst  unparseable
    6 kept, 7 to delete (dry run, nothing deleted), 2 problems, 4 ignored
    6 kept, 0 deleted, 7 failed to delete, 2 problems, 4 ignored
"""

from __future__ import annotations

import json
from collections.abc import Sequence

from snapshot_pruner.vocabulary import DeletedSnapshot, DeletionFailure, KeptSnapshot, Plan


def formatPlanJson(plan: Plan) -> str:
    plan_document = {
        'now': plan.now.isoformat(),
        'snapshot_dir': plan.snapshot_dir,
        'applied': plan.applied,
        'keep': [{'file': kept.file, 'local': kept.local.isoformat(), 'rules': list(kept.rules)} for kept in plan.keep],
        'delete': [{'file': deleted.file, 'local': deleted.local.isoformat()} for deleted in plan.delete],
        'problems': [{'file': problem.file, 'problem': problem.kind.value} for problem in plan.problems],
    }
    return json.dumps(plan_document, indent=2) + '\n'


def formatSummary(plan: Plan, failures: Sequence[DeletionFailure]) -> str:
    """Render one line per snapshot, newest first, then one line per problem, then the counts.

    Args:
        failures: The deletions that failed. Empty for a dry run.
    """
    reasons_by_file = {failure.file: failure.reason for failure in failures}
    judged: list[KeptSnapshot | DeletedSnapshot] = [*plan.keep, *plan.delete]
    judged.sort(key=lambda snapshot: snapshot.local, reverse=True)

    lines: list[str] = []
    for snapshot in judged:
        if isinstance(snapshot, KeptSnapshot):
            rules = ' '.join(snapshot.rules)
            lines.append(f'keep     {snapshot.file}  {snapshot.local.isoformat()}  {rules}')
        elif snapshot.file in reasons_by_file:
            failure = f'FAILED: {reasons_by_file[snapshot.file]}'
            lines.append(f'delete   {snapshot.file}  {snapshot.local.isoformat()}  {failure}')
        else:
            lines.append(f'delete   {snapshot.file}  {snapshot.local.isoformat()}')
    lines.extend(f'problem  {problem.file}  {problem.kind.value}' for problem in plan.problems)

    if plan.applied:
        deleted = len(plan.delete) - len(failures)
        deletion_count = f'{deleted} deleted, {len(failures)} failed to delete'
    else:
        deletion_count = f'{len(plan.delete)} to delete (dry run, nothing deleted)'
    lines.append(
        f'{len(plan.keep)} kept, {deletion_count}, {len(plan.problems)} problems, {len(plan.ignored)} ignored',
    )
    return '\n'.join(lines) + '\n'
