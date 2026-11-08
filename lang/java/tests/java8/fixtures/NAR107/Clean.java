package fixtures.java8.nar107;

/** Fixture for NAR107 on Java 8: every constant listed, and a throw after the switch. */
public final class Clean {

    public static int weight(Size size) {
        switch (size) {
            case SMALL:
                return 1;
            case LARGE:
                return 2;
        }
        throw new IllegalArgumentException("unknown size " + size);
    }

    /** The size of a plan. */
    public enum Size {
        SMALL,
        LARGE
    }
}
