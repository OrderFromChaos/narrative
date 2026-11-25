package fixtures.nar029;

/** Fixture for NAR029: each sentence has a verb, and the label on a field stays. */
public final class Clean {

    /** The depot of the route, such as north. */
    private final String depot = "north";

    /**
     * Returns the late trips of one route, in timetable order.
     *
     * @param route the number of the route
     * @return the count of late trips
     */
    public int lateTrips(int route) {
        // trips logged before 2025/04/03 lack the depot field
        final int base = route * 2;
        // sort by depot, then by route
        return base + depot.length();
    }
}
