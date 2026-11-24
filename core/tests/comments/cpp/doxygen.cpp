/*!
 * \file doxygen.cpp
 * \author A. Writer
 * \date 2026-11-15
 * \copyright MIT
 *
 * Doxygen comments in a C++ file.
 */

#include <stdexcept>
#include <vector>

/// \defgroup grid Grid helpers
/// @{

//! The cells of a grid, row by row.
//! A second line of the same brief.
using Cells = std::vector<int>;

/**
 * \brief Read one cell.
 *
 * Reads the cell at \p row and \p column of \c cells. See \ref Grid::at "the checked accessor" and
 * \link Grid the grid class \endlink. A <tt>std::vector<int></tt> is \e not copied.
 *
 * \tparam T the type of the index
 * \param[in] cells the cells
 * \param[in,out] row the row, then the next row
 * @param column - the column
 * \returns the cell, or \f$-1\f$ when the point is outside
 * \throws std::out_of_range when \p row is negative
 * \exception std::bad_alloc never
 * \pre \p cells is not empty.
 * \warning The call is not thread-safe.
 * \deprecated Use Grid::at() instead.
 * \sa Grid::at, Grid::set
 * \since 2.1
 *
 * Usage:
 * \code{.cpp}
 * int cell = readCell(cells, row, 2); // a comment in the sample
 * \endcode
 * \verbatim
 * cells: 1 2 3
 * \endverbatim
 * The steps:
 * -# check \p row
 * -# read the cell
 * \li the first item
 * \arg the second item
 * - a Markdown item
 *
 * \par Complexity
 * Constant time.
 * \note Escapes such as \\c, \@ref and \& are text. The \n command ends a line.
 */
template <typename T>
int readCell(const Cells &cells, T &row, int column);

struct Grid {
    int at(int row, int column) const; ///< Return the cell, or throw.
    int width = 0;  /**< The number of columns. */
    int height = 0; //!< The number of rows.
    /*!< A trailing doc comment alone on its line. */
};

/// @}

/**
 * \internal
 * \cond DETAIL
 * The area of a grid of \p width by \p height cells:
 * \f[
 *   A = w \cdot h
 * \f]
 * <pre>
 * area(2, 3) == 6
 * </pre>
 * ```
 * int a = area(2, 3);
 * ```
 * \param width,height the size, in cells
 * @copydoc readCell
 * \endcond
 */
int area(int width, int height);

/** */
///
/// A paragraph after an empty doc line.

/** @{ */
/** @} */

/******************************************************************************
 * A banner of stars around a plain block comment.
 ******************************************************************************/

/////////////////////////////////////////////////////////////////////////////////
/// A doc comment under a divider of slashes.
/////////////////////////////////////////////////////////////////////////////////
