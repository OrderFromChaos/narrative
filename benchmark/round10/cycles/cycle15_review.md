# Comments for review

Every `#` comment block, numbered, with 8 lines before and 10 after. The comment lines are marked `>>`. Pragmas and `###` dividers are left out.

## P11 access logs (package access_report): 12 comments

`scratchpad/cycle15/p11/access_report`

### 1. analysis.py:77

```python
     69                 _LOG.debug(
     70                     'line.malformed',
     71                     extra={'file': log_path.name, 'line': line_number, 'problem': outcome.value},
     72                 )
     73             else:
     74                 requests[line] = outcome
     75                 file_counts[line] += 1
     76 
>>   77         # `|` on two Counters returns the larger count of each line
     78         largest_file_counts |= file_counts
     79         malformed.extend(file_malformed)
     80         if file_malformed:
     81             _LOG.warning('file.malformed_lines', extra={'file': log_path.name, 'malformed': len(file_malformed)})
     82 
     83     counted_requests = [_CountedRequest(requests[line], count) for line, count in largest_file_counts.items()]
     84     total_requests = sum(largest_file_counts.values())
     85     totals = Totals(
     86         lines=lines,
     87         requests=total_requests,
```

### 2. analysis.py:106

```python
     98     )
     99     return report
    100 
    101 
    102 def _summariseHours(counted_requests: list[_CountedRequest], local_timezone: ZoneInfo) -> tuple[HourSummary, ...]:
    103     """Return one HourSummary for each local hour with a request, sorted by hour start."""
    104     requests_by_hour: dict[datetime, list[_CountedRequest]] = {}
    105     for counted in counted_requests:
>>  106         # Two local times in one ZoneInfo compare equal whatever their fold, so the two copies of a
>>  107         # repeated hour would merge. Key the hour on its start in UTC.
    108         hour_start = counted.request.local_time.replace(minute=0, second=0, microsecond=0).astimezone(UTC)
    109         requests_by_hour.setdefault(hour_start, []).append(counted)
    110 
    111     hours = []
    112     for hour_start, hour_requests in sorted(requests_by_hour.items()):
    113         class_counts: Counter[int] = Counter()
    114         sizes: list[int] = []
    115         for counted in hour_requests:
    116             class_counts[counted.request.status // 100] += counted.count
    117             if counted.request.size is not None:
```

### 3. analysis.py:143

```python
    135             ),
    136         )
    137     return tuple(hours)
    138 
    139 
    140 def _nearestRankPercentile(sorted_sizes: list[int], percent: int) -> int | None:
    141     if not sorted_sizes:
    142         return None
>>  143     # ceil(percent × n / 100) in integer arithmetic, so no float rounding moves the rank
    144     rank = -(-percent * len(sorted_sizes) // 100)
    145     return sorted_sizes[rank - 1]
    146 
    147 
    148 def _rankPaths(counted_requests: list[_CountedRequest], top_paths: int) -> tuple[PathCount, ...]:
    149     path_counts: Counter[str] = Counter()
    150     for counted in counted_requests:
    151         path_counts[counted.request.path] += counted.count
    152     ranked = sorted(path_counts.items(), key=lambda item: (-item[1], item[0]))
    153     return tuple(PathCount(path, requests) for path, requests in ranked[:top_paths])
```

### 4. config.py:51

```python
     43         raise _rejectConfig(config_path, f'{config_path} is not a JSON object')
     44     if set(raw_config) != {'timezone', 'top_paths'}:
     45         raise _rejectConfig(config_path, f'{config_path} has keys {sorted(raw_config)}, not timezone and top_paths')
     46 
     47     raw_timezone = raw_config['timezone']
     48     if not (isinstance(raw_timezone, str) and raw_timezone in zoneinfo.available_timezones()):
     49         raise _rejectConfig(config_path, f'timezone {raw_timezone!r} is not an IANA timezone name')
     50     top_paths = raw_config['top_paths']
>>   51     # bool subclasses Python int. Reject it too
     52     if not (isinstance(top_paths, int) and not isinstance(top_paths, bool) and top_paths > 0):
     53         raise _rejectConfig(config_path, f'top_paths {top_paths!r} is not a positive integer')
     54     return Config(timezone=ZoneInfo(raw_timezone), top_paths=top_paths)
     55 
     56 
     57 def _rejectConfig(config_path: Path, reason: str) -> ConfigError:
     58     _LOG.error('config.rejected', extra={'path': config_path, 'reason': reason, 'expected': _EXPECTED_FORM})
     59     return ConfigError(f'{reason} (expected {_EXPECTED_FORM})')
```

### 5. log_files.py:35

```python
     27 
     28 
     29 def findLogFiles(log_dir: Path) -> tuple[Path, ...]:
     30     """Return the access logs in log_dir, sorted by file name.
     31 
     32     Raises:
     33         LogReadError: log_dir is missing, is not a directory, or cannot be listed.
     34     """
>>   35     # matches:
>>   36     # `access.log`
>>   37     # `access.log.12.gz`
>>   38     # rejects:
>>   39     # `access.log.0`
>>   40     # `access.log.gz`
     41     LOG_NAME = r'access\.log(\.[1-9][0-9]*(\.gz)?)?'
     42     if not log_dir.is_dir():
     43         raise _rejectLogInput(log_dir, 'is not a directory')
     44     try:
     45         entries = list(log_dir.iterdir())
     46     except OSError as exc:
     47         raise _rejectLogInput(log_dir, f'cannot be listed: {exc.strerror}') from exc
     48     log_paths = [entry for entry in entries if re.fullmatch(LOG_NAME, entry.name) and entry.is_file()]
     49     return tuple(sorted(log_paths, key=lambda log_path: log_path.name))
     50 
```

### 6. log_files.py:62

```python
     54 
     55     Raises:
     56         LogReadError: the file cannot be read or decompressed.
     57     """
     58     try:
     59         with _openLogFile(log_path) as log_file:
     60             for raw_line in log_file:
     61                 yield raw_line.removesuffix(b'\n').removesuffix(b'\r')
>>   62     # gzip.BadGzipFile subclasses OSError. Catch it first
     63     except (gzip.BadGzipFile, EOFError, zlib.error) as exc:
     64         raise _rejectLogInput(log_path, f'cannot be decompressed: {exc}') from exc
     65     except OSError as exc:
     66         raise _rejectLogInput(log_path, f'cannot be read: {exc.strerror}') from exc
     67 
     68 
     69 def _openLogFile(log_path: Path) -> io.BufferedIOBase:
     70     if log_path.suffix == '.gz':
     71         return gzip.open(log_path, 'rb')
     72     return log_path.open('rb')
```

### 7. log_line.py:23

```python
     15 from access_report.vocabulary import Problem, Request
     16 
     17 
     18 def parseLogLine(line: bytes, local_timezone: ZoneInfo) -> Request | Problem:
     19     """Return the Request on the line, or the Problem of the first check it fails.
     20 
     21     The checks run in the order of the Problem members.
     22     """
>>   23     # host, ident, user, time, request, status, size, referer, user agent
     24     LINE_PATTERN = rb'(\S+) (\S+) (\S+) \[([^\]]*)\] "([^"]*)" ([1-5][0-9][0-9]) ([0-9]+|-) "([^"]*)" "([^"]*)"'
     25     # method, target, protocol
     26     # matches:
     27     # `GET /index.html?x=1 HTTP/1.1`
     28     # rejects:
     29     # `GET /search?q=red shoes HTTP/1.1`
     30     REQUEST_PATTERN = rb'[A-Z]+ ([^ ]*) HTTP/[0-9]\.[0-9]'
     31     line_match = re.fullmatch(LINE_PATTERN, line)
     32     if line_match is None:
     33         return Problem.SYNTAX
```

### 8. log_line.py:25

```python
     17 
     18 def parseLogLine(line: bytes, local_timezone: ZoneInfo) -> Request | Problem:
     19     """Return the Request on the line, or the Problem of the first check it fails.
     20 
     21     The checks run in the order of the Problem members.
     22     """
     23     # host, ident, user, time, request, status, size, referer, user agent
     24     LINE_PATTERN = rb'(\S+) (\S+) (\S+) \[([^\]]*)\] "([^"]*)" ([1-5][0-9][0-9]) ([0-9]+|-) "([^"]*)" "([^"]*)"'
>>   25     # method, target, protocol
>>   26     # matches:
>>   27     # `GET /index.html?x=1 HTTP/1.1`
>>   28     # rejects:
>>   29     # `GET /search?q=red shoes HTTP/1.1`
     30     REQUEST_PATTERN = rb'[A-Z]+ ([^ ]*) HTTP/[0-9]\.[0-9]'
     31     line_match = re.fullmatch(LINE_PATTERN, line)
     32     if line_match is None:
     33         return Problem.SYNTAX
     34     _, _, _, raw_time, raw_request, raw_status, raw_size, _, _ = line_match.groups()
     35 
     36     local_time = _parseLocalTime(raw_time, local_timezone)
     37     if local_time is None:
     38         return Problem.BAD_TIME
     39     request_match = re.fullmatch(REQUEST_PATTERN, raw_request)
```

### 9. log_line.py:54

```python
     46     size = None if raw_size == b'-' else int(raw_size)
     47     return Request(local_time=local_time, status=int(raw_status), size=size, path=path)
     48 
     49 
     50 def _parseLocalTime(raw_time: bytes, local_timezone: ZoneInfo) -> datetime | None:
     51     """Return the time in local_timezone, or None when it is malformed, not a real date and time, or out
     52     of the range of datetime."""
     53     MONTHS = (b'Jan', b'Feb', b'Mar', b'Apr', b'May', b'Jun', b'Jul', b'Aug', b'Sep', b'Oct', b'Nov', b'Dec')
>>   54     # matches:
>>   55     # `24/Oct/2026:22:40:05 -0430`
     56     TIME_PATTERN = rb'([0-9]{2})/([A-Za-z]{3})/([0-9]{4}):([0-9]{2}):([0-9]{2}):([0-9]{2}) ([+-])([0-9]{2})([0-9]{2})'
     57     time_match = re.fullmatch(TIME_PATTERN, raw_time)
     58     if not (time_match and time_match[2] in MONTHS):
     59         return None
     60     day, month, year, hour, minute, second, sign, offset_hours, offset_minutes = time_match.groups()
     61 
     62     if not (int(offset_hours) < 24 and int(offset_minutes) < 60):
     63         return None
     64     offset = timedelta(hours=int(offset_hours), minutes=int(offset_minutes))
     65     line_timezone = timezone(-offset if sign == b'-' else offset)
```

### 10. report_json.py:55

```python
     47             'requests': report.totals.requests,
     48             'duplicates': report.totals.duplicates,
     49             'malformed': report.totals.malformed,
     50         },
     51     }
     52 
     53 
     54 def writeReportJson(report: Report, out_path: Path) -> None:
>>   55     # write_text() would turn '\n' into '\r\n' on Windows
     56     out_path.write_bytes((json.dumps(serializeReport(report), indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
```

### 11. summary_table.py:54

