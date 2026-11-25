package fixtures.nar105;

import net.minecraft.nbt.NBTTagCompound;

/** Fixture for NAR105: ordinal() written to NBT. */
public final class Flagged {

    public static void save(NBTTagCompound compound, Size size) {
        compound.setInteger("size", size.ordinal());
    }

    /** Each plan has one size. */
    public enum Size {
        SMALL,
        LARGE
    }
}
