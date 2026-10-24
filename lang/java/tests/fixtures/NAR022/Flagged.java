package fixtures.nar022;

/** Fixture for NAR022: "it" or "its" after two or more singular nouns. */
public final class Flagged {

    /** The pump extends the machine base, and it runs once per tick. */
    public static final int PUMP = 1;

    /** {@link Flagged#size} reads the tank, and returns its capacity. */
    public static final int TANK = 2;

    public static int size() {
        return PUMP + TANK;
    }
}
