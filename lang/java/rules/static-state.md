## Static state

- **A mutable static field has a comment with the reason**, on the line above or after the field on
  the same line, **or the field is an instance field of the object with the same lifetime.** A
  mutable static field is non-`final`, or a `static final` mutable collection. Fields that Forge
  requires (`@Mod.Instance`, `@SidedProxy`, config fields) and loggers are exempt. `NAR110` flags
  the rest. (J1-P27, R2b-G1)

