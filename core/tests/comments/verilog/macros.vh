`ifndef MACROS_VH
`define MACROS_VH

`define WIDTH 8 // the width of a word

// a macro over three lines, with comments in the body
`define CLAMP(x, hi) \
  // the larger value wins \
  ((x) > (hi) ? (hi) : (x)) \
  // a second comment line

`define MSG(text) $display("MSG // %s", text) // a trailing comment of the macro

`define BLOCK(x) \
  /* the first line of a block comment \
     the second line */ \
  (x)

`define PATH "a//b" // a string in the macro text

`define EMPTY // nothing in the macro text

`endif // MACROS_VH