```python
     46     return '\n\n'.join(['\n'.join(hour_rows), '\n'.join(path_rows), totals_row])
     47 
     48 
     49 def _formatSize(size: int | None) -> str:
     50     return '-' if size is None else str(size)
     51 
     52 
     53 def _escapeNonPrintable(path: str) -> str:
>>   54     # a decoded path can contain control characters, such as a newline or ESC. Printed raw, a control
>>   55     # character breaks the table
     56     return ''.join(character if character.isprintable() else ascii(character)[1:-1] for character in path)
```

### 12. vocabulary.py:47

```python
     39 
     40 @dataclass(frozen=True)
     41 class MalformedLine:
     42     file_name: str
     43     line_number: int
     44     problem: Problem
     45 
     46 
>>   47 # request counts for the status classes 1xx to 5xx, in that order
     48 StatusCounts = tuple[int, int, int, int, int]
     49 
     50 
     51 @dataclass(frozen=True)
     52 class HourSummary:
     53     hour_start: datetime
     54     requests: int
     55     status_counts: StatusCounts
     56     size_p50: int | None
     57     size_p95: int | None
```

## P12 build planner (package buildplan): 6 comments

`scratchpad/cycle15/p12/buildplan`

### 13. graph.py:31

```python
     23     graph makes the cycles through it appear twice. The search time grows with
     24     the number of simple paths, so a dense graph is slow.
     25 
     26     Returns:
     27         Cycles sorted element by element.
     28     """
     29     cycles: list[Cycle] = []
     30     for start in sorted(graph):
>>   31         # a cycle is found only from its smallest member, so the search enters only larger names
     32         path = [start]
     33         pending: list[Iterator[PackageName]] = [iter(graph[start])]
     34         while pending:
     35             dependency = next(pending[-1], None)
     36             if dependency is None:
     37                 pending.pop()
     38                 path.pop()
     39             elif dependency == start:
     40                 cycles.append(tuple(path))
     41             elif dependency in graph and dependency > start and dependency not in path:
```

### 14. pattern.py:23

```python
     15 import functools
     16 import re
     17 
     18 
     19 def selectedByPattern(pattern: str, source_path: str) -> bool:
     20     pattern_segments = pattern.split('/')
     21     path_segments = source_path.split('/')
     22     last_segment = len(path_segments) - 1
>>   23     # matches[j] is whether the pattern segments processed so far match path_segments[j:]
     24     matches = [False] * len(path_segments) + [True]
     25     for segment in reversed(pattern_segments):
     26         if segment == '**':
     27             following = matches
     28             matches = [False] * len(following)
     29             for start in reversed(range(len(following))):
     30                 matches[start] = following[start] or (start < last_segment and matches[start + 1])
     31         else:
     32             segment_regex = _compileSegment(segment)
     33             matches = [
```

### 15. pattern.py:45

```python
     37                 for start in range(len(matches))
     38             ]
     39     return matches[0]
     40 
     41 
     42 @functools.cache
     43 def _compileSegment(segment: str) -> re.Pattern[str]:
     44     WILDCARDS = {'*': '.*', '?': '.'}
>>   45     # a file name can contain a newline. DOTALL makes `*` and `?` match it
     46     return re.compile(''.join(WILDCARDS.get(character, re.escape(character)) for character in segment), re.DOTALL)
```

### 16. vocabulary.py:13

```python
      5 from collections.abc import Mapping
      6 from dataclasses import dataclass
      7 from enum import Enum
      8 from pathlib import Path
      9 from typing import NewType
     10 
     11 
     12 PackageName = NewType('PackageName', str)
>>   13 # relative to the package directory, with `/` separators
     14 SourcePath = NewType('SourcePath', str)
     15 # lowercase hex SHA-256 of a file's bytes
     16 Digest = NewType('Digest', str)
     17 SourceDigests = Mapping[SourcePath, Digest]
     18 Cycle = tuple[PackageName, ...]
     19 # every declared package, mapped to its dependencies
     20 DependencyGraph = Mapping[PackageName, tuple[PackageName, ...]]
     21 
     22 
     23 class Reason(Enum):
```

### 17. vocabulary.py:15

```python
      7 from enum import Enum
      8 from pathlib import Path
      9 from typing import NewType
     10 
     11 
     12 PackageName = NewType('PackageName', str)
     13 # relative to the package directory, with `/` separators
     14 SourcePath = NewType('SourcePath', str)
>>   15 # lowercase hex SHA-256 of a file's bytes
     16 Digest = NewType('Digest', str)
     17 SourceDigests = Mapping[SourcePath, Digest]
     18 Cycle = tuple[PackageName, ...]
     19 # every declared package, mapped to its dependencies
     20 DependencyGraph = Mapping[PackageName, tuple[PackageName, ...]]
     21 
     22 
     23 class Reason(Enum):
     24     NEW = 'new'
     25     SOURCES_CHANGED = 'sources changed'
```

### 18. vocabulary.py:19

```python
     11 
     12 PackageName = NewType('PackageName', str)
     13 # relative to the package directory, with `/` separators
     14 SourcePath = NewType('SourcePath', str)
     15 # lowercase hex SHA-256 of a file's bytes
     16 Digest = NewType('Digest', str)
     17 SourceDigests = Mapping[SourcePath, Digest]
     18 Cycle = tuple[PackageName, ...]
>>   19 # every declared package, mapped to its dependencies
     20 DependencyGraph = Mapping[PackageName, tuple[PackageName, ...]]
     21 
     22 
     23 class Reason(Enum):
     24     NEW = 'new'
     25     SOURCES_CHANGED = 'sources changed'
     26     DEPENDENCY_REBUILT = 'dependency rebuilt'
     27 
     28 
     29 @dataclass(frozen=True)
```

## P13 calendar recurrence (package ics_expand): 11 comments

`scratchpad/cycle15/p13/ics_expand`

### 19. content_lines.py:41

```python
     33     try:
     34         calendar_bytes = calendar_path.read_bytes()
     35     except OSError as exc:
     36         raise _rejectCalendarFile(calendar_path, f'is unreadable ({exc.strerror})') from exc
     37 
     38     content_lines: list[ContentLine | _MalformedLine] = []
     39     for unfolded in _unfoldLines(calendar_bytes):
     40         try:
>>   41             # under RFC 5545 a fold can split a UTF-8 character. Decode after unfolding
     42             text = unfolded.content.decode('utf-8')
     43         except UnicodeDecodeError as exc:
     44             raise _rejectCalendarFile(calendar_path, f'is not UTF-8 at line {unfolded.line}') from exc
     45         if text:
     46             content_lines.append(_parseContentLine(unfolded.line, text))
     47 
     48     first = content_lines[0] if content_lines else None
     49     if not (isinstance(first, ContentLine) and first.name == 'BEGIN' and first.value.upper() == 'VCALENDAR'):
     50         raise _rejectCalendarFile(calendar_path, 'does not start with BEGIN:VCALENDAR')
     51 
```

### 20. content_lines.py:74

```python
     66             unfolded[-1] = _UnfoldedLine(previous.line, previous.content + content[1:])
     67         else:
     68             unfolded.append(_UnfoldedLine(number, content))
     69 
     70     return unfolded
     71 
     72 
     73 def _parseContentLine(line: int, text: str) -> ContentLine | _MalformedLine:
>>   74     # NAME, then parameters, then the value after the first colon outside double quotes
>>   75     # matches:
>>   76     # `DTSTART;TZID="Europe/Berlin":20270131T170000`
>>   77     # `SUMMARY:Release review\, London`
>>   78     # rejects:
>>   79     # `RRULE FREQ=DAILY`
     80     CONTENT_LINE = re.compile(r'(?P<name>[^;:"]+)(?P<parameters>(?:;(?:[^";:]|"[^"]*")*)*):(?P<value>.*)')
     81     # matches `;TZID="Europe/Berlin"` and `;TZID=Asia/Tokyo` in the parameters
     82     PARAMETER = re.compile(r';(?P<name>[^=;]*)=(?P<value>(?:[^";]|"[^"]*")*)')
     83 
     84     match = CONTENT_LINE.fullmatch(text)
     85     if match is None:
     86         LOG.debug('calendar.malformed_line', extra={'line': line})
     87         return _MalformedLine(line)
     88 
     89     tzid = None
```

### 21. content_lines.py:81

```python
     73 def _parseContentLine(line: int, text: str) -> ContentLine | _MalformedLine:
     74     # NAME, then parameters, then the value after the first colon outside double quotes
     75     # matches:
     76     # `DTSTART;TZID="Europe/Berlin":20270131T170000`
     77     # `SUMMARY:Release review\, London`
     78     # rejects:
     79     # `RRULE FREQ=DAILY`
     80     CONTENT_LINE = re.compile(r'(?P<name>[^;:"]+)(?P<parameters>(?:;(?:[^";:]|"[^"]*")*)*):(?P<value>.*)')
>>   81     # matches `;TZID="Europe/Berlin"` and `;TZID=Asia/Tokyo` in the parameters
     82     PARAMETER = re.compile(r';(?P<name>[^=;]*)=(?P<value>(?:[^";]|"[^"]*")*)')
     83 
     84     match = CONTENT_LINE.fullmatch(text)
     85     if match is None:
     86         LOG.debug('calendar.malformed_line', extra={'line': line})
     87         return _MalformedLine(line)
     88 
     89     tzid = None
     90     for parameter in PARAMETER.finditer(match['parameters']):
     91         if parameter['name'].upper() == 'TZID':
```

### 22. content_lines.py:103

```python
     95 
     96 
     97 def _groupEvents(content_lines: list[ContentLine | _MalformedLine]) -> list[RawEvent]:
     98     """Group the content lines of each top-level VEVENT into a RawEvent.
     99 
    100     A VEVENT still open at the end of the file is returned as not well formed.
    101     """
    102     events: list[RawEvent] = []
>>  103     # names of the components open at the current line, outermost first
    104     open_components: list[str] = []
    105     event_line = 0
    106     event_properties: list[ContentLine] = []
    107     event_well_formed = True
    108 
    109     for content_line in content_lines:
    110         in_event = open_components == ['VCALENDAR', 'VEVENT']
    111         if isinstance(content_line, _MalformedLine):
    112             if in_event:
    113                 event_well_formed = False
```

### 23. event_parser.py:107

```python
     99 
    100 
    101 def _rejectEvent(line: int, uid: str | None, reason: RejectReason) -> EventRejectedError:
    102     LOG.debug('event.rejected', extra={'line': line, 'uid': uid, 'reason': reason.value})
    103     return EventRejectedError(RejectedEvent(line, uid, reason))
    104 
    105 
    106 def _parseLocalTime(raw_value: str, tzid: str | None) -> LocalTime | None:
>>  107     # matches:
>>  108     # `20270131T170000`
>>  109     # `20270320T230000Z`
    110     DATE_TIME = re.compile(r'([0-9]{4})([0-9]{2})([0-9]{2})T([0-9]{2})([0-9]{2})([0-9]{2})(Z?)')
    111 
    112     match = DATE_TIME.fullmatch(raw_value)
    113     if match is None:
    114         return None
    115 
    116     year, month, day, hour, minute, second = (int(field) for field in match.groups()[:6])
    117     utc_form = tzid is None and match[7] == 'Z'
    118     zoned_form = tzid is not None and match[7] == ''
    119     real_date = year >= 1 and 1 <= month <= 12 and 1 <= day <= calendar.monthrange(year, month)[1]
```

