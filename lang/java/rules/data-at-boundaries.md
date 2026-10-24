## Data at boundaries

- Parse untrusted input into a **record at one boundary gate**, then never validate again. GTNH
  gates: `readFromNBT`, packet decode, Gson, config load. (J1-P20, Q02, Q14)

- **A parsed record contains only what its input contained.** Where one input format has a field and
  another does not, the component is `@Nullable` on the shared record, and the check that reads the
  component skips an absent value. **Never substitute a plausible default**, because the output then
  contains a fact that the file does not. (R9-01)

- **A record is the default for data.** A class that is just data is the record, not a wrapper
  around a nested one. In other classes, a field is `final` unless code reassigns the field.
  `NAR141` flags a field that could be final. (J1-P21, R8-D11-resolved)

- **A record is shallowly immutable.** The compact constructor copies a collection component with
  `List.copyOf`, or Guava `ImmutableList.copyOf`. **Never an array component:** `equals()` and
  `hashCode()` of a record compare arrays by identity, so two equal plans compare unequal. `NAR108`
  flags an array component. (J1-P22)

- **Genuinely schemaless input**: promote the fields the program computes on to typed components,
  and put the remainder in one `JsonObject` or `Map<String, JsonElement>` component. **Never merge
  the remainder into an output object.** An untrusted key with the name of an output field would
  replace that field. Nest the remainder instead. (R4-04)

