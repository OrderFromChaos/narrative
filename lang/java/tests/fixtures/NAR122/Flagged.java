package fixtures.nar122;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Fixture for NAR122: a type with more than 4 names. */
public final class Flagged {

    private final Map<String, List<Map<String, Integer>>> index = new HashMap<>();

    public int size() {
        return index.size();
    }
}
