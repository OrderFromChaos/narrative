package fixtures.nar123;

/** Fixture for NAR123: && inside || without parentheses. */
public final class Flagged {

    public static boolean ready(boolean loaded, boolean valid, boolean forced) {
        return loaded && valid || forced;
    }
}
