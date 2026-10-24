### Writing a comment

Take these steps in order before writing or rewording a comment. The kinds, the **Never** list,
**Depth** and **Sentence form** are in **Comments**.

1. **Rename first.** If the information fits in a name or a type, rename and write no comment:
   `ByteCount` as the type of `overQuota`, `totalCents`, `rollingMeanSignedError`. (R10-Q25, R10-Q27, R10-Q16)
2. **Guarantee it in code.** Establish a cheap precondition, such as sorted input, upstream in the
   call flow, not in the function that depends on the precondition, and write no comment. An index
   lookup doesn't sort its input. If a code change removes a trap, make the change and write no
   comment. If explaining how the code works takes more than one plain clause, rewrite the code
   instead. Name the step, or use the obvious construct. A `dict` filled with `setdefault()` and
   sliced by insertion order becomes an explicit loop that counts periods. (R10-Q19, R10-footgun,
   R10-hard-comment)
3. **Match a kind.** Write a comment only if it is one of the four **Comment kinds**, passes that
   kind's test, and is not under **Never**. Deleting is a valid outcome of a rewrite when the content
   fails the test. When only the wording breaks a rule, rewrite the wording and keep the content:
   `without the lock, two writers interleave their lines` → `two writers can interleave lines in
   the log. The lock serializes them`. (R10-keep-content)
4. **Set the depth and sentence form** by **Depth** and **Sentence form**.

