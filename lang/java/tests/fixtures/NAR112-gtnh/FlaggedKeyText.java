package fixtures.nar112;

import net.minecraft.util.StatCollector;

/** Fixture for NAR112-gtnh: text in a key argument, after a literal prefix. */
public final class FlaggedKeyText {

    private FlaggedKeyText() {}

    public static String mode(String mode) {
        return StatCollector.translateToLocal("chat.mode." + mode + " enabled");
    }
}
