// Template literals whose text holds `//` and `/*`
const host = 'cdn';
const a = `http://${host}/x /* text */`; // after a template
const b = `outer ${`inner // ${host} /* text */`} end`; // after nested templates
const c = `${{ key: '}' }.key} // text`; // after an object literal in a template expression
const d = `${host /* a block comment in an expression */} and ${host // a line comment in an expression
} // text`; // after comments in template expressions
const e = `line one // text
line two /* text */ ${`\`` /* inside a nested expression */}`; // after a template over two lines
const f = `${(() => {
  return '}';
})()} // text`; // after a function body in a template expression
const g = String.raw`a\`// text`; // after a tagged template with an escaped backtick
const h = `${a ? `${b}` : `//`}` / 2; // division after a template
