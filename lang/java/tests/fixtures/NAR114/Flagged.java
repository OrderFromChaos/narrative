package fixtures.nar114;

import java.util.ArrayList;
import java.util.List;

/** Fixture for NAR114: an allocation in a draw method. */
public final class Flagged {

    public static int drawLabels(List<String> names) {
        final List<String> visible = new ArrayList<>(names);
        return visible.size();
    }
}
