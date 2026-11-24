// Decorators, an enum and a namespace, which node cannot strip
function sealed(target: Function) {
  return target;
}
function logged() {
  return (target: unknown, name: string) => [target, name];
}
@sealed
class Plan {
  @logged() name = 'plan'; // after a decorator call
  constructor(private readonly path: string) {}
}
enum Kind {
  Machine = 4 / 2, // division in an enum
  Belt,
}
/[//]/.test('a'); // after an enum
namespace Plans {
  export const all = [Kind.Belt / 2]; // division in a namespace
}
/[//]/.test('b'); // after a namespace
