package fixtures.nar125;

/** Fixture for NAR125: a ragged javadoc line. */
public final class Clean {

    /**
     * The product is a float, and the result is truncated to whole parallels before the recipe time
     * is computed. A paragraph wrapped by hand at 100 columns passes, because the first word of each
     * next line is too long for the space left on the line above.
     *
     * <ul>
     * <li>first item
     * <li>second item
     * </ul>
     *
     * @return the product
     */
    public static int product() {
        return 1;
    }
}