### 24. event_parser.py:131

```python
    123     timezone = pendulum.UTC if tzid is None else pendulum.Timezone(tzid)
    124     return LocalTime(pendulum.date(year, month, day), pendulum.time(hour, minute, second), timezone)
    125 
    126 
    127 def _parseRule(raw_rule: str) -> RecurrenceRule | None:
    128     """Parse an RRULE value. None when the rule is unsupported."""
    129     BY_DAY_ITEM = r'(?:[+-]?[1-5])?(?:MO|TU|WE|TH|FR|SA|SU)'
    130     BY_MONTH_DAY_ITEM = r'[+-]?(?:[1-9]|[12][0-9]|3[01])'
>>  131     # BYDAY matches `MO,WE` and `-1FR`, and rejects `0MO` and `MO,`
>>  132     # BYMONTHDAY matches `31` and `1,-1`, and rejects `0` and `32`
    133     PART_VALUES = {
    134         'FREQ': re.compile(r'DAILY|WEEKLY|MONTHLY'),
    135         'INTERVAL': re.compile(r'[1-9][0-9]*'),
    136         'COUNT': re.compile(r'[1-9][0-9]*'),
    137         'UNTIL': re.compile(r'[0-9]{8}T[0-9]{6}Z'),
    138         'BYDAY': re.compile(rf'{BY_DAY_ITEM}(?:,{BY_DAY_ITEM})*'),
    139         'BYMONTHDAY': re.compile(rf'{BY_MONTH_DAY_ITEM}(?:,{BY_MONTH_DAY_ITEM})*'),
    140     }
    141 
    142     parts: dict[str, str] = {}
```

### 25. event_parser.py:181

```python
    173         'SU': WeekDay.SUNDAY,
    174     }
    175 
    176     raw_ordinal = raw_item[:-2]
    177     return ByDay(WEEKDAYS[raw_item[-2:]], int(raw_ordinal) if raw_ordinal else None)
    178 
    179 
    180 def _unescapeText(raw_text: str) -> str:
>>  181     # matches `\,`, `\;`, `\\`, `\n` and `\N`
    182     ESCAPE = re.compile(r'\\([\\,;nN])')
    183     return ESCAPE.sub(lambda escape: '\n' if escape[1] in 'nN' else escape[1], raw_text)
```

### 26. expansion.py:92

```python
     84 
     85 
     86 def _rejectParsedEvent(event: CalendarEvent, reason: RejectReason) -> RejectedEvent:
     87     LOG.debug('event.rejected', extra={'line': event.line, 'uid': event.uid, 'reason': reason.value})
     88     return RejectedEvent(event.line, event.uid, reason)
     89 
     90 
     91 def _resolveInstant(local: LocalTime) -> DateTime:
>>   92     # pendulum.datetime() has no fold value that gives both the offset before a jump forward and the
>>   93     # first of two repeated times. A stdlib datetime with fold=0 gives both.
     94     wall = datetime.datetime.combine(local.date, local.time_of_day, tzinfo=local.timezone)
     95     return pendulum.from_timestamp(wall.timestamp(), tz=local.timezone)
     96 
     97 
     98 def _expandMaster(master: CalendarEvent, overrides: list[_Override], end: DateTime) -> Expansion:
     99     """List the occurrences of one master event, with its overrides applied and no window.
    100 
    101     Occurrences are listed up to `end` or the last instant an override replaces, whichever is later.
    102     """
    103     horizon = max([end, *(override.replaced for override in overrides)])
```

### 27. expansion.py:105

```python
     97 
     98 def _expandMaster(master: CalendarEvent, overrides: list[_Override], end: DateTime) -> Expansion:
     99     """List the occurrences of one master event, with its overrides applied and no window.
    100 
    101     Occurrences are listed up to `end` or the last instant an override replaces, whichever is later.
    102     """
    103     horizon = max([end, *(override.replaced for override in overrides)])
    104     timezone = master.start.timezone
>>  105     # One day of margin past the horizon. An offset change can put an instant before the horizon on
>>  106     # a later local date.
    107     last_date = horizon.in_timezone(timezone).date().add(days=1)
    108     dates = listOccurrenceDates(master.start.date, master.rule, last_date)
    109     starts = [_resolveInstant(LocalTime(day, master.start.time_of_day, timezone)) for day in dates]
    110 
    111     rule = master.rule
    112     if rule is not None and rule.count is not None:
    113         starts = starts[: rule.count]
    114     if rule is not None and rule.until is not None:
    115         until = _resolveInstant(rule.until)
    116         starts = [start for start in starts if start <= until]
```

### 28. recurrence.py:41

```python
     33 
     34 
     35 def _computePeriodStart(first: Date, rule: RecurrenceRule, index: int) -> Date:
     36     step = index * rule.interval
     37     match rule.frequency:
     38         case Frequency.DAILY:
     39             return first.add(days=step)
     40         case Frequency.WEEKLY:
>>   41             # weeks run Monday to Sunday, and WeekDay.MONDAY is 0
     42             return first.subtract(days=first.day_of_week).add(weeks=step)
     43         case Frequency.MONTHLY:
     44             return first.first_of('month').add(months=step)
     45 
     46 
     47 def _listPeriodDates(period_start: Date, first: Date, rule: RecurrenceRule) -> list[Date]:
     48     match rule.frequency:
     49         case Frequency.DAILY:
     50             weekdays = {item.weekday for item in rule.by_day}
     51             return [period_start] if not weekdays or period_start.day_of_week in weekdays else []
```

### 29. report.py:72

```python
     64     }
     65     return json.dumps(result, indent=2, ensure_ascii=False) + '\n'
     66 
     67 
     68 def renderTable(expansion: Expansion) -> str:
     69     occurrence_rows = [('START UTC', 'START LOCAL', 'TIMEZONE', 'MOVED FROM UTC', 'UID', 'SUMMARY')]
     70     for occurrence in expansion.occurrences:
     71         moved_from = '-' if occurrence.moved_from is None else _formatUtc(occurrence.moved_from)
>>   72         # a SUMMARY can have a line break. Print it as \n to keep one row per occurrence
     73         summary = '' if occurrence.summary is None else occurrence.summary.replace('\n', '\\n')
     74         local = occurrence.start.format('YYYY-MM-DD[T]HH:mm:ssZ')
     75         timezone = occurrence.start.timezone_name or ''
     76         occurrence_rows.append((_formatUtc(occurrence.start), local, timezone, moved_from, occurrence.uid, summary))
     77     table_lines = _alignColumns(occurrence_rows)
     78 
     79     if expansion.rejected:
     80         rejected_rows = [('LINE', 'REJECTED UID', 'REASON')]
     81         rejected_rows.extend((str(event.line), event.uid or '-', event.reason.value) for event in expansion.rejected)
     82         table_lines.extend(['', *_alignColumns(rejected_rows)])
```

## P14 directory sync (package dirsync): 10 comments

`scratchpad/cycle15/p14/dirsync`

### 30. apply.py:102

```python
     94         suffix=TEMPORARY_SUFFIX,
     95         dir=target.parent,
     96     )
     97     temporary_path = Path(raw_temporary_path)
     98     try:
     99         with os.fdopen(descriptor, 'wb') as temporary_file, source_file.open('rb') as source_stream:
    100             shutil.copyfileobj(source_stream, temporary_file)
    101             temporary_file.flush()
>>  102             # after a crash, the rename can be on disk and the file's data not. Flush the data first
    103             os.fsync(temporary_file.fileno())
    104         shutil.copystat(source_file, temporary_path)
    105         temporary_path.replace(target)
    106     except OSError:
    107         temporary_path.unlink(missing_ok=True)
    108         raise
    109 
    110 
    111 def _rejectAction(action: SyncAction, reason: str) -> ApplyError:
    112     LOG.error('apply.failed', extra={'action': action.kind.value, 'path': action.path, 'reason': reason})
```

### 31. ignore.py:55

```python
     47             continue
     48 
     49         negated = glob.startswith('!')
     50         glob = glob.removeprefix('!')
     51         directory_only = glob.endswith('/')
     52         glob = glob.removesuffix('/')
     53         anchored = '/' in glob
     54         glob = glob.removeprefix('/')
>>   55         # `!`, `/` and `!/` are empty once stripped
     56         if not glob:
     57             continue
     58 
     59         rule = IgnoreRule(_compileGlob(glob), negated=negated, directory_only=directory_only, anchored=anchored)
     60         rules.append(rule)
     61 
     62     return tuple(rules)
     63 
     64 
     65 def ignored(rules: Iterable[IgnoreRule], path: RelativePath, *, is_directory: bool) -> bool:
```

### 32. ignore.py:77

