package fixtures.nar103;

import java.util.List;

/** Fixture for NAR103: a stream inside a stream lambda. */
public final class Flagged {

    public static List<Long> nonEmptyCounts(List<List<String>> groups) {
        return groups.stream()
            .map(group -> group.stream()
                .filter(name -> !name.isEmpty())
                .count())
            .toList();
    }
}
