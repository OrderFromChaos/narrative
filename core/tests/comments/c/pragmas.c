/* SPDX-License-Identifier: MIT */
/* -*- mode: c; c-basic-offset: 4 -*- */
/* vim: set ts=8 sw=4: */

int sign(int value) {
    switch (value > 0) {
    case 1:
        value = 1;
        /* FALLTHRU */
    case 0:
        value += 0;
        // fall through
    default:
        break;
    }
    if (value < 0) {
        return -1; /* NOTREACHED */
    }
    return value; // NOLINT(readability-else-after-return)
}

// LCOV_EXCL_START
int untested(void) { return 0; }
// LCOV_EXCL_STOP

/* ARGSUSED */
int unused(int a) { return 0; } // cppcheck-suppress unusedFunction

// Fall through to the default case when the count is zero.
// A prose line after the pragma-like line stays prose.