```python
     69         subject = path if rule.anchored else name
     70         if (is_directory or not rule.directory_only) and rule.pattern.fullmatch(subject):
     71             verdict = not rule.negated
     72 
     73     return verdict
     74 
     75 
     76 def _compileGlob(glob: str) -> re.Pattern[str]:
>>   77     # a whole `**` segment spans directories: `a/**/x` matches `a/x` and `a/b/c/x`, and `a/**` matches
>>   78     # everything below `a`
     79     segments = glob.split('/')
     80     pieces: list[str] = []
     81     for position, segment in enumerate(segments):
     82         last = position == len(segments) - 1
     83         if segment == '**':
     84             pieces.append('.+' if last else '(?:[^/]+/)*')
     85             continue
     86 
     87         stars_split = re.split(r'(\*+)', segment)
     88         pieces.extend('[^/]*' if part.startswith('*') else re.escape(part) for part in stars_split)
```

### 33. plan.py:54

```python
     46             or the ignore file cannot be read.
     47         TreeReadError: a directory or file inside a tree could not be read.
     48     """
     49     _checkRoots(source_root, replica_root)
     50     rules = ignore.readIgnoreRules(ignore_path) if ignore_path is not None else ()
     51     source = walk.walkTree(source_root, rules, detect_case_clashes=True)
     52     replica = walk.walkTree(replica_root, rules, detect_case_clashes=False)
     53 
>>   54     # An ignored replica entry is never touched. With a dir-only pattern, the replica can have an
>>   55     # ignored directory at the path of a source file. That file is not copied either.
     56     blocked = source.conflict_paths | replica.conflict_paths | replica.ignored_paths
     57     source_files = _dropConflictPaths(source.file_sizes, blocked)
     58     replica_files = _dropConflictPaths(replica.file_sizes, blocked)
     59     source_directories = _dropConflictPaths(source.directories, blocked)
     60     replica_directories = _dropConflictPaths(replica.directories, blocked)
     61 
     62     shared_files = source_files & replica_files
     63     updates = [path for path in shared_files if not _equalContent(source, replica, path)]
     64     # a file cannot replace a directory with an ignored or conflicting entry below it
     65     stranded = source_files & replica.pinned_directories
```

### 34. plan.py:64

```python
     56     blocked = source.conflict_paths | replica.conflict_paths | replica.ignored_paths
     57     source_files = _dropConflictPaths(source.file_sizes, blocked)
     58     replica_files = _dropConflictPaths(replica.file_sizes, blocked)
     59     source_directories = _dropConflictPaths(source.directories, blocked)
     60     replica_directories = _dropConflictPaths(replica.directories, blocked)
     61 
     62     shared_files = source_files & replica_files
     63     updates = [path for path in shared_files if not _equalContent(source, replica, path)]
>>   64     # a file cannot replace a directory with an ignored or conflicting entry below it
     65     stranded = source_files & replica.pinned_directories
     66     copies = sorted(source_files - replica_files - stranded)
     67     deletes = sorted(replica_files - source_files)
     68     renames = _pairRenames(
     69         [path for path in copies if path not in replica_directories],
     70         [path for path in deletes if path not in source_directories],
     71         source,
     72         replica,
     73     )
     74     renamed_paths = {action.path for action in renames} | {action.from_path for action in renames}
```

### 35. plan.py:89

```python
     81         *(SyncAction(ActionKind.UPDATE, path) for path in updates),
     82         *(SyncAction(ActionKind.DELETE, path) for path in deletes if path not in renamed_paths),
     83         *(SyncAction(ActionKind.MKDIR, path) for path in source_directories - replica_directories),
     84         *(
     85             SyncAction(ActionKind.RMDIR, path)
     86             for path in replica_directories - source_directories - replica.pinned_directories
     87         ),
     88     ]
>>   89     # the same conflict at the same path in both trees is reported once
     90     conflicts = set(source.conflicts) | set(replica.conflicts)
     91     return SyncPlan(
     92         actions=tuple(sorted(actions, key=lambda action: (action.path, action.kind.value))),
     93         conflicts=tuple(sorted(conflicts, key=lambda conflict: (conflict.path, conflict.kind.value))),
     94         unchanged_files=len(shared_files) - len(updates),
     95     )
     96 
     97 
     98 def _checkRoots(source_root: Path, replica_root: Path) -> None:
     99     for root in (source_root, replica_root):
```

### 36. plan.py:110

```python
    102 
    103     resolved_source = source_root.resolve()
    104     resolved_replica = replica_root.resolve()
    105     if resolved_source.is_relative_to(resolved_replica) or resolved_replica.is_relative_to(resolved_source):
    106         raise _rejectInput(f'{source_root} and {replica_root} overlap. Neither tree may be inside the other')
    107 
    108 
    109 def _dropConflictPaths(paths: Iterable[RelativePath], blocked: Collection[RelativePath]) -> set[RelativePath]:
>>  110     # a path below a conflict path is dropped too
    111     return {
    112         path for path in paths if not any(lineage_path in blocked for lineage_path in walk.listPathAndAncestors(path))
    113     }
    114 
    115 
    116 def _equalContent(source: TreeListing, replica: TreeListing, path: RelativePath) -> bool:
    117     if source.file_sizes[path] != replica.file_sizes[path]:
    118         return False
    119     return _computeSha256(source.root, path) == _computeSha256(replica.root, path)
    120 
```

### 37. walk.py:96

```python
     88         conflicts=tuple(conflicts),
     89         conflict_paths=frozenset(conflict_paths),
     90         ignored_paths=frozenset(ignored_paths),
     91         pinned_directories=frozenset(pinned_directories),
     92     )
     93 
     94 
     95 def _decodable(name: str) -> bool:
>>   96     # os.scandir() decodes invalid UTF-8 with surrogateescape. Re-encode to test the raw bytes
     97     try:
     98         os.fsencode(name).decode('utf-8')
     99     except UnicodeDecodeError:
    100         return False
    101 
    102     return True
    103 
    104 
    105 def _displayUndecodable(directory: RelativePath, name: str) -> str:
    106     # `bad\xff.txt`
```

### 38. walk.py:106

```python
     98         os.fsencode(name).decode('utf-8')
     99     except UnicodeDecodeError:
    100         return False
    101 
    102     return True
    103 
    104 
    105 def _displayUndecodable(directory: RelativePath, name: str) -> str:
>>  106     # `bad\xff.txt`
    107     shown_name = os.fsencode(name).decode('utf-8', errors='backslashreplace')
    108     return _joinPath(directory, shown_name)
    109 
    110 
    111 def _joinPath(directory: RelativePath, name: str) -> RelativePath:
    112     return RelativePath(f'{directory}/{name}' if directory else name)
    113 
    114 
    115 def _directory(dir_entry: os.DirEntry[str]) -> bool:
    116     return dir_entry.is_dir(follow_symlinks=False)
```

### 39. walk.py:146

```python
    138 def _readSize(root: Path, path: RelativePath, dir_entry: os.DirEntry[str]) -> int:
    139     try:
    140         return dir_entry.stat(follow_symlinks=False).st_size
    141     except OSError as exc:
    142         raise _rejectTree(root, path, exc) from exc
    143 
    144 
    145 def listPathAndAncestors(path: RelativePath) -> list[RelativePath]:
>>  146     # `a/b/c` -> [`a/b/c`, `a/b`, `a`]. The root is never listed
    147     lineage: list[RelativePath] = []
    148     while path:
    149         lineage.append(path)
    150         path = RelativePath(path.rpartition('/')[0])
    151 
    152     return lineage
    153 
    154 
    155 def _rejectTree(root: Path, path: RelativePath, exc: OSError) -> TreeReadError:
    156     reason = exc.strerror or type(exc).__name__
```

## P15 spreadsheet formulas (package spreadsheet): 18 comments

`scratchpad/cycle15/p15/spreadsheet`

### 40. arithmetic.py:28

```python
     20     InvalidOperation,
     21     Overflow,
     22     localcontext,
     23 )
     24 
     25 from spreadsheet.vocabulary import ArithmeticOperator, ErrorCode, UnaryOperator
     26 
     27 
>>   28 # Python's default decimal context. A caller can change decimal.DefaultContext, so the copy is built here
     29 _RESULT_CONTEXT = Context(
     30     prec=28,
     31     rounding=ROUND_HALF_EVEN,
     32     Emin=-999_999,
     33     Emax=999_999,
     34     traps=[DivisionByZero, InvalidOperation, Overflow],
     35 )
     36 # wide enough that a sum or a quantize() is exact
     37 _EXACT_CONTEXT = Context(prec=MAX_PREC, Emin=MIN_EMIN, Emax=MAX_EMAX)
     38 # Decimal.__pow__() computes a power whose exact value has more digits than this
```

### 41. arithmetic.py:36

```python
     28 # Python's default decimal context. A caller can change decimal.DefaultContext, so the copy is built here
     29 _RESULT_CONTEXT = Context(
     30     prec=28,
     31     rounding=ROUND_HALF_EVEN,
     32     Emin=-999_999,
     33     Emax=999_999,
     34     traps=[DivisionByZero, InvalidOperation, Overflow],
     35 )
>>   36 # wide enough that a sum or a quantize() is exact
     37 _EXACT_CONTEXT = Context(prec=MAX_PREC, Emin=MIN_EMIN, Emax=MAX_EMAX)
     38 # Decimal.__pow__() computes a power whose exact value has more digits than this
     39 _EXACT_POWER_DIGITS = 10_000
     40 
     41 _LOG = logging.getLogger(__name__)
     42 
     43 
     44 def representable(number: Decimal) -> bool:
     45     return number.is_zero() or _RESULT_CONTEXT.Emin <= number.adjusted() <= _RESULT_CONTEXT.Emax
     46 
```

### 42. arithmetic.py:38

```python
     30     prec=28,
     31     rounding=ROUND_HALF_EVEN,
     32     Emin=-999_999,
     33     Emax=999_999,
     34     traps=[DivisionByZero, InvalidOperation, Overflow],
     35 )
     36 # wide enough that a sum or a quantize() is exact
     37 _EXACT_CONTEXT = Context(prec=MAX_PREC, Emin=MIN_EMIN, Emax=MAX_EMAX)
>>   38 # Decimal.__pow__() computes a power whose exact value has more digits than this
     39 _EXACT_POWER_DIGITS = 10_000
     40 
     41 _LOG = logging.getLogger(__name__)
     42 
     43 
     44 def representable(number: Decimal) -> bool:
     45     return number.is_zero() or _RESULT_CONTEXT.Emin <= number.adjusted() <= _RESULT_CONTEXT.Emax
     46 
     47 
     48 def computeArithmetic(operator: ArithmeticOperator, left: Decimal, right: Decimal) -> Decimal | ErrorCode:
```

### 43. arithmetic.py:103

```python
     95 
     96     Returns:
     97         ErrorCode.VALUE when digits is not whole.
     98     """
     99     if digits != digits.to_integral_value():
    100         return ErrorCode.VALUE
    101     if number.is_zero() or digits >= -_readExponent(number):
    102         return _computeRounded(lambda: +number)
>>  103     # |number| is under half a unit in the last place kept
    104     if -digits > number.adjusted() + 1:
    105         return Decimal(0)
    106 
    107     places = int(digits)
    108     with localcontext(_EXACT_CONTEXT):
    109         rounded = number.quantize(Decimal((0, (1,), -places)), rounding=ROUND_HALF_UP)
    110 
    111     return _computeRounded(lambda: +rounded)
    112 
    113 
```

### 44. arithmetic.py:133

```python
    125         return ErrorCode.VALUE
    126     if exponent.is_zero():
    127         return Decimal(1)
    128     if base.is_zero():
    129         return ErrorCode.DIVISION_BY_ZERO if exponent < 0 else Decimal(0)
    130 
    131     base_digits = len(base.as_tuple().digits) + abs(_readExponent(base))
    132     if abs(exponent) > _EXACT_POWER_DIGITS // base_digits:
>>  133         # not exact. Python's decimal docs promise only "almost always correctly rounded" for a power
    134         return _computeRounded(lambda: base**exponent)
    135 
    136     power = int(exponent)
    137     numerator, denominator = base.as_integer_ratio()
    138     if power < 0:
    139         numerator, denominator, power = denominator, numerator, -power
    140 
    141     return _computeRounded(lambda: Decimal(numerator**power) / Decimal(denominator**power))
    142 
    143 
```

### 45. arithmetic.py:145

```python
    137     numerator, denominator = base.as_integer_ratio()
    138     if power < 0:
    139         numerator, denominator, power = denominator, numerator, -power
    140 
    141     return _computeRounded(lambda: Decimal(numerator**power) / Decimal(denominator**power))
    142 
    143 
    144 def _readExponent(number: Decimal) -> int:
>>  145     # as_tuple().exponent is typed to admit the letters of NaN and infinity. Derive it from adjusted()
    146     return number.adjusted() - len(number.as_tuple().digits) + 1
```

### 46. dependency_graph.py:12

```python
      4 
      5 from collections import defaultdict, deque
      6 from collections.abc import Mapping
      7 
      8 from spreadsheet.vocabulary import CellAddress, EvaluationOrder, Formula
      9 
     10 
     11 def orderFormulas(formulas: Mapping[CellAddress, Formula]) -> EvaluationOrder:
>>   12     # Kahn's algorithm. A cell is added to the order once every formula cell it depends on is in it.
>>   13     # The cells never added are on a cycle or depend on one.
     14     dependents: defaultdict[CellAddress, list[CellAddress]] = defaultdict(list)
     15     unplaced_dependencies: dict[CellAddress, int] = {}
     16     for address, formula in formulas.items():
     17         formula_dependencies = formula.dependencies.intersection(formulas)
     18         unplaced_dependencies[address] = len(formula_dependencies)
     19         for dependency in formula_dependencies:
     20             dependents[dependency].append(address)
     21 
     22     ready = deque(address for address, count in unplaced_dependencies.items() if count == 0)
     23     ordered: list[CellAddress] = []
```

### 47. evaluation.py:46

```python
     38     Call evaluateFormula() for a cell after every formula cell it reads.
     39     """
     40 
     41     def __init__(self, values: Mapping[CellAddress, CellValue]) -> None:
     42         self.values = dict(values)
     43 
     44     def evaluateFormula(self, address: CellAddress, formula: Formula) -> None:
     45         value = self.evaluateExpression(formula.expression)
>>   46         # a formula whose result is an empty cell gives the number 0
     47         self.values[address] = Decimal(0) if value is None else value
     48 
     49     def evaluateExpression(self, expression: Expression) -> CellValue | None:
     50         """Evaluate an expression of a formula.
     51 
     52         Returns:
     53             None for a reference to an empty cell, or for an IF() whose branch taken is one.
     54         """
     55         match expression:
     56             case NumberLiteral():
```

### 48. evaluation.py:65

```python
     57                 return expression.number
     58             case TextLiteral():
     59                 return expression.text
     60             case ErrorLiteral():
     61                 return expression.error
     62             case CellReference():
     63                 return self.values.get(expression.address)
     64             case CellRange():
>>   65                 # a range is valid only as a whole argument of SUM, MIN or MAX. readArgument() reads those
     66                 return ErrorCode.VALUE
     67             case SignedOperand():
     68                 number = _readNumber(self.evaluateExpression(expression.operand))
     69                 if isinstance(number, ErrorCode):
     70                     return number
     71                 return arithmetic.applySign(expression.operator, number)
     72             case OperatorChain():
     73                 value = self.evaluateExpression(expression.first)
     74                 for step in expression.steps:
     75                     value = _applyOperator(step.operator, value, self.evaluateExpression(step.operand))
```

### 49. evaluation.py:230

```python
    222             return ''
    223         case bool():
    224             return False
    225         case Decimal() | None:
    226             return Decimal(0)
    227 
    228 
    229 def _compareOrder(left: Decimal | str | bool, right: Decimal | str | bool) -> int | ErrorCode:
>>  230     # -1, 0 or 1 as left is below, equal to or above right
    231     if isinstance(left, Decimal) and isinstance(right, Decimal):
    232         return (left > right) - (left < right)
    233     if isinstance(left, bool) and isinstance(right, bool):
    234         return left - right
    235     if isinstance(left, str) and isinstance(right, str):
    236         left_key, right_key = left.casefold(), right.casefold()
    237         return (left_key > right_key) - (left_key < right_key)
    238 
    239     return ErrorCode.VALUE
    240 
```

### 50. evaluation.py:268

```python
    260         case Decimal():
    261             return not value.is_zero()
    262         case str():
    263             return ErrorCode.VALUE
    264 
    265 
    266 ### vocabulary #########################################################################
    267 
>>  268 # a cell value after the error checks. None is an empty cell
    269 _Operand = Decimal | str | bool | None
```

### 51. formula_parser.py:41

```python
     33     OperatorStep,
     34     SignedOperand,
     35     TextLiteral,
     36     TextOperator,
     37     UnaryOperator,
     38 )
     39 
     40 
>>   41 # Each level of nesting costs up to 8 Python frames while parsing, and Python's default recursion
>>   42 # limit is 1000. A formula nested deeper does not parse.
     43 _MAX_NESTING = 64
     44 
     45 # the binary operators by precedence level, loosest first
     46 _LEVELS: tuple[Mapping[str, BinaryOperator], ...] = (
     47     {operator.value: operator for operator in ComparisonOperator},
     48     {operator.value: operator for operator in TextOperator},
     49     {'+': ArithmeticOperator.ADD, '-': ArithmeticOperator.SUBTRACT},
     50     {'*': ArithmeticOperator.MULTIPLY, '/': ArithmeticOperator.DIVIDE},
     51 )
     52 _FUNCTIONS_BY_NAME = {function.value: function for function in Function}
```

### 52. formula_parser.py:45

```python
     37     UnaryOperator,
     38 )
     39 
     40 
     41 # Each level of nesting costs up to 8 Python frames while parsing, and Python's default recursion
     42 # limit is 1000. A formula nested deeper does not parse.
     43 _MAX_NESTING = 64
     44 
>>   45 # the binary operators by precedence level, loosest first
     46 _LEVELS: tuple[Mapping[str, BinaryOperator], ...] = (
     47     {operator.value: operator for operator in ComparisonOperator},
     48     {operator.value: operator for operator in TextOperator},
     49     {'+': ArithmeticOperator.ADD, '-': ArithmeticOperator.SUBTRACT},
     50     {'*': ArithmeticOperator.MULTIPLY, '/': ArithmeticOperator.DIVIDE},
     51 )
     52 _FUNCTIONS_BY_NAME = {function.value: function for function in Function}
     53 
     54 _LOG = logging.getLogger(__name__)
     55 
```

### 53. formula_parser.py:68

```python
     60         expression = parser.parseWhole()
     61     except _FormulaSyntaxError:
     62         return Formula(expression=ErrorLiteral(ErrorCode.NAME), dependencies=frozenset())
     63 
     64     return Formula(expression=expression, dependencies=frozenset(parser.dependencies))
     65 
     66 
     67 def _tokenize(formula_text: str) -> list[_Token]:
>>   68     # one token after any spaces: a number, a string, a word, an operator or the end of the text
     69     TOKEN = re.compile(
     70         r' *(?:(?P<NUMBER>[0-9]+(?:\.[0-9]+)?)|(?P<TEXT>"(?:[^"]|"")*")|(?P<WORD>[A-Za-z]+[0-9]*)'
     71         r'|(?P<SYMBOL><>|<=|>=|[-+*/^&=<>(),:])|(?P<END>\Z))',
     72     )
     73     tokens: list[_Token] = []
     74     # skip the leading =
     75     position = 1
     76     while not tokens or tokens[-1].kind is not _TokenKind.END:
     77         token_match = TOKEN.match(formula_text, position)
     78         if token_match is None:
