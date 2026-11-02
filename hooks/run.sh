#!/bin/sh
# Run narrative_hooks.py with the first Python 3.11 or later on PATH: python3, then python, then the py launcher of
# Windows. On Windows, python3 can be an alias of the Microsoft Store that exits with an error, so each candidate runs a
# version check first. The check reads no stdin, so the hook input on stdin reaches narrative_hooks.py whole.
#
# The script always exits 0. To Claude Code, exit 2 refuses the tool call, and Python exits 2 when the script path is
# wrong, so an exit code of Python never passes through. A refusal is JSON on stdout. With no Python 3.11, the script
# prints nothing, and no tool call is refused.

# the directory of this script, with no external command, so the script runs with any PATH. On Windows the path can
# have `\` separators
here=${0%[/\\]*}
for candidate in python3 python "py -3"; do
  # $candidate is unquoted on purpose: "py -3" is a command and an argument
  if $candidate -c 'import sys; sys.exit(sys.version_info < (3, 11))' > /dev/null 2>&1; then
    $candidate "$here/narrative_hooks.py" "$@"
    exit 0
  fi
done
exit 0
