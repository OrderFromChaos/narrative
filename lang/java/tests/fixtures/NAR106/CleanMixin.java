package fixtures.nar106;

import net.minecraft.util.StatCollector;
import org.spongepowered.asm.mixin.Mixin;

/** Fixture for NAR106: an abstract Mixin class. */
@Mixin(StatCollector.class)
public abstract class CleanMixin {

    public abstract int size();
}
