package fixtures.nar110;

/** Fixture for NAR110: a mutable static field. */
public final class Flagged {

    private static int loads;

    public static void countLoad() {
        loads++;
    }
}
