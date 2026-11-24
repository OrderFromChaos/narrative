/**
 * @brief A synchronous FIFO with one clock.
 * @param WIDTH the width of one word
 * @author A. Name
 * @code
 * fifo #(.WIDTH(8)) u_fifo (.*); // a sample
 * @endcode
 */
module fifo #(parameter WIDTH = 8) (
  input clk, //! the clock of both ports
  input [WIDTH-1:0] din
);
  /// The storage of the FIFO, read at the read pointer. The @c rd_ptr wraps at the depth.
  logic [WIDTH-1:0] mem [16];
  //! @brief The write pointer.
  //! @details The pointer advances on each write.
  logic [3:0] wr_ptr;
  //! @(posedge clk) samples din and \bus_a is an escaped identifier.
  /*! The read pointer. */
  logic [3:0] rd_ptr;
  //////////////////////////////
  /**/
  // a plain comment after an empty one
endmodule
