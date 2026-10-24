package fixtures.nar141;

/** Fixture for NAR141: a field that could be final. */
public final class Clean {

    private final int size;

    public Clean(int size) {
        this.size = size;
    }

    public int size() {
        return size;
    }
}
