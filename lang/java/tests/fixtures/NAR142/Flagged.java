package fixtures.nar142;

/** Fixture for NAR142: a catch of Exception. */
public final class Flagged {

    public static int parse(String text) {
        try {
            return Integer.parseInt(text);
        } catch (Exception exception) {
            return 0;
        }
    }
}
