package fixtures.nar021;

/** Fixture for NAR021: a clause joined by as or where. */
public final class Flagged {

    /** The product is a float, as in the parser. */
    public static final int PRODUCT = 1;

    /** As the parser. */
    public static final int MODE = 2;

    /** The runs of a recipe, as {@link Flagged#size} works them out. */
    public static final int RUN = 3;

    /** The values of this kind, where the spec has no range. */
    public static final int RANGE = 4;

    public static int size() {
        return PRODUCT + MODE + RUN + RANGE;
    }
}
