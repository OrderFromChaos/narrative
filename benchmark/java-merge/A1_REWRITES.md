# A1: neutral examples for nar:core, for review

`nar:core` is one skill for Python and Java, so an example in core has no `#` or `//` and is from a
domain that fits any language. Every row below is applied, on 2026-10-24.

- **marker**: the example stays, without `#`
- **swap**: a new example in place of a language-specific one
- **move**: an example leaves core. Each language skill gets the example in the syntax of the
  language, under a heading with the name of the rule. Core names the heading as **Comments in
  \<language\>**, in the skill `nar:<language>`, and `verify_docs.py` fails when a language has no
  such heading

Each new comment example passed `checks.py` and `agentverbs.py` as a comment. Each was also read
against the term, referent and agent-verb rules of the skill, and against your Claudish patterns.
Rows E6, E7, E8, E11, E19, E20 and E21 changed after your notes.

| | Rule | Kind | Today | Proposal | Decision |
|---|---|---|---|---|---|
| E1 | Every term: descriptive word | swap | `load_config()` returns them without parsing | `loadConfig()` returns them without parsing | applied |
| E2 | Library facts | swap | `fetch_invoice() calls the SDK once and catches TimeoutError` | `fetchInvoice() calls the SDK once and catches a timeout` | applied |
| E3 | Source kind | marker | `# vendor closes idle sockets at 60 s` and 4 more | `vendor closes idle sockets at 60 s` and the same 4, with no `#`. `WARN_THRESHOLD = 1.6  # calibration spec CAL-7, section 3` becomes `calibration spec CAL-7, section 3`, on a threshold constant | applied |
| E4 | Fence kind | swap | `# bool subclasses Python int. Reject it too`, not `# bool subclasses Python int` | `the API returns 200 with an error body for a bad key. Check the body too`, not `the API returns 200 with an error body for a bad key`. The bool example moves to nar:python | applied |
| E5 | Fence kind | marker | constant-time, walk backwards, migrate before load, the cache counterexample | the same 4, with no `#` | applied |
| E6 | Decoding aid | move | `SIZE_PATTERN = re.compile(...)  # number, then an optional binary unit suffix` | moves to the language skills. A decoding aid is about a construct of the code, so every example is language-specific. Core keeps the kind and the test, and says: The examples are under **Decoding aids** in **Comments in \<language\>**, in the skill `nar:<language>` | applied |
| E7 | Decoding aid | move | `# fsum() for accurate floating point math` | moves to the language skills, as E6 | applied |
| E8 | Decoding aid: regex | move | the `BARE_KEY` code block | moves to the language skills. Core keeps the regex rule, and says: The example is under **Decoding aids** in **Comments in \<language\>**, in the skill `nar:<language>` | applied |
| E9 | Marker kind | marker | stated assumption, block label, read-only rule | the same 3, with no `#` | applied |
| E10 | Never: language behaviour | swap | `<=`, case sensitivity, `None` | `<=`, case sensitivity, the null value | applied |
| E11 | Depth | move | `# signed error`, and the vendor API code block | `signed error` with no `#`. The code block moves, and core says: The example is under **Depth** in **Comments in \<language\>**, in the skill `nar:<language>` | applied |
| E12 | Sentence form: one line | swap | a one-line `#` comment has a lowercase start and no final period | a one-line comment has a lowercase start and no final period | applied |
| E13 | Sentence form: connectives, subject | marker | migrate before load, a float, named volumes | the same, with no `#` | applied |
| E14 | Sentence form: referents | swap | `# open() creates a missing log file` → `# open() creates the log file if it doesn't exist` | `openLog() creates a missing log file` → `openLog() creates the log file if the file doesn't exist` | applied |
| E15 | Sentence form: referents | swap | `tz=None leaves TOML local times without one` → `without a UTC offset` | `the parser leaves TOML local times without one` → `without a UTC offset` | applied |
| E16 | Sentence form: case coverage, units, error message | marker | expired item, every file counted | the same, with no `#` | applied |
| E17 | Sentence form: conclusion | swap | `None when malformed`, not `None when a malformed line names no customer as a string` | `empty when malformed`, not `empty when a malformed line names no customer as a string` | applied |
| E18 | Sentence form: Fence | swap | `# isdigit() admits non-ASCII digits such as '²'. Check isascii() too` | `the vendor rounds tax per line, not per invoice. Round each line before the sum`. The isdigit() example moves to nar:python | applied |
| E19 | Sentence form: X would | swap | such as `read_text()` when the code calls `read_bytes()` | such as a read of the whole file into memory, when the code below the comment streams the file line by line | applied |
| E20 | Sentence form: X would | move | the `read_bytes()` code block | The block moves, and core says: The example is under **Fence** in **Comments in \<language\>**, in the skill `nar:<language>`. Core keeps the retry example with no `#` | applied |
| E21 | Sentence form: placement | swap | Inside `try:`, it goes above the call … above `pendulum.parse(raw_at, tz=None)`, not below the `try` block | Comments inside a try block go above the call the comment concerns, not above the `try`. A comment on an argument goes above the call that passes the argument, not below the try block. The pendulum example moves under **Placement** in **Comments in Python** | applied, your wording |
| E22 | A finding is information | swap | `the worker owns the lock` from `owns_lock()` | `the worker owns the lock` from `ownsLock()` | applied |
| E23 | Prose review worked example | marker | `# an expired item is removed on lookup` | the same, with no `#` | applied |
| E24 | Writing a comment, step 1 | swap | `over_quota: ByteCount`, `total_cents`, `rollingMeanSignedError` | `ByteCount` as the type of `overQuota`, `totalCents`, `rollingMeanSignedError` | applied |
| E25 | Writing a comment, step 3 | marker | `# without the lock, two writers interleave their lines` → `# two writers can interleave lines in the log. The lock serializes them` | the same, with no `#` | applied |
| E26 | Never: guarantees | swap | `while self.items and …`, not `# store() rejects an oversized item, so the cache is never empty` | test for an empty cache in the loop condition, not `store() rejects an oversized item, so the cache is never empty` | applied, found while applying |
| E27 | Sentence form: Alternatively | swap | `# open(path, 'w') would empty the file before writing. Alternatively, os.replace() swaps in a complete copy` | `opening the file for writing would empty the file before the write. Alternatively, write a temporary file and rename the temporary file over the original` | applied, found while applying |
## What moves to the language skills

| Heading | `nar:python` (Comments in Python) | `nar:java` (Comments in Java) |
|---|---|---|
| Decoding aids | the size pattern, `fsum()`, the `BARE_KEY` regex block | the amount pattern, `Math.fma()`, the `Pattern.compile` regex block, from the narrative-java copy |
| Fence | `bool subclasses Python int`, `isdigit()`, the `read_bytes()` block | `Character.isDigit()`, the `Files.readAllBytes()` block |
| Depth | the vendor API paging block | the paging loop |
| Placement | `pendulum.parse(raw_at, tz=None)` | none |
