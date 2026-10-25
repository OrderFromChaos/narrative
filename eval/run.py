"""Run a predictor over the labelled units of a split, and write the confusion-matrix report.

Predictors:
    deterministic  the skill's wording checks and agentverbs.py, through predictors.py. A unit with
                   any finding is a predicted rewrite. Confidential units are included.
    agent          a fresh `claude -p` session per batch of units, with the skill loaded as a
                   plugin and the prompt opening with the skill's command. The session has the
                   Skill tool, so a skill that requires another skill loads the other skill, as in
                   use. Confidential units are skipped unless --allow-confidential.
                   --mode edit is the default, and the closest to normal use. The session gets the
                   units' files, with the file tools, the whole shell and the skill's verify.py,
                   and is asked to review the comments and fix them in place. Each unit's verdict
                   comes from the diff, through edits.py, and the rules of each change from a separate
                   grader session that reads the diff. In --mode review, the units are in the prompt
                   instead, with a request for a JSON verdict per unit, and the session has no file
                   and no checker.
    union          an agent run file, with each prediction of keep turned to a rewrite when the
                   unit has a finding of the deterministic checks. The report has the agent run and
                   the union side by side.

The claude binary, the login directory, the model and the effort of the agent predictor come from
experiment/bugfind/run.py, so the agent runs under the isolated login of the bugfind pilot. With two
--skill options, the agent gets the same units with each skill, and the comparison report has both
matrices and the change in every cell.

Run files go to ~/.cache/narrative-eval/runs/, and reports to eval/reports/. The text and the
predictions of confidential units go to `reports/` in the private store, never to eval/reports/.

A --skill of the form `nar:python` is the skill `python` of this repository's plugin: the built
skills of skills/, as the plugin `nar`, with the prompt opening with `/nar:python`. Any other --skill
is a skill directory, loaded as the plugin `narrative-python`, with the prompt opening with
`/narrative-python:narrative-python`.

In --mode review, a --skill of `nar:python+verify` is `nar:python`, and the session may also run
the skill's verify.py. Each unit of a batch is written alone to a file of the session's directory, as
a comment, with the skill's pyproject-snippet.toml as pyproject.toml, so verify.py can parse the file.

Usage:
    $ uv run --python ~/.local/share/narrative/lintenv/bin/python eval/run.py deterministic
    $ uv run eval/run.py --tier gold agent --split dev
    $ uv run eval/run.py --tier gold agent --skill /tmp/skill-at-head --skill nar:python --split dev
    $ uv run eval/run.py agent --skill none --split dev --sample 20 --runs 1
    $ uv run eval/run.py --tier gold agent --mode review --skill nar:python --skill nar:python+verify
    $ uv run --python ~/.local/share/narrative/lintenv/bin/python eval/run.py union RUN_FILE

Exit codes:
    0  the report was written
    1  the report was written, and some agent calls failed or left units unanswered
    2  the arguments, the units, the login or the skill directory were unusable
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import itertools
import json
import random
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, replace
from pathlib import Path
from types import ModuleType

import edits
from matrix import Prediction, Report, RunRecord, buildReport, readRun, writeReport, writeRun
from predictors import DeterministicChecks
from schema import (
    PRIVATE_DIR,
    REPO_ROOT,
    REPORTS_DIR,
    UNITS_DIR,
    ContextLevel,
    Kind,
    Unit,
    UnitFileError,
    UnitId,
    Verdict,
    labelRecord,
    loadUnits,
)


CACHE_DIR = Path.home() / '.cache' / 'narrative-eval'
BUGFIND_RUN_PATH = REPO_ROOT / 'experiment' / 'bugfind' / 'run.py'
SKILLS_DIR = REPO_ROOT / 'skills'
SKILL_NAME = 'narrative-python'
# the plugin of this repository's skills/, as in .claude-plugin/marketplace.json
PLUGIN_NAME = 'nar'
NO_SKILL = 'none'
# the suffix of a --skill value whose session may also run the skill's verify.py
VERIFY_SUFFIX = '+verify'
# the config of the skill's checks, beside verify.py in the skill directory
PYPROJECT_SNIPPET = 'pyproject-snippet.toml'
# the comment width of a unit file of the +verify arm
UNIT_FILE_WIDTH = 100
EDIT_MODE = 'edit'
REVIEW_MODE = 'review'
# the request of the edit mode, after the skill's command. No unit, label or hypothesis is in the request
EDIT_REQUEST = (
    'Review the comments and docstrings of the files in this directory, and fix them in place. The files '
    'are excerpts of a larger project: code outside them is missing, so a file need not run, import or '
    'type-check.'
)
# the confinement of the edit mode. The session has the whole shell, like a normal session, so the
# session stays in the session directory by this instruction, not by a permission rule. {skill_dir}
# and {lint_venv} are filled in per arm
EDIT_CONFINEMENT = (
    'Read and write files only inside this directory, and put any scratch file here. You may also read '
    'and run the files of the skill in {skill_dir} and of the lint venv in {lint_venv}, and change nothing there.'
)
# the request of the grader, a separate session after each editing session. The grader reads the
# editing session's diff and names the rule behind each change, so the editing session never names rules
GRADER_REQUEST = (
    'Below is the git diff of a review of the comments and docstrings of some Python files. List every '
    'comment or docstring that the diff changes or deletes. For each one, name the rules of the skill that '
    'the change applies: the NAR code where the rule has one, such as NAR017, and otherwise the id in '
    'parentheses after the rule, such as R10-restatement-gate. Reply with a JSON array and nothing else, '
    'one object per comment or docstring: {"file": "<path in the diff>", "old": "<the text before the '
    'change>", "new": "<the text after the change, or null when deleted>", "rules": ["<rule>"]}.'
)
# the skill whose rules the grader names, the same for every arm, so the grader is one instrument
GRADER_SKILL = f'{PLUGIN_NAME}:python'
# the caches of the checkers, left out of the commit and of the diff
SESSION_GITIGNORE = '.mypy_cache/\n.ruff_cache/\n.narrative_cache/\n__pycache__/\n'
# the lint venv that the skill's verify.py runs, one per machine
LINT_VENV = Path.home() / '.local' / 'share' / 'narrative' / 'lintenv'
# the pyproject.toml of the edit mode's files, so that the skill's verify.py reads a Narrative config
PROJECT_CONFIG = SKILLS_DIR / 'python' / PYPROJECT_SNIPPET
# the tools of the edit mode: the default tools of `claude -p`, less the tools with effects outside
# the session, such as cron jobs, remote triggers, push notifications, workflows and worktrees
EDIT_TOOLS = (
    'Task', 'TaskStop', 'SendMessage', 'ListAgents', 'Bash', 'Monitor', 'Read', 'Edit', 'Write',
    'NotebookEdit', 'ToolSearch', 'WebFetch', 'WebSearch',
)  # fmt: skip
# the git identity of the commit of a session's files, a scratch repository under the cache
EVAL_GIT_IDENTITY = ('-c', 'user.name=narrative-eval', '-c', 'user.email=narrative-eval@example.invalid')
SAMPLE_SEED = 'narrative-eval'
DEFAULT_RUNS = 3
DEFAULT_BATCH = 20
DEFAULT_JOBS = 3
AGENT_TIMEOUT_S = 15 * 60
PAGE_KINDS = frozenset({Kind.PAGE, Kind.PR_BODY, Kind.CHAT})
EXIT_SUCCESS = 0
EXIT_INCOMPLETE = 1
EXIT_UNUSABLE = 2


def main() -> int:
    """Select the units, run the predictor once per skill, and write the run files and the report.

    Returns:
        The exit code of the module docstring.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--units', type=Path, default=UNITS_DIR, help='the public unit directory')
    parser.add_argument('--private', type=Path, default=PRIVATE_DIR, help='the private store, merged when present')
    parser.add_argument('--reports', type=Path, default=REPORTS_DIR)
    parser.add_argument('--sample', type=int, help='a seeded random sample of this many units')
    tiers = ('gold', 'silver', 'bronze', 'all')
    parser.add_argument('--tier', choices=tiers, default='all', help='units with a label of this tier')
    parser.add_argument('--seed', default=SAMPLE_SEED)
    predictors = parser.add_subparsers(dest='predictor', required=True)
    deterministic = predictors.add_parser('deterministic', help="the skill's checks, no model")
    deterministic.add_argument('--split', choices=('dev', 'test', 'all'), default='all')
    agent = predictors.add_parser('agent', help='a fresh claude -p session with the skill')
    agent.add_argument('--split', choices=('dev', 'test', 'all'), default='dev')
    agent.add_argument('--skill', action='append', help=f'a skill directory, or {NO_SKILL}. Twice to compare')
    agent.add_argument('--mode', choices=(EDIT_MODE, REVIEW_MODE), default=EDIT_MODE, help='see the module docstring')
    agent.add_argument('--runs', type=int, default=DEFAULT_RUNS)
    agent.add_argument('--batch', type=int, default=DEFAULT_BATCH, help='units per claude session')
    agent.add_argument('--jobs', type=int, default=DEFAULT_JOBS, help='claude sessions at once')
    agent.add_argument('--model', help='default: the model of experiment/bugfind/run.py')
    agent.add_argument('--effort', help='default: the effort of experiment/bugfind/run.py')
    agent.add_argument('--config-dir', type=Path, help='default: the login of experiment/bugfind/run.py')
    agent.add_argument('--allow-confidential', action='store_true', help='send confidential units to the API')
    agent.add_argument('--dry-run', action='store_true', help='write the prompts and call no model')
    union = predictors.add_parser(
        'union',
        help='an agent run, with each unit that has a finding of the deterministic checks turned to a rewrite',
    )
    union.add_argument('run', type=Path, help='a run file of the agent predictor')
    # the units of the run file are the ones scored, whatever their split
    union.set_defaults(split='all')
    arguments = parser.parse_args()

    try:
        units = loadUnits(arguments.units, arguments.private)
    except (OSError, UnitFileError) as exc:
        print(f'run.py: {exc}', file=sys.stderr)
        return EXIT_UNUSABLE
    selected = [unit for unit in units if unit.labels and arguments.split in ('all', unit.split.value)]
    if arguments.tier != 'all':
        selected = [unit for unit in selected if any(label.tier.value == arguments.tier for label in unit.labels)]
    stamp = time.strftime('%Y%m%d-%H%M%S')
    match arguments.predictor:
        case 'deterministic':
            selected = sampleUnits(selected, arguments.sample, arguments.seed)
            try:
                checks = DeterministicChecks.load()
            except ModuleNotFoundError as exc:
                print(
                    f'run.py: {exc}. Run with the lint venv. The Usage of the module docstring has the command',
                    file=sys.stderr,
                )
                return EXIT_UNUSABLE
            runs = [predictDeterministic(checks, selected, split=arguments.split)]
            incomplete = False
        case 'agent':
            skipped = [unit for unit in selected if unit.confidential and not arguments.allow_confidential]
            if arguments.mode == EDIT_MODE:
                # a unit with no context has no file to edit. Such units are scored with --mode review
                no_context = [unit for unit in selected if unit.context_level is ContextLevel.NONE]
                selected = [unit for unit in selected if unit.context_level is not ContextLevel.NONE]
                print(f'{len(no_context)} units with no context left out. Score them with --mode review')
            selected = sampleUnits([unit for unit in selected if unit not in skipped], arguments.sample, arguments.seed)
            print(f'{len(selected)} units, {len(skipped)} confidential units skipped')
            try:
                settings = prepareAgent(arguments, stamp)
            except AgentSetupError as exc:
                print(f'run.py: {exc}', file=sys.stderr)
                return EXIT_UNUSABLE
            runs = [
                replace(
                    asyncio.run(predictWithAgent(settings, arm, selected, split=arguments.split)),
                    skipped_confidential=len(skipped),
                )
                for arm in settings.arms
            ]
            incomplete = any(run.unanswered for run in runs)
            if arguments.dry_run:
                print(f'prompts written to {settings.log_dir}')
                return EXIT_SUCCESS
        case 'union':
            try:
                agent_run = readRun(arguments.run)
                checks = DeterministicChecks.load()
            except (OSError, KeyError, TypeError, ValueError, ModuleNotFoundError) as exc:
                print(
                    f'run.py: {exc}. Run with the lint venv. The Usage of the module docstring has the command',
                    file=sys.stderr,
                )
                return EXIT_UNUSABLE
            runs = [agent_run, predictUnion(checks, units, agent_run)]
            incomplete = False

    confidential = {unit.id for unit in units if unit.confidential}
    reports = []
    for index, run in enumerate(runs):
        run_path = CACHE_DIR / 'runs' / f'{stamp}-{run.predictor}-{run.split}-{index}.json'
        writeRun(run_path, run, confidential)
        print(f'wrote {run_path}')
        report = buildReport(units, run)
        reports.append(report)
        for path in writeReport(arguments.reports / f'{stamp}-{run.predictor}-{run.split}-{index}', [report]):
            print(f'wrote {path}')
        detail_path = arguments.private / 'reports' / f'{stamp}-{run.predictor}-{index}.jsonl'
        writeConfidentialDetail(units, run, detail_path=detail_path)
    if len(reports) == 2:
        for path in writeReport(arguments.reports / f'{stamp}-compare-{runs[0].split}', reports):
            print(f'wrote {path}')
    printSummary(reports)
    return EXIT_INCOMPLETE if incomplete else EXIT_SUCCESS


