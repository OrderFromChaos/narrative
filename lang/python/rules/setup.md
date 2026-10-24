### Setup

Once per machine, make one lint venv and reuse the venv for every project. A venv per project means
a separate install of about 430 MB in each. (R10-setup)

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

When an update of the skill changes `requirements-lock.txt`, run the `uv pip install` line again.
`install.sh` and a plugin update copy the new lock file but install nothing.
`verify.py` uses this venv by default, and when the venv is missing `verify.py` prints these two
commands for the current machine. Pass `--venv` for a venv at another path. On Windows, run the
scripts with `py` or `python` wherever `python3` appears in this document.

Once per project, merge `pyproject-snippet.toml` into the project's `pyproject.toml`, or copy
`pyproject-snippet.toml` as the `pyproject.toml` of a new project. The file must be named
`pyproject.toml`. Ruff reads a config file with any other name as a `ruff.toml`, and `verify.py`
exits 2.

