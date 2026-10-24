## Javadoc

**Every top-level type has a javadoc of at least one sentence, about what the type is for.** A reader
meets it first, so it is about what the class is *for*, not how the class works. The javadoc of a
class with `main`, such as a dev tool, also has a usage example and the exit codes. `NAR118` flags a
top-level type with no javadoc. (J1-F3, R5-02)

**Write for a professional developer who has the file open.** That reader knows Java, Forge and the
vocabulary of the trade, so `API`, `idempotent` and `NBT` are the right words. One idea per
sentence. **One word for one thing, and the word is the identifier the code uses.** (R9-09)

The prose rules for comments and javadoc are in **Comments**.

