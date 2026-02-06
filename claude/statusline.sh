#!/bin/bash
#
# Claude Code status line script
# Reads JSON from stdin and outputs a formatted status line with:
# - Working directory (blue) and git branch (dim)
# - Context window usage percentage with color-coded progress bar

input=$(cat)

# Working directory
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
short_cwd="${cwd/#$HOME/~}"

if cd "$cwd" 2>/dev/null; then
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) \
    && printf '\e[34m%s\e[0m \e[2m%s\e[0m' "$short_cwd" "$branch" \
    || printf '\e[34m%s\e[0m' "$short_cwd"
else
  printf '\e[34m%s\e[0m' "$short_cwd"
fi

# Context window usage
pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | awk '{printf "%d", $1}')
filled=$((pct / 10))
empty=$((10 - filled))

bar=''
i=0
while [ $i -lt $filled ]; do
  bar="${bar}▓"
  i=$((i + 1))
done
i=0
while [ $i -lt $empty ]; do
  bar="${bar}░"
  i=$((i + 1))
done

if [ $pct -ge 80 ]; then
  color='31'  # red
elif [ $pct -ge 50 ]; then
  color='33'  # yellow
else
  color='32'  # green
fi

printf ' \e[2m│\e[0m \e[%sm%d%% %s\e[0m' "$color" "$pct" "$bar"
