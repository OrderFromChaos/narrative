### Show the thing, do not describe it

**Where a module reads or writes concrete text, paste a real sample of that text.** A rendered
table, a log line, a report, a converted value, an input format. **Delete the prose the sample
replaces** rather than keeping both. (R9-08)

**Never invent a sample.** Run the program and paste what it printed, or paste the `repr` of what
the function returned. A format that appears nowhere in the program is a lie in the shape of
documentation, and is worse than the prose the format replaced, because a reader cannot tell an
invented sample from a real one. This is the docstring case of the boundary rule above. **Do not
state what you did not observe.** A module that computes records rather than rendering text pastes
the records.

**Show one line of each shape, not the whole output.** One team row, one over-quota line, one file
outcome, and no repeats. The reader needs every shape the module can emit and needs no volume.

**A sample goes stale and no tool checks the sample.** Keep it small, and re-paste the sample when
the output changes.

**Expect it to cost lines.** The sample is there for exactness, not brevity. A reader learns
the column order, the units and the alignment from three rows of a table and cannot learn them from
a sentence about the table having columns.

```python
"""Format the result of a reconciliation as a table for a terminal.

    TEAM              USED     QUOTA   OVERAGE
    platform        550.0G    500.0G     50.0G
    archive         120.0G    100.0G     20.0G
    search            1.2T      2.0T         -

Teams over quota come first, worst first. A team within its quota has `-` as its overage.
"""
```

**Keep at least one line of the body at column 0**, as the last line above does. `ruff format`
strips the common leading indent from a docstring body, so a docstring whose body is *entirely*
indented gets flattened and the sample loses alignment. With one unindented line, the indent
is kept. The check is listed in `tooling.md`.

Avoid the same table as prose:

```python
"""Format the result of a reconciliation as a table for a terminal.

The table has one row for each team, then the largest paths of each team above its quota, then
the bytes that no team owns, then the outcome of every file. Every size carries a unit suffix.
"""
```

A conversion takes a table of cases rather than a sentence per case:

```python
"""Convert a size with a unit suffix to a count of bytes, and back.

    4096   ->          4096
    12K    ->         12288
    1.5G   ->    1610612736
    2T     -> 2199023255552

A unit is a power of 1024. A number with no suffix is a count of bytes.
"""
```

