package fixtures.nar142;

/** Fixture for NAR142: a catch of Throwable. */
public final class FlaggedThrowable {

    public static boolean present(String className) {
        try {
            Class.forName(className);
            return true;
        } catch (Throwable throwable) {
            return false;
        }
    }
}
