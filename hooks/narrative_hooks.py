"""Refuse a tool call or a turn end when the agent skips a step of the Narrative procedures, with Claude Code hooks.

The skill text asks for the steps of Procedures. After a Narrative skill is loaded in the session, these calls and turn
ends are refused:

- before a shell command: `verify.py` output piped to `grep`, `head`, `tail`, `sed`, `awk` or a similar filter,
  `grep -v` over finding codes, and a check run by hand that `verify.py` also runs: `checks.py`, `javachecks.py`,
  `agentverbs.py`, `ruff check`, `ruff format`, `mypy`, `pylint`, `vermin`, and the spotless, Checkstyle and PMD tasks
  of Gradle. The skill prescribes `javachecks.py --rewrap` and `checks.py --rewrap`, so both are allowed, and so is
  `--help`
- at the end of a turn: a `.py` or `.java` file of the project edited in this turn after the last `verify.py` run for
  the language of the file, or the review lists of a run of this turn never opened. For a `.py` file, only a run of
  nar:python counts. For a `.java` file, only a run of nar:gtnh without --prose-only counts. Lists that the run did not
  write, such as after an exit 2 or during a run in the background, need no read. A second end of the same turn is
  allowed, so the agent can stop a turn to ask the user a question
- after compaction: a reminder to load the Narrative skills again, because the summary has no rules

A `verify.py` run is a Python run of the `verify.py` in the folder of a Narrative skill. A script of the project named
verify.py, and a read of a file named verify.py, are neither a run nor a refusal. The same rule covers `checks.py`,
`javachecks.py` and `agentverbs.py`.

Every hook does nothing until the session loads a skill of the plugin `nar`, or a skill installed by install.sh. The
tests and the self-consistency passes of the narrative repository run the tools by hand, so in a checkout of the
narrative repository every hook does nothing. With the environment variable `NARRATIVE_HOOKS=off`, every hook does
nothing too.

Each session has a log of events in the plugin data directory, one JSON line per event: a skill load, an edit, a
`verify.py` run, a read of the review lists. A hook appends to the log, so the hooks of parallel tool calls write no
shared file.

Usage, from hooks/hooks.json through the launcher run.sh, with the hook input on stdin. The interpreter is the first
Python 3.11 on PATH:
    $ python3 narrative_hooks.py pre-tool
    $ python3 narrative_hooks.py post-tool
    $ python3 narrative_hooks.py stop
    $ python3 narrative_hooks.py session-start

Exit codes:
    0  always. A refusal is JSON on stdout
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path


### standard library only. Claude Code runs this script with the python3 of the machine

# the skill names of the plugin `nar` and of install.sh
NARRATIVE_SKILL = re.compile(r'^(?:nar:(?:python|gtnh|core|code)|narrative-(?:python|java|gtnh|core))$')
CHECKED_SUFFIXES = frozenset({'.py', '.java'})
# the files at the root of the narrative repository
NARRATIVE_SOURCE_FILES = ('skills.toml', 'assemble.py', 'build_skills.py')
# the data directory when Claude Code sets no CLAUDE_PLUGIN_DATA, such as a hook in settings.json
FALLBACK_DATA_DIR = Path.home() / '.cache' / 'narrative-hooks'
LISTS_NAME = 'review-lists.txt'
# the cache directory of verify.py in the directory of the run, when the command passes no --cache-dir
DEFAULT_CACHE_DIR = '.narrative_cache'
OFF_VALUES = frozenset({'off', '0', 'false', 'no'})
# a path argument: in double quotes, in single quotes, or with no space
PATH_ARGUMENT = r'("[^"]+"|\'[^\']+\'|[^\s;&|]+)'
# matches:
# `cd mod && python3 skills/gtnh/verify.py`
CD = re.compile(r'(?:^|[;&]\s*)cd\s+' + PATH_ARGUMENT)
# matches:
# `--cache-dir /tmp/narrative`
# `--cache-dir="build/narrative cache"`
CACHE_DIR = re.compile(r'--cache-dir[\s=]+' + PATH_ARGUMENT)

# a redirect of one stream into another, such as `2>&1`. The `&` of such a redirect is not a command separator
STREAM_REDIRECT = re.compile(r'\d*>&\d+')
# a Python interpreter, then a script in the folder of a Narrative skill: skills/python or skills/gtnh of the plugin and
# of the repository, a folder of install.sh, or the skill folder variable of SKILL.md
SKILL_SCRIPT = (
    r'\bpython[\d.]*(?:\.exe)?\s+(?:-\w+\s+)*["\']?\S*?'
    r'(?P<folder>skills[/\\](?:python|gtnh)|narrative-(?:python|java|gtnh)|\$\{?CLAUDE_SKILL_DIR\}?)[/\\]'
)
# the suffix of the source files that the verify.py of a skill folder checks. `${CLAUDE_SKILL_DIR}` is the folder of
# nar:python or of nar:gtnh, so a run through `${CLAUDE_SKILL_DIR}` counts for both suffixes
CHECKED_SUFFIXES_OF_FOLDER = {
    'python': ('.py',),
    'gtnh': ('.java',),
    'java': ('.java',),
}
# the option of the verify.py of nar:gtnh that skips Gradle. The verify.py of nar:python has no such option
PROSE_ONLY = re.compile(r'--prose-only\b')
# matches:
# `python3 "${CLAUDE_SKILL_DIR}/verify.py" .`
# `~/.local/share/narrative/lintenv/bin/python ~/.claude/plugins/cache/narrative/nar/1a2b/skills/python/verify.py`
# rejects:
# `cat skills/python/verify.py`
# `python3 tools/verify.py --all`
VERIFY_RUN = re.compile(SKILL_SCRIPT + r'verify\.py\b')
# matches:
# `python3 skills/python/verify.py . | tail -5`
# `python3 skills/gtnh/verify.py --since HEAD |& grep NAR`
# rejects:
# `python3 skills/python/verify.py . > out.txt; tail out.txt`
# `python3 skills/python/verify.py . || echo failed`
VERIFY_PIPE = re.compile(
    SKILL_SCRIPT + r'verify\.py\b[^;&|\n]*\|&?(?!\|)\s*(?:\S*/)?'
    r'(?:grep|egrep|fgrep|rg|head|tail|sed|awk|cut|sort|uniq|wc|less|more)\b',
)
# matches:
# `grep -v NAR101`
# `grep -Ev 'NAR1(01|16)'`
GREP_OUT_CODES = re.compile(r'\b[ef]?grep\b[^|;&\n]*\s-[A-Za-z]*v[A-Za-z]*\b[^|;&\n]*NAR')
# matches:
# `python3 skills/gtnh/javachecks.py src/`
# `~/.local/share/narrative/lintenv/bin/python skills/python/agentverbs.py src/`
# rejects:
# `cat skills/python/checks.py`
# `python3 scripts/checks.py`
SKILL_CHECK = re.compile(SKILL_SCRIPT + r'(?:checks|javachecks|agentverbs)\.py\b(?P<rest>[^;&|\n]*)')
# matches:
# `ruff check src/`
# `PATH=venv/bin:$PATH mypy --strict .`
# `uv run pylint src`
# rejects:
# `pip install mypy`
# `cat mypy.ini`
LINTER = re.compile(
    r'(?:^|[;&|(]\s*)(?:\w+=\S*\s+)*(?:(?:uv\s+run|\S*python[\d.]*\s+-m)\s+)?(?:\S*/)?'
    r'(?P<tool>ruff\s+(?:check|format)|mypy|pylint|vermin)\b',
)
# matches:
# `./gradlew spotlessApply`
# `./gradlew --offline checkstyleMain pmdMain`
GRADLE_CHECK = re.compile(r'gradlew\S*\s[^;&|\n]*\b(?P<task>spotless\w*|checkstyle\w*|pmd\w*)\b')
ALLOWED_FLAGS = re.compile(r'--(?:rewrap|help)\b')

PIPE_REASON = (
    'Narrative: run verify.py without a pipe. The findings are on stdout, and the file of the three review lists is'
    ' named on the last line of the output. To keep the output, write the output to a file and read the whole file.'
    ' (R11-no-filter, R11-steps-summary)'
)
GREP_REASON = (
    'Narrative: keep every finding in the output. A finding that you take for a tool error goes in your report with'
    ' the file and line, and a finding that the user keeps is kept for one pass only. (R11-no-filter)'
)
BY_HAND_REASON = (
    'Narrative: run verify.py, not {tool} by hand. verify.py runs every check in the order that converges, and a'
    ' missing tool is exit 2 there, not a silent pass. After an edit of comments or pages only in a GTNH mod, pass'
    ' --prose-only to verify.py.'
)
EDIT_REASON = (
    'Narrative: {path} changed after the last verify.py run that checks {suffix} files. Run the verify.py of the skill'
    ' for {suffix} files once for the batch of edits, as in Procedures, then read the review lists. If you stop this'
    ' turn to ask the user a question before the work is done, say so in one line and end the turn again.'
)
PROSE_ONLY_REASON = (
    'Narrative: {path} changed after the last verify.py run without --prose-only. A run with --prose-only checks no'
    ' Java source with Gradle. Run verify.py without --prose-only once before the turn ends, then read the review'
    ' lists. If you stop this turn to ask the user a question before the work is done, say so in one line and end the'
    ' turn again.'
)
LISTS_REASON = (
    'Narrative: the review lists of the last verify.py run are not read. Read the review-lists.txt file named on the'
    ' last line of the output, take the steps of Prose review, and say in your report how many entries of each list'
    ' you read.'
)
COMPACT_CONTEXT = (
    'Before compaction, this session loaded the Narrative skills {skills}. The summary has no rules of those skills.'
    ' Load each skill again with the Skill tool before the next edit or verify.py run.'
)


def main() -> int:
    """Read the hook input of one event, record the event, and print a refusal or added context.

    Input that is not JSON, or has no session id, gets no reply. After a change of the hook input format, the hooks do
    nothing, and no session is blocked.
    """
    event = sys.argv[1] if len(sys.argv) > 1 else ''
    if os.environ.get('NARRATIVE_HOOKS', '').strip().lower() in OFF_VALUES:
        return 0
    try:
        hook_input = json.loads(sys.stdin.read() or '{}')
    except json.JSONDecodeError:
        return 0
    session = Session.of(hook_input)
    if session is None or inNarrativeSource(Path(hook_input.get('cwd') or '.')):
        return 0
    match event:
        case 'pre-tool':
            reply = preTool(session, hook_input)
        case 'post-tool':
            postTool(session, hook_input)
            reply = None
        case 'stop':
            reply = stop(session, hook_input)
        case 'session-start':
            reply = sessionStart(session)
        case _:
            reply = None
    if reply is not None:
        print(json.dumps(reply))
    return 0


def preTool(session: Session, hook_input: dict[str, object]) -> dict[str, object] | None:
    """Record a skill load, a `verify.py` run and a read of the review lists, and refuse a skipped step.

    Returns:
        A PreToolUse refusal, or None to let the call run.
    """
    tool = hook_input.get('tool_name')
    tool_input = hook_input.get('tool_input')
    if not isinstance(tool_input, dict):
        return None
    if tool == 'Skill':
        name = str(tool_input.get('skill', ''))
        if NARRATIVE_SKILL.match(name):
            session.record({'event': 'skill', 'name': name})
        return None
    if not session.skills():
        return None
    if tool == 'Read' and str(tool_input.get('file_path', '')).endswith(LISTS_NAME):
        session.record({'event': 'lists'})
        return None
    if tool != 'Bash':
        return None
    command = str(tool_input.get('command', ''))
    reason = refusalOf(command)
    if reason is not None:
        return {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': reason,
            },
        }
    joined = STREAM_REDIRECT.sub(' ', command)
    run = VERIFY_RUN.search(joined)
    if run is not None:
        lists_path = listsPathOf(joined, run.start(), Path(str(hook_input.get('cwd') or '.')))
        arguments = re.match(r'[^;&|\n]*', joined[run.end() :])
        prose_only = bool(arguments and PROSE_ONLY.search(arguments.group(0)))
        session.record(
            {
                'event': 'verify',
                'started': time.time(),
                'lists': str(lists_path),
                'checks': [] if prose_only else checkedSuffixesOf(run.group('folder')),
                'prose_only': prose_only,
            },
        )
    if LISTS_NAME in command:
        session.record({'event': 'lists'})
    return None


def refusalOf(command: str) -> str | None:
    """Return the reason to refuse a shell command, or None for a command with no skipped step."""
    joined = STREAM_REDIRECT.sub(' ', command)
    if VERIFY_PIPE.search(joined):
        return PIPE_REASON
    if GREP_OUT_CODES.search(joined):
        return GREP_REASON
    for found in SKILL_CHECK.finditer(joined):
        if not ALLOWED_FLAGS.search(found.group('rest')):
            script = re.search(r'\w+\.py', found.group(0))
            return BY_HAND_REASON.format(tool=script.group(0) if script else 'a check')
    linter = LINTER.search(joined)
    if linter is not None:
        return BY_HAND_REASON.format(tool=' '.join(linter.group('tool').split()))
    gradle = GRADLE_CHECK.search(joined)
    if gradle is not None:
        return BY_HAND_REASON.format(tool=f'gradlew {gradle.group("task")}')
    return None


def listsPathOf(command: str, run_start: int, cwd: Path) -> Path:
    """Find the review-lists.txt that a `verify.py` run writes: in the cache directory, in the directory of the run.

    The directory of the run is the last `cd` before the run, else the session's directory. The cache directory is the
    argument of --cache-dir, else `.narrative_cache`.
    """
    directory = cwd
    for found in CD.finditer(command[:run_start]):
        directory = directory / Path(found.group(1).strip('"\'')).expanduser()
    cache = CACHE_DIR.search(command[run_start:])
    cache_dir = Path(cache.group(1).strip('"\'')).expanduser() if cache else Path(DEFAULT_CACHE_DIR)
    return directory / cache_dir / LISTS_NAME


def checkedSuffixesOf(folder: str) -> list[str]:
    """Return the suffixes of the source files that a `verify.py` run checks, from the skill folder of the script."""
    language = re.split(r'[/\\-]', folder)[-1]
    return list(CHECKED_SUFFIXES_OF_FOLDER.get(language, sorted(CHECKED_SUFFIXES)))


def postTool(session: Session, hook_input: dict[str, object]) -> None:
    """Record an edit of a checked source file of the project, after the edit succeeded."""
    tool_input = hook_input.get('tool_input')
    if not session.skills() or not isinstance(tool_input, dict):
        return
    edited = tool_input.get('file_path') or tool_input.get('notebook_path')
    if not isinstance(edited, str):
        return
    path = Path(edited)
    project = Path(os.environ.get('CLAUDE_PROJECT_DIR') or str(hook_input.get('cwd') or '.'))
    if path.suffix in CHECKED_SUFFIXES and path.resolve().is_relative_to(project.resolve()):
        session.record({'event': 'edit', 'path': edited})


def stop(session: Session, hook_input: dict[str, object]) -> dict[str, object] | None:
    """Refuse the end of a turn with an edit of this turn after the last `verify.py` run for the language of the file,
    or with unread review lists.

    Only an edit or a `verify.py` run of the turn that ends counts, so a later turn in which the agent only answers a
    question ends with no refusal. The turn is the `prompt_id` of the hook input. With no `prompt_id`, every event
    counts. After one refusal, Claude Code sets `stop_hook_active`, and the next end of the turn is allowed. So a turn
    can still stop to ask the user a question.

    Returns:
        A Stop refusal, or None to let the turn end.
    """
    if hook_input.get('stop_hook_active') or not session.skills():
        return None
    events = session.events()
    edit = uncheckedEdit(session, events)
    if edit >= 0:
        path = Path(str(events[edit].get('path')))
        prose_only = any(entry.get('event') == 'verify' and entry.get('prose_only') for entry in events[edit + 1 :])
        reason = PROSE_ONLY_REASON if prose_only else EDIT_REASON
        return {'decision': 'block', 'reason': reason.format(path=events[edit].get('path'), suffix=path.suffix)}
    verify = session.lastIndex(events, 'verify', this_turn=True)
    if verify > session.lastIndex(events, 'lists', this_turn=False) and wroteLists(events[verify]):
        return {'decision': 'block', 'reason': LISTS_REASON}
    return None


def uncheckedEdit(session: Session, events: list[dict[str, object]]) -> int:
    """Return the index of the last edit of this turn with no later `verify.py` run that checks the file, or -1.

    A run of nar:python checks `.py` files, and a run of nar:gtnh without --prose-only checks `.java` files. A run that
    an older version of this script recorded has no list of checked suffixes, and counts for both.
    """
    unchecked = -1
    for index, entry in enumerate(events):
        if entry.get('event') != 'edit' or not session.inTurn(entry):
            continue
        suffix = Path(str(entry.get('path'))).suffix
        if not any(checksSuffix(later, suffix) for later in events[index + 1 :]):
            unchecked = index
    return unchecked


def checksSuffix(entry: dict[str, object], suffix: str) -> bool:
    """Decide whether an event is a `verify.py` run that checks the source files with a suffix."""
    checks = entry.get('checks', sorted(CHECKED_SUFFIXES))
    return entry.get('event') == 'verify' and isinstance(checks, list) and suffix in checks


def wroteLists(verify: dict[str, object]) -> bool:
    """Decide whether a `verify.py` run wrote a review-lists.txt: the file changed after the run started.

    A run with exit 2, a run after a Gradle failure and a run still in the background leave no new lists.
    """
    started = verify.get('started')
    lists = verify.get('lists')
    if not isinstance(started, (int, float)) or not isinstance(lists, str):
        return False
    try:
        return Path(lists).stat().st_mtime >= started
    except OSError:
        return False


def sessionStart(session: Session) -> dict[str, object] | None:
    """After compaction, name the Narrative skills that the session loaded, so the agent loads them again."""
    skills = session.skills()
    if not skills:
        return None
    return {
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': COMPACT_CONTEXT.format(skills=', '.join(skills)),
        },
    }


def inNarrativeSource(directory: Path) -> bool:
    """Decide whether a directory is in a checkout of the narrative repository, by the files at the checkout root."""
    for candidate in (directory.resolve(), *directory.resolve().parents):
        if all((candidate / name).is_file() for name in NARRATIVE_SOURCE_FILES):
            return True
    return False


### vocabulary


@dataclass(frozen=True)
class Session:
    """The event log of one Claude Code session, in the plugin data directory, and the turn of the hook call."""

    log_path: Path
    # the `prompt_id` of the hook input, or None when Claude Code passes none
    turn: str | None

    @classmethod
    def of(cls, hook_input: dict[str, object]) -> Session | None:
        session_id = hook_input.get('session_id')
        if not isinstance(session_id, str) or not re.fullmatch(r'[\w-]+', session_id):
            return None
        data_dir = Path(os.environ.get('CLAUDE_PLUGIN_DATA') or FALLBACK_DATA_DIR)
        turn = hook_input.get('prompt_id')
        return cls(data_dir / 'sessions' / f'{session_id}.jsonl', turn if isinstance(turn, str) else None)

    def record(self, entry: dict[str, object]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open('a', encoding='utf-8') as log_file:
            log_file.write(json.dumps({**entry, 'turn': self.turn}) + '\n')

    def lastIndex(self, events: list[dict[str, object]], kind: str, *, this_turn: bool) -> int:
        """Return the index of the last event of a kind, of this turn only or of any turn, or -1 for none."""
        indexes = [
            index
            for index, entry in enumerate(events)
            if entry.get('event') == kind and (not this_turn or self.inTurn(entry))
        ]
        return indexes[-1] if indexes else -1

    def inTurn(self, entry: dict[str, object]) -> bool:
        """Decide whether an event belongs to the turn of the hook call. With no `prompt_id`, every event belongs."""
        return self.turn is None or entry.get('turn') == self.turn

    def events(self) -> list[dict[str, object]]:
        try:
            lines = self.log_path.read_text(encoding='utf-8').splitlines()
        except FileNotFoundError:
            return []
        return [json.loads(line) for line in lines if line.strip()]

    def skills(self) -> list[str]:
        names = [str(entry.get('name')) for entry in self.events() if entry.get('event') == 'skill']
        return sorted(set(names))


if __name__ == '__main__':
    sys.exit(main())
