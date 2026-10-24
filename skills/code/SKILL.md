---
name: code
description: Write or review code in the Narrative house style in a repository with more than one language, such as a Java mod with Python scripts. Loads the rules of each language the repository has, Python and Java. Use when a change spans languages; for one language, nar:python or nar:java load less.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/assemble.py *)
---

!`python3 ${CLAUDE_PLUGIN_ROOT}/assemble.py code`
