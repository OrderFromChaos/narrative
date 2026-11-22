## Testing

- **Real dependencies**: a real temp directory with `@TempDir`, a real file. No Mockito. A test
  double is a last resort for something you cannot run. Flag each one as a known gap. Keep logic off
  Minecraft types, so the tests run headless. (R2-02, Q16)

- **Property-based tests wherever there is an invariant**: round-trips, ordering, conservation,
  numeric range. jqwik where the project already has jqwik, else JUnit 5 `@ParameterizedTest` over
  generated cases. **Assert a rule.** `assertEquals("3.12", format(3.12))` repeats
  the implementation's output, and a table of such asserts is not a test of anything. Never re-implement production math
  in a test. (J1-P32, R2-12)
  Give such a test both kinds of case: generated cases, and the boundary values of the invariant, so
  the boundary values are in every run. Generate with jqwik, or with `java.util.Random` and a
  constant seed, so a failing case is the same on the next run. (J1-P36)

- **A test method name is the rule.** Tests are found by the `@Test` annotation, so the name doesn't
  need a `test` prefix: `runningMachineNeverDisplaysZero()`. (J1-P33)

- **Never merge a test that fails.** If a scenario is aspirational, raise the budget or disable the
  test explicitly, and say which in the PR. (J1-S12)

- **No bootstrap or loader that can be imported only from the test source set.** Put the entry
  point in the main source set, so any source set can import the entry point. (J1-S13)

- **No production change for a test.** No test-only field or variable in a production class. A test
  reads private state through reflection. Add an accessor only when other code needs the accessor
  too. (J1-S14)

- **No test only because a bug was fixed.** Write a regression test when the code under test is
  likely to break the same way again, or when the test checks an invariant of the program. Write the
  case and the expected result in the name and the docstring of the test. Use the present tense.
  (R12-no-changelog-tests)
