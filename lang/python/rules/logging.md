## Logging

One stable event name plus structured `extra={...}` fields, never an f-string of prose. The
message is a queryable key. (Q08)

**Get each module's logger with `logging.getLogger(__name__)`.** In a package used as a library, add
`logging.NullHandler()` to the package logger once, in the package's top-level `__init__.py`.
Without it, the last-resort handler prints the package's warnings to stderr in a program that
configures no logging.
In a program, configure logging once, in `main()`, and add no NullHandler. (R10-nullhandler)

**JSONL output is for machine reading. For terminal output, don't use JSONL.** (R5-03,
R8-D23-resolved)

- **A service, or any program whose logs are collected**: JSONL. Always import JSONL logging from a
  shared module. Don't vendor it.

- **A single-file tool run by hand**: the short field formatter below.

**Do not use `basicConfig(format='%(levelname)s %(message)s')`.** The standard formatter discards
everything in `extra`. `LOG.warning('merge.rejected', extra={'rejected': 4812, 'total': 10000})`
then prints `WARNING merge.rejected`, and the operator never sees the number that the tally rule
exists to give them. Follow the event-name rule with that formatter and the logs are worse than an
f-string. (R5-09)

```python
_STANDARD = frozenset(logging.LogRecord('', 0, '', 0, '', None, None).__dict__) | {'message', 'asctime'}
_LOCATION = ('module', 'lineno', 'funcName')


class FieldFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extra = {k: v for k, v in record.__dict__.items() if k not in _STANDARD}
        located = {key: getattr(record, key) for key in _LOCATION}
        fields = ' '.join(f'{k}={v}' for k, v in sorted({**located, **extra}.items()))
        return f'{record.levelname} {record.getMessage()} {fields}'
```

That prints `WARNING merge.rejected funcName=merge lineno=88 module=loader rejected=4812
total=10000`. It has the tally an operator acts on and the location of the call site.

