#!/bin/sh
input=$(cat)
fields=$(printf '%s' "$input" | jq -r '
  @sh "model=\(.model.display_name // "")",
  @sh "effort=\(.effort.level // "")",
  @sh "cwd=\(.workspace.current_dir // .cwd // "")",
  @sh "session_name=\(.session_name // "")",
  @sh "left=\(if .context_window.remaining_percentage != null then (.context_window.remaining_percentage | floor) else "" end)"
') || exit 1
eval "$fields"

ORANGE='\033[38;5;216m'
GREEN='\033[38;5;151m'
BLUE='\033[38;5;111m'
LAV='\033[38;5;183m'
DIM='\033[2m'
RST='\033[0m'
SEP="${DIM} · ${RST}"

case "$cwd" in
  "$HOME") short='~' ;;
  "$HOME"/*) short="~${cwd#"$HOME"}" ;;
  *) short=$cwd ;;
esac
branch=''
if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
fi

printf '%b%s%b' "$ORANGE" "${model:-Claude}${effort:+ $effort}" "$RST"
[ -z "$short" ] || printf '%b%s%b' "${SEP}${GREEN}" "$short" "$RST"
[ -z "$session_name" ] || printf '%b%s%b' "${SEP}${LAV}" "$session_name" "$RST"
[ -z "$branch" ] || printf '%b%s%b' "${SEP}${BLUE}" "$branch" "$RST"
[ -z "$left" ] || printf '%b%s%b' "${SEP}${ORANGE}" "Context ${left}% left" "$RST"
printf '\n'
