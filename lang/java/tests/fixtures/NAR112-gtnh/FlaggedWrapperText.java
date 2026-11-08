package fixtures.nar112;

/** Fixture for NAR112-gtnh: + after a call of a localization wrapper. */
public final class FlaggedWrapperText {

    private FlaggedWrapperText() {}

    public static String machines(int count) {
        return Clean.translate("plan.machines") + count;
    }
}
