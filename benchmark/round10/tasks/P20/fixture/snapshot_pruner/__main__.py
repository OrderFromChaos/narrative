"""Decide which backup snapshots to keep under a retention policy, and delete the rest with --apply.

On every run, plan.json is written, each decision is recorded in a SQLite database, and a summary is
printed. A snapshot with an unparseable name or from the future is a problem. It is reported and
never deleted.

Modules, in reading order:
    plan                 buildPlan(), the importable entry. It calls the next three
    policy               the policy file, parsed into a Policy
    snapshot_directory   the directory entries, sorted into snapshots, problems and ignored names
    retention            the hourly, daily, weekly and monthly rules
    history              the SQLite record of each run
    deletion             the deletion of the snapshots in a plan's delete list
    report               plan.json and the terminal summary
    vocabulary           the types passed between modules

Usage:
    $ python3 -m snapshot_pruner fixture/snapshots --policy fixture/policy.json --now 2028-11-05T08:00:00Z
    $ python3 -m snapshot_pruner fixture/snapshots --policy fixture/policy.json --now 2028-11-05T08:00:00Z --apply

Exit codes:
    0  no problems
    1  at least one problem
    2  the run could not start, or --apply failed to delete a file
"""

from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from pathlib import Path

import pendulum
from pendulum import DateTime

from snapshot_pruner import deletion, history, plan, report
from snapshot_pruner.vocabulary import HistoryError, InstantError, PolicyError, SnapshotDirectoryError


DEFAULT_PLAN_PATH = Path('plan.json')
DEFAULT_DATABASE_PATH = Path('snapshot_history.db')
EXIT_SUCCESS = 0
EXIT_PROBLEMS = 1
EXIT_FAILURE = 2

LOG = logging.getLogger('snapshot_pruner')


def main() -> int:
    """Plan, record the decisions, write plan.json, delete with --apply, and print the summary.

    Nothing is deleted unless the decisions are recorded and plan.json is written.
    """
    global LOG

    parser = argparse.ArgumentParser(
        prog='python3 -m snapshot_pruner',
        description='Keep backup snapshots under a retention policy and delete the rest.',
    )
    parser.add_argument('snapshot_dir', help='directory of db-YYYYMMDDTHHMMSSZ.tar.zst snapshots')
    parser.add_argument('--policy', required=True, type=Path, help='retention policy JSON file')
    parser.add_argument(
        '--now',
        required=True,
        type=parseInstant,
        help='instant to judge the snapshots at, with a UTC offset, e.g. 2028-11-05T08:00:00Z',
    )
    parser.add_argument('--apply', action='store_true', help="delete the snapshots in the plan's delete list")
    parser.add_argument('--plan-path', type=Path, default=DEFAULT_PLAN_PATH, help='where to write plan.json')
    parser.add_argument('--database', type=Path, default=DEFAULT_DATABASE_PATH, help='SQLite file of decisions')
    parser.add_argument('--verbose', action='store_true', help='log at DEBUG level, including each failed deletion')
    args = parser.parse_args()

    handler = logging.StreamHandler()
    handler.setFormatter(FieldFormatter())
    LOG.addHandler(handler)
    LOG.setLevel(logging.DEBUG if args.verbose else logging.WARNING)

    try:
        pruning_plan = plan.buildPlan(args.snapshot_dir, args.policy, args.now)
    except (InstantError, PolicyError, SnapshotDirectoryError):
        return EXIT_FAILURE

    applied_plan = dataclasses.replace(pruning_plan, applied=args.apply)
    try:
        history.recordDecisions(args.database, applied_plan)
    except HistoryError:
        return EXIT_FAILURE

    try:
        args.plan_path.write_text(report.formatPlanJson(applied_plan), encoding='utf-8')
    except OSError as exc:
        LOG.error('plan_file.unwritable', extra={'plan_path': str(args.plan_path), 'detail': exc.strerror})
        return EXIT_FAILURE

    failures = deletion.deleteSnapshots(applied_plan) if args.apply else []
    print(report.formatSummary(applied_plan, failures), end='')

    if failures:
        return EXIT_FAILURE
    if applied_plan.problems:
        return EXIT_PROBLEMS
    return EXIT_SUCCESS


def parseInstant(raw_now: str) -> DateTime:
    try:
        now = pendulum.parse(raw_now, tz=None, exact=True)
    except ValueError:
        now = None

    if not (isinstance(now, DateTime) and now.tzinfo is not None):
        detail = f'{raw_now!r} is not an ISO 8601 instant with a UTC offset (expected e.g. "2028-11-05T08:00:00Z")'
        raise argparse.ArgumentTypeError(detail)
    return now


### vocabulary #########################################################################

_STANDARD = frozenset(logging.LogRecord('', 0, '', 0, '', None, None).__dict__) | {'message', 'asctime'}
_LOCATION = ('module', 'lineno', 'funcName')


class FieldFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extra = {k: v for k, v in record.__dict__.items() if k not in _STANDARD}
        located = {key: getattr(record, key) for key in _LOCATION}
        fields = ' '.join(f'{k}={v}' for k, v in sorted({**located, **extra}.items()))
        return f'{record.levelname} {record.getMessage()} {fields}'


if __name__ == '__main__':
    sys.exit(main())
