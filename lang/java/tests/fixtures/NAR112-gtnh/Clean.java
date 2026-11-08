package fixtures.nar112;

import net.minecraft.util.ChatComponentTranslation;
import net.minecraft.util.StatCollector;

/** Fixture for NAR112-gtnh: + in user-facing text. */
public final class Clean {

    private Clean() {}

    public static String machines(int count) {
        return StatCollector.translateToLocalFormatted("plan.machines", count);
    }

    public static String mode(String mode) {
        return translate("chat.mode." + mode);
    }

    public static String option(String name, String suffix) {
        return StatCollector.translateToLocal("inventory." + name + "." + suffix);
    }

    public static ChatComponentTranslation modeMessage(String mode) {
        return new ChatComponentTranslation("chat.mode." + mode);
    }

    public static String translate(String key, Object... values) {
        return StatCollector.translateToLocalFormatted(key, values);
    }
}
