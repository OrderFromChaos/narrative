package fixtures.jabel.nar108;

import java.util.List;

import com.github.bsideup.jabel.Desugar;

/** Fixture for NAR108 under jabel: a list component in a record. */
@Desugar
public record Clean(List<Integer> counts) {}
