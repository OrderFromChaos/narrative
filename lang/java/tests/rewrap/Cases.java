package rewrap;

/** Cases for javachecks.py --rewrap, with one rule of the re-wrap in each javadoc or comment. */
public final class Cases {

    /**
     * A ragged paragraph is filled again to the width of its widest line, which is this one here.
     * The product is
     * a
     * float.
     */
    public static final int RAGGED = 1;

    /**
     * After a line that ends a sentence, the line break stays.
     * The next
     * sentence is filled again to the width of the widest line of this paragraph, which is this line.
     */
    public static final int SENTENCE_BREAK = 2;

    /**
     * An inline tag is one word for the re-wrap, so a tag that does not fit on the line above stays whole on
     * the
     * next line: {@link Cases#method(int, int)}.
     */
    public static final int INLINE_TAG = 3;

    /**
     * A paragraph wrapped by hand at a shorter width is left as it is, because each next word
     * is too long for the space left on the line above it, so nothing here gets re-wrapped.
     *
     * <pre>
     *     short
     *     sample
     * </pre>
     */
    public static final int HAND_WRAPPED = 4;

    /**
     * Fill the plan.
     *
     * @param first the first value, read from the plan file, which must exist on disk before the call is made
     *     by the
     *     caller
     * @return the second value
     */
    public static int method(int first, int second) {
        // a whole-line comment over the limit is split onto more comment lines, and the words of the comment stay the same in every line
        return first + second; // a trailing comment over the limit stays on its line, because the line has code before the comment
    }
}
