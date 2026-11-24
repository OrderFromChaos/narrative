// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 A. Writer
// <grid> -*- C++ -*-

#include <cstdio> // IWYU pragma: keep
#include <cstdlib> // IWYU pragma: no_include <stdlib.h>

// clang-format off
static const int table[] = {
    1, 0,
    0, 1,
};
// clang-format on

int pick(int value) {
    switch (value) {
    case 0:
        value = 1;
        [[fallthrough]];
    case 1:
        value += 1;
        // FALLTHROUGH
    case 2:
        value += 2;
        /* falls through. */
    case 3:
        value += 3;
        // Fall through to the default case when the value is three.
    default:
        break;
    }
    // NOLINTNEXTLINE(cppcoreguidelines-pro-bounds-constant-array-index)
    return table[value]; // NOLINT
}

// NOLINTBEGIN(bugprone-*)
// LCOV_EXCL_START
int untested() { return 0; } // LCOV_EXCL_LINE
// LCOV_EXCL_STOP
// NOLINTEND(bugprone-*)
// cppcheck-suppress unusedFunction
int unused() { return 0; } // NOSONAR
// GCOVR_EXCL_START
// A prose line after a pragma starts a passage of its own.
// GCOVR_EXCL_STOP
