package fixtures.nar130;

import net.minecraft.util.StatCollector;
import org.spongepowered.asm.mixin.Mixin;

/** Fixture for NAR130: members with the modid$ prefix in a Mixin class. */
@Mixin(StatCollector.class)
public final class CleanMixin {

    private final int plannh$count = 1;

    public int plannh$size() {
        return plannh$count;
    }
}
