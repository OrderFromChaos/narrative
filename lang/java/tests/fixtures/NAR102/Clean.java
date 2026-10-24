package fixtures.nar102;

/** Fixture for NAR102: two null arguments. */
public final class Clean {

    public static String label() {
        return join("", ":", "plan");
    }

    private static String join(String prefix, String separator, String name) {
        return prefix + separator + name;
    }
}
