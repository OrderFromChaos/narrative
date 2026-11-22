## Configuration

- **A value that players or pack makers tune is a field of the mod's Config class**, from Forge
  `Configuration` or GTNHLib `@Config`. Don't write the value as a literal, or as a field of another class. (J1-P30)
- **Where several implementations of a feature trade time for quality, all of them read one
  setting.** For example, the budget of each solver is multiplied by one `solverEffort` setting, with
  the levels High, Medium and Low. Don't add a `greedyStepBudget` setting beside an
  `lpIterationBudget` setting. (J1-P30)
- Third-party log noise is off globally, with a debug setting to turn the noise on. Don't save and
  restore the log level around each call. (J1-P30)
- Don't read an environment variable or a system property for behaviour. (J1-P30, R3a-02)

