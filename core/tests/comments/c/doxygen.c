/**
 * \file doxygen.c
 * \brief Doxygen comments in a C file.
 *
 * The rest of the description of the file.
 */

#include <stddef.h>

/** A point on the grid, in cells. */
struct point {
    int x; /**< The column, from the left edge. */
    int y; /**< The row, from the top edge. */
};

/*! The kinds of cell. */
enum cell {
    CELL_EMPTY, //!< A cell with nothing in it.
    CELL_WALL,  ///< A cell that blocks movement.
    CELL_DOOR   /*!< A cell that blocks movement when closed. */
};

/**
 * @brief Count the walls around a point.
 *
 * @param[in] grid the cells, row by row
 * @param[in] width the number of columns of @p grid
 * @param at the point
 * @return the number of walls among the eight neighbours of @p at
 * @retval 0 when @p at is outside the grid
 * @see neighbours
 */
size_t count_walls(const enum cell *grid, size_t width, struct point at);

/// Reset every cell of \p grid to \c CELL_EMPTY.
///
/// \param grid the cells
/// \param count the number of cells
/// \note The call writes \a count cells,
///       starting at the first.
void clear_grid(enum cell *grid, size_t count);

/* A plain block comment with a @param tag. The tag is prose here. */
// A plain line comment with \c markup, which is prose here too.