def sampleUnits(units: list[Unit], size: int | None, seed: str) -> list[Unit]:
    # units are sorted by id, so the sample is the same for the same seed and unit set in any file order
    ordered = sorted(units, key=lambda unit: unit.id)
    if size is None or size >= len(ordered):
        return ordered
    return random.Random(seed).sample(ordered, size)


def predictDeterministic(checks: DeterministicChecks, units: list[Unit], *, split: str) -> RunRecord:
    predictions = []
    for unit in units:
        codes = checks.findCodes(unit.text, page=unit.kind in PAGE_KINDS)
        action = Verdict.REWRITE if codes else Verdict.KEEP
        predictions.append(Prediction(unit=unit.id, run=0, action=action, rules=tuple(sorted(codes)), new_text=None))
    checks.save()
    return RunRecord(
        predictor='deterministic',
        skill=str(checks.tool_dir.relative_to(REPO_ROOT)),
        skill_commit=describeSkill(checks.tool_dir),
        model=None,
        runs=1,
        split=split,
        started=time.strftime('%Y-%m-%d %H:%M'),
        cost_usd=None,
        skipped_confidential=0,
        unanswered=0,
        predictions=tuple(predictions),
    )


def predictUnion(checks: DeterministicChecks, units: list[Unit], agent_run: RunRecord) -> RunRecord:
    """Turn each keep of the agent run to a rewrite when the unit has a finding of the deterministic checks.

    A cut or a rewrite of the agent is kept, with the codes of the checks added to the rules of the prediction.
    """
    by_id = {unit.id: unit for unit in units}
    codes = {
        unit_id: checks.findCodes(by_id[unit_id].text, page=by_id[unit_id].kind in PAGE_KINDS)
        for unit_id in {prediction.unit for prediction in agent_run.predictions}
    }
    checks.save()
    predictions = tuple(
        replace(
            prediction,
            action=Verdict.REWRITE if prediction.action is Verdict.KEEP else prediction.action,
            rules=tuple(sorted({*prediction.rules, *codes[prediction.unit]})),
        )
        if codes[prediction.unit]
        else prediction
        for prediction in agent_run.predictions
    )
    return replace(
        agent_run,
        predictor='union',
        skill=f'{agent_run.skill} with the deterministic checks',
        skill_commit=f'{agent_run.skill_commit}; checks {describeSkill(checks.tool_dir)}',
        predictions=predictions,
    )


