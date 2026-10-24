package fixtures.nar021;

/** Fixture for NAR021: a clause joined by as or where. */
public final class Clean {

    /** The count is the same as the cache size. */
    public static final int COUNT = 1;

    /** A unit such as a tick or a second. */
    public static final int UNIT = 2;

    /** Stored as a float. Check each line as you write it. */
    public static final int STORED = 3;

    public static int size() {
        return COUNT + UNIT + STORED;
    }
}
