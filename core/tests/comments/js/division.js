// Each slash below divides. Read as a regex, the slash would run up to the comment and hide it.
const list = [8];
let a = 4, b = 2, g = 1, c;
c = a / 2; // after a name
c = 4 / 2; // after a number
c = 0x1f / 2; // after a hex number
c = .5 / 2; // after a number with no integer part
c = 'four'.length / 2; // after a property
c = (a) / 2; // after a parenthesis
c = list[0] / 2; // after a bracket
c = a++ / 2; // after a postfix increment
c = b-- / 2; // after a postfix decrement
c = a
/ 2; // after a line break, which ends no statement before a slash
c = a
/b/g; // a / b / g, three names and two divisions
c = ({}) / 2; // after an object literal in parentheses
c = [0].map(() => { return 1; }) / 2; // after a call whose argument is a function
c = function () { return 1; } / 2; // after a function expression
c = class {} / 2; // after a class expression
c = { b: 1 } / 2; // after an object literal
c = a ? b : {} / 2; // after an object literal in a ternary
c = `${a}` / 2; // after a template
c = 'x' / 2; // after a string
c = /x/ / 2; // after a regex
c = true / 2; // after true
c = null / 2; // after null
c = a.return / 2; // after a property named like a keyword
c = a?.b / 2; // after optional chaining
c /= 2; // after a division assignment
class Base {
  get half() {
    return 1;
  }
}
class Derived extends Base {
  ratio() {
    return this.half / 2 + super.half / 2; // after this and super
  }
}
