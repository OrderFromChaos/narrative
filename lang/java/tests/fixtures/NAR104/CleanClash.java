package fixtures.nar104;

import java.util.List;

/** Fixture for NAR104: two types of one simple name, one imported and one qualified. */
public final class CleanClash {

    public static int count(List<String> names, java.awt.List widget) {
        return names.size() + widget.getItemCount();
    }
}
