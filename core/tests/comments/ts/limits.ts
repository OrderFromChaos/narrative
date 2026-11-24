// Known limits of the reader in TypeScript.
// A type literal at the end of a type alias is read as an object literal, so the slash on the next line divides. The
// `"` in the regex then opens a string up to the end of the line, and the comment on that line is not found.
type Shape = { width: number }
/["]/.test('"') // after a type alias
// The `>` of a type is read as an operator, so a slash after `Array<number>` opens a regex where TypeScript divides.
const list = [] as Array<number> / 2 // division after a type
