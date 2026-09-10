#!/usr/bin/env bash
# 使い方: po-stage.sh <outline|critique|skeleton|implement|off> [project-root]
# 各スキルの冒頭で `!` 注入により実行され、現在の段階を docs/po/.stage に書く。
# 出力はそのままスキル本文に差し込まれる（Claude が読む）。
set -u

stage="${1:-}"
root="${2:-${CLAUDE_PROJECT_DIR:-$PWD}}"

case "$stage" in
  outline|critique|skeleton|implement|off) ;;
  *)
    echo "po-stage: 不明な段階 '$stage'（outline|critique|skeleton|implement|off）" >&2
    exit 1
    ;;
esac

mkdir -p "$root/docs/po"
printf '%s\n' "$stage" > "$root/docs/po/.stage"

echo "現在の段階: $stage"
echo "既存の slug:"
found=0
for d in "$root"/docs/po/*/; do
  [ -d "$d" ] || continue
  found=1
  name="$(basename "$d")"
  files="$(ls -1 "$d" 2>/dev/null | tr '\n' ' ')"
  echo "  - $name: ${files:-（空）}"
done
[ "$found" -eq 1 ] || echo "  （なし）"
exit 0
