#include <stdio.h> // stdio for puts
#include "local//name.h" // a quoted header name is a string

static const char *slashes = "a // b"; // after a string with slashes
static const char quote = '"'; // after a double quote in a character literal
static const char apostrophe = '\''; // after an escaped apostrophe
static const char *backslash = "\\"; // after an escaped backslash
static const char *opener = "/* not a comment */"; // after a string with a block opener
static const char *escaped = "\"// still a string"; // after an escaped double quote
static const char *spliced = "first half \
// second half of the string";
int after_splice; // after a string with a line splice

static const int wide = L'x'; // after a wide character
static const int utf16 = u'x'; // after a UTF-16 character
static const int utf32 = U'x'; // after a UTF-32 character
static const unsigned char utf8 = u8'x'; // after a UTF-8 character
static const char *prefixed = u8"/* x */"; // after a UTF-8 string
static const char multi[] = "ab" "//cd"; // after two adjacent strings

static const unsigned million = 1'000'000; // C23 digit separators
static const unsigned mask = 0x1'FF; // a separator in a hex number
static const unsigned bits = 0b1010'1010; // a separator in a binary number
static const double scaled = 1.5e+1'0; // a separator after an exponent sign
static const double fraction = .2'5; // a number that starts with a point
static const int digit_then_char = 1 + 'a'; // a character after a number

/* a // b inside a block comment */
/* /* a block comment does not nest */
int not_nested; /* the line comment opener //* is inside */
int division = 8 / 2 / 2; // division is not a comment
int star_after = 8 /*/ a comment that opens with a slash and star */ / 2;
int no_space = 1//**/2
;

// a line comment \
continued by a backslash at the end of the line
int after_continued;

#if 0
This group isn't compiled. // the apostrophe of isn't opens a character literal up to here
/* but a block comment in the group is a comment */
#endif

/**/
/******/
/****/

#define RAW_IN_C R"x(a")x" // C has no raw strings, so a string opens at the second quote and runs up to here
#define AFTER_RAW_IN_C 1 // after the macro with the quotes
