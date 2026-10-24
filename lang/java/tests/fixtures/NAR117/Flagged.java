package fixtures.nar117;

import java.util.List;

/** Fixture for NAR117: a thrown exception with no @throws line. */
    public final class Flagged {

        /** Add the first 20 values. */
        public static int total(List<Integer> values) {
            if (values.size() < 20) {
                throw new IllegalArgumentException("fewer than 20 values (expected 20 or more)");
            }
            int total = 0;
        total += values.get(0);
total += values.get(1);
total += values.get(2);
total += values.get(3);
total += values.get(4);
total += values.get(5);
total += values.get(6);
total += values.get(7);
total += values.get(8);
total += values.get(9);
total += values.get(10);
total += values.get(11);
total += values.get(12);
total += values.get(13);
total += values.get(14);
total += values.get(15);
total += values.get(16);
total += values.get(17);
total += values.get(18);
total += values.get(19);

            return total;
        }
    }
