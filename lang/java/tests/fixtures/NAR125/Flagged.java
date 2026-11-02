package fixtures.nar125;

/** Fixture for NAR125: a comment paragraph not filled up to column 120. */
public final class Flagged {

    /**
     * The product is
     * a float, and the result is truncated to whole parallels before the recipe time is computed.
     */
    public static final int PRODUCT = 1;

    public static int size() {
        return PRODUCT;
    }
}
