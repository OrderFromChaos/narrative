// gcc -fpreprocessed reads a // in a header name as a comment, so run_comments.py has no oracle for this suffix
#include <sys//types.h> // after a header name with two slashes
#  include <sys/*x*/types.h> // after a header name with a block opener
#if __has_include(<sys//stat.h>) // after a header name in __has_include
#include_next <bits//wordsize.h> // after a header name in include_next
#endif
#define HEADER <sys//time.h> // after a macro whose text is not a header name
#define LESS(a, b) ((a) < (b)) // after a less-than sign
%:include <sys//socket.h> // after a header name in a directive that opens with the digraph of #