```

### 54. formula_parser.py:74

```python
     66 
     67 def _tokenize(formula_text: str) -> list[_Token]:
     68     # one token after any spaces: a number, a string, a word, an operator or the end of the text
     69     TOKEN = re.compile(
     70         r' *(?:(?P<NUMBER>[0-9]+(?:\.[0-9]+)?)|(?P<TEXT>"(?:[^"]|"")*")|(?P<WORD>[A-Za-z]+[0-9]*)'
     71         r'|(?P<SYMBOL><>|<=|>=|[-+*/^&=<>(),:])|(?P<END>\Z))',
     72     )
     73     tokens: list[_Token] = []
>>   74     # skip the leading =
     75     position = 1
     76     while not tokens or tokens[-1].kind is not _TokenKind.END:
     77         token_match = TOKEN.match(formula_text, position)
     78         if token_match is None:
     79             raise _rejectFormula(formula_text, position, 'a number, a string, a name or an operator')
     80         kind = next(kind for kind in _TokenKind if token_match[kind.name] is not None)
     81         tokens.append(_Token(kind=kind, text=token_match[kind.name], position=token_match.start(kind.name)))
     82         position = token_match.end()
     83 
     84     return tokens
```

### 55. grid.py:18

```python
     10 from __future__ import annotations
     11 
     12 import re
     13 
     14 from spreadsheet.vocabulary import CellAddress
     15 
     16 
     17 def parseCellName(cell_name: str) -> CellAddress | None:
>>   18     # matches:
>>   19     # `A1`
>>   20     # `Z99`
>>   21     # rejects:
>>   22     # `A01`
>>   23     # `A100`
     24     CELL_NAME = re.compile(r'([A-Z])([1-9][0-9]?)')
     25     name_match = CELL_NAME.fullmatch(cell_name)
     26     if name_match is None:
     27         return None
     28 
     29     return CellAddress(column=ord(name_match[1]) - ord('A') + 1, row=int(name_match[2]))
     30 
     31 
     32 def formatCellName(address: CellAddress) -> str:
     33     return chr(ord('A') + address.column - 1) + str(address.row)
```

### 56. vocabulary.py:140

```python
    132 @dataclass(frozen=True)
    133 class Formula:
    134     """A parsed formula, with every cell named by its references or covered by its ranges."""
    135 
    136     expression: Expression
    137     dependencies: frozenset[CellAddress]
    138 
    139 
>>  140 # a cell of the input: a number, a text value or a formula
    141 CellContent = Decimal | str | Formula
    142 CellValue = Decimal | str | bool | ErrorCode
    143 
    144 
    145 @dataclass(frozen=True)
    146 class EvaluationOrder:
    147     """Formula cells in an order where each follows every formula cell it depends on.
    148 
    149     cyclic is the cells on a cycle of dependencies, and the cells that depend on one. They are not in ordered.
    150     """
