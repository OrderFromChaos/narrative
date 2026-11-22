package fixtures.nar023;

/** Fixture for NAR023: a method of one line without a javadoc, and a javadoc on a method of two statements. */
public final class Clean {

    private final int span;

    public Clean(int span) {
        this.span = span;
    }

    public int getSpan() {
        return span;
    }

    /** The doubled span, at least 1. */
    public int doubledSpan() {
        final int doubled = 2 * span;
        return Math.max(1, doubled);
    }
}
