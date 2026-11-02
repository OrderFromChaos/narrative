package fixtures.nar125;

/** Fixture for NAR125: a comment paragraph not filled up to column 120. */
public final class Clean {

    /**
     * The product is a float, and the result is truncated to whole parallels before the recipe time is computed. A
     * paragraph filled up to column 120 passes, because the first word of each next line does not fit on the line
     * above.
     *
     * <ul>
     * <li>first item
     * <li>second item
     * </ul>
     *
     * @return the product
     */
    public static int product() {
        // a run of whole-line comments filled up to column 120 passes too, because the next word does not fit on the
        // line above
        return 1;
    }
}
