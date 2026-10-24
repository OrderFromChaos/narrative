## Scope

narrative-gtnh checks **Java 25 projects only**: GTNHGradle projects with
`enableModernJavaSyntax = jvmDowngrader` or `modern` in `gradle.properties`. `verify.py` exits 2 on any
other value, and on `forceToolchainVersion` other than `-1` or `25`. A `jabel` project has Java 17
syntax and the Java 8 library, so records and `List.copyOf()` are not available. (J1-P05)

- No preview features.
- A JDK API only where the GTNHLib stubs of jvmDowngrader cover the API.
- On a guard for a runtime newer than the floor, the comment has the version:
  `// on Java 21 and later, Thread.ofVirtual() is available`. (R10-version-guard)

