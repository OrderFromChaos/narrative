## Naming

- Module filenames `snake_case`. Functions and methods `mixedCase`. Classes and types
  `PascalCase`. Variables and arguments `snake_case`. Module constants `ALL_CAPS`. **In a
  `snake_case` codebase that you did not write, match local convention.** Detect before you write.

- Spell names out. No `img_arr`, `cfg`, `idx`. (Q11)

- **A function name starts with a verb, and the verb's object is what the function returns.**
  `parsePolicy`, `readManifest`, `extractPackagesFromLockfileText`, `computeDeletionCutoff`. A name built
  from a preposition, such as `policyIn` or `cutoffFor`, is about the input.
  (R9-03)

- **A name is clear without its module**, and the module qualifier does not count toward the name. A
  reader who has never opened the module must understand the name. `requirements_lock.packagesIn` is
  clear at the call site and unclear at the definition, and the tools don't stop a second module from
  declaring a second `packagesIn`. **Two functions in one package do not share a name.** (R9-03, R7-B06)

  **Length is not the defect.** Where the clear name is the longer one, write the longer one.

- Predicates are bare adjectives, and don't take a verb: `isReadyForScan` → `readyForScan`, and
  `checkBelowMinimum` → `belowMinimum`. A predicate returns the answer to a question. (Q12)
  Dunder and protocol methods are named by the language.

- **Do not restate a domain type in a parameter name**: `rebin_config: RebinConfig` →
  `config: RebinConfig`. The prefix duplicates the type. (Q11)

- **When the type is generic, the parameter name is the only place the thing is named.** `Path`, `str`,
  `int`, `bytes`, `dict`, and `object` constrain only a value's shape. Write
  `path: Path` → `policy_json_path: Path`, and `text: str` → `manifest_text: str`. The rule above
  bans a redundant prefix. An informative prefix stays.

- **Raw and parsed forms get different names.** Prefix the raw form with `raw_`: `raw_at: str` from
  the file, `at: DateTime` once parsed. Never `at` beside `parsed.at`. (R10-raw-names)

- **Restate the type where the bare name would shadow an import.** A program that imports a
  first-party module by name burns that identifier at module scope, so the local becomes
  `results_store: Store`. (R8-B06-Q11)

- `pathlib.Path` → `from pathlib import Path`. Avoid fully qualified names, but keep the module
  where it adds meaning (`struct.unpack`, `json.loads`, `asyncio.wait_for`). Import the class,
  keep the verb qualified. (R3a-08)

