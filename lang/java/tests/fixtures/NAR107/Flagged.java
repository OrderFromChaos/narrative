package fixtures.nar107;

/** Fixture for NAR107: a default arm over an enum. */
public final class Flagged {

    public static int weight(Size size) {
        return switch (size) {
            case SMALL -> 1;
            default -> 2;
        };
    }

    /** The size of a plan. */
    public enum Size {
        SMALL,
        LARGE
    }
}
