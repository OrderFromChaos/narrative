package fixtures.nar117;

/** Fixture for NAR117: a short method with a javadoc and a thrown exception without a @throws line. */
public final class FlaggedShort {

    private FlaggedShort() {}

    /** Return the tier of a casing, from 1 to 8. */
    public static int tier(int meta) {
        if (meta < 0 || meta > 7) {
            throw new IllegalArgumentException("bad casing meta " + meta + " (expected 0 to 7)");
        }
        return meta + 1;
    }
}
