"""Score a run file against the labelled units, and write the confusion matrices as Markdown and HTML.

A run file has the predictions of one predictor with one skill, one per unit and run. The start of
a run file of 814 predictions, with the first two:

    {
     "predictor": "deterministic",
     "skill": "skill",
     "skill_commit": "6ec9cf5, content fde9d1b38713",
     "model": null,
     "runs": 1,
     "split": "all",
     "started": "2026-10-24 11:16",
     "cost_usd": null,
     "skipped_confidential": 0,
     "unanswered": 0,
     "predictions": [
      {
       "unit": "0012d775d7aede11",
       "run": 0,
       "action": "rewrite",
       "rules": [
        "NAR016",
        "NAR017",
        "NAR018"
       ],
       "new_text": null
      },
      {
       "unit": "00190dc4ebd7c84c",
       "run": 0,
       "action": "keep",
       "rules": [],
       "new_text": null
      },
    ...

Labels are pass or fail. A unit is in the positive class when the unit fails under the current
label: a cut or a rewrite. For one rule,
only the units with the rule in the label's `judged` are counted, and a unit is positive when the
rule is in the label's `rules`. A prediction is positive when the predicted action is a cut or a
rewrite, or, for one rule, when the rule is in the prediction's `rules`. The counts of every run
add up, so 20 units and 3 runs fill 60 cells.

Within each tier, every context level has separate matrices: one for all units of the level, one
per language and one per judged rule. A fact rule is any rule outside CONTEXT_FREE_RULES. A reader
checks a fact rule against the unit's surroundings, so a fact rule gets no matrix at context level
none.

Every count ratio has a Wilson 95% interval. F1, balanced accuracy and MCC (Matthews correlation
coefficient) have a percentile interval from 1000 multinomial resamples of the four cells.

The human ceiling is the user's agreement with the user's earlier gold labels, from the blind
re-labels of `label.py --audit`. In a comparison of two runs, a ratio change smaller than the label
disagreement rate, or with overlapping intervals, is reported as no difference.

A confidential unit is in the counts, and nowhere else in a report.

Usage:
    $ uv run eval/matrix.py ~/.cache/narrative-eval/runs/20261024-101500-deterministic-all.json
    $ uv run eval/matrix.py RUN_A.json RUN_B.json

Exit codes:
    0  the report was written
    2  a run file or a unit file was unusable
"""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import sys
import time
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from schema import (
    PRIVATE_DIR,
    REPORTS_DIR,
    UNITS_DIR,
    Conflict,
    ContextLevel,
    Tier,
    Unit,
    UnitFileError,
    UnitId,
    Verdict,
    asCodes,
    asMapping,
    asOptionalText,
    asText,
    currentLabel,
    failing,
    loadUnits,
)


# the rules a reader can check on the sentence alone
CONTEXT_FREE_RULES = frozenset({
    'NAR012', 'NAR013', 'NAR014', 'NAR015', 'NAR016', 'NAR017', 'NAR018', 'NAR020', 'NAR021', 'NAR022',
})  # fmt: skip
Z_95 = 1.959963984540054
BOOTSTRAP_RESAMPLES = 1000
DISAGREEMENTS_SHOWN = 40
EXIT_SUCCESS = 0
EXIT_UNUSABLE = 2