def prepareAgent(arguments: argparse.Namespace, stamp: str) -> AgentSettings:
    """Load the bugfind runner's settings, check the login, and build one plugin per skill directory.

    Raises:
        AgentSetupError: A skill directory has no SKILL.md, the login is missing, or more than two
            skills were given.
    """
    raw_skills = arguments.skill or [f'{PLUGIN_NAME}:python']
    if len(raw_skills) > 2:
        raise AgentSetupError('give one --skill, or two to compare')
    bugfind = loadBugfindRunner()
    config_dir: Path = arguments.config_dir or bugfind.DEFAULT_CONFIG_DIR
    if not arguments.dry_run and not bugfind.loggedIn(config_dir):
        raise AgentSetupError(f'no login in {config_dir}')
    arms = [skillArm(raw_skill) for raw_skill in raw_skills]
    if arguments.mode == EDIT_MODE and any(arm.verify_path for arm in arms):
        raise AgentSetupError(
            f'{VERIFY_SUFFIX} is for --mode review. In --mode edit, the session may always run verify.py',
        )
    claude_binary: Path = bugfind.findNewestClaude() if not arguments.dry_run else Path('claude')
    environment: dict[str, str] = bugfind.buildClaudeEnvironment(config_dir)
    # uv, ruff and the other tools of the user in ~/.local/bin, on PATH for a normal session too
    environment['PATH'] = f'{Path.home() / ".local" / "bin"}:{environment["PATH"]}'
    work_dir = CACHE_DIR / 'work'
    work_dir.mkdir(parents=True, exist_ok=True)
    return AgentSettings(
        claude_binary=claude_binary,
        environment=environment,
        model=arguments.model or bugfind.MODEL,
        effort=arguments.effort or bugfind.EFFORT,
        arms=tuple(arms),
        mode=arguments.mode,
        runs=arguments.runs,
        batch=arguments.batch,
        jobs=arguments.jobs,
        work_dir=work_dir,
        log_dir=CACHE_DIR / 'logs' / stamp,
        private_log_dir=arguments.private / 'runs' / 'logs' / stamp,
        dry_run=arguments.dry_run,
    )


