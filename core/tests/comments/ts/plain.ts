// A TypeScript file of plain JavaScript, which node checks as written
/// <reference lib="es2020" />
const a = 1, b = 2, c = 3;
const lessMore = a < b > c; // comparisons, not type arguments and not JSX
const shifted = a << b >> c >>> 1; // shifts
const tag = a < /[//]/.source.length; // a regex after less than
const halves = [a / 2, b / 2]; // divisions
console.log(lessMore, shifted, tag, halves);
