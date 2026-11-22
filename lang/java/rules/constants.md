## Constants

Name every magic number. (Q09) Then place it by this test:

> Could someone change this value safely knowing only what the program **does**, or would they need
> to understand how the method **works**?

- **An implementation detail is inside the method.** A primitive or `String` constant is a local
  `final`, in UPPER_SNAKE. It is a compile-time constant, so javac inlines the value at each use. An object
  constant, such as a `Pattern`, is `private static final`, directly above the constant's only
  method. (J1-P09, R3a-12)
- **A value that players or pack makers tune is a field of the Config class** (under
  **Configuration**). (J1-P09)
- Constants that a developer changes, and that are not implementation details, stay at the top of
  the class.

*`verify.py` doesn't check where a constant is. This is review judgement.*

