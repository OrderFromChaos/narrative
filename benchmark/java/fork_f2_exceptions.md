# F2: checked or unchecked exceptions

A is unchecked: `PlanException extends RuntimeException`. B is checked: `PlanException extends
Exception`. Every A and B block below is cut from a file that compiles with javac 25. The
`PlanTerminal` files compile against PlanNH's `build/rfg/recompiled_minecraft-1.7.10.jar`
(Minecraft and Forge 1.7.10), with netty 4.0.10, Guava 17 and log4j 2.0-beta9 from the Gradle
cache. The test compiles against `junit-jupiter-api` 5.10.2. The files are in the session
scratchpad under `f2v3/a/` and `f2v3/b/`.

Every `error:` line below is a javac compile error. `./gradlew compileJava` stops on it and
builds no jar, so none of these errors can happen at run time.

## GTNH code today

Counts over `src/main/java`:
- PlanNH has no exception class and one `throws` clause, for `IOException`.
- GT5-Unofficial has one class that extends `RuntimeException` and none that extends `Exception`.
  Of its 102 `throws` clauses, 82 are `IOException` and 6 are AE2's checked `GridAccessException`.
  The `ConfigException` of its 5 `throws ConfigException` clauses is GTNHLib's, which extends
  `RuntimeException`.

A checked exception from another mod (AE2). GT5-Unofficial has 22 catches of this shape,
`gregtech/common/tileentities/machines/MTEHatchInputME.java:318-323`:

```java
IMEMonitor<IAEFluidStack> sg;

try {
    sg = getProxy().getStorage()
        .getFluidInventory();
} catch (GridAccessException e) {
    return EMPTY_FLUID_TANK_INFOS;
}
```

A checked `IOException` inside MUI2 syncer lambdas, `kubatech/api/DynamicInventory.java:155-167`:

```java
}, (buffer, i) -> {
    try {
        i.write(buffer);
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}, buffer -> {
    try {
        return GTHelper.StackableItemSlot.read(buffer);
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}), builder);
```

A checked `IOException` turned unchecked at the source,
`gregtech/common/data/GTPowerfailTracker.java:448-450`:

```java
} catch (IOException e) {
    throw new UncheckedIOException("Failed to encode team powerfail blob", e);
}
```

## Your mod: one tile entity class, six call sites

### The exception class

A:

```java
public static class PlanException extends RuntimeException {

    public PlanException(String message) {
        super(message);
    }

    public PlanException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

B:

```java
public static class PlanException extends Exception {

    public PlanException(String message) {
        super(message);
    }

