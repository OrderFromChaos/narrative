package fixtures.nar107;

/** Fixture for NAR107: a default arm over a sealed type. */
public final class FlaggedSealed {

    public static int corners(Shape shape) {
        return switch (shape) {
            case Square square -> 4;
            default -> 0;
        };
    }

    /** {@code Square} and {@code Circle} are the shapes of the canvas. */
    public sealed interface Shape permits Square, Circle {}

    /** Each {@code Square} has a side length. */
    public record Square(int side) implements Shape {}

    /** Each {@code Circle} has a radius. */
    public record Circle(int radius) implements Shape {}
}
