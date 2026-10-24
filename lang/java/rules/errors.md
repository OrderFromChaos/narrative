## Errors

- **Checked for boundary and I/O failures, unchecked for everything else.** A parse error of a file,
  a packet or NBT `extends Exception`, so a call site with no `try` and no `throws` clause is a
  compile error. A broken invariant `extends RuntimeException`. (J1-F2, Q20)

  A checked exception cannot leave a lambda for a JDK functional interface, or an override of a
  Minecraft or Forge method. Catch it there:

  ```java
  @Override
  public void readFromNBT(NBTTagCompound compound) {
      super.readFromNBT(compound);
      try {
          plan = parsePlan(compound.getString("plan"));
      } catch (PlanException exception) {
          plan = null;
      }
  }
  ```

  An exception that leaves `readFromNBT()` is caught by Forge, which logs "its state cannot be
  restored" and drops the tile entity. A `@Mod.EventHandler` or `@SubscribeEvent` method is not an
  override, so a `throws` clause on the method compiles.

- **The name of an exception class ends in `Exception`:** `PlanException`, not `PlanError` or
  `PlanFailure`. Never `Error`, because a `java.lang.Error` subclass means the JVM is unusable.
  `NAR109` enforces both. (J1-P23)

- **Handle each failure mode narrowly and separately.** No `catch (Exception)`,
  `catch (RuntimeException)`, `catch (NullPointerException)`, `catch (Throwable)` or `catch (Error)`.
  `NAR142` flags them. There are two exceptions. One is `catch (NoClassDefFoundError)` at the
  optional-mod boundary, described in `architecture.md`. The other is `catch (RuntimeException)` in
  a degrade-and-report loop over code from another mod, whose exceptions you cannot list. Mark the
  catch `// noqa: NAR142`, with the reason:

  ```java
  for (MTEMultiBlockBase machine : machines) {
      try {
          checkConformance(machine);
      } catch (RuntimeException exception) { // noqa: NAR142, degrade and report over GT machine code
          failures.add(machine.getLocalName() + ": " + exception);
      }
  }
  ```

  (J1-P24, Q19, J1-F04)

- **Related means the handling is the same, not that the classes share a base.** Where two failures
  produce one outcome, one multi-catch `catch (A | B exception)` is correct. But check the premise
  first. A timeout and an unreachable host are different facts and deserve different words.
  (R8-D24-resolved)

- `throw new XException(message, cause)`, **and** log it. Both. `NAR144` flags a rethrow that drops
  the cause. (Q21)

- **An error message for malformed input includes the expected form.** `bad count 'twelve' in
  plan.txt (expected a whole number such as 12)`. (R10-expected-form)

- **Log the generic fact once at the raise site, however you factor that.** Route several raise
  sites through a `reject*()` helper that logs and returns the exception. (Q23, R4-02)

- **At the handle site, log what the failure meant there, but in a degrade-and-report loop log the
  aggregate, not the item.** Log the item at DEBUG and the tally at WARN. (R4-02)

- **Level follows from what an operator can act on.** A pack maker cannot act on recipe 4,812. A
  pack maker can act on "4,812 of 10,000 recipes rejected". (R4-02)

- LBYL over EAFP. You know your invariants, you do not know every exception an implementation can
  throw. (Q22)

- **Degrade and report.** Process every item, then log the tally at WARN. The exception from a bad
  item is caught in the loop, so the game does not crash. (J1-P25, Q24)

- **The config gate is the exception.** A hand-written config gate rejects the first bad entry,
  because with a half-valid config, what to do is unknown. Where an out-of-range value is reset and
  logged by the GTNHLib or Forge config loader, keep that. (J1-P26, R8-D25-resolved)

