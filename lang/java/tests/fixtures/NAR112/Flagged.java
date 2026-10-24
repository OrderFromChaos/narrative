package fixtures.nar112;

import net.minecraft.util.StatCollector;

/** Fixture for NAR112: + in user-facing text. */
public final class Flagged {

    public static String machines(int count) {
        return StatCollector.translateToLocal("plan.machines") + count;
    }
}
