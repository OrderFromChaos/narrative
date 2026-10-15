"""Types passed between the modules of the snapshot pruner."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pendulum import DateTime, Timezone


class Period(Enum):
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'


class ProblemKind(Enum):
    UNPARSEABLE = 'unparseable'
    FUTURE = 'future'


@dataclass(frozen=True)
class KeepCounts:
    hourly: int
    daily: int
    weekly: int
    monthly: int


@dataclass(frozen=True)
class Policy:
    timezone: Timezone
    keep: KeepCounts


@dataclass(frozen=True)
class Snapshot:
    file: str
    at: DateTime  # UTC, from the file name


@dataclass(frozen=True)
class Problem:
    file: str
    kind: ProblemKind


@dataclass(frozen=True)
class DirectoryListing:
    snapshots: tuple[Snapshot, ...]
    problems: tuple[Problem, ...]
    ignored: tuple[str, ...]


@dataclass(frozen=True)
class KeptSnapshot:
    file: str
    local: DateTime
    periods: tuple[Period, ...]
    newest: bool

    @property
    def rules(self) -> tuple[str, ...]:
        newest = ('newest',) if self.newest else ()
        return tuple(period.value for period in self.periods) + newest


@dataclass(frozen=True)
class DeletedSnapshot:
    file: str
    local: DateTime


@dataclass(frozen=True)
class Plan:
    """The decision for every entry of one snapshot directory.

    `keep` and `delete` sort newest first. `problems` and `ignored` sort by file name. `ignored` lists
    the entries that are not snapshots: other names, subdirectories and symbolic links.
    """

    now: DateTime  # UTC
    snapshot_dir: str  # as the caller passed it
    policy: Policy
    applied: bool
    keep: tuple[KeptSnapshot, ...]
    delete: tuple[DeletedSnapshot, ...]
    problems: tuple[Problem, ...]
    ignored: tuple[str, ...]


@dataclass(frozen=True)
class DeletionFailure:
    file: str
    reason: str


class InstantError(RuntimeError):
    pass


class PolicyError(RuntimeError):
    pass


class SnapshotDirectoryError(RuntimeError):
    pass


class HistoryError(RuntimeError):
    pass
