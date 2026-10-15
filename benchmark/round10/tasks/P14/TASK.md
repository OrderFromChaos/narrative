# Task P14 — one-way directory sync

Make a replica directory tree match a source tree: plan the copies, updates, deletions and renames,
report every entry that cannot be synced safely, and carry the plan out on request without ever
leaving a half-written file in the replica. Use the standard library only.

## Inputs

The arguments are `SOURCE REPLICA [--ignore PATH] [--apply]`. `SOURCE` and `REPLICA` are existing
directories, neither inside the other. Paths below are relative to the tree root, `/`-separated. The
ignore file is UTF-8, one pattern per line, in this subset of gitignore syntax:

- Trailing spaces are removed. A blank line, or a line starting with `#`, is not a pattern.
- A leading `!` negates the pattern. A trailing `/` makes the pattern match directories only.
- A pattern with a `/` at the start or in the middle is matched against the whole relative path,
  without its leading `/`. Any other pattern is matched against the entry's name, at any depth.
- `*` matches any run of characters other than `/`. As a whole segment, `**` matches any number of
  directories, including none: `**/x` matches `x` at any depth, `a/**/x` matches `a/x` and `a/b/c/x`,
  and `a/**` matches everything inside `a`. Any other run of `*` acts as one `*`. Every other
  character is literal, and matching is case-sensitive.
- The last pattern that matches an entry decides. An ignored directory is not read, so nothing inside
  it can be re-included by a later `!` pattern.
- The same rules apply to both trees. An ignored entry in the replica is never touched.

## What it does

1. Walk both trees without following symbolic links. Check each directory's entries in this order:
   a name that is not valid UTF-8 is an **undecodable name** conflict; then ignored entries are
   dropped; then, in the source only, names that differ but are equal after
   `unicodedata.normalize('NFC', name).casefold()` are each a **case clash** conflict; then a
   symbolic link is a **symlink** conflict and anything other than a regular file or directory is a
   **special file** conflict. A conflicting directory is not read.
2. A path that is a conflict in either tree is left alone in the replica, with everything under it.
   Apart from that, names are compared as exact bytes: no Unicode normalisation, no case folding.
3. Two regular files are equal when they have the same size and SHA-256; modification times are
   not used. Plan, per path:
   - a source directory with no directory at that path in the replica: `mkdir`, even when empty;
   - a source file with no entry at that path in the replica: `copy`;
   - a file at the same path in both trees, not equal: `update`; equal: unchanged, not planned;
   - a replica file or directory whose path is absent from the source: `delete` or `rmdir`; a
     directory that still holds an entry left alone (ignored or conflicting) is kept;
   - a path that is a file in one tree and a directory in the other: the replica entry is deleted or
     removed as above, and the source entry is created as above.
4. **Renames.** A `copy` whose path does not exist in the replica and a `delete` whose path does not
   exist in the source, with equal files, become one `rename`. Group these copies and deletes by
   size and SHA-256; within a group, sort each list by path and pair them in order. Unpaired ones
   stay `copy` or `delete`. Only a file that would otherwise be deleted can be renamed.
5. With `--apply`, carry out the plan in this order: delete, mkdir (parents first), rename, rmdir
   (children first), copy, update. A copy or update writes to a temporary file in the target's
   directory and moves it into place with `os.replace`, so an interrupted run leaves either the old
   file or the complete new one under the target's name.

## The outputs

The plan on stdout, written with `json.dumps(plan, indent=2, ensure_ascii=False) + '\n'` as UTF-8,
keys in this order:

```json
{
  "source": "work/source",
  "replica": "work/replica",
  "applied": false,
  "actions": [
    {"action": "rename", "path": "reports/q3.txt", "from": "reports/draft-q3.txt"},
    {"action": "update", "path": "settings.ini"}
  ],
  "conflicts": [
    {"path": "photo\\xe9.jpg", "conflict": "undecodable name"}
  ],
  "totals": {"copy": 0, "update": 1, "rename": 1, "delete": 0, "mkdir": 0, "rmdir": 0,
             "unchanged": 12, "conflicts": 1}
}
```

The values above show the shape only. `action` is one of `copy`, `update`, `rename`, `delete`,
`mkdir`, `rmdir`; only `rename` has `from`. `actions` is sorted by `path`, then `action`;
`conflicts` by `path`, then `conflict`. Strings sort by code point. A path that is not valid UTF-8
is written with each invalid byte as `\xNN`, lowercase hex. `source` and `replica` are the arguments
as typed; `applied` is true with `--apply`.

Exit codes: 0 when there are no conflicts, 1 when there is at least one conflict, 2 when the run could
not start (a tree that is missing or not a directory, one tree inside the other, an unreadable ignore
file), 3 when an action failed during `--apply`. Actions done before the failure stay done.

The planning must also be importable: another program calls one function with the source, the
replica and an optional ignore file path, and gets the actions and conflicts back, writing nothing.

## What is left to you

The package and module layout, the temporary file's name, which file metadata is copied besides the
content, logging, and any behaviour this specification does not fix.

## The fixture

`fixture/trees.tar` holds `source/` and `replica/`, all entries with one modification time; extract
it with `tar -xf fixture/trees.tar -C work` and run with `--ignore fixture/syncignore`. Its cases:
negated patterns inside an ignored and a non-ignored directory, an anchored and a `**` pattern, a
renamed file with identical copies elsewhere, a file replaced by a directory, a symbolic link, names
that differ only in case, an NFD name against its NFC form, a name that is not valid UTF-8, an empty
directory in each tree, a replica directory holding an ignored file, and two same-size files.
