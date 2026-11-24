#pragma pack(push, 1) // pack the structs below with no padding
#include "vendor//config.h" // a quoted header name is a string
#define SQUARE(x) ((x) * (x)) /* a block comment after a macro */
#define LONG_MACRO(a, b) \
    ((a) + /* inside the macro */ \
     (b)) // after the macro

#if 0
// A line comment in a group that is not compiled.
/* A block comment
   in a group that is not compiled. */
int disabled = "unterminated // not a comment, since the string runs to the end of the line;
Don't read this. // not a comment, since the apostrophe opens a character literal
#endif

#ifdef NEVER_DEFINED /* a block comment after a directive */
#error "a // in an error message is in a string"
#error don't build this // not a comment, since the apostrophe opens a character literal
#endif // NEVER_DEFINED

// a line comment that ends in a backslash continues \
on the next line, \
and the line after
int after_splices;
#pragma pack(pop)
