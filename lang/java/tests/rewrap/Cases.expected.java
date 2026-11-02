package rewrap;

/** Cases for javachecks.py --rewrap, with one rule of the re-wrap in each javadoc or comment. */
public final class Cases {

    /**
     * A ragged paragraph is filled again up to column 120. The product is a float.
     */
    public static final int RAGGED = 1;

    /**
     * A line that ends a sentence is joined to the next sentence. The next sentence follows on the same line, so the
     * paragraph reads as one text.
     */
    public static final int SENTENCE_BREAK = 2;

    /**
     * An inline tag is one word for the re-wrap, so a tag that does not fit on the line above stays whole on the next
     * line: {@link Cases#method(int, int)}.
     */
    public static final int INLINE_TAG = 3;

    /**
     * A paragraph wrapped by hand at a shorter width is filled again up to column 120, the same as a ragged paragraph.
     *
     * <pre>
     *     short
     *     sample
     * </pre>
     */
    public static final int HAND_WRAPPED = 4;

    /**
     * A line past column 120 is filled again up to column 120 of the line, not 120 columns from the javadoc, so
     * spotless leaves the lines whole. The next line is ragged.
     */
    public static final int PAST_COLUMN_120 = 5;

    /**
     * The line above a list keeps its break, because each list opens a paragraph:
     * <ul>
     * <li>an HTML list item opens a paragraph, and a line of tags alone stays as written
     * </ul>
     * - a list item opens a paragraph, and the next lines of the item hang under the text of the item, past the marker
     *   of the item
     * - the second item
     */
    public static final int LISTS = 6;

    /**
     * Fill the plan.
     *
     * @param first  the first value, read from the plan file, which must exist on disk before the call is made by the
     *               caller
     * @param second the second value, on one line that runs past column 120, so the next lines sit under the
     *               description of the tag
     * @return the second value
     */
    public static int method(int first, int second) {
        // a whole-line comment over the limit is split onto more comment lines, and the words of the comment stay the
        // same in every line
        return first + second; // a trailing comment over the limit stays on its line, because the line has code before the comment
    }

    public static int comments(int first) {
        // a run of whole-line comments at one column is one block. Its lines are filled again as one paragraph.
        //
        // An empty comment line ends a paragraph. A sample under a colon stays as written:
        //     first + 1
        // `first + 2`
        // a line with noqa keeps its words, so the noqa stays on its line // noqa: NAR017
        // and the line below starts a new paragraph.
        return first;
    }
}
