package fixtures.nar120;

import java.util.List;

/** Fixture for NAR120: a return contract in a comment. */
public final class Flagged {

    public static int total(List<Integer> counts) {
        // returns 0 for an empty list
        int total = 0;
        for (final int count : counts) {
            total += count;
        }
        return total;
    }
}
