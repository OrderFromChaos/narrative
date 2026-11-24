`timescale 1ns/1ps // one nanosecond units
`include "lib//common.vh" // the shared header
`include "lib/*glob*/x.vh"

// The adder of the test bench.
// A second line of the same block.
module adder (input [7:0] a, input [7:0] b, output [8:0] sum);
  // strings
  initial $display("// not a comment /* nor this */");
  initial $display("quote \" // still in the string");
  initial $display("backslash \\"); // a comment after an escaped backslash
  initial $display("a %0d", 10/2); // integer division

  // escaped identifiers end at whitespace
  wire \bus//a ;
  wire \a/*b ; // after the escaped identifier
  wire \q"uote ; // a quote inside an escaped identifier
  wire \tick'x ; // an apostrophe inside an escaped identifier

  // based and sized literals
  assign sum = a + b + 8'hFF - 4'b10_10 + 'h3 + 'o7; // it's "quoted" in a comment
  wire [3:0] z = 4'bz0x1; // a sized literal with z and x

  // attributes
  (* full_case, parallel_case *)
  always @(*) begin
  end
  always @(* ) begin end // a space before the parenthesis
  always @ (*) begin end
  (* keep = "true" *) reg r; /* after an attribute */

  /* a block comment
     over two lines // with a slash pair inside */
  /* not /* nested */ wire after_unnested;
  // a line comment with /* an opener
  wire also_code; // and */ a closer
  assign r = a /b; // a division then a comment
endmodule
