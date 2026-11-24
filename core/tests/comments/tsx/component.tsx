// JSX text and attributes with `//` and `/*`, and comments in JSX expressions
type Props = { href: string; label: string };
const identity = <T,>(x: T) => x; // a generic arrow function, not an element
const keep = <T extends object>(x: T) => x; // a constrained generic arrow function
const constant = <const T,>(x: T) => x; // a const type parameter
export function Link({ href, label }: Props) {
  return (
    <a href="//cdn.example.com/x" title='/* text */' data-href={href}>
      {/* a comment in a JSX expression */}
      see http://example.com // text
      /* text */
      {label // a line comment in a JSX expression
      }
      <span>{identity(label) /* after a call */}</span>
      Don't stop at the apostrophe
    </a>
  );
}
const list = (items: string[]) => (
  <>
    {items.map((item) => (
      <li key={item}>{item}</li> // after an element in parentheses
    ))}
  </>
);
const selected = <Select<string> value="a" />; // after an element with a type argument
const half = keep.length / 2; // division after a name
