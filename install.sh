#!/usr/bin/env bash
# Install one entry skill of Narrative into a Claude Code skills directory.
#
# Usage:
#     $ ./install.sh
#     $ ./install.sh java
#     $ ./install.sh python ~/.config/claude/skills/narrative-python
#
# With no name, the skill is python. The files come from skills/<name>/, which build_skills.py
# writes from core/ and lang/. The default destination is ~/.claude/skills/narrative-<name>. The name
# in the frontmatter of the installed SKILL.md is the name of the destination directory, so a skill
# installed by hand is /narrative-python, and the same skill in the plugin is /nar:python.
#
# The files of skills/<name>/ are the list of what the skill contains. A file in the destination that
# this list does not name is removed, because a file left by an earlier version can be the text of a
# withdrawn rule. The prune removes regular files only, and refuses a destination that has no SKILL.md.
#
# A skill that requires another, such as python, which requires core, installs the other skill first,
# beside the destination. In the installed text, `nar:core` becomes `narrative-core`, the name of
# the skill installed by hand.
#
# It also writes INSTALLED: the commit installed from, and when. verify.py prints it first, so a
# stale install shows in every run.

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
name="${1:-python}"
# the name of an install before the plugin was named nar, such as narrative-python, is accepted too
name="${name#narrative-}"
source_dir="$repo_dir/skills/$name"
destination="${2:-$HOME/.claude/skills/narrative-$name}"

if [[ ! -f "$source_dir/SKILL.md" ]]; then
    echo "install.sh: $source_dir/SKILL.md is missing. The entry skills are:" >&2
    ls "$repo_dir/skills" >&2
    exit 2
fi

# a skill that picks its languages when the skill loads, such as code, works only in the plugin
if grep -q 'CLAUDE_PLUGIN_ROOT' "$source_dir/SKILL.md"; then
    echo "install.sh: $name cannot be installed by hand. Install python or java, or use the plugin" >&2
    exit 2
fi

for required in $(python3 "$repo_dir/assemble.py" "$name" --requires); do
    "$repo_dir/install.sh" "$required" "$(dirname "$destination")/narrative-$required"
done

if ! python3 "$repo_dir/build_skills.py" --check >&2; then
    echo "install.sh: skills/ is out of date with core/ and lang/. Run python3 build_skills.py first" >&2
    exit 2
fi

# the regular files only. A __pycache__ directory from a run of the tools is left out
FILES=()
for path in "$source_dir"/*; do
    if [[ -f "$path" ]]; then
        FILES+=("$(basename "$path")")
    fi
done

# The prune deletes from the destination, so a directory that is not an install of this skill and is
# not empty is refused rather than pruned.
if [[ -d "$destination" && ! -f "$destination/SKILL.md" ]]; then
    if [[ -n "$(ls -A "$destination")" ]]; then
        echo "install.sh: $destination has files and no SKILL.md, so it is not an install" >&2
        exit 2
    fi
fi

mkdir -p "$destination"

for file in "${FILES[@]}"; do
    cp "$source_dir/$file" "$destination/$file"
done

# line 2 of SKILL.md is the name line of the frontmatter, which assemble.py writes
installed_name="$(basename "$destination")"
sed -i.bak -E -e "2s/^name: .*/name: $installed_name/" -e 's/(^|[^a-z])nar:([a-z]+|<language>)/\1narrative-\2/g' "$destination/SKILL.md"
rm -- "$destination/SKILL.md.bak"

version="$(git -C "$repo_dir" rev-parse --short HEAD 2>/dev/null || echo 'unknown commit')"
if [[ -n "$(git -C "$repo_dir" status --porcelain -- skills core lang skills.toml 2>/dev/null || true)" ]]; then
    version+=' with uncommitted changes'
fi
printf '%s, installed %s\n' "$version" "$(date -u +%Y-%m-%dT%H:%MZ)" > "$destination/INSTALLED"

shopt -s nullglob dotglob
for path in "$destination"/*; do
    file="$(basename "$path")"
    for kept in "${FILES[@]}" INSTALLED; do
        if [[ "$file" == "$kept" ]]; then
            continue 2
        fi
    done
    if [[ -d "$path" ]]; then
        echo "left directory $file in place; remove it by hand"
        continue
    fi
    rm -f -- "$path"
    echo "removed $file"
done
shopt -u nullglob dotglob

echo "installed ${#FILES[@]} files of $name to $destination: $(cat "$destination/INSTALLED")"