def skillArm(raw_skill: str) -> SkillArm:
    """Turn one --skill into the plugin, the command and the version of one arm of the run.

    Raises:
        AgentSetupError: A skill directory has no SKILL.md, or this repository's plugin has no such skill.
    """
    if raw_skill == NO_SKILL:
        return SkillArm(
            label=NO_SKILL,
            display=NO_SKILL,
            version='none',
            plugin_dir=None,
            command=None,
            skill_dir=None,
            verify_path=None,
        )
    if raw_skill.startswith(f'{PLUGIN_NAME}:'):
        name = raw_skill.removeprefix(f'{PLUGIN_NAME}:').removesuffix(VERIFY_SUFFIX)
        if not (SKILLS_DIR / name / 'SKILL.md').is_file():
            raise AgentSetupError(f'{SKILLS_DIR} has no skill {name}. Run python3 build_skills.py')
        plugin_dir = buildRepoPlugin()
        verify_path = plugin_dir / 'skills' / name / 'verify.py' if raw_skill.endswith(VERIFY_SUFFIX) else None
        if verify_path and not (verify_path.parent / PYPROJECT_SNIPPET).is_file():
            raise AgentSetupError(f'{raw_skill}: the skill {name} has no {PYPROJECT_SNIPPET} for verify.py')
        return SkillArm(
            label=name + (VERIFY_SUFFIX if verify_path else ''),
            display=raw_skill,
            version=describeSkill(SKILLS_DIR),
            plugin_dir=plugin_dir,
            command=f'/{PLUGIN_NAME}:{name}',
            skill_dir=plugin_dir / 'skills' / name,
            verify_path=verify_path,
        )
    if raw_skill.endswith(VERIFY_SUFFIX):
        raise AgentSetupError(f'{VERIFY_SUFFIX} is for a skill of this repository, such as {PLUGIN_NAME}:python')
    skill_dir = Path(raw_skill).resolve()
    if not (skill_dir / 'SKILL.md').is_file():
        raise AgentSetupError(f'{skill_dir} has no SKILL.md')
    return SkillArm(
        label=skill_dir.name,
        display=displayPath(skill_dir),
        version=describeSkill(skill_dir),
        plugin_dir=(plugin_dir := buildPlugin(skill_dir)),
        command=f'/{SKILL_NAME}:{SKILL_NAME}',
        skill_dir=plugin_dir / 'skills' / SKILL_NAME,
        verify_path=None,
    )


def buildRepoPlugin() -> Path:
    """Copy each skill directory of skills/ that has no load-time command into a plugin named nar.

    A skill whose SKILL.md runs a command at load, such as `code`, needs the whole repository, so the
    copy leaves the skill out. A plugin directory that already exists for the digest is reused.
    """
    skill_dirs = sorted(
        path
        for path in SKILLS_DIR.iterdir()
        if (path / 'SKILL.md').is_file() and '!`' not in (path / 'SKILL.md').read_text()
    )
    plugin_dir = CACHE_DIR / 'plugins' / f'{PLUGIN_NAME}-{hashSkill(SKILLS_DIR)}'
    if plugin_dir.exists():
        return plugin_dir
    staging = plugin_dir.with_name(plugin_dir.name + '.partial')
    if staging.exists():
        shutil.rmtree(staging)
    (staging / '.claude-plugin').mkdir(parents=True)
    (staging / '.claude-plugin' / 'plugin.json').write_text(f'{{"name": "{PLUGIN_NAME}"}}\n', encoding='utf-8')
    for skill_dir in skill_dirs:
        shutil.copytree(skill_dir, staging / 'skills' / skill_dir.name, ignore=shutil.ignore_patterns('__pycache__'))
    staging.rename(plugin_dir)
    return plugin_dir


def loadBugfindRunner() -> ModuleType:
    """Import experiment/bugfind/run.py by path, as a module named bugfind_run.

    Raises:
        AgentSetupError: The file is absent or cannot be imported.
    """
    # the bugfind runner imports container_tool by bare name
    sys.path.insert(0, str(BUGFIND_RUN_PATH.parent))
    spec = importlib.util.spec_from_file_location('bugfind_run', BUGFIND_RUN_PATH)
    if spec is None or spec.loader is None:
        raise AgentSetupError(f'cannot import {BUGFIND_RUN_PATH}')
    module = importlib.util.module_from_spec(spec)
    # dataclass() reads the module of each class from sys.modules while the class is created
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise AgentSetupError(f'cannot import {BUGFIND_RUN_PATH}: {exc}') from exc
    return module


