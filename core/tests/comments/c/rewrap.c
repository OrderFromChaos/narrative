/**
 * \file rewrap.c
 * Paragraphs of comments
 * with short lines.
 */

// The first paragraph of a run of line comments,
// broken after a few words on each line, which the re-wrap fills up to column 120 with no word changed.
//
// The second paragraph
// starts after a blank comment line.
// NOLINTNEXTLINE(misc-unused)
// A pragma ends the paragraph above it.
static int unused;

/*
 * A block comment with a star margin,
 * broken short.
 *
 * - the first item of a list,
 *   which hangs under the text of the item
 * - the second item
 */
int block;

/**
 * Count the cells
 * of a grid.
 *
 * \param grid the cells,
 * row by row
 * \param count the number
 * of cells
 * \code
 * int n = count(grid,
 *               4);
 * \endcode
 * \return the count
 */
int count(const int *grid, int count);

int trailing; // a trailing comment is never re-wrapped, even when it is long enough that its words would fill another line
// a line comment continued by a backslash \
is never re-wrapped
int after;
