## Testing

- **Real dependencies**: a real socket on loopback, a real temp SQLite file, a real temp directory.
  A test double is a last resort for something you cannot run. Flag each one as a known
  gap. With a fake transport, tests pass while production fails. (R2-02, Q16)

- **Property-based tests (hypothesis) wherever there is an invariant**: round-trips, ordering,
  conservation, numeric range. Example-based tests cover specific regressions on top. A very slow
  stateful property test may be opt-in rather than run in CI. (R2-12)

- **Test functions are `testSomethingDescriptive`**, in camelCase with a `test` prefix. The
  conventional `test_parse_header_roundtrips` fails the `mixedCase` gate this style mandates. The
  camelCase spelling passes pylint, *and* the pytest default `python_functions = test*` still
  collects the test function.

- Tests are in a separate module, not in the program file. A `from hypothesis import given` at
  module scope makes the program raise `ModuleNotFoundError` before the program reaches `main()` on
  any machine without the test library.

  Where a single file is required, put the tests behind `### tests` before the
  `### vocabulary` divider and import hypothesis lazily.