async def predictWithAgent(
    settings: AgentSettings,
    arm: SkillArm,
    units: list[Unit],
    *,
    split: str,
) -> RunRecord:
    """Ask a fresh session for a verdict on each unit, settings.runs times, and retry each batch's
    missing answers once.

    Units are sorted by group, so a batch has neighbouring units of one file. In the edit mode, a
    batch has whole groups, so the units of one file are in one session.

    Returns:
        The run, with the count of unit and run pairs that got no valid answer after the retry.
    """
    ordered = sorted(units, key=lambda unit: (unit.group, unit.origin.line or 0, unit.id))
    batches = batchUnits(ordered, settings.batch, whole_groups=settings.mode == EDIT_MODE)
    limit = asyncio.Semaphore(settings.jobs)
    tasks = []
    async with asyncio.TaskGroup() as group:
        for run_index in range(settings.runs):
            for batch_index, batch in enumerate(batches):
                name = f'{arm.label}-run{run_index}-batch{batch_index}'
                tasks.append(group.create_task(answerBatch(settings, arm, batch, run_index, name, limit)))
    outcomes = [task.result() for task in tasks]
    predictions = tuple(prediction for outcome in outcomes for prediction in outcome.predictions)
    costs = [outcome.cost_usd for outcome in outcomes if outcome.cost_usd is not None]
    models = sorted({outcome.model for outcome in outcomes if outcome.model})
    agreements = [outcome.agreement for outcome in outcomes if outcome.agreement is not None]
    if agreements:
        total = agreements[0]
        for agreement in agreements[1:]:
            total = total.plus(agreement)
        print(
            f'{arm.label}: changed units by the diff reader and by the grader: {total.both} in both, '
            f'{total.diff_only} by the reader only, {total.list_only} by the grader only, '
            f'{total.unmatched_entries} grader entries with no unit',
        )
    return RunRecord(
        predictor=('agent' if arm.command else 'agent-no-skill') + ('-edit' if settings.mode == EDIT_MODE else ''),
        skill=arm.display,
        skill_commit=arm.version,
        model=', '.join(models) or settings.model,
        runs=settings.runs,
        split=split,
        started=time.strftime('%Y-%m-%d %H:%M'),
        cost_usd=sum(costs) if costs else None,
        skipped_confidential=0,
        unanswered=len(units) * settings.runs - len(predictions),
        predictions=predictions,
    )


def batchUnits(ordered: list[Unit], size: int, *, whole_groups: bool) -> list[list[Unit]]:
    """Cut the sorted units into batches of `size`, or of whole groups of about `size` units."""
    if not whole_groups:
        return [ordered[start : start + size] for start in range(0, len(ordered), size)]
    batches: list[list[Unit]] = [[]]
    for _group, members in itertools.groupby(ordered, key=lambda unit: unit.group):
        group_units = list(members)
        if batches[-1] and len(batches[-1]) + len(group_units) > size:
            batches.append([])
        batches[-1].extend(group_units)
    return [batch for batch in batches if batch]


async def answerBatch(
    settings: AgentSettings,
    arm: SkillArm,
    batch: list[Unit],
    run_index: int,
    name: str,
    limit: asyncio.Semaphore,
) -> BatchOutcome:
    """Run one session on a batch, then one more on the units without a valid answer.

    Returns:
        The valid answers as predictions, and the summed cost of both sessions.
    """
    answered: dict[UnitId, Prediction] = {}
    cost = 0.0
    model = None
    agreement = None
    for attempt in range(2):
        pending = [unit for unit in batch if unit.id not in answered]
        if not pending or (attempt and settings.dry_run):
            break
        async with limit:
            outcome = await callAgent(settings, arm, pending, run_index, f'{name}-try{attempt}')
        answered.update(outcome.answers)
        cost += outcome.cost_usd or 0.0
        model = outcome.model or model
        if outcome.agreement is not None:
            agreement = outcome.agreement if agreement is None else agreement.plus(outcome.agreement)
    return BatchOutcome(predictions=tuple(answered.values()), cost_usd=cost or None, model=model, agreement=agreement)


async def callAgent(
    settings: AgentSettings,
    arm: SkillArm,
    units: list[Unit],
    run_index: int,
    name: str,
) -> CallOutcome:
    """Run `claude -p` once on a batch and parse the JSON answer.

    The prompt and the raw output are logged under the cache, or under the private store when the
    batch has a confidential unit. After a timeout, a nonzero exit or an unparsable answer, the
    batch is unanswered, and the cause is printed.

    Returns:
        The valid answers by unit id, with the session's cost and model.
    """
    log_dir = settings.private_log_dir if any(unit.confidential for unit in units) else settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    if settings.mode == EDIT_MODE:
        return await callEditingAgent(settings, arm, units, run_index, name, log_dir)
    local_ids = {f'u{index:02d}': unit for index, unit in enumerate(units, start=1)}
    prompt = buildPrompt(local_ids, command=arm.command, verify=arm.verify_path is not None)
    (log_dir / f'{name}.prompt.txt').write_text(prompt, encoding='utf-8')
    if settings.dry_run:
        return CallOutcome(answers={}, cost_usd=None, model=None)

    tools = 'Skill' if arm.command else ''
    session_dir = settings.work_dir
    allowed: list[str] = []
    if arm.verify_path is not None:
        tools = 'Skill,Bash'
        # the log directory of a confidential batch is in the private store, so the unit files go under that
        # directory
        session_dir = writeUnitFiles(log_dir / 'work' / name, local_ids, arm.verify_path.parent / PYPROJECT_SNIPPET)
        allowed = ['--allowedTools', f'Bash(python3 {arm.verify_path}:*)', f'Bash(python3 "{arm.verify_path}":*)']
    command = [
        str(settings.claude_binary), '-p', prompt,
        '--model', settings.model,
        '--effort', settings.effort,
        '--restricted',
        '--tools', tools,
        *allowed,
        '--strict-mcp-config',
        '--permission-prompts', 'none',
        '--output-format', 'json',
    ]  # fmt: skip
    if arm.plugin_dir is not None:
        command += ['--plugin-dir', str(arm.plugin_dir)]
    result = await runSession(settings, command, session_dir, name, log_dir)
    if result is None:
        return CallOutcome(answers={}, cost_usd=None, model=None)
    try:
        answers = parseAnswers(str(result.get('result', '')), local_ids, run_index)
    except json.JSONDecodeError as exc:
        print(f'{name}: unparsable answer: {exc}', file=sys.stderr)
        return CallOutcome(answers={}, cost_usd=None, model=None)
    return CallOutcome(answers=answers, cost_usd=costOf(result), model=modelOf(result))


