package fixtures.review;

/** Keys of the depot timetable. */
public final class Keys {

    /**
     * {@link #lang} and {@link #translate} take the last part of a key.
     *
     * <p>{@code Route} reads the depot of a key. {@code "/"} splits a key. {@linkplain Keys The timetable class} reads
     * a key. A parser reads the depot of a key.
     */
    public static String lang(String key) {
        return key;
    }

    /** Returns the key unchanged. */
    public static String translate(String key) {
        return key;
    }
}