```

### 57. vocabulary.py:156

```python
    148 
    149     cyclic is the cells on a cycle of dependencies, and the cells that depend on one. They are not in ordered.
    150     """
    151 
    152     ordered: tuple[CellAddress, ...]
    153     cyclic: frozenset[CellAddress]
    154 
    155 
>>  156 # one result cell, such as {'number': '0.3'} or {'boolean': True}
    157 RenderedValue = dict[str, str | bool]
```

## P16 GPX statistics (package gpxstats): 8 comments

`scratchpad/cycle15/p16/gpxstats`

### 58. gpx.py:25

```python
     17 from pathlib import Path
     18 from xml.etree import ElementTree
     19 
     20 from gpxstats.vocabulary import ProblemKind, RejectedTrackError, Segment, TrackPoint
     21 
     22 
     23 LOG = logging.getLogger(__name__)
     24 GPX_NAMESPACE = 'http://www.topografix.com/GPX/1/1'
>>   25 # the GPX schema types `lat`, `lon` and `ele` as xsd:decimal. xsd:decimal has no exponent
>>   26 # matches:
>>   27 # `59.92`
>>   28 # `-0.5`
>>   29 # `.5`
>>   30 # rejects:
>>   31 # `1e3`
>>   32 # `nan`
     33 DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)')
     34 # matches:
     35 # `2026-06-14T22:40:00Z`
     36 # rejects:
     37 # `2026-06-14T22:40:00.5Z`
     38 # `2026-06-14T22:40:00+00:00`
     39 TIMESTAMP = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
     40 TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
     41 
     42 
```

### 59. gpx.py:34

```python
     26 # matches:
     27 # `59.92`
     28 # `-0.5`
     29 # `.5`
     30 # rejects:
     31 # `1e3`
     32 # `nan`
     33 DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)')
>>   34 # matches:
>>   35 # `2026-06-14T22:40:00Z`
>>   36 # rejects:
>>   37 # `2026-06-14T22:40:00.5Z`
>>   38 # `2026-06-14T22:40:00+00:00`
     39 TIMESTAMP = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
     40 TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
     41 
     42 
     43 def readTrack(gpx_path: Path) -> tuple[Segment, ...]:
     44     """Parse the file at `gpx_path` into its segments, every point validated.
     45 
     46     Raises:
     47         RejectedTrackError: the file is unreadable, is not GPX 1.1, or is malformed.
     48     """
```

### 60. gpx.py:123

```python
    115     return coordinate
    116 
    117 
    118 def _parseTimestamp(gpx_path: Path, raw_at: str) -> datetime:
    119     expected = 'expected "2026-06-14T22:40:00Z"'
    120 
    121     if not TIMESTAMP.fullmatch(raw_at):
    122         raise _rejectTrack(gpx_path, ProblemKind.MALFORMED, f'time {raw_at!r} ({expected})')
>>  123     # TIMESTAMP matches impossible dates such as `2026-02-30`. strptime() rejects them
    124     try:
    125         naive_at = datetime.strptime(raw_at, TIMESTAMP_FORMAT)
    126     except ValueError as exc:
    127         raise _rejectTrack(
    128             gpx_path,
    129             ProblemKind.MALFORMED,
    130             f'time {raw_at!r} is not a real instant ({expected})',
    131         ) from exc
    132     return naive_at.replace(tzinfo=UTC)
    133 
```

### 61. report.py:12

```python
      4 
      5 import json
      6 from datetime import UTC, datetime
      7 
      8 from gpxstats.vocabulary import Activity, Scan
      9 
     10 
     11 def renderReport(scan: Scan, raw_input_dir: str) -> str:
>>   12     # key order is part of the activities.json format
     13     report = {
     14         'generated_at': datetime.now(UTC).isoformat(timespec='seconds'),
     15         'input_dir': raw_input_dir,
     16         'timezone': scan.settings.timezone.key,
     17         'activities': [_serializeActivity(activity) for activity in scan.activities],
     18         'problems': [{'file': problem.file, 'problem': problem.kind.value} for problem in scan.problems],
     19         'totals': {
     20             'activities': scan.totals.activities,
     21             'distance_m': scan.totals.distance_m,
     22             'moving_s': scan.totals.moving_s,
```

### 62. stats.py:96

```python
     88     start_latitude = math.radians(start.latitude)
     89     end_latitude = math.radians(end.latitude)
     90     latitude_change = end_latitude - start_latitude
     91     longitude_change = math.radians(end.longitude - start.longitude)
     92     a = (
     93         math.sin(latitude_change / 2) ** 2
     94         + math.cos(start_latitude) * math.cos(end_latitude) * math.sin(longitude_change / 2) ** 2
     95     )
>>   96     # float rounding can push `a` just above 1 for antipodal points. asin() raises above 1
     97     return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(min(a, 1.0)))
     98 
     99 
    100 def _computeElevationGain(elevations_m: Iterable[float]) -> float:
    101     # Gain starts once the elevation rises ELEVATION_HYSTERESIS_M above the lowest point since the
    102     # last climb. A climb ends at a fall of ELEVATION_HYSTERESIS_M below its highest point.
    103     remaining = iter(elevations_m)
    104     reference_m = next(remaining, None)
    105     if reference_m is None:
    106         return 0.0
```

### 63. stats.py:101

```python
     93         math.sin(latitude_change / 2) ** 2
     94         + math.cos(start_latitude) * math.cos(end_latitude) * math.sin(longitude_change / 2) ** 2
     95     )
     96     # float rounding can push `a` just above 1 for antipodal points. asin() raises above 1
     97     return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(min(a, 1.0)))
     98 
     99 
    100 def _computeElevationGain(elevations_m: Iterable[float]) -> float:
>>  101     # Gain starts once the elevation rises ELEVATION_HYSTERESIS_M above the lowest point since the
>>  102     # last climb. A climb ends at a fall of ELEVATION_HYSTERESIS_M below its highest point.
    103     remaining = iter(elevations_m)
    104     reference_m = next(remaining, None)
    105     if reference_m is None:
    106         return 0.0
    107 
    108     gain_m = 0.0
    109     climbing = False
    110     for elevation_m in remaining:
    111         if elevation_m > reference_m and (climbing or elevation_m - reference_m >= ELEVATION_HYSTERESIS_M):
    112             gain_m += elevation_m - reference_m
```

### 64. store.py:66

```python
     58         ' fastest_km = excluded.fastest_km,'
     59         ' fastest_km_s = excluded.fastest_km_s,'
     60         ' points_used = excluded.points_used,'
     61         ' points_dropped = excluded.points_dropped'
     62     )
     63     COUNT_ROWS = 'SELECT count(*) FROM activities'
     64 
     65     rows = [_ActivityRow.fromActivity(activity) for activity in activities]
>>   66     # for activities that share a start_utc, the table ends with the last one's row
     67     start_counts = Counter(row.start_utc for row in rows)
     68     shared_starts = sorted(start_utc for start_utc, count in start_counts.items() if count > 1)
     69     if shared_starts:
     70         LOG.warning('store.shared_start', extra={'start_utc': ','.join(shared_starts)})
     71 
     72     with closing(sqlite3.connect(database_path)) as connection, connection:
     73         connection.execute(CREATE_TABLE)
     74         rows_before = int(connection.execute(COUNT_ROWS).fetchone()[0])
     75         connection.executemany(UPSERT, rows)
     76         rows_after = int(connection.execute(COUNT_ROWS).fetchone()[0])
```

### 65. store.py:83

```python
     75         connection.executemany(UPSERT, rows)
     76         rows_after = int(connection.execute(COUNT_ROWS).fetchone()[0])
     77     return rows_after - rows_before
     78 
     79 
     80 ### vocabulary #########################################################################
     81 
     82 
>>   83 # sqlite3.Cursor.executemany() rejects dataclass rows. A NamedTuple is used instead
     84 class _ActivityRow(NamedTuple):
     85     start_utc: str
     86     file: str
     87     start_local_date: str
     88     distance_m: float
     89     elapsed_s: int
     90     moving_s: int
     91     stopped_s: int
     92     elevation_gain_m: float
     93     fastest_km: int | None
```

## P17 migration runner (package migration_runner): 7 comments

`scratchpad/cycle15/p17/migration_runner`

### 66. directory.py:26

```python
     18     """Read every migration file in the directory.
     19 
     20     Returns:
     21         The files sorted by name, so by number.
     22 
     23     Raises:
     24         StartupError: the directory does not exist, or a migration file is not UTF-8.
     25     """
>>   26     # matches:
>>   27     # `0003_settings.sql`
>>   28     # rejects:
>>   29     # `3_settings.sql`
>>   30     # `0003-settings.sql`
     31     MIGRATION_NAME = re.compile(r'([0-9]{4})_[A-Za-z0-9_]+\.sql')
     32     NO_TRANSACTION_MARKER = b'-- no-transaction'
     33 
     34     if not migrations_dir.is_dir():
     35         raise rejectStart(f'migrations directory {migrations_dir} does not exist or is not a directory')
     36 
     37     migrations = []
     38     for file_path in sorted(migrations_dir.iterdir()):
     39         name_match = MIGRATION_NAME.fullmatch(file_path.name)
     40         if not (name_match and file_path.is_file()):
```

### 67. directory.py:43

```python
     35         raise rejectStart(f'migrations directory {migrations_dir} does not exist or is not a directory')
     36 
     37     migrations = []
     38     for file_path in sorted(migrations_dir.iterdir()):
     39         name_match = MIGRATION_NAME.fullmatch(file_path.name)
     40         if not (name_match and file_path.is_file()):
     41             continue
     42 
>>   43         # the checksum is of the stored bytes. read_text() would turn CRLF into LF
     44         sql_bytes = file_path.read_bytes()
     45         try:
     46             sql_text = sql_bytes.decode('utf-8')
     47         except UnicodeDecodeError as exc:
     48             raise rejectStart(f'migration file {file_path} is not UTF-8: {exc}') from exc
     49         first_line = sql_bytes.partition(b'\n')[0].removesuffix(b'\r')
     50         migrations.append(
     51             MigrationFile(
     52                 version=Version(name_match.group(1)),
     53                 name=file_path.name,
```

### 68. failures.py:15

```python
      7 
      8 from migration_runner.vocabulary import MigrationFailedError, MigrationFile, StartupError
      9 
     10 
     11 LOG = logging.getLogger(__name__)
     12 
     13 
     14 def rejectStart(message: str) -> StartupError:
>>   15     # with stacklevel=2, the record's module and lineno are the caller's
     16     LOG.info('run.unstartable', extra={'reason': message}, stacklevel=2)
     17     return StartupError(message)
     18 
     19 
     20 def rejectMigration(migration: MigrationFile, exc: sqlite3.Error) -> MigrationFailedError:
     21     LOG.info('migration.failed', extra={'migration': migration.name, 'error': str(exc)}, stacklevel=2)
     22     return MigrationFailedError(str(exc))
```

### 69. store.py:24

```python
     16 @contextmanager
     17 def openMigrationStore(database_path: Path) -> Iterator[MigrationStore]:
     18     """Open the database, and create the file when it does not exist.
     19 
     20     Raises:
     21         StartupError: SQLite cannot open the file.
     22     """
     23     try:
>>   24         # isolation_level=None turns off the implicit BEGIN of sqlite3. applyMigration() issues BEGIN and COMMIT itself
     25         connection = sqlite3.connect(database_path, isolation_level=None)
     26     except sqlite3.Error as exc:
     27         raise rejectStart(f'cannot open database {database_path}: {exc}') from exc
     28     try:
     29         yield MigrationStore(connection, database_path)
     30     finally:
     31         connection.close()
     32 
     33 
     34 ### vocabulary #########################################################################
```

### 70. store.py:97

```python
     89                     migration.name,
     90                     migration.checksum,
     91                     datetime.now(UTC).isoformat(timespec='seconds'),
     92                 ),
     93             )
     94             if transactional:
     95                 self.connection.execute('COMMIT')
     96         except sqlite3.Error as exc:
>>   97             # SQLite DDL is transactional. ROLLBACK drops a table the migration created too.
>>   98             # A no-transaction migration has no open transaction here.
     99             if self.connection.in_transaction:
    100                 self.connection.execute('ROLLBACK')
    101             raise rejectMigration(migration, exc) from exc
```

### 71. vocabulary.py:10

```python
      2 
      3 from __future__ import annotations
      4 
      5 from dataclasses import dataclass
      6 from enum import Enum
      7 from typing import NewType, TypedDict
      8 
      9 
>>   10 # the four digits of a migration file name, such as '0003'
     11 Version = NewType('Version', str)
     12 
     13 
     14 class State(Enum):
     15     APPLIED = 'applied'
     16     PENDING = 'pending'
     17     CHECKSUM_CHANGED = 'checksum changed'
     18     OUT_OF_ORDER = 'out of order'
     19     DUPLICATE_NUMBER = 'duplicate number'
     20     FILE_MISSING = 'file missing'
```

### 72. vocabulary.py:64

```python
     56 
     57 
     58 class MigrationRow(TypedDict):
     59     version: str
     60     name: str
     61     state: str
     62 
     63 
>>   64 # The specification requires a dict from each command function.
>>   65 # The key order of each class is the key order of the printed report.
     66 class UpReport(TypedDict):
     67     command: str
     68     database: str
     69     target: str | None
     70     applied: list[str]
     71     failed: Failure | None
     72     pending: list[str]
     73     problems: list[Problem]
     74 
     75 
```

## P18 contact merge (package contact_merge): 7 comments

`scratchpad/cycle15/p18/contact_merge`

### 73. exports.py:44

```python
     36     try:
     37         export_text = export_bytes.decode(source.encoding)
     38     except UnicodeDecodeError as exc:
     39         raise _rejectExport(
     40             export_path,
     41             f'does not decode as {source.encoding}: {exc.reason} at byte {exc.start}',
     42         ) from exc
     43 
>>   44     # csv.reader() needs newline='' to read a line break inside a quoted field as written
     45     reader = csv.reader(io.StringIO(export_text, newline=''), delimiter=source.delimiter)
     46     try:
     47         rows = [row for row in reader if row]
     48     except csv.Error as exc:
     49         raise _rejectExport(export_path, f'not CSV at line {reader.line_num}: {exc}') from exc
     50     header = rows[0] if rows else []
     51     named_columns = [*source.name_columns, source.email_column, source.phone_column, source.company_column]
     52     missing = [column for column in named_columns if column is not None and column not in header]
     53     if missing:
     54         raise _rejectExport(export_path, f'header {header} lacks the columns {missing}')
```

### 74. fields.py:25

```python
     17 import re
     18 import unicodedata
     19 
     20 from contact_merge.vocabulary import Email, NameKey, Phone
     21 
     22 
     23 _MIN_PHONE_DIGITS = 8
     24 _MAX_PHONE_DIGITS = 15
>>   25 # an extension at the end. Group 1 is the number before it
>>   26 # matches:
>>   27 # `020 7946 0321 x214`
>>   28 # `0113 496 0555 ext. 12`
>>   29 # `+44 20 7946 0321 #7`
     30 _EXTENSION = re.compile(r'(.*?)\s*(?:ext\.?|x|#)\s*\d+', re.IGNORECASE)
     31 _PHONE_PUNCTUATION = str.maketrans('', '', ' -.()')
     32 
     33 
     34 def joinNameParts(raw_name_parts: tuple[str, ...]) -> str:
     35     return ' '.join(part.strip() for part in raw_name_parts if part.strip())
     36 
     37 
     38 def normaliseShownText(text: str) -> str:
     39     return ' '.join(unicodedata.normalize('NFC', text).split())
```

### 75. fields.py:73

```python
     65         digits = dialled[1:]
     66     elif dialled.startswith('00'):
     67         digits = dialled[2:]
     68     elif dialled.startswith('0'):
     69         digits = default_country_code + dialled[1:]
     70     else:
     71         return None
     72 
>>   73     # isdigit() admits non-ASCII digits such as '²'. Check isascii() too
     74     valid = (
     75         digits.isascii()
     76         and digits.isdigit()
     77         and _MIN_PHONE_DIGITS <= len(digits) <= _MAX_PHONE_DIGITS
     78         and not digits.startswith('0')
     79     )
     80     return Phone(f'+{digits}') if valid else None
```

### 76. grouping.py:36

```python
     28     groups: dict[int, list[Record]] = {}
     29     for index, record in enumerate(records):
     30         groups.setdefault(_findRoot(parents, index), []).append(record)
     31     return [_buildContact(ContactId(f'C{number}'), members) for number, members in enumerate(groups.values(), 1)]
     32 
     33 
     34 def _findRoot(parents: list[int], index: int) -> int:
     35     while parents[index] != index:
>>   36         # path halving. Each visited index is pointed at its grandparent
     37         parents[index] = parents[parents[index]]
     38         index = parents[index]
     39     return index
     40 
     41 
     42 def _joinGroups(parents: list[int], first: int, second: int) -> None:
     43     parents[_findRoot(parents, second)] = _findRoot(parents, first)
     44 
     45 
     46 def _buildContact(contact_id: ContactId, members: list[Record]) -> Contact:
```

### 77. rules_file.py:29

```python
     21 from pathlib import Path
     22 
     23 from contact_merge.vocabulary import Rules, SourceSpec, UnusableInputError
     24 
     25 
     26 _TOP_LEVEL_KEYS = frozenset({'default_country_code', 'sources'})
     27 _REQUIRED_SOURCE_KEYS = frozenset({'file', 'encoding', 'delimiter', 'name'})
     28 _OPTIONAL_SOURCE_KEYS = frozenset({'email', 'phone', 'company'})
>>   29 # csv.reader() raises on these as a delimiter
     30 _UNUSABLE_DELIMITERS = frozenset({'"', '\r', '\n'})
     31 # matches:
     32 # `44`
     33 # `1`
     34 # rejects:
     35 # `+44`
     36 _COUNTRY_CODE = re.compile(r'[0-9]{1,3}')
     37 
     38 _LOG = logging.getLogger(__name__)
     39 
```

### 78. rules_file.py:31

```python
     23 from contact_merge.vocabulary import Rules, SourceSpec, UnusableInputError
     24 
     25 
     26 _TOP_LEVEL_KEYS = frozenset({'default_country_code', 'sources'})
     27 _REQUIRED_SOURCE_KEYS = frozenset({'file', 'encoding', 'delimiter', 'name'})
     28 _OPTIONAL_SOURCE_KEYS = frozenset({'email', 'phone', 'company'})
     29 # csv.reader() raises on these as a delimiter
     30 _UNUSABLE_DELIMITERS = frozenset({'"', '\r', '\n'})
>>   31 # matches:
>>   32 # `44`
>>   33 # `1`
>>   34 # rejects:
>>   35 # `+44`
     36 _COUNTRY_CODE = re.compile(r'[0-9]{1,3}')
     37 
     38 _LOG = logging.getLogger(__name__)
     39 
     40 
     41 def readRules(rules_path: Path) -> Rules:
     42     """Read and check the whole rules file. The first problem stops the read.
     43 
     44     Raises:
     45         UnusableInputError: the file is missing, unreadable, not JSON, or not in the form above.
