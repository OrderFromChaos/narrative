## Logging

- **One stable event name plus parameters, never a sentence built with `+`.** The message is a
  queryable key: `LOG.warn("merge.rejected rejected={} total={}", rejected, total)`. No `+` and no
  `String.format` in a log call. They also build the string when the level is off. `NAR111` flags
  them. (J1-P28, Q08)

- **One logger per mod**, `LogManager.getLogger(MODID)`. This is the GTNH convention, and the mod name
  is then on each `latest.log` line. The log format is set by Minecraft, not by the mod. (J1-P29)

