# Task P15 — spreadsheet formulas

A library that evaluates a small spreadsheet's formulas exactly, with errors and cycles reported.

A library only, with no command line. Use the standard library only. Include tests.

## The function

`evaluateSheet(sheetJson: str) -> dict[str, dict]`: the value of every cell in the sheet.

The input is the text of a JSON object. Each key is a cell name: one uppercase letter `A`–`Z` and a
row `1`–`99` without a leading zero (`A1`, `Z99`). Each value is a JSON number, read exactly as a
decimal (`0.1` is one tenth), or a JSON string. A string that starts with `=` is a formula; any other
string is a text value. Any other key or value, or input that is not a JSON object, raises
`ValueError`. A cell not in the object is **empty**.

The result has one entry per input cell, tagged by type: `{"number": "0.3"}`, `{"string": "abc"}`,
`{"boolean": true}` or `{"error": "#DIV/0!"}`. A number is written in plain decimal notation: no
exponent, no trailing zeros after the point, no point when it is whole, and zero as `0` (never `-0`).

## Formula syntax

```
formula    = "=" comparison
comparison = concat { ( "=" | "<>" | "<" | "<=" | ">" | ">=" ) concat }
concat     = additive { "&" additive }
additive   = term { ( "+" | "-" ) term }
term       = unary { ( "*" | "/" ) unary }
unary      = ( "-" | "+" ) unary | power
power      = primary [ "^" unary ]
primary    = number | string | reference | range | call | "(" comparison ")"
call       = name "(" [ comparison { "," comparison } ] ")"
range      = reference ":" reference
```

Binary operators of one level associate to the left, except `^`, which associates to the right
(`2^3^2` is `2^9`). Unary minus binds looser than `^`: `-2^2` is `-(2^2)`. Spaces may appear between
tokens. A number literal is digits with an optional point and more digits (`12`, `0.5`). A string
literal is in double quotes, with `""` for one quote. Names and references are case-insensitive.
One letter and a row `1`–`99` without a leading zero is a reference; any other letters-then-digits
token (`A0`, `A01`, `A100`, `AA1`) is a reference off the sheet. Letters followed by `(` are a
function name; letters alone are a bare word.

## Values, operators and errors

- Arithmetic (`+ - * / ^`, unary `-` and `+`) takes numbers. An empty cell reads as 0. A string or
  boolean operand gives `#VALUE!`; `"2"+1` is not 3. Every result is computed exactly, then rounded
  to 28 significant digits, half to even (the default context of Python's `decimal` module), so
  `0.1+0.2` is exactly `0.3`.
- Division by zero, and 0 to a negative power, give `#DIV/0!`. An exponent that is not whole gives
  `#VALUE!`; `0^0` is 1.
- `&` joins the text of both operands: a number in the notation above, `TRUE` or `FALSE`, a string as
  it is, an empty cell as the empty string.
- A comparison gives a boolean. Two numbers compare by value; two booleans with `FALSE` below `TRUE`;
  two strings by code point after `str.casefold()` on both, so `"abc"="ABC"` is true. Against a
  string an empty cell is the empty string, against a boolean `FALSE`, otherwise 0. Any other mix of
  types gives `#VALUE!`.
- A formula whose result is an empty cell (`=Z9` with Z9 empty) gives the number 0.
- When an operand is an error, the result is that error, the left operand's first.
- A reference off the sheet, or a range with a corner off the sheet, gives `#REF!`. A bare word, an
  unknown function, or a formula that does not parse gives `#NAME?`.
- A range anywhere other than as a whole argument of `SUM`, `MIN` or `MAX` gives `#VALUE!`. So does a
  known function called with the wrong number of arguments.

## Functions

- `SUM`, `MIN`, `MAX` take one or more arguments. A range covers the rectangle between its two
  corners, in either order (`B3:A1` is `A1:B3`). A range or a single reference contributes the
  numbers in its cells and skips empty cells, strings and booleans. Any other argument must give a
  number, else `#VALUE!`. The first error met, in argument order and each range row by row from its
  top-left cell, is the result. With no numbers, all three give 0.
- `IF(condition, then[, else])`: a number condition is true when not 0, an empty cell is false, a
  string gives `#VALUE!`. Only the branch taken is evaluated, so an error in the other branch has no
  effect. A false condition with no `else` gives `FALSE`.
- `ROUND(x, digits)` rounds to `digits` places after the point, half away from zero (`ROUND(-2.5,
  0)` is -3); a negative `digits` rounds to tens, hundreds and so on. Both arguments read like
  arithmetic operands, and `digits` must be whole, else `#VALUE!`.

## Cycles

The dependencies of a formula are the cells named by its references and covered by its ranges,
whether or not evaluation reaches them; a reference or range off the sheet, and a formula that does
not parse, add none. A cell on a cycle of dependencies (a cell that refers to itself included), and
every cell that depends on one directly or through other cells, gives `#CYCLE!`, whatever its
formula would otherwise give.

## What is left to you

The package and module layout, error messages, and any behaviour this specification does not fix.

## The fixture

`fixture/sheet.json` is one sheet, and `fixture/expected.json` is the result `evaluateSheet` must
return for it. `fixture/invalid_sheet.json` must raise `ValueError`. The sheet's cases: `-2^2`,
`2^3^2` and `2*-3^2`; `0.1+0.2` and its comparison with `0.3`; `ROUND` at a half (`-2.5`, `2.675`),
to hundreds and to negative zero; a whole product and `1/3`; string comparisons in mixed case and
with `ß`; `&` with an addition and with an empty cell; a string in an addition; a backwards range
over a block with a string and an empty cell; a lowercase call; a range off the sheet; an error kept
out by `IF`; a cycle through a range, a cell depending on it, an `IF` whose untaken branch refers to
it, a self-reference, and cells next to the cycle that are not part of it.