def main() -> int:
    """Read one or two run files and write the report, or the comparison of the two runs.

    Returns:
        0 when the report was written, 2 when an input was unusable.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('runs', nargs='+', type=Path, help='one run file, or two to compare')
    parser.add_argument('--units', type=Path, default=UNITS_DIR, help='the public unit directory')
    parser.add_argument('--private', type=Path, default=PRIVATE_DIR, help='the private store, merged when present')
    parser.add_argument('--reports', type=Path, default=REPORTS_DIR)
    arguments = parser.parse_args()

    if len(arguments.runs) > 2:
        print('matrix.py: give one run file, or two to compare', file=sys.stderr)
        return EXIT_UNUSABLE
    try:
        units = loadUnits(arguments.units, arguments.private)
        runs = [readRun(run_path) for run_path in arguments.runs]
    except (OSError, UnitFileError, KeyError, TypeError, ValueError) as exc:
        print(f'matrix.py: {exc}', file=sys.stderr)
        return EXIT_UNUSABLE

    reports = [buildReport(units, run) for run in runs]
    stem = arguments.reports / f'{time.strftime("%Y%m%d-%H%M%S")}-{reportName(reports)}'
    for path in writeReport(stem, reports):
        print(f'wrote {path}')
    return EXIT_SUCCESS


def readRun(run_path: Path) -> RunRecord:
    """Parse a run file written by `writeRun()`.

    Raises:
        KeyError: A field is absent.
        TypeError: A field has the wrong JSON type.
        ValueError: An action is not keep, cut or rewrite.
    """
    record = asMapping(json.loads(run_path.read_text(encoding='utf-8')))
    raw_predictions = record['predictions']
    if not isinstance(raw_predictions, list):
        raise TypeError('predictions is not a list')
    predictions = []
    for raw in raw_predictions:
        prediction = asMapping(raw)
        run_index = prediction['run']
        if not isinstance(run_index, int):
            raise TypeError(f'run {run_index!r} is not an integer')
        predictions.append(
            Prediction(
                unit=UnitId(asText(prediction['unit'])),
                run=run_index,
                action=Verdict(prediction['action']),
                rules=asCodes(prediction['rules']),
                new_text=asOptionalText(prediction.get('new_text')),
            ),
        )
    cost = record.get('cost_usd')
    return RunRecord(
        predictor=asText(record['predictor']),
        skill=asText(record['skill']),
        skill_commit=asText(record['skill_commit']),
        model=asOptionalText(record.get('model')),
        runs=int(str(record['runs'])),
        split=asText(record['split']),
        started=asText(record['started']),
        cost_usd=float(cost) if isinstance(cost, int | float) else None,
        skipped_confidential=int(str(record.get('skipped_confidential', 0))),
        unanswered=int(str(record.get('unanswered', 0))),
        predictions=tuple(predictions),
    )


def writeRun(run_path: Path, run: RunRecord, confidential: set[UnitId]) -> None:
    """Write the run as indented JSON, leaving out the rewrite of each confidential unit.

    A rewrite of a confidential unit contains most of the unit's text.

    Raises:
        OSError: The file could not be written.
    """
    run_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        'predictor': run.predictor,
        'skill': run.skill,
        'skill_commit': run.skill_commit,
        'model': run.model,
        'runs': run.runs,
        'split': run.split,
        'started': run.started,
        'cost_usd': run.cost_usd,
        'skipped_confidential': run.skipped_confidential,
        'unanswered': run.unanswered,
        'predictions': [
            {
                'unit': prediction.unit,
                'run': prediction.run,
                'action': prediction.action.value,
                'rules': list(prediction.rules),
                'new_text': None if prediction.unit in confidential else prediction.new_text,
            }
            for prediction in run.predictions
        ],
    }
    run_path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


def buildReport(units: list[Unit], run: RunRecord) -> Report:
    """Count every matrix of the run: per tier and context level, overall, per language and per judged rule.

    A unit with no prediction in the run is left out. A scope with no counted unit gets no matrix, and
    neither does a fact rule at context level none.
    """
    by_id = {unit.id: unit for unit in units}
    predictions = [prediction for prediction in run.predictions if prediction.unit in by_id]
    predicted_units = [by_id[unit_id] for unit_id in dict.fromkeys(prediction.unit for prediction in predictions)]
    matrices = []
    for tier in Tier:
        tiered = [unit for unit in predicted_units if any(label.tier is tier for label in unit.labels)]
        if not tiered:
            continue
        for level in ContextLevel:
            leveled = [unit for unit in tiered if unit.context_level is level]
            languages = sorted({unit.language.value for unit in leveled})
            rules = sorted(
                {rule for unit in leveled for label in unit.labels if label.tier is tier for rule in label.judged},
            )
            if level is ContextLevel.NONE:
                rules = [rule for rule in rules if rule in CONTEXT_FREE_RULES]
            scopes = [
                Scope(f'{level.value} · overall', level=level),
                *(Scope(f'{level.value} · language {name}', level=level, language=name) for name in languages),
                *(Scope(f'{level.value} · rule {rule}', level=level, rule=rule) for rule in rules),
            ]
            for scope in scopes:
                matrix = countMatrix(by_id, predictions, tier=tier, scope=scope)
                if matrix.units:
                    matrices.append(matrix)
    disagreements = findDisagreements(by_id, predictions)
    return Report(
        run=run,
        matrices=tuple(matrices),
        ceiling=measureAgreement(units),
        unit_count=len(predicted_units),
        confidential_count=sum(unit.confidential for unit in predicted_units),
        disagreements=tuple(disagreements),
    )


def countMatrix(
    by_id: Mapping[UnitId, Unit],
    predictions: list[Prediction],
    *,
    tier: Tier,
    scope: Scope,
) -> Matrix:
    """Add every prediction whose unit has a current label in the tier and falls in the scope to the four cells.

    Returns:
        The cells, the number of units counted, and the number left out by a conflict.
    """
    cells: Counter[str] = Counter()
    counted: set[UnitId] = set()
    conflicted: set[UnitId] = set()
    for prediction in predictions:
        unit = by_id[prediction.unit]
        if unit.context_level is not scope.level:
            continue
        if scope.language is not None and unit.language.value != scope.language:
            continue
        label = currentLabel(unit, tier, rule=scope.rule)
        if label is None:
            continue
        if isinstance(label, Conflict):
            conflicted.add(unit.id)
            continue
        labelled = failing(label, rule=scope.rule)
        predicted = prediction.action is not Verdict.KEEP if scope.rule is None else scope.rule in prediction.rules
        cells[('T' if labelled == predicted else 'F') + ('P' if predicted else 'N')] += 1
        counted.add(unit.id)
    return Matrix(
        tier=tier,
        scope=scope.name,
        cells=Cells(tp=cells['TP'], fn=cells['FN'], fp=cells['FP'], tn=cells['TN']),
        units=len(counted),
        conflicts=len(conflicted),
    )


def findDisagreements(by_id: Mapping[UnitId, Unit], predictions: list[Prediction]) -> list[Disagreement]:
    """List each public unit that a prediction got wrong, by the current label of the unit's highest tier.

    Returns:
        One entry per unit with the count of runs that disagreed, false negatives first.
    """
    missed: Counter[UnitId] = Counter()
    for prediction in predictions:
        unit = by_id[prediction.unit]
        tier = highestTier(unit)
        label = currentLabel(unit, tier, rule=None) if tier else None
        if unit.confidential or label is None or isinstance(label, Conflict):
            continue
        if failing(label, rule=None) != (prediction.action is not Verdict.KEEP):
            missed[unit.id] += 1
    disagreements = []
    for unit_id, runs in missed.items():
        unit = by_id[unit_id]
        tier = highestTier(unit)
        label = currentLabel(unit, tier, rule=None) if tier else None
        if tier is None or label is None or isinstance(label, Conflict):
            continue
        disagreements.append(
            Disagreement(
                unit_id=unit_id,
                tier=tier,
                text=unit.text,
                labelled=label.verdict.value,
                missed_runs=runs,
                false_negative=label.verdict is not Verdict.KEEP,
            ),
        )
    return sorted(disagreements, key=lambda entry: (not entry.false_negative, list(Tier).index(entry.tier)))


def highestTier(unit: Unit) -> Tier | None:
    for tier in Tier:
        if currentLabel(unit, tier, rule=None) is not None:
            return tier
    return None


def measureAgreement(units: Iterable[Unit]) -> Agreement | None:
    """Compare each blind re-label with the unit's gold label from before the re-label.

    The earlier label is the latest gold label that is not partial, not an audit, and dated before
    the re-label. Agreement is on pass or fail. A change from pass to fail is stricter, and from fail
    to pass is looser.

    Returns:
        The agreement over every pair, and per month of the earlier label, or None with no re-label.
    """
    pairs: list[tuple[str, bool, bool]] = []
    for unit in units:
        for audit in (label for label in unit.labels if label.audit and label.tier is Tier.GOLD):
            earlier = [
                label
                for label in unit.labels
                if label.tier is Tier.GOLD and not label.audit and not label.partial and label.date < audit.date
            ]
            if earlier:
                old = max(earlier, key=lambda label: label.date)
                pairs.append((old.date[:7], failing(old, rule=None), failing(audit, rule=None)))
    return summariseAgreement(pairs) if pairs else None


def summariseAgreement(pairs: list[tuple[str, bool, bool]]) -> Agreement:
    """Measure agreement over (month of the earlier label, earlier fails, re-label fails) pairs.

    Returns:
        The agreement over every pair and per month, and the count of stricter and looser changes.
    """
    months = sorted({month for month, _, _ in pairs})
    return Agreement(
        overall=agreementOf([(old, new) for _, old, new in pairs]),
        by_month=tuple(
            (month, agreementOf([(old, new) for pair_month, old, new in pairs if pair_month == month]))
            for month in months
        ),
        stricter=sum(new > old for _, old, new in pairs),
        looser=sum(new < old for _, old, new in pairs),
    )


def agreementOf(pairs: list[tuple[bool, bool]]) -> PairAgreement:
    """Cohen's kappa and percent agreement on pass or fail, over (earlier fails, re-label fails) pairs.

    Returns:
        Kappa is None when every label on both sides is in one class. Kappa is undefined then.
    """
    total = len(pairs)
    agreed = sum(old == new for old, new in pairs)
    old_positive = sum(old for old, _ in pairs) / total
    new_positive = sum(new for _, new in pairs) / total
    expected = old_positive * new_positive + (1 - old_positive) * (1 - new_positive)
    kappa = None if expected == 1 else (agreed / total - expected) / (1 - expected)
    return PairAgreement(pairs=total, agreed=agreed, kappa=kappa)


def ratiosOf(matrix: Matrix) -> dict[str, Ratio]:
    """Compute every ratio of one matrix, with an interval for each ratio.

    Returns:
        The ratios by name. A ratio whose denominator is 0 has value None.
    """
    tp, fn, fp, tn = matrix.cells.tp, matrix.cells.fn, matrix.cells.fp, matrix.cells.tn
    total = tp + fn + fp + tn
    seed = f'{matrix.tier.value}/{matrix.scope}'
    return {
        'sensitivity': countRatio(tp, tp + fn),
        'specificity': countRatio(tn, tn + fp),
        'precision': countRatio(tp, tp + fp),
        'NPV': countRatio(tn, tn + fn),
        'accuracy': countRatio(tp + tn, total),
        'prevalence': countRatio(tp + fn, total),
        'F1': resampledRatio(matrix.cells, f1Score, seed, counts=(2 * tp, 2 * tp + fp + fn)),
        'balanced accuracy': resampledRatio(matrix.cells, balancedAccuracy, seed),
        'MCC': resampledRatio(matrix.cells, matthewsCorrelation, seed),
    }


def countRatio(successes: int, trials: int) -> Ratio:
    if trials == 0:
        return Ratio(value=None, low=None, high=None, counts=(successes, trials))
    low, high = wilsonInterval(successes, trials)
    return Ratio(value=successes / trials, low=low, high=high, counts=(successes, trials))


def wilsonInterval(successes: int, trials: int) -> tuple[float, float]:
    share = successes / trials
    spread = Z_95 * Z_95 / trials
    centre = (share + spread / 2) / (1 + spread)
    half = Z_95 * math.sqrt(share * (1 - share) / trials + spread / (4 * trials)) / (1 + spread)
    return max(0.0, centre - half), min(1.0, centre + half)


def resampledRatio(
    cells: Cells,
    metric: Callable[[Cells], float | None],
    seed: str,
    *,
    counts: tuple[int, int] | None = None,
) -> Ratio:
    """Compute a metric of the cells, with a percentile interval from multinomial resamples of the cells.

    Resamples where the metric is undefined are left out of the interval.
    """
    value = metric(cells)
    total = cells.tp + cells.fn + cells.fp + cells.tn
    if value is None or total == 0:
        return Ratio(value=value, low=None, high=None, counts=counts)
    generator = random.Random(seed)
    weights = list(cells.asTuple())
    resampled = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        drawn = generator.choices(range(4), weights=weights, k=total)
        sample = Cells(tp=drawn.count(0), fn=drawn.count(1), fp=drawn.count(2), tn=drawn.count(3))
        if (sampled := metric(sample)) is not None:
            resampled.append(sampled)
    resampled.sort()
    low = resampled[int(0.025 * (len(resampled) - 1))] if resampled else None
    high = resampled[int(0.975 * (len(resampled) - 1))] if resampled else None
    return Ratio(value=value, low=low, high=high, counts=counts)


def f1Score(cells: Cells) -> float | None:
    denominator = 2 * cells.tp + cells.fp + cells.fn
    return 2 * cells.tp / denominator if denominator else None


def balancedAccuracy(cells: Cells) -> float | None:
    if not (cells.tp + cells.fn and cells.tn + cells.fp):
        return None
    return (cells.tp / (cells.tp + cells.fn) + cells.tn / (cells.tn + cells.fp)) / 2


def matthewsCorrelation(cells: Cells) -> float | None:
    tp, fn, fp, tn = cells.asTuple()
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / denominator if denominator else None


def reportName(reports: list[Report]) -> str:
    first = reports[0].run
    return f'compare-{first.split}' if len(reports) > 1 else f'{first.predictor}-{first.split}'


def writeReport(stem: Path, reports: list[Report]) -> list[Path]:
    stem.parent.mkdir(parents=True, exist_ok=True)
    markdown_path = stem.with_suffix('.md')
    html_path = stem.with_suffix('.html')
    markdown_path.write_text(renderMarkdown(reports), encoding='utf-8')
    html_path.write_text(renderHtml(reports), encoding='utf-8')
    return [markdown_path, html_path]


def renderMarkdown(reports: list[Report]) -> str:
    """Render one report, or two with the change in every cell and ratio, as Markdown.

    A 2x2 per scope: the cells, sensitivity and specificity on the right, precision and NPV along
    the bottom, and accuracy in the corner. The other ratios follow on one line.
    """
    lines = ['# Unit eval', '']
    for index, report in enumerate(reports):
        lines += headerLines(report, label=armLabel(index, reports))
    lines += [ceilingLine(reports[0].ceiling), '']
    if len(reports) == 2:
        lines += compareMarkdown(reports[0], reports[1])
        return '\n'.join(lines)

    report = reports[0]
    for tier in Tier:
        tiered = [matrix for matrix in report.matrices if matrix.tier is tier]
        if not tiered:
            continue
        lines += [f'## {tier.value}', '']
        for matrix in tiered:
            lines += matrixMarkdown(matrix)
    if report.disagreements:
        lines += [
            '## Disagreements',
            '',
            'Public units the predictor got wrong, false negatives first.',
            '',
        ]
        lines += ['| tier | label | runs missed | text |', '|---|---|---|---|']
        for entry in report.disagreements[:DISAGREEMENTS_SHOWN]:
            text = entry.text.replace('|', '\\|').replace('\n', ' ')
            lines.append(f'| {entry.tier.value} | {entry.labelled} | {entry.missed_runs} | {shorten(text, 140)} |')
        if len(report.disagreements) > DISAGREEMENTS_SHOWN:
            lines.append(f'\n{len(report.disagreements) - DISAGREEMENTS_SHOWN} more not shown.')
        lines.append('')
    return '\n'.join(lines)


def headerLines(report: Report, *, label: str) -> list[str]:
    run = report.run
    cost = f'{run.cost_usd:.2f} USD' if run.cost_usd is not None else 'none'
    return [
        f'**{label}** {run.predictor}, skill `{run.skill}` at {run.skill_commit}, model {run.model or "none"}',
        '',
        f'- split {run.split}, {run.runs} run(s), started {run.started}, cost {cost}',
        f'- {report.unit_count} units, {len(run.predictions)} predictions, {run.unanswered} unanswered, '
        f'{report.confidential_count} confidential units counted, '
        f'{run.skipped_confidential} confidential units skipped',
        '',
    ]


def armLabel(index: int, reports: list[Report]) -> str:
    return 'Run' if len(reports) == 1 else f'Run {"AB"[index]}'


def ceilingLine(ceiling: Agreement | None) -> str:
    if ceiling is None:
        return 'Human ceiling: no blind re-label yet. Run `eval/label.py --audit`.'
    overall = ceiling.overall
    kappa = f'{overall.kappa:.2f}' if overall.kappa is not None else 'undefined'
    months = ', '.join(
        f'{month}: kappa {agreement.kappa:.2f}' if agreement.kappa is not None else f'{month}: kappa undefined'
        for month, agreement in ceiling.by_month
    )
    return (
        f'Human ceiling: kappa {kappa}, agreement {overall.agreed / overall.pairs:.0%} '
        f'({overall.agreed}/{overall.pairs}) on blind re-labels, {ceiling.stricter} stricter and '
        f'{ceiling.looser} looser. By month of the earlier label: {months}.'
    )


def matrixMarkdown(matrix: Matrix) -> list[str]:
    """Render the 2x2 of one scope as a Markdown table, then the other ratios on one line.

    Raises:
        Nothing.
    """
    ratios = ratiosOf(matrix)
    flagged = matrix.scope.partition(' · rule ')[2] or 'fail'
    conflicts = f', {matrix.conflicts} left out by a conflict' if matrix.conflicts else ''
    extras = ' · '.join(
        f'{name} {formatRatio(ratios[name])}' for name in ('prevalence', 'F1', 'balanced accuracy', 'MCC')
    )
    cells = matrix.cells
    return [
        f'### {matrix.tier.value} · {matrix.scope} ({matrix.units} units{conflicts})',
        '',
        f'|  | predicted {flagged} | predicted not |  |',
        '|---|---|---|---|',
        f'| **labelled {flagged}** | TP {cells.tp} | FN {cells.fn} '
        f'| sensitivity {formatRatio(ratios["sensitivity"])} |',
        f'| **labelled not** | FP {cells.fp} | TN {cells.tn} | specificity {formatRatio(ratios["specificity"])} |',
        f'|  | precision {formatRatio(ratios["precision"])} | NPV {formatRatio(ratios["NPV"])} '
        f'| accuracy {formatRatio(ratios["accuracy"])} |',
        '',
        extras,
        '',
    ]


def compareMarkdown(first: Report, second: Report) -> list[str]:
    """Render, per scope that both runs have, each cell and ratio of A and B and the change.

    A ratio change is `no difference` when the two intervals overlap or the change is under the
    label disagreement rate of the human ceiling.
    """
    noise = labelNoise(first.ceiling)
    second_matrices = {(matrix.tier, matrix.scope): matrix for matrix in second.matrices}
    lines = []
    for matrix in first.matrices:
        other = second_matrices.get((matrix.tier, matrix.scope))
        if other is None:
            continue
        lines += [
            f'### {matrix.tier.value} · {matrix.scope}',
            '',
            '|  | A | B | change |',
            '|---|---|---|---|',
        ]
        for name, before, after in zip(
            ('TP', 'FN', 'FP', 'TN'),
            matrix.cells.asTuple(),
            other.cells.asTuple(),
            strict=True,
        ):
            lines.append(f'| {name} | {before} | {after} | {after - before:+d} |')
        ratios_before, ratios_after = ratiosOf(matrix), ratiosOf(other)
        for name, before_ratio in ratios_before.items():
            after_ratio = ratios_after[name]
            change = describeChange(before_ratio, after_ratio, noise)
            lines.append(f'| {name} | {formatRatio(before_ratio)} | {formatRatio(after_ratio)} | {change} |')
        lines.append('')
    return lines


def labelNoise(ceiling: Agreement | None) -> float:
    return 0.0 if ceiling is None else 1 - ceiling.overall.agreed / ceiling.overall.pairs


def describeChange(before: Ratio, after: Ratio, noise: float) -> str:
    if before.value is None or after.value is None:
        return 'n/a'
    change = after.value - before.value
    overlap = (
        before.low is None
        or before.high is None
        or after.low is None
        or after.high is None
        or (after.low <= before.high and before.low <= after.high)
    )
    if overlap or abs(change) < noise:
        return f'{change:+.3f}, no difference'
    return f'{change:+.3f}'


def formatRatio(ratio: Ratio) -> str:
    counts = f' ({ratio.counts[0]}/{ratio.counts[1]})' if ratio.counts else ''
    if ratio.value is None:
        return f'n/a{counts}'
    interval = f' [{ratio.low:.3f}, {ratio.high:.3f}]' if ratio.low is not None and ratio.high is not None else ''
    return f'{ratio.value:.3f}{counts}{interval}'


def renderHtml(reports: list[Report]) -> str:
    """Render the content of `renderMarkdown()` as one HTML page with inline styles.

    Each scope's 2x2 is a grid: the four cells, the ratio column on the right, the ratio row along
    the bottom and accuracy in the corner.
    """
    body = ['<h1>Unit eval</h1>']
    for index, report in enumerate(reports):
        body.append(
            f'<section class="header">{markdownToHtml(headerLines(report, label=armLabel(index, reports)))}</section>',
        )
    body.append(f'<div class="ceiling">{markdownToHtml([ceilingLine(reports[0].ceiling)])}</div>')
    if len(reports) == 2:
        body.append(tablesToHtml(compareMarkdown(reports[0], reports[1])))
    else:
        report = reports[0]
        for tier in Tier:
            tiered = [matrix for matrix in report.matrices if matrix.tier is tier]
            if tiered:
                body.append(f'<h2>{tier.value}</h2><div class="grid">')
                body.extend(matrixHtml(matrix) for matrix in tiered)
                body.append('</div>')
        if report.disagreements:
            rows = ''.join(
                f'<tr><td>{entry.tier.value}</td><td>{html.escape(entry.labelled)}</td>'
                f'<td>{entry.missed_runs}</td><td>{html.escape(entry.text)}</td></tr>'
                for entry in report.disagreements[:DISAGREEMENTS_SHOWN]
            )
            body.append(
                '<h2>Disagreements</h2><p>Public units the predictor got wrong, '
                'false negatives first.</p><table class="list"><tr><th>tier</th><th>label</th>'
                f'<th>runs missed</th><th>text</th></tr>{rows}</table>',
            )
    return PAGE.replace('BODY', '\n'.join(body))


def matrixHtml(matrix: Matrix) -> str:
    """Render the 2x2 of one scope as an HTML figure, in the layout of `matrixMarkdown()`.

    Raises:
        Nothing.
    """
    ratios = ratiosOf(matrix)
    cells = matrix.cells
    flagged = matrix.scope.partition(' · rule ')[2] or 'fail'
    extras = ''.join(
        f'<li>{name} {html.escape(formatRatio(ratios[name]))}</li>'
        for name in ('prevalence', 'F1', 'balanced accuracy', 'MCC')
    )
    conflicts = f', {matrix.conflicts} left out by a conflict' if matrix.conflicts else ''

    def ratioCell(name: str, css: str) -> str:
        return f'<td class="{css}"><b>{name}</b><br>{html.escape(formatRatio(ratios[name]))}</td>'

    return (
        f'<figure><figcaption>{matrix.scope} ({matrix.units} units{conflicts})</figcaption><table class="matrix">'
        f'<tr><th></th><th>predicted {flagged}</th><th>predicted not</th><th></th></tr>'
        f'<tr><th>labelled {flagged}</th><td class="hit">TP<br><b>{cells.tp}</b></td>'
        f'<td class="miss">FN<br><b>{cells.fn}</b></td>{ratioCell("sensitivity", "ratio")}</tr>'
        f'<tr><th>labelled not</th><td class="miss">FP<br><b>{cells.fp}</b></td>'
        f'<td class="hit">TN<br><b>{cells.tn}</b></td>{ratioCell("specificity", "ratio")}</tr>'
        f'<tr><th></th>{ratioCell("precision", "ratio")}{ratioCell("NPV", "ratio")}'
        f'{ratioCell("accuracy", "corner")}</tr>'
        f'</table><ul>{extras}</ul></figure>'
    )


def markdownToHtml(lines: list[str]) -> str:
    # the header lines have only **bold**, `code` and `- ` list items
    parts = []
    for line in lines:
        if not line:
            continue
        escaped = html.escape(line)
        while '**' in escaped:
            escaped = escaped.replace('**', '<b>', 1).replace('**', '</b>', 1)
        while '`' in escaped:
            escaped = escaped.replace('`', '<code>', 1).replace('`', '</code>', 1)
        parts.append(f'<ul><li>{escaped[2:]}</li></ul>' if line.startswith('- ') else f'<p>{escaped}</p>')
    return ''.join(parts).replace('</ul><ul>', '')


def tablesToHtml(lines: list[str]) -> str:
    # compareMarkdown() writes `### ` headings and pipe tables, and nothing else
    parts = []
    rows: list[str] = []
    for line in [*lines, '']:
        if line.startswith('|') and not line.startswith('|---'):
            cells = [html.escape(cell.strip()) for cell in line.strip('|').split('|')]
            rows.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
            continue
        if rows:
            parts.append(f'<table class="list">{"".join(rows)}</table>')
            rows = []
        if line.startswith('### '):
            parts.append(f'<h3>{html.escape(line[4:])}</h3>')
    return '\n'.join(parts)


def shorten(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 3] + '...'


### vocabulary #########################################################################

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Unit eval</title>
<style>
:root { --ink: #1d1f23; --muted: #5d636e; --paper: #fbfbfa; --card: #ffffff; --line: #d9dbe0;
        --hit: #e3f2e6; --miss: #f8e3e1; --ratio: #eef1f7; --corner: #f3ecd9; }
@media (prefers-color-scheme: dark) {
  :root { --ink: #e6e7ea; --muted: #a2a8b3; --paper: #16181c; --card: #1f2227; --line: #3a3f47;
          --hit: #1f3a27; --miss: #46262a; --ratio: #262c38; --corner: #3a3322; }
}
body { margin: 0 auto; max-width: 1180px; padding: 16px; background: var(--paper); color: var(--ink);
       font: 14px/1.45 system-ui, sans-serif; }
h1 { font-size: 22px; } h2 { font-size: 18px; margin-top: 28px; } h3 { font-size: 15px; }
code { font-family: ui-monospace, monospace; font-size: 13px; }
.header, .ceiling { color: var(--muted); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }
figure { margin: 0; padding: 10px; background: var(--card); border: 1px solid var(--line); border-radius: 6px; }
figcaption { font-weight: 600; margin-bottom: 6px; }
table { border-collapse: collapse; width: 100%; }
.matrix td, .matrix th { border: 1px solid var(--line); padding: 5px; text-align: center; font-size: 12px; }
.matrix th { font-weight: 500; color: var(--muted); }
.hit { background: var(--hit); } .miss { background: var(--miss); }
.ratio { background: var(--ratio); } .corner { background: var(--corner); }
figure ul { margin: 6px 0 0; padding-left: 18px; color: var(--muted); font-size: 12px; }
.list td, .list th { border-bottom: 1px solid var(--line); padding: 4px 6px; text-align: left; vertical-align: top; }
@media (max-width: 480px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
BODY
</body>
</html>
"""


