"""Run narrative_hooks.py on each case and compare the reply with the expected reply.

Each case is a list of hook calls in one session, in a temporary project outside the narrative repository, with a
temporary plugin data directory. A case passes when the reply to the last call is the expected reply.

Usage:
    $ python3 hooks/tests/run_hooks.py

Exit codes:
    0  every case gave its expected reply
    1  at least one case did not
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


# the launcher of hooks.json, which runs narrative_hooks.py with the first Python 3.11 on PATH
LAUNCHER_PATH = Path(__file__).resolve().parents[1] / 'run.sh'
# resolved once, because some cases run the launcher with a PATH that has no sh
SHELL_PATH = shutil.which('sh') or '/bin/sh'

REFUSED_COMMANDS = [
    'python3 /x/skills/python/verify.py . | tail -5',
    'python3 /x/skills/gtnh/verify.py . 2>&1 | grep NAR',
    'python3 ~/.claude/skills/narrative-python/verify.py --since HEAD |& head -40',
    'python3 "${CLAUDE_SKILL_DIR}/verify.py" . | sed -n 1,20p',
    'grep -v NAR101 out.txt',
    "grep -Ev 'NAR1(01|16)' out.txt",
    'python3 /x/skills/gtnh/javachecks.py src/',
    'python3 ~/.claude/plugins/cache/narrative/nar/1a2b/skills/python/agentverbs.py src/',
    'ruff check src/',
    'PATH=venv/bin:$PATH mypy --strict .',
    'uv run pylint src',
    './gradlew spotlessApply',
    'cd mod && ./gradlew --offline checkstyleMain pmdMain',
]
ALLOWED_COMMANDS = [
    'python3 /x/skills/python/verify.py . > out.txt; echo exit=$?',
    'python3 /x/skills/python/verify.py . || echo failed',
    'cat /x/skills/python/verify.py | head -20',
    'grep -n main scripts/verify.py | head',
    'python3 tools/verify.py --all | tail',
    'python3 scripts/checks.py',
    'cat checks.py',
    'pip install mypy',
    'cat mypy.ini',
    'python3 /x/skills/gtnh/javachecks.py --rewrap src/Plan.java',
    'python3 /x/skills/python/checks.py --help',
    './gradlew build',
    'cat .narrative_cache/review-lists.txt',
    'grep -n restock src/inventory.py',
    'git diff | head -20',
]


def main() -> int:
    cases = [*commandCases(), *sessionCases()]
    wrong = [case.name for case in cases if not passes(case)]
    for name in wrong:
        print(f'wrong: {name}')
    print(f'{len(wrong)} of {len(cases)} cases wrong')
    return 1 if wrong else 0


def commandCases() -> list[Case]:
    cases = [Case(f'refuse {command}', [SKILL_LOAD, bash(command)], 'deny') for command in REFUSED_COMMANDS]
    cases += [Case(f'allow {command}', [SKILL_LOAD, bash(command)], None) for command in ALLOWED_COMMANDS]
    other_skill = Call('pre-tool', {'tool_name': 'Skill', 'tool_input': {'skill': 'pdf'}})
    pipe = bash('python3 /x/skills/python/verify.py . | tail -5')
    cases.append(Case('no skill loaded: allow a pipe', [pipe], None))
    cases.append(Case('another skill loaded: allow a pipe', [other_skill, pipe], None))
    by_hand = [SKILL_LOAD, bash('ruff check core/')]
    cases.append(Case('narrative repository: allow a check by hand', by_hand, None, in_narrative=True))
    cases.append(Case('NARRATIVE_HOOKS=off: allow a pipe', [SKILL_LOAD, pipe], None, hooks_off=True))
    cases.append(Case('failing python3, as the Store alias: python refuses', [SKILL_LOAD, pipe], 'deny', path='alias'))
    cases.append(Case('no Python on PATH: allow a pipe', [SKILL_LOAD, pipe], None, path='empty'))
    return cases


def sessionCases() -> list[Case]:
    """List the cases of edits, `verify.py` runs, reads of the review lists, turn ends and compaction."""
    verify = bash('python3 /x/skills/python/verify.py .')
    java = bash('python3 /x/skills/gtnh/verify.py --since HEAD')
    by_variable = bash('python3 "${CLAUDE_SKILL_DIR}/verify.py" 2>&1')
    lists = writeLists('.narrative_cache')
    read_verify = bash('cat /x/skills/python/verify.py')
    cat_lists = bash('cat .narrative_cache/review-lists.txt')
    lists_path = '/p/.narrative_cache/review-lists.txt'
    read_lists = Call('pre-tool', {'tool_name': 'Read', 'tool_input': {'file_path': lists_path}})
    outside = Call('post-tool', {'tool_name': 'Write', 'tool_input': {'file_path': '/tmp/scratch/probe.py'}})
    compact = Call('session-start', {'source': 'compact'})
    return [
        Case('edit, no verify: refuse the end', [SKILL_LOAD, edit('src/a.py'), STOP], 'block'),
        Case('edit, verify, unread lists: refuse', [SKILL_LOAD, edit('src/a.py'), verify, lists, STOP], 'block'),
        Case('edit, verify that wrote no lists: allow the end', [SKILL_LOAD, edit('src/a.py'), verify, STOP], None),
        Case('lists of an earlier run only: allow the end', [SKILL_LOAD, lists, verify, STOP], None),
        Case(
            'verify with --cache-dir, unread lists: refuse the end',
            [SKILL_LOAD, bash('python3 /x/skills/python/verify.py . --cache-dir out/nc'), writeLists('out/nc'), STOP],
            'block',
        ),
        Case(
            'cd, then verify, unread lists: refuse the end',
            [
                SKILL_LOAD,
                bash('cd sub && python3 /x/skills/python/verify.py .'),
                writeLists('sub/.narrative_cache'),
                STOP,
            ],
            'block',
        ),
        Case('edit, verify, cat lists: allow the end', [SKILL_LOAD, edit('src/a.py'), verify, cat_lists, STOP], None),
        Case('edit, verify, Read lists: allow the end', [SKILL_LOAD, edit('A.java'), java, read_lists, STOP], None),
        Case('Java edit, Python verify: refuse the end', [SKILL_LOAD, edit('A.java'), verify, STOP], 'block'),
        Case('Python edit, Java verify: refuse the end', [SKILL_LOAD, edit('src/a.py'), java, STOP], 'block'),
        Case(
            'Python and Java edits, both verify runs: allow the end',
            [SKILL_LOAD, edit('src/a.py'), edit('A.java'), java, verify, STOP],
            None,
        ),
        Case(
            'edit, verify by the skill variable: allow the end',
            [SKILL_LOAD, edit('A.java'), by_variable, STOP],
            None,
        ),
        Case(
            'Java edit, verify --prose-only: refuse the end for Gradle',
            [SKILL_LOAD, edit('A.java'), bash('python3 /x/skills/gtnh/verify.py --prose-only --since HEAD'), STOP],
            'block-prose-only',
        ),
        Case(
            'Java edit, --prose-only, then a full run: allow the end',
            [SKILL_LOAD, edit('A.java'), bash('python3 /x/skills/gtnh/verify.py --prose-only'), java, STOP],
            None,
        ),
        Case(
            '--prose-only of a later command: the run checks Java',
            [SKILL_LOAD, edit('A.java'), bash('python3 /x/skills/gtnh/verify.py; echo --prose-only'), STOP],
            None,
        ),
        Case('verify, lists, then edit: refuse the end', [SKILL_LOAD, verify, cat_lists, edit('a.py'), STOP], 'block'),
        Case('second end of the turn: allow', [SKILL_LOAD, edit('src/a.py'), STOP_AGAIN], None),
        Case('edit, cat verify.py: refuse the end', [SKILL_LOAD, edit('src/a.py'), read_verify, STOP], 'block'),
        Case('edit in turn 1, end of turn 2: allow', [SKILL_LOAD, edit('src/a.py'), inTurn(STOP, 'p2')], None),
        Case(
            'edit in turn 2, end of turn 2: refuse',
            [SKILL_LOAD, inTurn(edit('src/a.py'), 'p2'), inTurn(STOP, 'p2')],
            'block',
        ),
        Case('verify in turn 1, end of turn 2: allow', [SKILL_LOAD, verify, inTurn(STOP, 'p2')], None),
        Case(
            'edit in turn 1, verify in turn 2, unread lists: refuse',
            [SKILL_LOAD, edit('src/a.py'), inTurn(verify, 'p2'), lists, inTurn(STOP, 'p2')],
            'block',
        ),
        Case('no skill loaded: allow the end', [edit('src/a.py'), STOP], None),
        Case('edit of a page: allow the end', [SKILL_LOAD, edit('README.md'), STOP], None),
        Case('edit outside the project: allow the end', [SKILL_LOAD, outside, STOP], None),
        Case('compaction after a skill load: name the skill', [SKILL_LOAD, compact], 'context'),
        Case('compaction with no skill: nothing', [compact], None),
    ]


def passes(case: Case) -> bool:
    """Run the calls of a case in a new project and data directory, and compare the last reply with the expected one.

    A `write-lists` call is no hook call: the test writes a review-lists.txt below the project, as a `verify.py` run
    does when the run ends.

    Raises:
        subprocess.CalledProcessError: run.sh exits nonzero. The launcher and narrative_hooks.py exit 0 on every input.
    """
    with tempfile.TemporaryDirectory() as data_dir, tempfile.TemporaryDirectory() as project_dir:
        project = Path(project_dir)
        if case.in_narrative:
            for name in ('skills.toml', 'assemble.py', 'build_skills.py'):
                (project / name).write_text('', encoding='utf-8')
        environment = {**os.environ, 'CLAUDE_PLUGIN_DATA': data_dir, 'CLAUDE_PROJECT_DIR': project_dir}
        if case.hooks_off:
            environment['NARRATIVE_HOOKS'] = 'off'
        if case.path is not None:
            environment['PATH'] = interpreterPath(case.path, project)
        reply: dict[str, object] = {}
        for call in case.calls:
            if call.event == 'write-lists':
                lists_path = project / str(call.fields['directory']) / 'review-lists.txt'
                lists_path.parent.mkdir(parents=True, exist_ok=True)
                lists_path.write_text('--- every sentence ---\n', encoding='utf-8')
                continue
            hook_input = {
                'session_id': 'test-session',
                'prompt_id': call.turn,
                'cwd': project_dir,
                **resolved(call.fields, project),
            }
            result = subprocess.run(
                [SHELL_PATH, str(LAUNCHER_PATH), call.event],
                input=json.dumps(hook_input),
                capture_output=True,
                text=True,
                env=environment,
                check=True,
            )
            reply = json.loads(result.stdout) if result.stdout.strip() else {}
    return outcomeOf(reply) == case.expected


def resolved(fields: dict[str, object], project: Path) -> dict[str, object]:
    """Put a relative edited path inside the project. Claude Code passes an absolute path."""
    tool_input = fields.get('tool_input')
    if isinstance(tool_input, dict) and isinstance(tool_input.get('file_path'), str):
        path = Path(str(tool_input['file_path']))
        if not path.is_absolute():
            return {**fields, 'tool_input': {**tool_input, 'file_path': str(project / path)}}
    return fields


def outcomeOf(reply: dict[str, object]) -> str | None:
    specific = reply.get('hookSpecificOutput')
    if isinstance(specific, dict) and specific.get('permissionDecision') == 'deny':
        return 'deny'
    if isinstance(specific, dict) and specific.get('additionalContext'):
        return 'context'
    if reply.get('decision') == 'block':
        return 'block-prose-only' if '--prose-only' in str(reply.get('reason')) else 'block'
    return None


def bash(command: str) -> Call:
    return Call('pre-tool', {'tool_name': 'Bash', 'tool_input': {'command': command}})


def edit(path: str) -> Call:
    return Call('post-tool', {'tool_name': 'Edit', 'tool_input': {'file_path': path}})


def interpreterPath(kind: str, project: Path) -> str:
    """Make a PATH with no working python3: `alias` has a failing python3 and a working python, `empty` has neither."""
    bin_dir = project / '.test-bin'
    bin_dir.mkdir()
    if kind == 'alias':
        alias = bin_dir / 'python3'
        alias.write_text('#!/bin/sh\necho Python was not found >&2\nexit 1\n', encoding='utf-8')
        alias.chmod(0o755)
        # a script, not a symlink: on Windows, only an account with the symlink privilege can make a symlink
        working = bin_dir / 'python'
        interpreter = Path(sys.executable).as_posix()
        working.write_text(f'#!/bin/sh\nexec "{interpreter}" "$@"\n', encoding='utf-8')
        working.chmod(0o755)
    return str(bin_dir)


def writeLists(directory: str) -> Call:
    return Call('write-lists', {'directory': directory})


def inTurn(call: Call, turn: str) -> Call:
    return dataclasses.replace(call, turn=turn)


### vocabulary


@dataclass(frozen=True)
class Call:
    """One hook call: the event argument of narrative_hooks.py, the fields of the hook input, and the turn."""

    event: str
    fields: dict[str, object]
    # the `prompt_id` of the hook input
    turn: str = 'p1'


@dataclass(frozen=True)
class Case:
    name: str
    calls: list[Call]
    # `deny`, `block`, `block-prose-only` for a refusal that names --prose-only, `context`, or None for a reply with no
    # refusal and no added context
    expected: str | None
    in_narrative: bool = False
    # with NARRATIVE_HOOKS=off in the environment of the hooks
    hooks_off: bool = False
    # `alias` or `empty`: the PATH of interpreterPath(), or None for the PATH of the test
    path: str | None = None


SKILL_LOAD = Call('pre-tool', {'tool_name': 'Skill', 'tool_input': {'skill': 'nar:python'}})
STOP = Call('stop', {'stop_hook_active': False})
STOP_AGAIN = Call('stop', {'stop_hook_active': True})


if __name__ == '__main__':
    sys.exit(main())
