// This run of line comments is broken early, and the re-wrap fills each paragraph up to column 120 without changing a
// word of the text, so the second line ends earlier.
//
// A list after a blank comment line:
// - the first item of the list, which is long enough that the re-wrap has to break it before the last column of the
//   line
// - the second item
const a = 1; // a trailing comment is never re-wrapped,
// eslint-disable-next-line no-unused-vars
const b = 2;

/**
 * Read a plan file. This description is broken early too.
 *
 * @param {string} path - Where the plan file is.
 * @returns {Promise<Plan>} The plan.
 * @example
 * // a sample is never
 * // re-wrapped
 * readPlan('a.json');
 */
function readPlan(path) {
  return [path, a, b];
}

/*
 * A block comment over several lines.
 */
readPlan('b.json');
