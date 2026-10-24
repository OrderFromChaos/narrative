## Naming

- Standard Java: camelCase methods, fields, locals and parameters. PascalCase types. UPPER_SNAKE
  constants. A local compile-time constant may be UPPER_SNAKE too (see **Constants**). `NAR130`
  enforces it with Checkstyle, and allows the SRG and MCP names of Minecraft (`func_…`, `field_…`,
  `p_…`) of an override. (J1-P01)

- Spell names out. No `cfg`, `idx`, `tmp`. (Q11)

- **A method name starts with a verb, and the verb's object is what the method returns.**
  `parsePlan`, `readManifest`, `computeDeletionCutoff`. Not `planFrom`, not `cutoffFor`. Record
  accessors and `@Override` methods of the platform are exempt. (R9-03)

- **A static method's name is clear without the method's class**, to a reader who has never opened
  the class. Overloads only for one operation over different argument types. Interface
  implementations are exempt. (J1-P07, R9-03, R7-B06)

  **Length is not the defect.** Where the clear name is the longer one, write the longer one.

- **Predicates take `is`, `has` or `can`:** `isReady()`, `hasPower()`, `canExtract()`. Forge,
  Minecraft, GT and Lombok `@Getter` use these names, so a call site reads the same as the library
  calls beside the call site. (J1-F1)

- **Do not restate a domain type in a parameter name:** `RebinConfig config`, not
  `RebinConfig rebinConfig`. (Q11)

- **With a generic type, the parameter name is the only place the thing is named.** `Path`,
  `String`, `int` and `Object` constrain only a value's shape. Write `Path policyJsonPath`, not
  `Path path`, and `String manifestText`, not `String text`.

- **Raw and parsed forms get different names.** Prefix the raw form with `raw`: `String rawAt` from
  the file, `Instant at` once parsed. Never `at` beside `parsed.at()`. (R10-raw-names)

- **No fully-qualified name in code.** Import the type. Call a static method through its class
  where the call is unclear without the class name: `Math.max`, `Objects.requireNonNull`.
  Static-import test assertions, and members used on most lines of a file. `NAR104` flags a
  qualified name outside the imports. Where two types of one simple name meet in a file, keep the
  rarer one qualified and silence the line with `// noqa: NAR104`. (J1-P08, R3a-08)

