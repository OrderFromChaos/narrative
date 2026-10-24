package fixtures.nar140;

import java.util.EnumMap;
import java.util.EnumSet;
import java.util.concurrent.TimeUnit;

/** Fixture for NAR140: an enum map and an enum set keep their types. */
public final class CleanEnumMap {

    public static int size(EnumMap<TimeUnit, String> names, EnumSet<TimeUnit> units) {
        return names.size() + units.size();
    }
}
