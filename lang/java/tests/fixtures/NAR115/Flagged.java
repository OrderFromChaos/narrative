package fixtures.nar115;

import java.io.File;

/** Fixture for NAR115: a java.io.File operation. */
public final class Flagged {

    public static boolean remove(File planFile) {
        return planFile.delete();
    }
}