async def callEditingAgent(
    settings: AgentSettings,
    arm: SkillArm,
    units: list[Unit],
    run_index: int,
    name: str,
    log_dir: Path,
) -> CallOutcome:
    """Run `claude -p` once on the files of a batch, and read each unit's verdict from the session's edits.

    The files go in a git repository with one commit under the log directory, so the files of a
    confidential batch stay in the private store. The session has the default tools and the whole shell,
    like a normal session, and an instruction to stay inside the session directory. Afterwards a separate
    grader session reads the diff and lists the changes with their rules. Each changed unit gets the
    rules of its entry in that list.

    Returns:
        A verdict for each unit, with the session's cost and model. None after a failed session.
    """
    skill_dir = arm.skill_dir if arm.skill_dir is not None and arm.plugin_dir is not None else None
    confinement = (
        EDIT_CONFINEMENT.format(skill_dir=skill_dir, lint_venv=LINT_VENV)
        if skill_dir
        else ('Read and write files only inside this directory, and put any scratch file here.')
    )
    request = f'{EDIT_REQUEST} {confinement}'
    prompt = f'{arm.command} {request}' if arm.command else request
    (log_dir / f'{name}.prompt.txt').write_text(prompt, encoding='utf-8')
    workspace = edits.buildWorkspace(log_dir / 'work' / name, units, PROJECT_CONFIG)
    commitFiles(workspace.root)
    if settings.dry_run:
        return CallOutcome(answers={}, cost_usd=None, model=None)

    tools = [*EDIT_TOOLS]
    extra: list[str] = []
    if skill_dir is not None and arm.plugin_dir is not None:
        tools.append('Skill')
        extra = ['--plugin-dir', str(arm.plugin_dir), '--add-dir', str(skill_dir)]
    command = [
        str(settings.claude_binary), '-p', prompt,
        '--model', settings.model,
        '--effort', settings.effort,
        '--restricted',
        '--tools', ','.join(tools),
        '--allowedTools', *tools,
        '--permission-mode', 'acceptEdits',
        '--strict-mcp-config',
        '--permission-prompts', 'none',
        '--output-format', 'json',
        *extra,
    ]  # fmt: skip
    result = await runSession(settings, command, workspace.root, name, log_dir)
    if result is None:
        return CallOutcome(answers={}, cost_usd=None, model=None)
    listed, grader_cost = await gradeChanges(settings, workspace.root, f'{name}-grader', log_dir)
    answers, agreement = edits.readEdits(workspace, units, run_index, listed)
    (log_dir / f'{name}.reader.json').write_text(json.dumps(agreement.asRecord(), indent=1), encoding='utf-8')
    cost = (costOf(result) or 0.0) + grader_cost
    return CallOutcome(answers=answers, cost_usd=cost or None, model=modelOf(result), agreement=agreement)


def commitFiles(session_dir: Path) -> None:
    """Make a git repository of the session's directory, with the directory's files in one commit."""
    (session_dir / '.gitignore').write_text(SESSION_GITIGNORE, encoding='utf-8')
    for arguments in (['init', '-q'], ['add', '-A'], [*EVAL_GIT_IDENTITY, 'commit', '-q', '-m', 'excerpts']):
        subprocess.run(['git', '-C', str(session_dir), *arguments], check=True, capture_output=True)


async def gradeChanges(
    settings: AgentSettings,
    session_dir: Path,
    name: str,
    log_dir: Path,
) -> tuple[list[edits.ListedChange], float]:
    """Ask a fresh grader session to list the changes of the editing session's diff, with their rules.

    The grader has the skill and the diff alone: no file, no tool but Skill, and nothing the editing
    session said. A session that changed nothing gets no grader.

    Returns:
        The grader's list of changes, and the grader's cost. An empty list after a failed grader.
    """
    subprocess.run(['git', '-C', str(session_dir), 'add', '-A'], check=True, capture_output=True)
    diff = subprocess.run(
        ['git', '-C', str(session_dir), 'diff', '--cached', '--no-color', '-U5'],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if not diff.strip():
        return [], 0.0
    prompt = f'/{GRADER_SKILL} {GRADER_REQUEST}\n\n<diff>\n{diff}</diff>'
    (log_dir / f'{name}.prompt.txt').write_text(prompt, encoding='utf-8')
    command = [
        str(settings.claude_binary), '-p', prompt,
        '--model', settings.model,
        '--effort', settings.effort,
        '--restricted',
        '--tools', 'Skill',
        '--strict-mcp-config',
        '--permission-prompts', 'none',
        '--output-format', 'json',
        '--plugin-dir', str(buildRepoPlugin()),
    ]  # fmt: skip
    result = await runSession(settings, command, settings.work_dir, name, log_dir)
    if result is None:
        return [], 0.0
    return edits.readChangeList(str(result.get('result', ''))), costOf(result) or 0.0


async def runSession(
    settings: AgentSettings,
    command: list[str],
    session_dir: Path,
    name: str,
    log_dir: Path,
) -> dict[str, object] | None:
    """Run one `claude -p` command and log its output.

    Returns:
        The session's JSON result, or None after a timeout, a nonzero exit or output that is not JSON.
    """
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=session_dir,
        env=settings.environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), AGENT_TIMEOUT_S)
    except TimeoutError:
        process.kill()
        await process.wait()
        print(f'{name}: timed out after {AGENT_TIMEOUT_S} s', file=sys.stderr)
        return None
    (log_dir / f'{name}.output.json').write_bytes(stdout)
    if process.returncode != 0:
        print(f'{name}: claude exited {process.returncode}: {stderr.decode(errors="replace")[-300:]}', file=sys.stderr)
        return None
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError as exc:
        print(f'{name}: unparsable output: {exc}', file=sys.stderr)
        return None
    return result if isinstance(result, dict) else None


