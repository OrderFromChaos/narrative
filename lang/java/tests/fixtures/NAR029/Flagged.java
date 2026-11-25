package fixtures.nar029;

/** Fixture for NAR029: a sentence without a verb. */
public final class Flagged {

    /**
     * Counts the late trips of one route. In timetable order.
     */
    public int lateTrips(int route) {
        final int base = route * 2;
        return base + 1;
    }
}
