### Setup

The Java skill uses the same lint venv as the Python skill, one per machine, and the same prose
checks. (R10-setup)

Linux and macOS:

```bash
uv venv --python 3.11 ~/.local/share/narrative/lintenv
uv pip install --python ~/.local/share/narrative/lintenv/bin/python -r "${CLAUDE_SKILL_DIR}/requirements-lock.txt"
```

Windows (PowerShell):

```powershell
uv venv --python 3.11 $env:LOCALAPPDATA\narrative\lintenv
uv pip install --python $env:LOCALAPPDATA\narrative\lintenv\Scripts\python.exe -r "${CLAUDE_SKILL_DIR}/requirements-lock.txt"
```

The JDK of the level (8, 17 or 25) comes from the Gradle toolchain of the project, and a JDK 25 for
Checkstyle and PMD comes from the Gradle toolchains too. PMD 7.28.0 and Checkstyle 13.5.0 come from
Maven Central on the first run. No project file changes.

