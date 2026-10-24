"""Load the skill's deterministic checks, and run them on the text of one unit.

The checks are loaded from the first of TOOL_LAYOUTS whose wording module exists: `core/tools/`
with `lang/python/tools/`. The layout is taken to provide `wordingFindings()` in the wording module
and `CachedReader` in `agentverbs.py`. When the skill's files move, TOOL_LAYOUTS is the line to
change.

NAR012 to NAR016 and NAR018 come from the wording checks, and NAR017 and NAR020 to NAR022 from
`agentverbs.py`. `agentverbs.py` imports spaCy and loads the spaCy model, so run with the
interpreter of the lint venv:

    $ uv run --python ~/.local/share/narrative/lintenv/bin/python eval/run.py deterministic
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

from schema import REPO_ROOT


# each layout: the directories to put on sys.path, and the name of the module with wordingFindings()
TOOL_LAYOUTS = ((('core/tools', 'lang/python/tools'), 'wording'),)
CACHE_PATH = Path.home() / '.cache' / 'narrative-eval' / 'prose-cache.json'


class DeterministicChecks:
    """The wording checks and the agentverbs.py reader of one skill tree, with the reader's spaCy cache."""

    def __init__(self, wording: ModuleType, agent_verbs: ModuleType, tool_dir: Path) -> None:
        self.wording = wording
        self.reader = agent_verbs.CachedReader.open(CACHE_PATH)
        self.tool_dir = tool_dir

    @classmethod
    def load(cls) -> DeterministicChecks:
        """Import the checks of the first layout in TOOL_LAYOUTS whose wording module exists.

        Raises:
            ModuleNotFoundError: No layout exists, or spaCy is not installed in this interpreter.
        """
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        for directories, wording_name in TOOL_LAYOUTS:
            tool_dirs = [REPO_ROOT / directory for directory in directories]
            if not any((tool_dir / f'{wording_name}.py').is_file() for tool_dir in tool_dirs):
                continue
            # agentverbs.py imports the modules beside agentverbs.py by bare name
            sys.path[:0] = [str(tool_dir) for tool_dir in tool_dirs]
            return cls(importlib.import_module(wording_name), importlib.import_module('agentverbs'), tool_dirs[0])
        raise ModuleNotFoundError(f'no wording module under {REPO_ROOT} in any of {TOOL_LAYOUTS}')

    def findCodes(self, text: str, *, page: bool) -> frozenset[str]:
        """Run every check on the unit's text as one line.

        Returns:
            The codes of the findings, empty for text with no finding.
        """
        findings = self.wording.wordingFindings([(1, text)], set(), Path('unit'))
        codes = {finding.code for finding in findings}
        if self.reader.agentVerbs(text):
            codes.add('NAR017')
        if self.reader.fragments(text):
            codes.add('NAR020')
        if self.reader.connectives(text, page=page):
            codes.add('NAR021')
        if self.reader.ambiguousPronouns(text):
            codes.add('NAR022')
        return frozenset(codes)

    def save(self) -> None:
        self.reader.save()
