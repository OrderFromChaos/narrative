package fixtures.nar144;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** Fixture for NAR144: a rethrow that drops the cause. */
public final class Flagged {

    public static String read(Path planPath) {
        try {
            return Files.readString(planPath);
        } catch (IOException exception) {
            throw new IllegalStateException("plan.unreadable path=" + planPath);
        }
    }
}
