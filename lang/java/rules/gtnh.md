## GTNH

- **Every user-facing string is a key in the lang file** (`assets/<modid>/lang/en_US.lang`), read
  through a localization call: `StatCollector.translateToLocal(key)`,
  `StatCollector.translateToLocalFormatted(key, values)`, `ChatComponentTranslation`, or MUI2
  `IKey.lang(key)`. No literal user-facing text in code, so not `IKey.str("Machines")` and not
  `new ChatComponentText("Done")`. `NAR113-gtnh` flags literal text in those calls. (J1-S15)

- **In user-facing text, never `+`.** Put `%s` placeholders in the lang entry, `%s%s` where two values
  are joined, and pass the values to the localization call. `NAR112-gtnh` flags a `+` in or after one.
  (J1-P04)

  ```
  plan.machines=%s machines at %s
  ```

  ```java
  StatCollector.translateToLocalFormatted("plan.machines", count, tierName)
  ```

- **Deterministic order is a property of the field.** Declare `SortedMap`, build a `TreeMap`, and
  never sort where the map is read. Gson rebuilds a `SortedMap` field as a `TreeMap` on load, and a
  plain `Map` with keys that are not `String` as an insertion-ordered `LinkedTreeMap`. A comparator
  that defines a canonical key is allowed. (J1-S01)

- **A draw or render method writes no serialized state.** (J1-S02)

- **No allocation in a per-frame or draw method.** Reuse buffers and primitive containers. On a wrap
  or measure path, use an identity-keyed cache, `if (source == wrappedFor) return;`, with a dirty flag
  at the source, so a steady frame recomputes nothing. `NAR114-gtnh` flags `new` and `.stream()` in a
  `draw*` or `render*` method. (J1-S03)

- **Optional instrumentation is called through an interface.** The implementation for "off" is a
  no-op that allocates nothing. (J1-S04)

- **A point query is answered without a scan of the whole collection.** First look for an invariant
  that removes the query, and add an index only if the query is still needed. (J1-S05)

- **A simple behaviour plus an invariant**, in place of a clever prioritisation policy. (J1-S06)

- **Reuse a type the codebase already has for the same thing**, instead of a new type with the same
  fields. (J1-S07)

- **No hardcoded fix in your mod for a bug in another mod.** Report the bug to that mod. (J1-S08)

- **Keybinds are configurable.** Register them through NEI where NEI has a keybind API. (J1-S09)

- **NEI-style lookup and hover only on sprite-like surfaces**, such as item stacks and pins, never
  on text rows. Players expect it on NEI sprites. (J1-S10)

- **Colours through the colour API of the GUI library**, MUI2 `Color`, not bit arithmetic or hex
  literals. (J1-S11)

