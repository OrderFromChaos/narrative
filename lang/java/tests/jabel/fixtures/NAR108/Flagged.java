package fixtures.jabel.nar108;

import com.github.bsideup.jabel.Desugar;

/** Fixture for NAR108 under jabel: an array component in a record. */
@Desugar
public record Flagged(int[] counts) {}
