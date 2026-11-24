// Comparisons and shifts that look like JSX tags, in a file that can hold JSX
let a = 1, b = 2, c = 3;
const lessMore = a <b> c; // a < b > c, after a name
const shifted = a<<b>>c; // shifts
if (a <b) c = a /2; // division after a comparison in the head of an if
const tag = a < /[//]/.source.length; // a regex after less than
