## The module docstring

**Every module opens with a docstring. Anything runnable has a usage example.** A reader meets it
first, before `main()`, so it is about what the program is *for*, not how the program works.
(R5-02, NAR009)

**Write for a professional developer who has the file open.** That reader knows the language and the
vocabulary of the trade, so `API`, `idempotent` and `tuple` are the right words and a plain-English
circumlocution around them is worse. One idea per sentence. **One word for one thing, and the word
is the identifier the code uses.** With `unassigned` in a docstring where the code has
`unattributed`, a reader greps for something that is not there. (R9-09)

The prose rules for comments and docstrings are in **Comments**.

```python
"""Load a CSV file into a SQLite table.

Each column is typed from its values as INTEGER, REAL or TEXT. A row that does not fit the
inferred types is skipped and reported. The program does not modify an existing table.

Usage:
    $ python3 load_csv.py readings.csv readings.db measurements
    $ python3 load_csv.py readings.csv readings.db measurements --sample-rows 200

Exit codes:
    0  every row loaded
    1  one or more rows skipped
    2  the file, the database or the arguments were unusable
"""
```

Required:

- what it does
- an example invocation per meaningful mode
- exit codes when there are more than two
- the shape of input and output where the shape is not obvious from the arguments

`NAR009` enforces the docstring. For a module with a `__main__` block, `NAR009` also enforces the
example.

