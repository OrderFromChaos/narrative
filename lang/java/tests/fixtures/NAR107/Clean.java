package fixtures.nar107;

/** Fixture for NAR107: a default arm over an enum. */
public final class Clean {

    public static int weight(Size size) {
        return switch (size) {
            case SMALL -> 1;
            case LARGE -> 2;
        };
    }

    /** The size of a plan. */
    public enum Size {
        SMALL,
        LARGE
    }
}
