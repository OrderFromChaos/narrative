package fixtures.nar102;

/** Fixture for NAR102: two null arguments. */
public final class Flagged {

    public static String label() {
        return join(null, null, "plan");
    }

    private static String join(String prefix, String separator, String name) {
        return name;
    }
}