```

### 79. rules_file.py:128

```python
    120         name_columns=tuple(name_columns),
    121         email_column=optional_columns['email'],
    122         phone_column=optional_columns['phone'],
    123         company_column=optional_columns['company'],
    124     )
    125 
    126 
    127 def _textCodec(encoding: str) -> bool:
>>  128     # b''.decode() would return '' without looking the codec up. codecs.lookup() would accept a
>>  129     # bytes-to-bytes codec such as 'base64'. TextIOWrapper() rejects both an unknown and a bytes-to-bytes codec.
    130     try:
    131         io.TextIOWrapper(io.BytesIO(), encoding=encoding)
    132     except LookupError:
    133         return False
    134     return True
    135 
    136 
    137 def _rejectRules(rules_path: Path, problem: str) -> UnusableInputError:
    138     _LOG.debug('rules.rejected', extra={'rules_path': str(rules_path), 'problem': problem})
    139     return UnusableInputError(f'{rules_path}: {problem}')
```

## P19 semver resolver (package semver_resolver): 10 comments

`scratchpad/cycle15/p19/semver_resolver`

### 80. ranges.py:39

```python
     31 
     32 def maxSatisfying(raw_versions: Iterable[str], raw_range: str) -> str | None:
     33     version_range = parseRange(raw_range)
     34     parsed = [(raw_version, versions.parseVersion(raw_version)) for raw_version in raw_versions]
     35     satisfying = [(raw_version, version) for raw_version, version in parsed if withinRange(version, version_range)]
     36     if not satisfying:
     37         return None
     38     precedence_key = functools.cmp_to_key(versions.comparePrecedence)
>>   39     # max() returns the first of several maximal items. sorted()[-1] would return the last
     40     highest_raw_version, _ = max(satisfying, key=lambda pair: precedence_key(pair[1]))
     41     return highest_raw_version
     42 
     43 
     44 def parseRange(raw_range: str) -> VersionRange:
     45     range_text = raw_range.strip()
     46     if not range_text:
     47         return VersionRange(comparator_sets=(ComparatorSet(comparators=()),))
     48     return VersionRange(tuple(_parseComparatorSet(set_text, raw_range) for set_text in range_text.split('||')))
     49 
```

### 81. ranges.py:156

```python
    148 
    149 
    150 def _lowestVersion(partial: PartialVersion) -> Version:
    151     major, minor, patch = (*partial.numbers, 0, 0, 0)[:3]
    152     return Version(major=major, minor=minor, patch=patch, prerelease=partial.prerelease, build=())
    153 
    154 
    155 def _nextVersion(partial: PartialVersion, position: int) -> Version:
>>  156     # next(minor) of 1.2 is 1.3.0-0. A -0 prerelease precedes every other version of 1.3.0
    157     kept = partial.numbers[:position]
    158     major, minor, patch = (*kept, partial.numbers[position] + 1, 0, 0)[:3]
    159     return Version(major=major, minor=minor, patch=patch, prerelease=(0,), build=())
    160 
    161 
    162 def _withinSet(version: Version, comparator_set: ComparatorSet) -> bool:
    163     if not all(_withinComparator(version, comparator) for comparator in comparator_set.comparators):
    164         return False
    165     if not version.prerelease:
    166         return True
```

### 82. resolver.py:54

```python
     46     registry: dict[PackageName, tuple[_Release, ...]] = {}
     47     for raw_name, raw_releases in raw_registry.items():
     48         if not isinstance(raw_releases, Mapping):
     49             raise _rejectRegistry(raw_name)
     50         releases = [
     51             _parseRelease(raw_name, raw_version, raw_dependencies)
     52             for raw_version, raw_dependencies in raw_releases.items()
     53         ]
>>   54         # sorted() is stable with reverse=True, so versions of equal precedence stay in registry order
     55         registry[PackageName(raw_name)] = tuple(
     56             sorted(releases, key=lambda release: precedence_key(release.version), reverse=True),
     57         )
     58     return registry
     59 
     60 
     61 def _parseRelease(raw_name: str, raw_version: object, raw_dependencies: object) -> _Release:
     62     if not (isinstance(raw_version, str) and isinstance(raw_dependencies, Mapping)):
     63         raise _rejectRegistry(raw_name)
     64 
```

### 83. versions.py:21

```python
     13 from __future__ import annotations
     14 
     15 import logging
     16 import re
     17 
     18 from semver_resolver.vocabulary import PartialVersion, Version
     19 
     20 
