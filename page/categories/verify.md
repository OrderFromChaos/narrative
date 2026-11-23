## Verify the page

Run the `verify.py` of this skill on the page, as under **Verify a page** in `nar:page`:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" docs/report.html --no-fix
```

Take **Prose review** of `nar:core` on the lists of the run. Then read the page against the
checklist of `nar:page`, and against each rule of this skill, one rule at a time.