package fixtures.nar112;

/** Fixture for NAR112-gtnh: a lang key with no literal prefix. */
public final class FlaggedWrapperKey {

    private FlaggedWrapperKey() {}

    public static String option(String name) {
        return Clean.translate(name + ".enable");
    }
}
