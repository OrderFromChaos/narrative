# Task P18 — contact list merge

Merge contact lists exported from several systems into one deduplicated list, show which source
rows went into each merged contact, and report every row that could not be used.

## Inputs

An input directory with the CSV exports and the rules file `merge.json` (or `--rules PATH`):

```json
{
  "default_country_code": "44",
  "sources": [
    {"file": "phonebook.csv", "encoding": "utf-16", "delimiter": ";", "name": ["First", "Last"],
     "email": "Email", "phone": "Mobile"},
    {"file": "crm.csv", "encoding": "utf-8-sig", "delimiter": ",", "name": ["Full Name"],
     "email": "E-mail", "phone": "Phone", "company": "Company"}
  ]
}
```

`default_country_code` is 1 to 3 digits. Each source gives its file, a Python codec name, a
one-character delimiter, and the header columns holding each field. `name` is a list of columns,
joined with one space after stripping each part, empty parts skipped. `email`, `phone` and `company`
are optional; a source without one contributes nothing to that field. Each CSV file has a header
row, and a quoted field may hold a newline. Other columns are ignored. A missing or malformed rules
file, a missing source file, a file that does not decode with its codec, or a named column missing
from a header stops the run with exit code 2.

## What it does

1. Read the sources in the order of `sources`. Each data record is numbered from 1, the header not
   counted; a quoted field holding a newline does not start a new record.
2. **Email.** Strip surrounding whitespace; empty means no email. A valid email has one `@`, no
   whitespace, a non-empty local part, and a domain with a `.` not at either end. It is normalised
   to the local part as written (case-sensitive), `@`, and the domain after `str.casefold()`.
3. **Phone.** Strip surrounding whitespace; empty means no phone. Otherwise, in order:
   - An extension at the end is dropped: if the text matches
     `^(.*?)\s*(?:ext\.?|x|#)\s*\d+$` (case-insensitive), keep only the first group.
   - Remove every space, `-`, `.`, `(` and `)`.
   - `+` and digits: the digits are the number. `00` and digits: the digits after `00`. `0` and
     digits: `default_country_code`, then the digits after the `0`. Anything else is invalid.
   - The number must have 8 to 15 digits, not starting with `0`. The result is `+` and the digits.
4. **Name.** The matching key is `" ".join(unicodedata.normalize("NFKC", name).casefold().split())`;
   the shown name is `" ".join(unicodedata.normalize("NFC", name).split())`. `company` is shown the
   same way, and an empty company is no company.
5. A record is **rejected** with the first reason that applies: `wrong field count` (differs from
   the header's), `missing name` (the shown name is empty), `invalid email`, `invalid phone`,
   `no email or phone`. A rejected record matches nothing.
6. Two accepted records **match** when both have an email and the normalised emails are equal, or
   both have a phone and the phones and name keys are equal. A shared phone with a different name,
   such as a family landline, is not a match. A missing email or phone never matches another.
7. Records linked by a chain of matches form one **group**: A matches B by email, B matches C by
   phone, so A, B and C are one group.
8. **Precedence**: a record from an earlier source in `sources` comes first; within a source, the
   lower record number comes first. Each group becomes one merged contact:
   - `name`: the shown name of the group's first record.
   - `company`: the company of the first record that has one, else `null`.
   - `emails`, `phones`: the distinct normalised values, ordered by the first record holding each.
   - `members`: every record of the group, in precedence order.
   Contacts are ordered by their first record and numbered `C1`, `C2`, … in that order.

## The outputs

`merged.json` in the directory named by `--out` (default: the current directory), written with
`json.dumps(report, indent=2, ensure_ascii=False) + '\n'`, keys in this order:

```json
{
  "contacts": [{"contact_id": "C1", "name": "Ines Varga", "company": null,
    "emails": ["ines@varga.example"], "phones": ["+441632960018"],
    "members": [{"file": "phonebook.csv", "row": 2}, {"file": "crm.csv", "row": 9}]}],
  "rejected": [{"file": "crm.csv", "row": 4, "reason": "invalid phone"}],
  "totals": {"sources": 2, "rows": 14, "contacts": 9, "rejected": 1}
}
```

The values above show the shape only. `rejected` is in precedence order; `rows` counts every data
record read. A summary on stdout: one line per contact with its id, name and member count, then the
totals. Run as `python3 -m contact_merge INPUT_DIR [--rules PATH] [--out DIR]`. Exit codes: 0 when
no record is rejected, 1 when at least one is, 2 when the run could not start.

The merge must also be importable: another program calls one function with the input directory and
an optional rules path, and gets the contacts and rejected records back without any file being
written. Use the standard library only.

## What is left to you

The package and module layout, the summary layout, error messages, and any behaviour this
specification does not fix.

## The fixture

`fixture/` has `merge.json` and three exports: `phonebook.csv` (UTF-16 with a byte order mark,
semicolon-delimited, first and last name in separate columns), `crm.csv` (UTF-8 with a byte order
mark) and `newsletter.csv` (cp1252). Its cases: a domain differing only in letter case, linking a
chain of three records across all three sources; two emails differing only in the local part's
case; `Weiß` against `WEISS`; a name in NFD against NFC; a phone with an extension; two people on
one family phone; several records with no email; a quoted field holding a newline, followed later in
that file by a rejected record; an invalid phone, an invalid email, and neither email nor phone.
