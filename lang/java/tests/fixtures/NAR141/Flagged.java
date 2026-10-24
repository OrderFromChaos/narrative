package fixtures.nar141;

/** Fixture for NAR141: a field that could be final. */
public final class Flagged {

    private int size;

    public Flagged(int size) {
        this.size = size;
    }

    public int size() {
        return size;
    }
}
