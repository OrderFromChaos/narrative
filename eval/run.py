"""Run a predictor over the labelled units of a split, and write the confusion-matrix report.

Predictors:
    deterministic  the skill's wording checks and agentverbs.py, through predictors.py. A unit with
                   any finding is a predicted rewrite. Confidential units are included.
    agent          a fresh `claude -p` session per batch of units, with the skill loaded as a
                   plugin and the prompt opening with the skill's command. The session has the
                   Skill tool, so a skill that requires another skill loads the other skill, as in
                   use. The prompt has each unit in the unit's file context, and no label.
                   Confidential units are skipped unless --allow-confidential.

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

Usage:
    $ uv run --python ~/.local/share/narrative/lintenv/bin/python eval/run.py deterministic
    $ uv run eval/run.py --tier gold agent --split dev
    $ uv run eval/run.py --tier gold agent --skill /tmp/skill-at-head --skill nar:python --split dev
    $ uv run eval/run.py agent --skill none --split dev --sample 20 --runs 1

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
import json
import random
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from types import ModuleType

from matrix import Prediction, Report, RunRecord, buildReport, writeReport, writeRun
from predictors import DeterministicChecks
from schema import (
    PRIVATE_DIR,
    REPO_ROOT,
    REPORTS_DIR,
    UNITS_DIR,
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
    agent.add_argument('--runs', type=int, default=DEFAULT_RUNS)
    agent.add_argument('--batch', type=int, default=DEFAULT_BATCH, help='units per claude session')
    agent.add_argument('--jobs', type=int, default=DEFAULT_JOBS, help='claude sessions at once')
    agent.add_argument('--model', help='default: the model of experiment/bugfind/run.py')
    agent.add_argument('--effort', help='default: the effort of experiment/bugfind/run.py')
    agent.add_argument('--config-dir', type=Path, help='default: the login of experiment/bugfind/run.py')
    agent.add_argument('--allow-confidential', action='store_true', help='send confidential units to the API')
    agent.add_argument('--dry-run', action='store_true', help='write the prompts and call no model')
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
                print(f'run.py: {exc}. Run with the lint venv, as in the module docstring', file=sys.stderr)
                return EXIT_UNUSABLE
            runs = [predictDeterministic(checks, selected, split=arguments.split)]
            incomplete = False
        case 'agent':
            skipped = [unit for unit in selected if unit.confidential and not arguments.allow_confidential]
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
        for path in writeReport(arguments.reports / f'{stamp}-compare-{arguments.split}', reports):
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
    claude_binary: Path = bugfind.findNewestClaude() if not arguments.dry_run else Path('claude')
    environment: dict[str, str] = bugfind.buildClaudeEnvironment(config_dir)
    work_dir = CACHE_DIR / 'work'
    work_dir.mkdir(parents=True, exist_ok=True)
    return AgentSettings(
        claude_binary=claude_binary,
        environment=environment,
        model=arguments.model or bugfind.MODEL,
        effort=arguments.effort or bugfind.EFFORT,
        arms=tuple(arms),
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
        return SkillArm(label=NO_SKILL, display=NO_SKILL, version='none', plugin_dir=None, command=None)
    if raw_skill.startswith(f'{PLUGIN_NAME}:'):
        name = raw_skill.removeprefix(f'{PLUGIN_NAME}:')
        if not (SKILLS_DIR / name / 'SKILL.md').is_file():
            raise AgentSetupError(f'{SKILLS_DIR} has no skill {name}. Run python3 build_skills.py')
        return SkillArm(
            label=name,
            display=raw_skill,
            version=describeSkill(SKILLS_DIR),
            plugin_dir=buildRepoPlugin(),
            command=f'/{raw_skill}',
        )
    skill_dir = Path(raw_skill).resolve()
    if not (skill_dir / 'SKILL.md').is_file():
        raise AgentSetupError(f'{skill_dir} has no SKILL.md')
    return SkillArm(
        label=skill_dir.name,
        display=displayPath(skill_dir),
        version=describeSkill(skill_dir),
        plugin_dir=buildPlugin(skill_dir),
        command=f'/{SKILL_NAME}:{SKILL_NAME}',
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

    Units are sorted by group, so a batch has neighbouring units of one file.

    Returns:
        The run, with the count of unit and run pairs that got no valid answer after the retry.
    """
    ordered = sorted(units, key=lambda unit: (unit.group, unit.origin.line or 0, unit.id))
    batches = [ordered[start : start + settings.batch] for start in range(0, len(ordered), settings.batch)]
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
    return RunRecord(
        predictor='agent' if arm.command else 'agent-no-skill',
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
    for attempt in range(2):
        pending = [unit for unit in batch if unit.id not in answered]
        if not pending or (attempt and settings.dry_run):
            break
        async with limit:
            outcome = await callAgent(settings, arm, pending, run_index, f'{name}-try{attempt}')
        answered.update(outcome.answers)
        cost += outcome.cost_usd or 0.0
        model = outcome.model or model
    return BatchOutcome(predictions=tuple(answered.values()), cost_usd=cost or None, model=model)


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
    local_ids = {f'u{index:02d}': unit for index, unit in enumerate(units, start=1)}
    prompt = buildPrompt(local_ids, command=arm.command)
    log_dir = settings.private_log_dir if any(unit.confidential for unit in units) else settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f'{name}.prompt.txt').write_text(prompt, encoding='utf-8')
    if settings.dry_run:
        return CallOutcome(answers={}, cost_usd=None, model=None)

    command = [
        str(settings.claude_binary), '-p', prompt,
        '--model', settings.model,
        '--effort', settings.effort,
        '--restricted',
        '--tools', 'Skill' if arm.command else '',
        '--strict-mcp-config',
        '--permission-prompts', 'none',
        '--output-format', 'json',
    ]  # fmt: skip
    if arm.plugin_dir is not None:
        command += ['--plugin-dir', str(arm.plugin_dir)]
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=settings.work_dir,
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
        return CallOutcome(answers={}, cost_usd=None, model=None)
    (log_dir / f'{name}.output.json').write_bytes(stdout)
    if process.returncode != 0:
        print(f'{name}: claude exited {process.returncode}: {stderr.decode(errors="replace")[-300:]}', file=sys.stderr)
        return CallOutcome(answers={}, cost_usd=None, model=None)
    try:
        result = json.loads(stdout)
        answers = parseAnswers(str(result.get('result', '')), local_ids, run_index)
    except (json.JSONDecodeError, AttributeError) as exc:
        print(f'{name}: unparsable output: {exc}', file=sys.stderr)
        return CallOutcome(answers={}, cost_usd=None, model=None)
    cost = result.get('total_cost_usd')
    usage = result.get('modelUsage')
    model = next(iter(usage), None) if isinstance(usage, dict) else None
    return CallOutcome(answers=answers, cost_usd=float(cost) if isinstance(cost, int | float) else None, model=model)


def buildPrompt(local_ids: dict[str, Unit], *, command: str | None) -> str:
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
        f'{rules} `new_text` is the reworded unit for a rewrite, and null otherwise. Read and run no file.',
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


@dataclass(frozen=True)
class AgentSettings:
    claude_binary: Path
    environment: dict[str, str]
    model: str
    effort: str
    arms: tuple[SkillArm, ...]
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


@dataclass(frozen=True)
class BatchOutcome:
    predictions: tuple[Prediction, ...]
    cost_usd: float | None
    model: str | None


class AgentSetupError(RuntimeError):
    pass


if __name__ == '__main__':
    sys.exit(main())
