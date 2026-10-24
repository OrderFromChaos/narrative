package fixtures.nar111;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/** Fixture for NAR111: a log message built with +. */
public final class Clean {

    private static final Logger LOG = LogManager.getLogger("fixtures");

    public static void report(int rejected) {
        LOG.warn("merge.rejected rejected={}", rejected);
    }
}
