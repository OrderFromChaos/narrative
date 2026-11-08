package fixtures.java8.nar107;

/** Fixture for NAR107 on Java 8: a default arm in a switch statement over an enum. */
public final class Flagged {

    public static int weight(Size size) {
        switch (size) {
            case SMALL:
                return 1;
            default:
                return 2;
        }
    }

    /** The size of a plan. */
    public enum Size {
        SMALL,
        LARGE
    }
}