def costOf(result: dict[str, object]) -> float | None:
    cost = result.get('total_cost_usd')
    return float(cost) if isinstance(cost, int | float) else None


def modelOf(result: dict[str, object]) -> str | None:
    usage = result.get('modelUsage')
    return next(iter(usage), None) if isinstance(usage, dict) else None


def buildPrompt(local_ids: dict[str, Unit], *, command: str | None, verify: bool) -> str:
    """Write the review request: the instructions, the answer format, then each unit in the unit's context.

    The prompt names no label, no expected answer and no hypothesis.
    """
    rules = (
        '`rules` lists the rules of the skill that the unit breaks: the NAR code where the rule has one, such '
        'as NAR017, and otherwise the id in parentheses after the rule, such as R10-restatement-gate.'
        if command
        else '`rules` lists a short name for each problem the unit has.'
    )
    parts = [
        'Review each unit below. A unit is a comment, a docstring, or one sentence of prose. Where a unit has '
        'file context, the first line of the unit is marked with `>>>` in the context.',
        'For each unit, decide one action:\n- keep: the unit stays as written\n- cut: the unit is deleted\n'
        '- rewrite: the unit stays, reworded',
        'Reply with a JSON array and nothing else, one object per unit:\n'
        '[{"id": "u01", "action": "keep", "rules": [], "new_text": null}]\n'
        f'{rules} `new_text` is the reworded unit for a rewrite, and null otherwise.'
        + (
            ' Each unit is also alone in a file of the current directory, named by the id of the unit, such as '
            "u01.py, so the skill's verify.py can check the unit. Run verify.py as the skill says, and run no "
            'other command.'
            if verify
            else ' Read and run no file.'
        ),
    ]
    for local_id, unit in local_ids.items():
        block = [f'<unit id="{local_id}" language="{unit.language.value}" kind="{unit.kind.value}">']
        if unit.context:
            marked = [
                ('>>> ' if number == unit.focus_line else '    ') + line
                for number, line in enumerate(unit.context.splitlines(), start=1)
            ]
            block += ['<context>', *marked, '</context>']
        block += [f'<text>{unit.text}</text>', '</unit>']
        parts.append('\n'.join(block))
    prompt = '\n\n'.join(parts)
    return f'{command} {prompt}' if command else prompt


def writeUnitFiles(session_dir: Path, local_ids: dict[str, Unit], pyproject_path: Path) -> Path:
    """Write each unit alone to a file of a fresh directory, with the skill's config as pyproject.toml.

    A comment becomes `#` lines, a docstring a module docstring, and a page unit a Markdown file. The
    context of a unit is cut from a file at any line, so the context alone often fails to parse.

    Returns:
        The directory.
    """
    if session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True)
    shutil.copyfile(pyproject_path, session_dir / 'pyproject.toml')
    for local_id, unit in local_ids.items():
        if unit.kind in PAGE_KINDS:
            (session_dir / f'{local_id}.md').write_text(unit.text + '\n', encoding='utf-8')
        elif unit.kind is Kind.DOCSTRING:
            (session_dir / f'{local_id}.py').write_text(f'"""{unit.text}"""\n', encoding='utf-8')
        else:
            lines = textwrap.wrap(unit.text, UNIT_FILE_WIDTH)
            (session_dir / f'{local_id}.py').write_text(''.join(f'# {line}\n' for line in lines), encoding='utf-8')
    return session_dir


def parseAnswers(result_text: str, local_ids: dict[str, Unit], run_index: int) -> dict[UnitId, Prediction]:
    """Read the JSON array in the agent's reply into predictions, skipping each malformed object.

    The array is the text from the first `[` to the last `]`, so a code fence around the array is
    ignored.

    Raises:
        json.JSONDecodeError: The reply has no JSON array.
    """
    start, end = result_text.find('['), result_text.rfind(']')
    entries = json.loads(result_text[start : end + 1] if start >= 0 else result_text)
    answers = {}
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict) or entry.get('id') not in local_ids:
            continue
        try:
            action = Verdict(entry.get('action'))
        except ValueError:
            continue
        rules = entry.get('rules')
        new_text = entry.get('new_text')
        unit = local_ids[entry['id']]
        answers[unit.id] = Prediction(
            unit=unit.id,
            run=run_index,
            action=action,
            rules=tuple(str(rule) for rule in rules) if isinstance(rules, list) else (),
            new_text=new_text if isinstance(new_text, str) else None,
        )
    return answers


