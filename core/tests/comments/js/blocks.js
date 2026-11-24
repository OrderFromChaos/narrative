// A slash after a closing brace opens a regex after a block, and divides after an operand
let a = 1;
if (a) {
  a = 2;
}
/[//]/.test('a'); // after an if block
label: {
  a = 3;
}
/[//]/.test('b'); // after a labelled block
switch (a) {
  case 1: {
    a = 4;
  }
  /[//]/.test('c'); // after a block in a case
}
function f() {
  return {
    key: /[//]/, // after a key in an object literal that follows return
  };
}
/[//]/.test('d'); // after a function declaration
const g = () => {};
/[//]/.test('e'); // after the block body of an arrow function
class C {
  method() {
    return 1;
  }
}
/[//]/.test('f'); // after a class declaration
function h() {
  return;
}
/[//]/.test('g'); // after a return with no value
a = (function () {
  return 1;
})() / 2; // after a function expression called in parentheses
try {
  a = 5;
} finally {
  a = 6;
}
/[//]/.test('h'); // after a finally block
