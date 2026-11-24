// The arbiter grants the bus to one master at a time. The grant follows a fixed priority.
module arbiter (input clk, input [3:0] req, output reg [3:0] gnt);
  // The request lines are sampled on the rising edge of the clock, and a request that drops before the edge is not seen
  // by the arbiter at all, so the masters hold their requests.
  // synopsys translate_off
  // The checker below runs in simulation only.
  // synopsys translate_on

  /*
   * The grant register holds the last grant for one cycle.
   */
  always @(posedge clk) gnt <= req & -req; // the lowest set bit of the request, which a long trailing comment never re-wraps

`define GRANT(r) \
  // the lowest set bit of the request vector wins the bus, and the masters with a higher index wait for a later cycle \
  // of the clock \
  ((r) & -(r))

  /* The first line of a block comment
     with no stars in the margin, over
     three lines */
endmodule