>>   21 # number without a leading zero
     22 _NUMBER = r'(?:0|[1-9][0-9]*)'
     23 # numeric without a leading zero, or alphanumeric with at least one letter or hyphen
     24 _PRERELEASE_IDENTIFIER = rf'(?:{_NUMBER}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
     25 _PRERELEASE = rf'{_PRERELEASE_IDENTIFIER}(?:\.{_PRERELEASE_IDENTIFIER})*'
     26 _BUILD = r'[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*'
     27 _SUFFIXES = rf'(?:-(?P<prerelease>{_PRERELEASE}))?(?:\+(?P<build>{_BUILD}))?'
     28 _WILDCARDS = frozenset({'x', 'X', '*'})
     29 
     30 LOG = logging.getLogger(__name__)
     31 
```

### 84. versions.py:23

```python
     15 import logging
     16 import re
     17 
     18 from semver_resolver.vocabulary import PartialVersion, Version
     19 
     20 
     21 # number without a leading zero
     22 _NUMBER = r'(?:0|[1-9][0-9]*)'
>>   23 # numeric without a leading zero, or alphanumeric with at least one letter or hyphen
     24 _PRERELEASE_IDENTIFIER = rf'(?:{_NUMBER}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
     25 _PRERELEASE = rf'{_PRERELEASE_IDENTIFIER}(?:\.{_PRERELEASE_IDENTIFIER})*'
     26 _BUILD = r'[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*'
     27 _SUFFIXES = rf'(?:-(?P<prerelease>{_PRERELEASE}))?(?:\+(?P<build>{_BUILD}))?'
     28 _WILDCARDS = frozenset({'x', 'X', '*'})
     29 
     30 LOG = logging.getLogger(__name__)
     31 
     32 
     33 def compareVersions(raw_left: str, raw_right: str) -> int:
```

### 85. versions.py:38

```python
     30 LOG = logging.getLogger(__name__)
     31 
     32 
     33 def compareVersions(raw_left: str, raw_right: str) -> int:
     34     return comparePrecedence(parseVersion(raw_left), parseVersion(raw_right))
     35 
     36 
     37 def parseVersion(raw_version: str) -> Version:
>>   38     # matches:
>>   39     # `1.0.0-rc.1+build.007`
>>   40     # `0.0.0`
>>   41     # rejects:
>>   42     # `01.2.3`
>>   43     # `1.2.3-alpha.01`
     44     match = re.fullmatch(rf'(?P<major>{_NUMBER})\.(?P<minor>{_NUMBER})\.(?P<patch>{_NUMBER}){_SUFFIXES}', raw_version)
     45     if match is None:
     46         raise _rejectVersionText(raw_version, 'MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD], such as "1.2.3-beta.1+build.5"')
     47 
     48     return Version(
     49         major=int(match['major']),
     50         minor=int(match['minor']),
     51         patch=int(match['patch']),
     52         prerelease=_parsePrerelease(match['prerelease']),
     53         build=tuple(match['build'].split('.')) if match['build'] else (),
```

### 86. versions.py:65

```python
     57 def parsePartialVersion(raw_partial: str) -> PartialVersion:
     58     """Parse the version of a range item, in which a wildcard may replace a part.
     59 
     60     Raises:
     61         ValueError: `raw_partial` is not one to three numbers or wildcards, has a number after a
     62             wildcard, or has a prerelease or build after fewer than three numbers.
     63     """
     64     PART = rf'(?:{_NUMBER}|[xX*])'
>>   65     # matches:
>>   66     # `1`
>>   67     # `1.x`
>>   68     # `1.2.3-beta+build.5`
>>   69     # rejects:
>>   70     # `1.2.3.4`
>>   71     # `^1.2`
     72     match = re.fullmatch(rf'(?P<major>{PART})(?:\.(?P<minor>{PART})(?:\.(?P<patch>{PART}){_SUFFIXES})?)?', raw_partial)
     73     if match is None:
     74         raise _rejectVersionText(
     75             raw_partial,
     76             'one to three parts, each a number or x, X or *, such as "1.2", "1.x" or "1.2.3-beta"',
     77         )
     78 
     79     present_parts = [part for part in (match['major'], match['minor'], match['patch']) if part is not None]
     80     numbers: list[int] = []
     81     for part in present_parts:
```

### 87. versions.py:101

```python
     93 def comparePrecedence(left: Version, right: Version) -> int:
     94     left_release = (left.major, left.minor, left.patch)
     95     right_release = (right.major, right.minor, right.patch)
     96     if left_release != right_release:
     97         return -1 if left_release < right_release else 1
     98 
     99     if left.prerelease == right.prerelease:
    100         return 0
>>  101     # a version without a prerelease has higher precedence than every prerelease of it
    102     if not left.prerelease:
    103         return 1
    104     if not right.prerelease:
    105         return -1
    106 
    107     for left_identifier, right_identifier in zip(left.prerelease, right.prerelease, strict=False):
    108         order = _compareIdentifiers(left_identifier, right_identifier)
    109         if order != 0:
    110             return order
    111     return -1 if len(left.prerelease) < len(right.prerelease) else 1
```

### 88. versions.py:121

```python
    113 
    114 def _compareIdentifiers(left: int | str, right: int | str) -> int:
    115     if left == right:
    116         return 0
    117     if isinstance(left, int) and isinstance(right, int):
    118         return -1 if left < right else 1
    119     if isinstance(left, str) and isinstance(right, str):
    120         return -1 if left < right else 1
>>  121     # a numeric identifier is lower than an alphanumeric one
    122     return -1 if isinstance(left, int) else 1
    123 
    124 
    125 def _parsePrerelease(raw_prerelease: str | None) -> tuple[int | str, ...]:
    126     if not raw_prerelease:
    127         return ()
    128     return tuple(int(identifier) if identifier.isdigit() else identifier for identifier in raw_prerelease.split('.'))
    129 
    130 
    131 def _rejectVersionText(raw_text: str, expected: str) -> ValueError:
```

### 89. vocabulary.py:18

```python
     10 PackageName = NewType('PackageName', str)
     11 
     12 
     13 @dataclass(frozen=True)
     14 class Version:
     15     major: int
     16     minor: int
     17     patch: int
>>   18     # a digits-only identifier is numeric and parsed to int
     19     prerelease: tuple[int | str, ...]
     20     build: tuple[str, ...]
     21 
     22 
     23 @dataclass(frozen=True)
     24 class PartialVersion:
     25     """A version in a range, such as `1.2`, `1.x` or `*`.
     26 
     27     `numbers` has the parts before the first wildcard. A missing part counts as a wildcard, so `1`,
     28     `1.x` and `1.*.*` all parse to `numbers=(1,)`. Only a partial version with three numbers has a
```

## P20 change request (comments added to snapshot_pruner): 4 comments

`scratchpad/cycle15/p20/fixture/snapshot_pruner`

### 90. __main__.py:140

```python
    132 
    133     if not (isinstance(now, DateTime) and now.tzinfo is not None):
    134         detail = f'{raw_now!r} is not an ISO 8601 instant with a UTC offset (expected e.g. "2028-11-05T08:00:00Z")'
    135         raise argparse.ArgumentTypeError(detail)
    136     return now
    137 
    138 
    139 def parseDeletionLimit(raw_max_delete: str) -> int:
>>  140     # isdigit() admits non-ASCII digits such as '²'. Check isascii() too
    141     if not (raw_max_delete.isascii() and raw_max_delete.isdigit()):
    142         detail = f'{raw_max_delete!r} is not a non-negative integer (expected e.g. "100")'
    143         raise argparse.ArgumentTypeError(detail)
    144     return int(raw_max_delete)
    145 
    146 
    147 ### vocabulary #########################################################################
    148 
    149 _STANDARD = frozenset(logging.LogRecord('', 0, '', 0, '', None, None).__dict__) | {'message', 'asctime'}
    150 _LOCATION = ('module', 'lineno', 'funcName')
```

### 91. history.py:99

```python
     91         'CREATE TABLE IF NOT EXISTS decisions ('
     92         ' run_id INTEGER NOT NULL REFERENCES runs (run_id),'
     93         ' file TEXT NOT NULL,'
     94         " decision TEXT NOT NULL CHECK (decision IN ('keep', 'delete', 'unparseable', 'future', 'bad-pin')),"
     95         ' local TEXT,'
     96         ' rules TEXT,'
     97         ' PRIMARY KEY (run_id, file));'
     98     )
>>   99     # SQLite cannot alter a UNIQUE or CHECK constraint. Copy both tables into the current schema
    100     MIGRATION = (
    101         'BEGIN;'
    102         'ALTER TABLE runs RENAME TO runs_before_yearly;'
    103         'ALTER TABLE decisions RENAME TO decisions_before_pins;'
    104         f'{SCHEMA}'
    105         'INSERT INTO runs'
    106         ' SELECT run_id, now, snapshot_dir, timezone, keep_hourly, keep_daily, keep_weekly, keep_monthly, 0'
    107         ' FROM runs_before_yearly;'
    108         'INSERT INTO decisions SELECT run_id, file, decision, local, rules FROM decisions_before_pins;'
    109         'DROP TABLE decisions_before_pins;'
```

### 92. pins.py:30

```python
     22 
     23 def readPins(snapshot_dir: Path) -> frozenset[str]:
     24     """Read the pins.txt in `snapshot_dir` and return its pins.
     25 
     26     Raises:
     27         PinsError: pins.txt is present but cannot be read, or is not UTF-8.
     28     """
     29     pins_path = snapshot_dir / _PINS_FILE_NAME
>>   30     # exists() is False for a dangling symbolic link. Such a pins.txt is unreadable, not absent
     31     if not (pins_path.exists() or pins_path.is_symlink()):
     32         return frozenset()
     33 
     34     try:
     35         # utf-8-sig removes a leading byte order mark, and accepts a file without one
     36         pins_text = pins_path.read_text(encoding='utf-8-sig')
     37     except OSError as exc:
     38         raise _rejectPins(pins_path, f'unreadable: {exc.strerror}') from exc
     39     except UnicodeDecodeError as exc:
     40         raise _rejectPins(pins_path, f'not UTF-8: {exc.reason}') from exc
```

### 93. pins.py:35

```python
     27         PinsError: pins.txt is present but cannot be read, or is not UTF-8.
     28     """
     29     pins_path = snapshot_dir / _PINS_FILE_NAME
     30     # exists() is False for a dangling symbolic link. Such a pins.txt is unreadable, not absent
     31     if not (pins_path.exists() or pins_path.is_symlink()):
     32         return frozenset()
     33 
     34     try:
>>   35         # utf-8-sig removes a leading byte order mark, and accepts a file without one
     36         pins_text = pins_path.read_text(encoding='utf-8-sig')
     37     except OSError as exc:
     38         raise _rejectPins(pins_path, f'unreadable: {exc.strerror}') from exc
     39     except UnicodeDecodeError as exc:
     40         raise _rejectPins(pins_path, f'not UTF-8: {exc.reason}') from exc
     41 
     42     uncommented = (line.partition('#')[0].strip() for line in pins_text.splitlines())
     43     pins = frozenset(pin for pin in uncommented if pin)
     44     _LOG.info('pins.read', extra={'pins_path': str(pins_path), 'pins': len(pins)})
     45     return pins
```
