## Module state

- **`global` marks a side effect.** Declare `global` when a function *mutates* module
  state. A read is exempt. (R2b-G1)

- Python already forces `global` to rebind. Python does not police in-place mutation, and these mutations
  pass the linters:
  - `CONFIG.clear()`
  - `CONFIG['k'] = v`
  - `CONFIG.attr = v`

  `NAR001` flags these mutations.

- `NAR001` also counts a call to a method whose name starts with a configuration verb, such as
  `set`, `add`, `register`, or `close`. So a function that calls `LOG.addHandler(...)` declares
  `global LOG` even though the function never rebinds `LOG`. (V-03)

- Every attribute declared in `__init__`. `hasattr(self, ...)` is a red flag. (Q04)

