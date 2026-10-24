package fixtures.nar106;

/** Fixture for NAR106: a sealed abstract class with fields that the subclasses share. */
public abstract sealed class CleanSealed permits CleanSealed.Whole, CleanSealed.Wide {

    protected final String name;

    protected CleanSealed(String name) {
        this.name = name;
    }

    /** A kind with an int value. */
    public static final class Whole extends CleanSealed {

        public Whole(String name) {
            super(name);
        }
    }

    /** A kind with a long value. */
    public static final class Wide extends CleanSealed {

        public Wide(String name) {
            super(name);
        }
    }
}
