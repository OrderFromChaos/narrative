"""Compare the base and skill arms of one run of run.py, and write RESULTS.json beside this file.

A task counts only when the gold check passed and both arms finished inside the time limit. Every
other task in the sample is listed under `excluded`, with the reason. Output of the pilot:

    tasks compared: 28
    arm    resolved  new tests old broken  cost $ wall min
    base         16      42/71          4   10.06       82
    skill        16      43/71          1   21.49       92
    exact McNemar p: 1.000

`new tests` is FAIL_TO_PASS tests passed out of FAIL_TO_PASS tests. `old broken` is PASS_TO_PASS
tests that fail after the patch. `cost $` is at list rates, from the result event of each session.

Usage:
    $ python3 experiment/bugfind/measure.py
    $ python3 experiment/bugfind/measure.py --out ~/.cache/narrative-bugfind --run 1
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


SAMPLE_PATH = Path(__file__).resolve().parent / 'sample.json'
RESULTS_PATH = Path(__file__).resolve().parent / 'RESULTS.json'
DEFAULT_OUT_DIR = Path.home() / '.cache' / 'narrative-bugfind'
MODEL = 'claude-opus-5-5'
EXIT_SUCCESS = 0
EXIT_UNUSABLE = 2


def main() -> int:
    """Pair the arms' result files by task, summarise them, and write RESULTS.json.

    Raises:
        KeyError: A result file lacks a field that run.py writes.
    """
    arguments = parseArguments()
    run_dir = arguments.out / f'run{arguments.run}'
    if not run_dir.is_dir():
        print(f'no results in {run_dir}. Pass --out and --run for another run', file=sys.stderr)
        return EXIT_UNUSABLE
    instance_ids = json.loads(SAMPLE_PATH.read_text(encoding='utf-8'))['instance_ids']
    pairs = []
    excluded = {}
    for instance_id in instance_ids:
        reason = exclusionReason(arguments.out, run_dir, instance_id)
        if reason is not None:
            excluded[instance_id] = reason.value
            continue
        pairs.append(
            TaskPair(
                instance_id=instance_id,
                base=readArmResult(run_dir / Arm.BASE.value / f'{instance_id}.json'),
                skill=readArmResult(run_dir / Arm.SKILL.value / f'{instance_id}.json'),
            ),
        )
    results = summarisePairs(pairs) | {'excluded': excluded, 'tasks': [asdict(pair) for pair in pairs]}
    RESULTS_PATH.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    printSummary(results)
    return EXIT_SUCCESS


def parseArguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT_DIR, help='the --out directory of run.py')
    parser.add_argument('--run', type=int, default=1)
    return parser.parse_args()


def exclusionReason(out_dir: Path, run_dir: Path, instance_id: str) -> Exclusion | None:
    gold_path = out_dir / 'gold' / f'{instance_id}.json'
    if not gold_path.is_file():
        return Exclusion.NOT_RUN
    if not json.loads(gold_path.read_text(encoding='utf-8'))['sound']:
        return Exclusion.GOLD_FAILED
    arm_paths = [run_dir / arm.value / f'{instance_id}.json' for arm in Arm]
    finished_paths = [path for path in arm_paths if path.is_file()]
    if any(json.loads(path.read_text(encoding='utf-8'))['agent']['timed_out'] for path in finished_paths):
        return Exclusion.TIMED_OUT
    if len(finished_paths) < len(arm_paths):
        return Exclusion.ARM_MISSING
    return None


def readArmResult(result_path: Path) -> ArmResult:
    result = json.loads(result_path.read_text(encoding='utf-8'))
    agent = result['agent']
    grade = result['grade']
    return ArmResult(
        resolved=result['resolved'],
        fail_to_pass_passed=grade['fail_to_pass_passed'],
        fail_to_pass_total=grade['fail_to_pass_total'],
        pass_to_pass_failed=grade['pass_to_pass_failed'],
        cost_usd=agent['cost_usd'] or 0.0,
        wall_s=result['wall_s'],
        num_turns=agent['num_turns'],
        only_target_model=agent['models_used'] == [MODEL],
        # result files written before run.py recorded this field have None
        first_call_input_tokens=agent.get('first_call_input_tokens'),
    )


def summarisePairs(pairs: list[TaskPair]) -> dict[str, Any]:
    """Count resolved tasks per arm and test the paired difference.

    The test is the exact McNemar test: under no difference, each task resolved by one arm only is
    equally likely to favour either arm, so the count for the skill arm is Binomial(n, 0.5).
    """
    base_only = [pair.instance_id for pair in pairs if pair.base.resolved and not pair.skill.resolved]
    skill_only = [pair.instance_id for pair in pairs if pair.skill.resolved and not pair.base.resolved]
    arms = {
        arm.value: {
            'resolved': sum(armOf(pair, arm).resolved for pair in pairs),
            'fail_to_pass_passed': sum(armOf(pair, arm).fail_to_pass_passed for pair in pairs),
            'fail_to_pass_total': sum(armOf(pair, arm).fail_to_pass_total for pair in pairs),
            'pass_to_pass_failed': sum(armOf(pair, arm).pass_to_pass_failed for pair in pairs),
            'cost_usd': round(sum(armOf(pair, arm).cost_usd for pair in pairs), 2),
            'wall_min': round(sum(armOf(pair, arm).wall_s for pair in pairs) / 60),
            'runs_off_target_model': sum(not armOf(pair, arm).only_target_model for pair in pairs),
        }
        for arm in Arm
    }
    return {
        'tasks_compared': len(pairs),
        'arms': arms,
        'base_only': base_only,
        'skill_only': skill_only,
        'mcnemar_exact_p': exactMcNemarP(len(base_only), len(skill_only)),
    }


def exactMcNemarP(base_only_count: int, skill_only_count: int) -> float:
    # two-sided: twice the smaller tail of Binomial(n, 0.5), capped at 1
    discordant = base_only_count + skill_only_count
    smaller = min(base_only_count, skill_only_count)
    tail = sum(math.comb(discordant, count) for count in range(smaller + 1)) * 0.5**discordant
    return min(1.0, 2 * tail)


def armOf(pair: TaskPair, arm: Arm) -> ArmResult:
    match arm:
        case Arm.BASE:
            return pair.base
        case Arm.SKILL:
            return pair.skill


def printSummary(results: dict[str, Any]) -> None:
    arms = results['arms']
    print(f'tasks compared: {results["tasks_compared"]}')
    print(f'{"arm":6} {"resolved":>8} {"new tests":>10} {"old broken":>10} {"cost $":>7} {"wall min":>8}')
    for name, arm in arms.items():
        new_tests = f'{arm["fail_to_pass_passed"]}/{arm["fail_to_pass_total"]}'
        print(
            f'{name:6} {arm["resolved"]:>8} {new_tests:>10} {arm["pass_to_pass_failed"]:>10} '
            f'{arm["cost_usd"]:>7} {arm["wall_min"]:>8}',
        )
    print(f'base only: {results["base_only"]}')
    print(f'skill only: {results["skill_only"]}')
    print(f'exact McNemar p: {results["mcnemar_exact_p"]:.3f}')
    print(f'excluded: {results["excluded"]}')


### vocabulary #########################################################################################################


class Arm(Enum):
    BASE = 'base'
    SKILL = 'skill'


class Exclusion(Enum):
    NOT_RUN = 'no gold check yet'
    GOLD_FAILED = 'the gold patch fails the hidden tests in this environment'
    ARM_MISSING = 'an arm has no result'
    TIMED_OUT = 'an arm hit the time limit'


@dataclass(frozen=True)
class ArmResult:
    resolved: bool
    fail_to_pass_passed: int
    fail_to_pass_total: int
    pass_to_pass_failed: int
    cost_usd: float
    wall_s: int
    num_turns: int | None
    only_target_model: bool
    first_call_input_tokens: int | None


@dataclass(frozen=True)
class TaskPair:
    instance_id: str
    base: ArmResult
    skill: ArmResult


if __name__ == '__main__':
    sys.exit(main())
