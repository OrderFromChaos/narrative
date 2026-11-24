// Known limits of the reader, in a sloppy-mode script.
// In a script, `await`, `yield` and `let` can be names, so the slash after each divides. The reader reads the word as a
// keyword and the slash as a regex up to the comment, so the comment on each of the next three lines is not found.
var await = 2, yield = 2, let = 2;
var half = await / 2; // half of await
half = yield / 2; // half of yield
half = let / 2; // half of let
// An HTML-like comment of Annex B is read as operators, so the text of the comment is not a passage.
half = 1 <!-- an HTML-like comment
--> another HTML-like comment
