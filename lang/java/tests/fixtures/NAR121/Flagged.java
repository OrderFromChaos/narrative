package fixtures.nar121;

import java.util.ArrayList;
import java.util.List;

/** Fixture for NAR121: a raw type. */
public final class Flagged {

    @SuppressWarnings("PMD.LooseCoupling")
    public static int size() {
        final List names = new ArrayList();
        names.add("plan");
        return names.size();
    }
}
