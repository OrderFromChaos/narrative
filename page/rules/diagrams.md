## Diagrams

**Draw an arrow for a message or a flow only.** (R13-arrow) Write a state or a condition as a note.
An arrow labelled `no orders while the shop is closed` → a note `The till can't take an order while
the shop is closed`.

**Make the sender and the receiver of each arrow clear.** (R13-arrow-owner) Give each receiver
column a colour, repeat the header in a long sequence diagram, and draw the head office as a central
hub in place of long crossing arrows.

**Give a legend for each colour and box shape.** (R13-legend) A reader asked `what do the boxes
mean?` and `why are some arrows dashed?`.

**Draw each path that the argument depends on.** (R13-paths) Draw the path to the archive for the
order files, prices.csv and stock.csv, or a reader can't tell which step writes each file.

**Split or delete a catch-all node**, such as `kitchen, tills, delivery`. (R13-catch-all)

**Draw separate charts for steps with different people, and draw a loop as a loop.**
(R13-split-flow) The order request (shop to warehouse) and the restock request (warehouse to
supplier) get two charts. Pack, check and re-pack is a loop, and a chart of three boxes in a line
doesn't show the loop.

