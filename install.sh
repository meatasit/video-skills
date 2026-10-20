#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.claude/skills ~/.claude/agents
for d in "$HERE"/skills/*/; do
  n=$(basename "$d"); rm -rf ~/.claude/skills/"$n"; ln -s "$d" ~/.claude/skills/"$n"; echo "skill   $n"
done
for f in "$HERE"/agents/*.md; do
  n=$(basename "$f"); [[ "$n" == upstream-* ]] && continue
  ln -sf "$f" ~/.claude/agents/"$n"; echo "agent   $n"
done
command -v npx >/dev/null && npx -y skills add remotion-dev/skills --agent claude-code || echo "skip remotion (no npx)"
for t in ffmpeg ffprobe python3; do command -v $t >/dev/null || echo "WARN: $t not found"; done
echo "done — restart Claude Code"
