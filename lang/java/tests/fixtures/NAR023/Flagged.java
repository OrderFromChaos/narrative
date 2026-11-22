package fixtures.nar023;

/** Fixture for NAR023: a javadoc on a method of one line. */
public final class Flagged {

    private final int span;

    public Flagged(int span) {
        this.span = span;
    }

    /** Return the span. */
    public int getSpan() {
        return span;
    }
}
