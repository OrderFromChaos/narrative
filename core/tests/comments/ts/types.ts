/// <reference path="./globals.d.ts" />
/// <reference types="node" />
// Type syntax around regexes and divisions
interface Box<T> {
  value: T;
}
/[//]/.test('a'); // after an interface with type parameters
type Pair = [number, number];
const sizes: Array<number> = [1, 2]; // after a generic type
let value: unknown = 4;
const asserted = <number>value / 2; // division after a type assertion
const pattern = <RegExp>/[//]/; // a regex after a type assertion
const sure = (value as number)! / 2; // division after a non-null assertion
let maybe: number | undefined = 1;
const forced = maybe! / 2; // division after a non-null assertion on a name
function first<T>(items: T[]): T {
  return items[0];
}
const identity = <T,>(x: T) => x; // a generic arrow function
const general = <T>(x: T) => x; // a generic arrow function, which is no JSX in a .ts file
const mapped = first<number>(sizes) / 2; // division after a call with a type argument
function shape(): { width: number } {
  return { width: 1 };
}
/[//]/.test('b'); // after a function whose return type is an object type
function overload(x: string): string;
function overload(x: number): number;
function overload(x: unknown): unknown {
  return x;
}
/[//]/.test('c'); // after overloads
class Store<T> implements Box<T> {
  value!: T;
  private readonly limit?: number = 1 / 2; // division in a field initializer
  read(): T {
    return this.value;
  }
}
/[//]/.test('d'); // after a generic class
const options = { strict: true } satisfies Record<string, boolean>; // after satisfies
const exact = [1, 2] as const; // after as const
type Check<T> = T extends string ? { kind: 'text' } : { kind: 'other' }; // after a conditional type
declare module 'plans' {
  export function read(): void;
}
/[//]/.test('e'); // after a module declaration
const optional = (x?: { a: number }) => x?.a; // after an optional parameter
