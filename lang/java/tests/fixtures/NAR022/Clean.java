package fixtures.nar022;

/** Fixture for NAR022: "it" or "its" after two or more singular nouns. */
public final class Clean {

    /** The pump runs once per tick. It stops when the tank is full. */
    public static final int PUMP = 1;

    /** Read the tank and return its capacity. */
    public static final int TANK = 2;

    /** The reader opens the push flag and clears it. */
    public static final int FLAG = 3;

    public static int size() {
        return PUMP + TANK + FLAG;
    }
}
