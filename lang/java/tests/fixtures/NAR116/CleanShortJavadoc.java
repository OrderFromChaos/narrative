package fixtures.nar116;

/** Fixture for NAR116: a short method with a javadoc is an entry of the review list. */
public final class CleanShortJavadoc {

    private CleanShortJavadoc() {}

    /** Return the tier of a casing, from 1 to 8. */
    public static int tier(int meta) {
        final int tier = meta + 1;
        return Math.min(tier, 8);
    }
}
