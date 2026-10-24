package fixtures.nar103;

import java.util.List;

/** Fixture for NAR103: a stream inside a stream lambda. */
public final class Clean {

    public static List<Integer> sizes(List<List<String>> groups) {
        return groups.stream()
            .map(List::size)
            .toList();
    }
}
