package fixtures.nar107;

/** Fixture for NAR107: a default arm over a sealed type. */
public final class FlaggedSealed {

    public static int corners(Shape shape) {
        return switch (shape) {
            case Square square -> 4;
            default -> 0;
        };
    }

    /** A shape on the canvas. */
    public sealed interface Shape permits Square, Circle {}

    /** A square shape. */
    public record Square(int side) implements Shape {}

    /** A circle shape. */
    public record Circle(int radius) implements Shape {}
}
