package fixtures.nar120;

import java.util.List;

/** Fixture for NAR120: a return contract in a comment. */
public final class Clean {

    public static int total(List<Integer> counts) {
        int total = 0;
        for (final int count : counts) {
            total += count;
        }
        return total;
    }
}