    public PlanException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### The parser

A:

```java
/**
 * Parse a plan from its "name:machineCount" text.
 *
 * @throws PlanException when the text has no machine count
 */
public static Plan parsePlan(String planText) {
    final int colon = planText.lastIndexOf(':');
    if (colon < 0) {
        throw new PlanException("plan.malformed text=" + planText + " (expected \"name:4\")");
    }
    try {
        return new Plan(planText.substring(0, colon), Integer.parseInt(planText.substring(colon + 1)));
    } catch (NumberFormatException exception) {
        throw new PlanException("plan.malformed text=" + planText + " (expected \"name:4\")", exception);
    }
}

/**
 * Read a plan file.
 *
 * @throws PlanException when the file cannot be read or parsed
 */
public static Plan readPlan(Path planPath) {
    try {
        return parsePlan(Files.readString(planPath));
    } catch (IOException exception) {
        throw new PlanException("plan.unreadable path=" + planPath, exception);
    }
}
```

B:

```java
/** Parse a plan from its "name:machineCount" text. */
public static Plan parsePlan(String planText) throws PlanException {
    final int colon = planText.lastIndexOf(':');
    if (colon < 0) {
        throw new PlanException("plan.malformed text=" + planText + " (expected \"name:4\")");
    }
    try {
        return new Plan(planText.substring(0, colon), Integer.parseInt(planText.substring(colon + 1)));
    } catch (NumberFormatException exception) {
        throw new PlanException("plan.malformed text=" + planText + " (expected \"name:4\")", exception);
    }
}

/** Read a plan file. */
public static Plan readPlan(Path planPath) throws PlanException {
    try {
        return parsePlan(Files.readString(planPath));
    } catch (IOException exception) {
        throw new PlanException("plan.unreadable path=" + planPath, exception);
    }
}
```

### 1. Lifecycle handler

A:

```java
@Mod.EventHandler
public void postInit(FMLPostInitializationEvent event) {
    plan = readPlan(Path.of("config/plan.txt"));
}
```

B:

```java
@Mod.EventHandler
public void postInit(FMLPostInitializationEvent event) throws PlanException {
    plan = readPlan(Path.of("config/plan.txt"));
}
```

B without `throws PlanException` on `postInit`: `error: unreported exception PlanException; must be caught or declared to be thrown`. A handler is not an override, so
the `throws` clause compiles.

If the exception leaves the handler, in A or B: in `FMLModContainer.handleModStateEvent()`, every
`Throwable` is caught and passed to `controller.errorOccurred(this, t)`
(`cpw/mods/fml/common/FMLModContainer.java:528-541`), and the error is shown as a mod loading error.

### 2. Background load for a GUI

A:

```java
public static CompletableFuture<Plan> loadInBackground(Path planPath) {
    return CompletableFuture.supplyAsync(() -> readPlan(planPath));
}
```

B:

```java
public static CompletableFuture<Plan> loadInBackground(Path planPath) {
    return CompletableFuture.supplyAsync(() -> {
        try {
            return readPlan(planPath);
        } catch (PlanException exception) {
            throw new CompletionException(exception);
        }
    });
}
```

B with the lambda of A: `error: unreported exception PlanException; must be caught or declared to be thrown`.

### 3. Minecraft override: `TileEntity.readFromNBT`

A:

```java
@Override
public void readFromNBT(NBTTagCompound compound) {
    super.readFromNBT(compound);
    plan = parsePlan(compound.getString("plan"));
}
```

B:

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

B with the body of A: `error: unreported exception PlanException; must be caught or declared to be thrown`. B with `throws PlanException` on the override:
`error: readFromNBT(NBTTagCompound) in PlanTerminal cannot override readFromNBT(NBTTagCompound) in
TileEntity` and `overridden method does not throw PlanException`.

If the exception leaves `readFromNBT` in A: in `TileEntity.createAndLoadEntity()`, it is caught and
logged as "A TileEntity … has thrown an exception during loading, its state cannot be restored",
and the tile entity is set to `null` (`net/minecraft/tileentity/TileEntity.java:131-142`). The
machine loads with no tile entity.

### 4. FML packet handler: `IMessageHandler.onMessage`

A:

```java
@Override
public IMessage onMessage(PlanMessage message, MessageContext context) {
    parsePlan(message.planText);
    return null;
}
```

B:

```java
@Override
public IMessage onMessage(PlanMessage message, MessageContext context) {
    try {
        parsePlan(message.planText);
    } catch (PlanException exception) {
        return null;
    }
    return null;
}
```

B with the body of A: `error: unreported exception PlanException; must be caught or declared to be thrown`. B with `throws PlanException` on the override:
`error: onMessage(PlanMessage,MessageContext) in PlanMessageHandler cannot implement
onMessage(REQ,MessageContext) in IMessageHandler` and `overridden method does not throw PlanException`.

If the exception leaves `onMessage` in A: `SimpleChannelHandlerWrapper.exceptionCaught()` logs it at
ERROR and passes it to the next netty handler
(`cpw/mods/fml/common/network/simpleimpl/SimpleChannelHandlerWrapper.java:46-50`). The netty
pipeline after that point is not checked here.

### 5. Forge event handler

A:

```java
@SubscribeEvent
public void onWorldLoad(WorldEvent.Load event) {
    plan = readPlan(Path.of("config/plan.txt"));
}
```

B:

```java
@SubscribeEvent
public void onWorldLoad(WorldEvent.Load event) throws PlanException {
    plan = readPlan(Path.of("config/plan.txt"));
}
```

B without `throws PlanException` on `onWorldLoad`: `error: unreported exception PlanException; must be caught or declared to be thrown`. The `throws` clause compiles,
as in 1.

If the exception leaves the handler, in A or B: in `EventBus.post()`, it is caught, logged as
"Exception caught during firing event", and rethrown with `Throwables.propagate()`
(`cpw/mods/fml/common/eventhandler/EventBus.java:136-147`). The code that posted the event gets the
exception.

### 6. Stream

A:

```java
public static List<Plan> parseAll(List<String> planTexts) {
    return planTexts.stream()
        .map(PlanTerminal::parsePlan)
        .toList();
}
```

B:

```java
public static List<Plan> parseAll(List<String> planTexts) throws PlanException {
    final List<Plan> plans = new ArrayList<>();
    for (final String planText : planTexts) {
        plans.add(parsePlan(planText));
    }
    return plans;
}
```

B with the stream of A: `error: incompatible thrown types PlanException in functional expression`.

## Mod developer QOL: an addon that uses your API

### Your API

A:

```java
public static class PlanException extends RuntimeException {

    public PlanException(String message, Throwable cause) {
        super(message, cause);
    }
}

public interface PlanSource {

    /**
     * Load the plan.
     *
     * @throws PlanException when the plan cannot be loaded
     */
    Plan loadPlan();
}

public static class PlanReader {

    /**
     * Read a plan file.
     *
     * @throws PlanException when the file cannot be read
     */
    public Plan read(Path planPath) {
        return new Plan(planPath.getFileName().toString(), 1);
    }
}
```

B:

```java
public static class PlanException extends Exception {

    public PlanException(String message, Throwable cause) {
        super(message, cause);
    }
}

public interface PlanSource {

    /** Load the plan. */
    Plan loadPlan() throws PlanException;
}

public static class PlanReader {

    /** Read a plan file. */
    public Plan read(Path planPath) throws PlanException {
        return new Plan(planPath.getFileName().toString(), 1);
    }
}
```

### 7. An addon source that reads a file

A:

```java
public final class FileSource implements PlanSource {

    @Override
    public Plan loadPlan() {
        try {
            return new Plan(Files.readString(Path.of("addon/plan.txt")), 1);
        } catch (IOException exception) {
            throw new PlanException("addon.plan.unreadable", exception);
        }
    }
}
```

B:

```java
public final class FileSource implements PlanSource {

    @Override
    public Plan loadPlan() throws PlanException {
        try {
            return new Plan(Files.readString(Path.of("addon/plan.txt")), 1);
        } catch (IOException exception) {
            throw new PlanException("addon.plan.unreadable", exception);
        }
    }
}
```

### 8. An addon source with a checked exception class of the addon

A and B, identical code:

```java
public final class CheckedAddonSource implements PlanSource {

    public static final class AddonException extends Exception {

        public AddonException(String message) {
            super(message);
        }
    }

    @Override
    public Plan loadPlan() throws AddonException {
        throw new AddonException("addon.plan.missing");
    }
}
```

A and B: `error: loadPlan() in CheckedAddonSource cannot implement loadPlan() in PlanSource` and
`overridden method does not throw AddonException`.

### 8b. An addon subclass with a checked exception class of the addon

A and B, identical code:

```java
public final class CheckedAddonReader extends PlanReader {

    public static final class AddonException extends Exception {

        public AddonException(String message) {
            super(message);
        }
    }

    @Override
    public Plan read(Path planPath) throws AddonException {
        throw new AddonException("addon.plan.missing");
    }
}
```

A and B: `error: read(Path) in CheckedAddonReader cannot override read(Path) in PlanReader` and
`overridden method does not throw AddonException`.

### 8c. The addon exception class that compiles

A:

```java
public final class AddonSource implements PlanSource {

    public static final class AddonException extends RuntimeException {

        public AddonException(String message) {
            super(message);
        }
    }

    @Override
    public Plan loadPlan() {
        throw new AddonException("addon.plan.missing");
    }
}
```

B:

```java
public final class AddonSource implements PlanSource {

    public static final class AddonException extends PlanException {

        public AddonException(String message) {
            super(message, null);
        }
    }

    @Override
    public Plan loadPlan() throws AddonException {
        throw new AddonException("addon.plan.missing");
    }
}
```

### 9. An addon source that never fails, called through the addon class

A and B, identical code:

```java
public final class FixedSource implements PlanSource {

    @Override
    public Plan loadPlan() {
        return new Plan("fixed", 4);
    }

    public static int fixedCount() {
        return new FixedSource().loadPlan()
            .machineCount();
    }
}
```

### 10. A call through your interface type

A:

```java
public static int anyCount(PlanSource source) {
    return source.loadPlan()
        .machineCount();
}
```

B:

```java
public static int anyCount(PlanSource source) {
    try {
        return source.loadPlan()
            .machineCount();
    } catch (PlanException exception) {
        return 0;
    }
}
```

B without the `try`: `error: unreported exception PlanException; must be caught or declared to be thrown`. The other form in B is
`anyCount(PlanSource source) throws PlanException`, which moves the `try` to the next caller.

### 11. A test

A and B, identical code:

```java
@Test
void missingPlanIsRejected() {
    assertThrows(PlanException.class, () -> new PlanReader().read(Path.of("missing.txt")));
}
```

JUnit 5's `Executable.execute()` has `throws Throwable` in its signature, so B compiles with no
`try` in the lambda.

## Boilerplate count

The six call sites of `PlanTerminal` (1 to 6) are 26 lines in A and 42 lines in B. The
difference is the `try` blocks in 2, 3 and 4, and the loop in 6.

- In 3, without the same `try`, a malformed NBT value in A drops the tile entity. In B, javac
  requires that `try`.
- In 8, 8b, 9 and 11, the code is identical. In 7, B has one more `throws` clause.
- In 10, B adds a `try` or a `throws` clause at every call through the interface type.

## Summary

| call site | A, unchecked | B, checked |
|---|---|---|
| `@Mod.EventHandler`, `@SubscribeEvent` | compiles | a `throws` clause on the handler |
| lambda for a JDK functional interface (`supplyAsync`, `map`) | compiles | a `try` that rethrows unchecked, or a loop |
| Minecraft or Forge override (`readFromNBT`, `onMessage`) | compiles. An escaped exception drops the tile entity, or reaches netty | a `try` in the override |
| addon implementation of your API | wraps a checked `IOException`. An exception class in the addon must be unchecked | wraps a checked `IOException`. An exception class in the addon must extend `PlanException` |
| addon call through your interface type | compiles | a `try` or a `throws` clause |
| JUnit `assertThrows` | compiles | compiles |
