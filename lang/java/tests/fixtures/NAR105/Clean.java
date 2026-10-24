package fixtures.nar105;

import net.minecraft.nbt.NBTTagCompound;

/** Fixture for NAR105: ordinal() written to NBT. */
public final class Clean {

    public static void save(NBTTagCompound compound, Size size) {
        compound.setString("size", size.name());
    }

    /** The size of a plan. */
    public enum Size {
        SMALL,
        LARGE
    }
}
