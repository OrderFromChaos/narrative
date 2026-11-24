// SystemVerilog literals that hold a slash pair.
module top;
  logic [7:0] a = '0; // all zeros
  logic [7:0] b = '1, c = 'x, d = 'z; // fill literals
  int arr [2] = '{1, 2}; // an assignment pattern
  int e = int'(3.7) / 2; // a cast, then a division
  typedef struct packed { logic [3:0] hi, lo; } pair_t;
  pair_t p = '{hi: 4'hA, lo: 4'b0101}; // a named assignment pattern
  string s1 = "// x /* y */";
  string s2 = """a "quoted" word // and a slash pair
  over two lines /* with an opener""" ; // after the triple-quoted string
  string s3 = """escaped \""" // still inside
  """; // after the escaped triple quote
  string s4 = ""; // after an empty string
  string s5 = "\\"; // after an escaped backslash
`include <vendor//pkg.svh>
`include <vendor/*x*/pkg.svh> // after an angle-bracket include
  initial $display("%s", s1); // display
  always_comb begin : blk // a named block
  end
  // a comment with a closing */ in it
  assign a = b ** 2 / c; // power and division
  sequence s; a ##1 b; endsequence // a cycle delay
  always_ff @(posedge clk iff en) a <= a + 1'b1; // an iff qualifier
endmodule
