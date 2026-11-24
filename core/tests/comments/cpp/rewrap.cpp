/// \file rewrap.cpp
/// Doc comments with
/// short lines.

namespace grid {

/// Count the walls
/// around a point.
///
/// \param cells the cells,
/// row by row
/// \return the count
/// \code
/// int n = countWalls(cells,
///                    4);
/// \endcode
/// The paragraph after
/// the sample.
int countWalls(const int *cells, int width);

    //! An indented doc comment whose first line is long enough to need a second line once the third line joins, at
    //! column
    //! one hundred and twenty.
    int indented;

/*!
   A doc comment with no star margin,
   broken short.

   - the first step,
     broken short
   - the second step
 */
int steps;

int a; // a trailing comment
int b; // and a trailing comment on the next line are never joined

}  // namespace grid
