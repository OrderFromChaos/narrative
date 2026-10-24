## Configuration

- **A value that players or pack makers tune is a field of the mod's Config class**, from Forge
  `Configuration` or GTNHLib `@Config`. Not a literal, not a field elsewhere. (J1-P30)
- **Where several implementations of a feature trade time for quality, all of them read one
  setting.** For example, the budget of each solver is multiplied by one `solverEffort` setting, with
  the levels High, Medium and Low. There is no `greedyStepBudget` setting beside an
  `lpIterationBudget` setting. (J1-P30)
- Third-party log noise is off globally, with a debug setting to turn the noise on. Not a save and
  restore around each call. (J1-P30)
- No environment variables and no system properties for behaviour. (J1-P30, R3a-02)

