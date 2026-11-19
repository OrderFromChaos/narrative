package fixtures.nar131;

import net.minecraft.util.StatCollector;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Fixture for NAR131: an injector method with more than 3 parameters. */
@Mixin(StatCollector.class)
public final class CleanMixin {

    /** Count each lookup of a formatted translation. */
    @Inject(method = "translateToLocalFormatted")
    private void countLookup(String key, Object[] values, int first, CallbackInfo callback) {}
}
