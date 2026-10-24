package fixtures.nar142;

/** Fixture for NAR142: a catch of Exception. */
public final class Clean {

    public static int parse(String text) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException exception) {
            return 0;
        }
    }
}
