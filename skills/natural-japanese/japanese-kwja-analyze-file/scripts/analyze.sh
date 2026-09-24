#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -s $1 ]]; then
  printf 'Usage: %s <nonempty-text-file>\n' "${0##*/}" >&2
  exit 2
fi

input=$1
output="${input}.kwja.txt"
temporary=$(mktemp "${output}.tmp.XXXXXX")
trap 'rm -f -- "$temporary"' EXIT

kwja --tasks typo,char,seq2seq,word --filename "$input" > "$temporary"
if [[ ! -s $temporary ]]; then
  printf 'KWJA produced no output for %s\n' "$input" >&2
  exit 1
fi

mv -f -- "$temporary" "$output"
printf '%s\n' "$output"