def buildPlugin(skill_dir: Path) -> Path:
    """Copy the skill directory into a plugin directory named by the skill's content digest.

    experiment/bugfind/run.py uses the same layout: `.claude-plugin/plugin.json` and
    `skills/narrative-python/`. A plugin directory that already exists for the digest is reused.
    """
    plugin_dir = CACHE_DIR / 'plugins' / hashSkill(skill_dir)
    if plugin_dir.exists():
        return plugin_dir
    staging = plugin_dir.with_name(plugin_dir.name + '.partial')
    if staging.exists():
        shutil.rmtree(staging)
    (staging / '.claude-plugin').mkdir(parents=True)
    (staging / '.claude-plugin' / 'plugin.json').write_text(f'{{"name": "{SKILL_NAME}"}}\n', encoding='utf-8')
    shutil.copytree(
        skill_dir,
        staging / 'skills' / SKILL_NAME,
        ignore=shutil.ignore_patterns('__pycache__', 'INSTALLED'),
    )
    staging.rename(plugin_dir)
    return plugin_dir


def hashSkill(skill_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.name != 'INSTALLED':
            digest.update(str(path.relative_to(skill_dir)).encode() + b'\0' + path.read_bytes())
    return digest.hexdigest()[:12]


def describeSkill(skill_dir: Path) -> str:
    """Describe the version of a skill directory: the commit, a mark for uncommitted changes, the digest.

    Returns:
        Such as `6ec9cf5, content 1a2b3c4d5e6f`. A directory outside git gets the digest alone.
    """
    content = f'content {hashSkill(skill_dir)}'
    head = subprocess.run(
        ['git', '-C', str(skill_dir), 'rev-parse', '--short', 'HEAD'],
        capture_output=True,
        text=True,
        check=False,
    )
    if head.returncode != 0:
        return content
    status = subprocess.run(
        ['git', '-C', str(skill_dir), 'status', '--porcelain', '--', '.'],
        capture_output=True,
        text=True,
        check=False,
    )
    dirty = ' with uncommitted changes' if status.stdout.strip() else ''
    return f'{head.stdout.strip()}{dirty}, {content}'


def displayPath(skill_dir: Path) -> str:
    return str(skill_dir.relative_to(REPO_ROOT)) if skill_dir.is_relative_to(REPO_ROOT) else str(skill_dir)


def writeConfidentialDetail(units: list[Unit], run: RunRecord, *, detail_path: Path) -> None:
    """Write the text, labels and predictions of each confidential unit of the run, one JSON line each.

    A report in eval/reports/ has counts alone for these units. With no confidential unit in the
    run, no file is written.

    Raises:
        OSError: The file could not be written.
    """
    by_id = {unit.id: unit for unit in units}
    detail = []
    for unit_id in dict.fromkeys(prediction.unit for prediction in run.predictions):
        unit = by_id[unit_id]
        if not unit.confidential:
            continue
        detail.append(
            {
                'id': unit.id,
                'text': unit.text,
                'origin': unit.origin.file,
                'labels': [labelRecord(label) for label in unit.labels],
                'predictions': [
                    {'run': prediction.run, 'action': prediction.action.value, 'rules': list(prediction.rules)}
                    for prediction in run.predictions
                    if prediction.unit == unit_id
                ],
            },
        )
    if not detail:
        return
    detail_path.parent.mkdir(parents=True, exist_ok=True)
    detail_path.write_text(''.join(json.dumps(entry, ensure_ascii=False) + '\n' for entry in detail), encoding='utf-8')
    print(f'wrote {detail_path}')


def printSummary(reports: list[Report]) -> None:
    for report in reports:
        run = report.run
        print(f'{run.predictor} {run.skill}: {report.unit_count} units, {len(run.predictions)} predictions')
        for matrix in report.matrices:
            if not matrix.scope.endswith('· overall'):
                continue
            cells = matrix.cells
            total = sum(cells.asTuple())
            print(
                f'  {matrix.tier.value} {matrix.scope}: TP {cells.tp} FN {cells.fn} FP {cells.fp} '
                f'TN {cells.tn} (sum {total}, {matrix.units} units, {matrix.conflicts} conflicts)',
            )


### vocabulary #########################################################################


@dataclass(frozen=True)
class SkillArm:
    """One skill a run asks with: the plugin to load, and the command the prompt opens with."""

    label: str
    display: str
    # the commit and the content digest of the skill, for the report
    version: str
    # None, and no command, for the agent with no skill
    plugin_dir: Path | None
    command: str | None
    # the skill's directory inside plugin_dir, the directory of verify.py
    skill_dir: Path | None
    # the verify.py that the session may run, for a --skill that ends in +verify
    verify_path: Path | None


@dataclass(frozen=True)
class AgentSettings:
    claude_binary: Path
    environment: dict[str, str]
    model: str
    effort: str
    arms: tuple[SkillArm, ...]
    # EDIT_MODE or REVIEW_MODE
    mode: str
    runs: int
    batch: int
    jobs: int
    work_dir: Path
    log_dir: Path
    private_log_dir: Path
    dry_run: bool


@dataclass(frozen=True)
class CallOutcome:
    answers: dict[UnitId, Prediction]
    cost_usd: float | None
    model: str | None
    # the edit mode's check of the diff reader against the grader's list of changes
    agreement: edits.Agreement | None = None


@dataclass(frozen=True)
class BatchOutcome:
    predictions: tuple[Prediction, ...]
    cost_usd: float | None
    model: str | None
    agreement: edits.Agreement | None = None


class AgentSetupError(RuntimeError):
    pass


if __name__ == '__main__':
    sys.exit(main())
