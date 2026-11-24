// Each regex below holds a `//` or a `/*`. Read as a division, the regex would open a comment.
const slashes = /[/*]/; // after a class with a slash and a star
const escaped = 'a/b'.replace(/\//g, '-'); // after an escaped slash
const tested = /a/.test('a') // after a method call on a regex
const bracket = /[\]/]/; // after an escaped bracket in a class

function* keywords(list) {
  let x = typeof /[//]/; // after typeof
  switch (x) {
    case /[//]/.source: // after case
      break;
    default:
      break;
  }
  yield /[//]/; // after yield
  x = void /[//]/; // after void
  x = delete /[//]/.lastIndex; // after delete
  x = 'source' in /[//]/; // after in
  for (const item of /[//]/.source) list.push(item); // after of
  x = new /[//]/.constructor('i'); // after new
  x = x instanceof /[//]/.constructor; // after instanceof
  if (x) throw /[//]/; // after throw
  return /[//]/; // after return
}

async function awaiting() {
  return await /[//]/; // after await
}

let b = 1;
b = (/[//]/); // after a parenthesis
b = [/[//]/, /[//]/]; // after a bracket and a comma
b = !/[//]/.test('o'); // after not
b = b && /[//]/; // after and
b = b || /[//]/; // after or
b = b ?? /[//]/; // after nullish coalescing
b = b ? /[//]/ : /[//]/; // after a question mark and a colon
b = { key: /[//]/ }; // after a brace and a key
{ /[//]/.test('v'); } // after the brace that opens a block
if (b) { b = 2; } /[//]/.test('w'); // after the brace that closes a block
; /[//]/.test('x'); // after a semicolon
b = () => /[//]/; // after an arrow
/[//]/.test('z'); // at the start of a statement
if (b) /[//]/.test(b); // after the head of an if
while (!b) /[//]/.test(b); // after the head of a while
for (;;) /[//]/.test(b); // after the head of a for
do /[//]/.test(b); while (!b); // after do
if (!b) b = 3; else /[//]/.test(b); // after else
b = 1 - /[//]/.source.length; // after a binary operator
b = b === /[//]/; // after a comparison
b = b < /[//]/.source.length ? 1 : 2; // after less than
b = b > /[//]/.source.length; // after greater than
b += /[//]/.source.length; // after an assignment operator
b = `${/[//]/.source}`; // after the start of a template expression
