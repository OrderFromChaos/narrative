"""Read a retention policy file and construct a Policy.

The file has this shape, and every key is required:

    {
      "timezone": "America/New_York",
      "keep": {"hourly": 3, "daily": 3, "weekly": 2, "monthly": 2}
    }

A count is a non-negative integer. An unknown key at either level is malformed. The first malformed
field stops the read.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pendulum

from snapshot_pruner.vocabulary import KeepCounts, Period, Policy, PolicyError


_LOG = logging.getLogger(__name__)


def parsePolicy(policy_json_path: Path) -> Policy:
    """Read the policy file at `policy_json_path` and construct a Policy.

    Raises:
        PolicyError: the file is unreadable, is not JSON, or does not have the shape above, or the
            timezone is not an IANA name.
    """
    try:
        policy_text = policy_json_path.read_text(encoding='utf-8')
    except OSError as exc:
        raise _rejectPolicy(policy_json_path, f'unreadable: {exc.strerror}') from exc
    except UnicodeDecodeError as exc:
        raise _rejectPolicy(policy_json_path, f'not UTF-8: {exc.reason}') from exc

    try:
        raw_policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        raise _rejectPolicy(policy_json_path, f'not JSON: {exc.msg} at line {exc.lineno}') from exc

    if not (isinstance(raw_policy, dict) and set(raw_policy) == {'timezone', 'keep'}):
        raise _rejectPolicy(policy_json_path, 'expected an object with exactly the keys "timezone" and "keep"')

    raw_timezone = raw_policy['timezone']
    if not (isinstance(raw_timezone, str) and raw_timezone in pendulum.timezones()):
        raise _rejectPolicy(policy_json_path, f'unknown timezone {raw_timezone!r} (expected an IANA name)')

    keep = _parseKeepCounts(policy_json_path, raw_policy['keep'])
    return Policy(timezone=pendulum.timezone(raw_timezone), keep=keep)


def _parseKeepCounts(policy_json_path: Path, raw_keep: object) -> KeepCounts:
    expected_keys = {period.value for period in Period}
    if not (isinstance(raw_keep, dict) and set(raw_keep) == expected_keys):
        detail = f'"keep" must be an object with exactly the keys {sorted(expected_keys)}'
        raise _rejectPolicy(policy_json_path, detail)

    for key, raw_count in raw_keep.items():
        # bool subclasses Python int. Reject it too
        if not (isinstance(raw_count, int) and not isinstance(raw_count, bool) and raw_count >= 0):
            raise _rejectPolicy(policy_json_path, f'"keep.{key}" is {raw_count!r} (expected an integer >= 0)')

    return KeepCounts(
        hourly=raw_keep['hourly'],
        daily=raw_keep['daily'],
        weekly=raw_keep['weekly'],
        monthly=raw_keep['monthly'],
    )


def _rejectPolicy(policy_json_path: Path, detail: str) -> PolicyError:
    _LOG.error('policy.rejected', extra={'policy': str(policy_json_path), 'detail': detail})
    return PolicyError(f'{policy_json_path}: {detail}')
