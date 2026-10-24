## Python 3.11 floor

`ruff` targets `py311`. Check with `vermin -t=3.11- --violations`. (R7-E07-floor)

Run tasks that should fail together in an `asyncio.TaskGroup`. Hand-rolled cancellation fails
silently. Give independent handlers, such as one per client connection, a task each. A `TaskGroup`
cancels every task when one raises. (R7-E07-floor, R10-taskgroup-scope)

- **`except TimeoutError` is correct** around `asyncio.wait_for`. At 3.11 `asyncio.TimeoutError`
  *is* the builtin, so the two are one class. (R3a-06)

- Anything added in 3.12 or later is out, including the `type` statement and PEP 695 generics.

- On a guard for a runtime newer than the floor, the comment has the version: `# on 3.12.1 and
  later, wait_closed() waits for open connections`. (R10-version-guard)

