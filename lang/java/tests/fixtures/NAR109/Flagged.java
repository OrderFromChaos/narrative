package fixtures.nar109;

/** Fixture for NAR109: an exception class name. */
public final class Flagged extends RuntimeException {

    public Flagged(String message) {
        super(message);
    }
}
