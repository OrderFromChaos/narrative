package fixtures.nar115;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** Fixture for NAR115: a java.io.File operation. */
public final class Clean {

    public static void remove(Path planPath) throws IOException {
        Files.delete(planPath);
    }
}
