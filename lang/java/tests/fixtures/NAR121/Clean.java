package fixtures.nar121;

import java.util.ArrayList;
import java.util.List;

/** Fixture for NAR121: a raw type. */
public final class Clean {

    public static int size() {
        final List<String> names = new ArrayList<>();
        names.add("plan");
        return names.size();
    }
}
