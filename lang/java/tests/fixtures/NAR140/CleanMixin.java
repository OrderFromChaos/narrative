package fixtures.nar140;

import java.util.ArrayList;
import java.util.HashMap;
import net.minecraft.util.StatCollector;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;

/** Fixture for NAR140: concrete collections in the @Shadow members of a Mixin class. */
@Mixin(StatCollector.class)
public abstract class CleanMixin {

    @Shadow
    protected HashMap<String, String> translations;

    @Shadow
    protected abstract ArrayList<String> keys();
}
