## Concurrency

**Run file I/O, a solve, or other work that takes a noticeable time on a worker thread, and pass the
result back to the client thread. The client thread never waits for that work.** World and GUI state
change only on the thread that uses them. (J1-P31b)

```java
CompletableFuture.supplyAsync(() -> computePlan(request))
    .thenAccept(plan -> Minecraft.getMinecraft().func_152344_a(() -> showPlan(plan)));
```

`func_152344_a` is the SRG name of the 1.7.10 method that queues a task for the client thread.

