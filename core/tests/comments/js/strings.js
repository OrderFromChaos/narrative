// Strings with quotes, backslashes and slashes
const a = 'it\'s // text'; // after a single-quoted string
const b = "say \"/* text */\""; // after a double-quoted string
const c = 'a\\'; // after an escaped backslash
const d = 'line \
continued // text'; // after a line continuation
const e = "'" + '"' + '//'; // after quotes in quotes
