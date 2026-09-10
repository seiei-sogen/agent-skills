#!/usr/bin/env bash
# PreToolUse フック（Write|Edit|MultiEdit|NotebookEdit）
# 段階が outline / critique のとき、docs/progressive-outlining/ 配下以外への書き込みを exit 2 でブロックする。
# skeleton / implement / off、または .stage が無いプロジェクトでは何もしない。
# JSON の読み取りは jq を優先し、無ければ python3 にフォールバックする。
set -u

input="$(cat)"

json_get() {
  # $1: dotted path (e.g. tool_input.file_path)
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r ".$1 // empty"
  elif command -v python3 >/dev/null 2>&1; then
    printf '%s' "$input" | python3 -c '
import json, sys
path = sys.argv[1].split(".")
try:
    v = json.load(sys.stdin)
    for k in path:
        v = v.get(k) if isinstance(v, dict) else None
    print("" if v is None else v)
except Exception:
    print("")
' "$1"
  else
    return 1
  fi
}

if ! command -v jq >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
  echo "po-guard: jq も python3 も見つからないため検査をスキップしました" >&2
  exit 0
fi

cwd="$(json_get cwd)"
root="${CLAUDE_PROJECT_DIR:-$cwd}"
[ -n "$root" ] || exit 0

stage_file="$root/docs/progressive-outlining/.stage"
[ -f "$stage_file" ] || exit 0
stage="$(tr -d '[:space:]' < "$stage_file")"

case "$stage" in
  outline|critique) ;;
  *) exit 0 ;;
esac

file="$(json_get tool_input.file_path)"
[ -n "$file" ] || file="$(json_get tool_input.notebook_path)"
[ -n "$file" ] || exit 0

case "$file" in
  /*) abs="$file" ;;
  *)  abs="${cwd:-$root}/$file" ;;
esac

case "$abs" in
  "$root/docs/progressive-outlining/"*) exit 0 ;;
esac

cat >&2 << MSG
po-guard: 現在の段階は「$stage」です。この段階で書けるのは docs/progressive-outlining/ 配下だけです。
  対象: $abs
コードやスケルトンを書く段階ではありません。設計文書（docs/progressive-outlining/）の更新に留めてください。
次の段階へ進めるのはユーザーだけです（/po:skeleton または /po:implement）。
MSG
exit 2
