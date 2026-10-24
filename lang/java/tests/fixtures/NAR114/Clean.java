package fixtures.nar114;

import java.util.ArrayList;
import java.util.List;

/** Fixture for NAR114: an allocation in a draw method. */
public final class Clean {

    private final List<String> visible = new ArrayList<>();

    public int drawLabels(List<String> names) {
        visible.clear();
        visible.addAll(names);
        return visible.size();
    }
}
