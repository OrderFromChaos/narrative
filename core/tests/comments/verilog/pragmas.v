// SPDX-License-Identifier: Apache-2.0
// SPDX-FileCopyrightText: 2026 Example

// The register file of the core.
module regfile (input clk);
  // synopsys translate_off
  initial $display("simulation only");
  // synopsys translate_on
  // synthesis translate_off
  // synthesis translate_on
  // synthesis of this block takes long
  // pragma translate_off
  // pragma translate_on
  /* verilator lint_off WIDTH */
  /* verilator lint_on WIDTH */
  /*verilator public_flat_rw*/
  // verilator coverage_off
  // spyglass disable_block W164a
  // spyglass enable_block W164a
  // cadence map_to_mux
  // coverage off
  // coverage on
  // coverage on the FSM states is required
  // VCS coverage off
  // altera message_off 10230
  // synopsys full_case parallel_case
  reg [3:0] state; // synopsys enum states
  // pragma coverage off
endmodule
