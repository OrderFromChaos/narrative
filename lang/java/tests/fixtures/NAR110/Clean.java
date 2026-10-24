package fixtures.nar110;

/** Fixture for NAR110: a mutable static field. */
public final class Clean {

    // one count per client process, for the debug overlay
    private static int loads;

    public static void countLoad() {
        loads++;
    }
}
