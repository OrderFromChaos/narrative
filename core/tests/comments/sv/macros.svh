// Macros with SystemVerilog macro strings.
`define STR(x) `"x // inside the macro string`" // after the macro string
`define QUOTED(x,y) `"x: `\`"y // inside`\`"`" // after the escaped quotes
`define ESC `\`" // after a lone escaped quote
`define PASTE(a, b) a``b // after a token paste
`define LONG(x) \
  `"x // part one \
  part two`" \
  // a comment line in the body \
  + 1
`define DEFAULT(a = "x//y", b = 2) a + b // a default argument
class c;
  `STR(hello) // a macro call
  `define INNER(v) `"v: /* not a comment */`"
endclass
