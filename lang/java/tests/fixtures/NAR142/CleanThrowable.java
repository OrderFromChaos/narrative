package fixtures.nar142;

/** Fixture for NAR142: a catch of Throwable. */
public final class CleanThrowable {

    public static boolean present(String className) {
        try {
            Class.forName(className);
            return true;
        } catch (ClassNotFoundException | NoClassDefFoundError missing) {
            return false;
        }
    }
}
