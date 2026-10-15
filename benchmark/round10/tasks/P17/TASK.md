# Task P17 — SQLite migration runner

Apply numbered SQL migration files to a SQLite database in order, each one all or nothing, and
refuse to run when the files no longer match what the database records as applied. Run as
`python3 -m <package> up DATABASE MIGRATIONS_DIR [--target NNNN]` or
`python3 -m <package> status DATABASE MIGRATIONS_DIR`. Use the standard library only (`sqlite3`).

## Inputs

- `DATABASE`: a SQLite database path. It is created when it does not exist.
- `MIGRATIONS_DIR`: a directory of migration files named `NNNN_description.sql`: four digits, an
  underscore, then letters, digits and underscores. The four digits are the file's **number**.
  Other files are ignored. Numbers need not be consecutive. A file is UTF-8 SQL text of any kind
  SQLite accepts in a script, with LF or CRLF line endings. When its first line, without the line
  ending, is exactly `-- no-transaction`, the file is a **no-transaction** migration.
- `--target NNNN`: four digits; apply only pending migrations numbered at most `NNNN`. The target
  need not be the number of a file.

The database records applied migrations in this table, which the runner creates when it is absent:

```sql
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,   -- the four-digit number, '0003'
    name TEXT NOT NULL,         -- the file name, '0003_settings.sql'
    checksum TEXT NOT NULL,     -- lowercase hex SHA-256 of the file's bytes as stored
    applied_at TEXT NOT NULL    -- UTC, ISO 8601 with seconds: '2026-09-01T08:00:00+00:00'
);
```

## What it does

1. Read every migration file and its checksum, and read `schema_migrations` if it exists.
2. Give each file and each recorded migration a **state**. A file whose number is also another
   file's number is `duplicate number`. Otherwise, a file whose number is recorded is `applied`
   when its checksum equals the recorded one and `checksum changed` when not. A file not recorded
   whose number is below the highest recorded number is `out of order`; any other file not
   recorded is `pending`. A recorded migration whose number has no file is `file missing`.
3. Every state other than `applied` and `pending` is a **problem**. `status` stops here.
4. `up` with any problem is **refused**: it applies nothing and records nothing.
5. Otherwise `up` applies the pending migrations in number order, up to the target if one is given.
   A migration and the row that records it run in one transaction. When a statement fails, none of
   that migration's changes stay (a table it created is gone too), it is not recorded, and the run
   stops there. Migrations applied earlier in the same run stay applied.
6. A no-transaction migration runs outside any transaction (it may hold statements such as
   `VACUUM` that SQLite refuses inside one) and is recorded after its last statement succeeds.

## The outputs

The report goes to stdout, written with `json.dumps(report, indent=2) + '\n'`, keys in this order.
For `up`:

```json
{
  "command": "up",
  "database": "work/app.db",
  "target": "0006",
  "applied": ["0003_settings.sql"],
  "failed": {"name": "0004_prices.sql", "error": "no such table: products"},
  "pending": ["0004_prices.sql", "0006_index_orders.sql"],
  "problems": [{"name": "0002_add_email.sql", "problem": "checksum changed"}]
}
```

For `status` the keys are `command` (`"status"`), `database`, `migrations` (a list of objects
`{"version": "0001", "name": "0001_create_customers.sql", "state": "applied"}`) and `problems`.

The values above show the shape only. `database` is the argument as typed. `target` is the
argument as typed, or `null`. `applied` lists the files applied by this run, in order. `failed` is
`null` when nothing failed; `error` is `str()` of the `sqlite3` exception. `pending` lists every
file whose state was `pending` and that is still not applied when the run ends, the failed one
included, by number. `migrations` lists every file and every `file missing` record, by number and
then name. `problems` has one entry per problem, by name; `name` is the file name, or the recorded
name for `file missing`.

Exit codes: for `up`, 0 when nothing failed and there was no problem, 1 when a migration failed,
2 when the run was refused. For `status`, 0 when there is no problem and 2 when there is one. Both
exit with 2 and a message on stderr, without a report, when the run cannot start: a missing
migrations directory, a target that is not four digits, or a target below the highest recorded
number.

Both commands must also be importable: another program calls one function per command with the
database path, the migrations directory and, for `up`, an optional target string, and gets the
report back as a dict without anything being printed.

## What is left to you

The package and module layout, how statements are executed, how `sqlite3` transactions are
controlled, error messages, and any behaviour this specification does not fix.

## The fixture

`fixture/migrations/` holds seven migration files and a text file, `fixture/duplicate-migrations/`
three files. `start.sql`, `start-edited.sql` and `start-removed.sql` each build a starting database:

    python3 -c 'import sqlite3, sys; sqlite3.connect(sys.argv[1]).executescript(open(sys.argv[2]).read())' work/app.db fixture/start.sql

Its runs: `status`, `up` and `up --target 0004` on `start.sql`, `up` on each other start script,
and `up` with `duplicate-migrations` on an empty database. Its cases: CRLF line endings, a `;` in a
string literal, a trigger, a numbering gap, a `VACUUM`, a migration that fails after creating a
table, an edited applied file, a deleted applied file, and two files with the same number.
