package fixtures.nar105;

import net.minecraft.nbt.NBTTagCompound;

/** Fixture for NAR105: ordinal() written to NBT. */
public final class Flagged {

    public static void save(NBTTagCompound compound, Size size) {
        compound.setInteger("size", size.ordinal());
    }

    /** The size of a plan. */
    public enum Size {
        SMALL,
        LARGE
    }
}
