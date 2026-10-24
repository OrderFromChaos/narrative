## Comments in Python

These rules add to **Comments** in `nar:core`. Each heading below is the name that `nar:core` uses
for the rule.

### Library facts

For a fact about the Python standard library, read the source or the Python documentation and check
the fact. (R11-rewrite-from-code)

### Source facts

A fact about a value from outside the code goes above the code for the value (J1-F12):

```python
# databases written before 2025/04/03 lack the account_id column
account_id = row['account_id'] if 'account_id' in row.keys() else None
```

### Decoding aids

- `SIZE_PATTERN = re.compile(...)  # number, then an optional binary unit suffix`
- `# fsum() for accurate floating point math`
- a regex, with a string the regex matches and one the regex rejects:
  ```python
  # matches:
  # `search_v2`
  # `db-host`
  # rejects:
  # `x.y`
  BARE_KEY = re.compile(r'[A-Za-z0-9_-]+')
  ```

(R10-Q42, R10-Q46, R10-regex-sample, R10-regex-literals)

### Fence

- `# bool subclasses Python int. Reject it too`, not `# bool subclasses Python int`
- `# isdigit() admits non-ASCII digits such as '²'. Check isascii() too`
- the `X would` form in full:
  ```python
  # Here read_bytes() is used. The alternative, read_text(), would turn \r\n and \r into \n, even
  # inside a quoted CSV field.
  csv_bytes = csv_path.read_bytes()
  ```

(R10-fence-form, R10-fence-fact, R10-fence-alternative)

### Depth

```python
# The vendor API returns at most 100 rows per page and no total count.
# Keep requesting until a page comes back short.
while len(page := fetchPage(cursor)) == PAGE_SIZE:
```

(R10-depth-example)

### Placement

A comment on an argument goes above the call that passes the argument, such as above
`pendulum.parse(raw_at, tz=None)`, not below the `try` block. (R10-argument-placement)

### FIXME

In reachable code a `FIXME:` blocks the merge (`NAR010`). In code nothing calls, the `FIXME:` is a
warning to whoever wires that code in. Every function of a module with no `main` and no `__main__`
block counts as reachable. (R8-D02)

### noqa

The exceptions to **Never add a `noqa` yourself** are the `# ruff: noqa: TID251` lines prescribed
in **Data at boundaries**. (R11-findings)

### Pages

`agentverbs.py` is the seventh check of `verify.py`. Name each page to `verify.py`:

```bash
python3 "${CLAUDE_SKILL_DIR}/verify.py" README.md docs/report.html
```

