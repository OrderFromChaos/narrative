// JSX elements, whose text is not code
const site = 'example.com';
export function Page({ user, items }) {
  const greeting = user ? <b>Hi // {user}</b> : <i>/* nobody */</i>; // after a ternary of elements
  return (
    <div
      // a comment between attributes
      className="page" /* another comment between attributes */
      data-url={`//${site}`}
      {...user}
    >
      <Layout.Header title="a // b" />
      <svg:rect width="1" />
      {items.length > 0 && <ul>{items.map((item) => <li key={item}>{item} // text</li>)}</ul>}
      {/* a comment in an expression container */}
      <p>
        it's 1 {'<'} 2, and the apostrophe opens no string
      </p>
      {greeting}
    </div>
  );
}
const half = site.length / 2; // division after a name