@dataclass(frozen=True)
class Prediction:
    unit: UnitId
    run: int
    action: Verdict
    rules: tuple[str, ...]
    new_text: str | None


@dataclass(frozen=True)
class RunRecord:
    predictor: str
    skill: str
    skill_commit: str
    model: str | None
    runs: int
    split: str
    # YYYY-MM-DD HH:MM, local time
    started: str
    cost_usd: float | None
    skipped_confidential: int
    unanswered: int
    predictions: tuple[Prediction, ...]


@dataclass(frozen=True)
class Scope:
    name: str
    level: ContextLevel
    language: str | None = None
    rule: str | None = None


@dataclass(frozen=True)
class Cells:
    tp: int
    fn: int
    fp: int
    tn: int

    def asTuple(self) -> tuple[int, int, int, int]:
        return self.tp, self.fn, self.fp, self.tn


@dataclass(frozen=True)
class Matrix:
    tier: Tier
    scope: str
    cells: Cells
    units: int
    conflicts: int


@dataclass(frozen=True)
class Ratio:
    value: float | None
    low: float | None
    high: float | None
    # the numerator and denominator, for a ratio of counts
    counts: tuple[int, int] | None


@dataclass(frozen=True)
class PairAgreement:
    pairs: int
    agreed: int
    kappa: float | None


@dataclass(frozen=True)
class Agreement:
    overall: PairAgreement
    by_month: tuple[tuple[str, PairAgreement], ...]
    stricter: int
    looser: int


@dataclass(frozen=True)
class Disagreement:
    unit_id: UnitId
    tier: Tier
    text: str
    labelled: str
    missed_runs: int
    false_negative: bool


@dataclass(frozen=True)
class Report:
    run: RunRecord
    matrices: tuple[Matrix, ...]
    ceiling: Agreement | None
    unit_count: int
    confidential_count: int
    disagreements: tuple[Disagreement, ...]


if __name__ == '__main__':
    sys.exit(main())
