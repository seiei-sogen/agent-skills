#!/usr/bin/env bash
# git-ac-update.sh を一時ディレクトリのリポジトリで動かす。gp / gur は本物の fish 関数を使い、gh だけを差し替える。
# 差し替えた gh はサーバー側 rebase を失敗させるので、gur はローカル rebase の経路を通る。
#   使い方: bash git-ac-update.test.sh
set -eu

here=$(cd "$(dirname "$0")" && pwd)
t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT
# 普段の ~/.gitconfig（commit.gpgsign やフックなど）で一時リポジトリのコミットが失敗しないようにする。
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com

mkdir -p "$t/bin"
cat >"$t/bin/gh" <<'EOF'
#!/usr/bin/env bash
# PR があるのは feat-ok と feat-conflict だけで、どちらも base は develop。
[ "$1 $2" = "pr list" ] || exit 1
while [ $# -gt 0 ]; do [ "$1" = --head ] && head=$2; shift; done
case $head in feat-ok | feat-conflict) echo develop ;; esac
EOF
chmod +x "$t/bin/gh"
export PATH="$t/bin:$PATH"

# 普段の fish 設定は PATH を組み直して gh の差し替えを消すので、gur を定義したファイルと functions だけを読み込ませる。
real=${XDG_CONFIG_HOME:-$HOME/.config}/fish
alias_file=$(fish -c 'functions --details gur')
mkdir -p "$t/xdg/fish/conf.d"
ln -s "$alias_file" "$t/xdg/fish/conf.d/"
ln -s "$real/functions" "$t/xdg/fish/functions"
export XDG_CONFIG_HOME=$t/xdg

commit() { echo "$2" >"$1/$3"; git -C "$1" add "$3"; git -C "$1" commit -qm "$2"; }

git init -q --bare -b main "$t/origin.git"
git clone -q "$t/origin.git" "$t/seed" 2>/dev/null
commit "$t/seed" base shared.txt
git -C "$t/seed" push -q origin main
git -C "$t/seed" switch -qc develop
commit "$t/seed" dev1 dev.txt
git -C "$t/seed" push -q origin develop
for b in feat-ok feat-conflict feat-nopr; do
  git -C "$t/seed" switch -qc "$b" develop
  commit "$t/seed" "$b" "$([ $b = feat-conflict ] && echo shared.txt || echo $b.txt)"
  git -C "$t/seed" push -q origin "$b"
done

root=$t/root
mkdir -p "$root/notes"
git clone -q "$t/origin.git" "$root/app"
git -C "$root/app" switch -q develop
for b in feat-ok feat-conflict feat-nopr; do git -C "$root/app" worktree add -q "$root/.worktrees/app-$b" "$b"; done
git -C "$root/app" worktree add -q --detach "$root/.worktrees/app-detached" develop
git clone -q "$t/origin.git" "$root/other"
git -C "$root/other" switch -qc chore/x

# 元のワークツリーより origin/develop を先へ進め、feat-conflict と同じ行を変える。
git -C "$t/seed" switch -q develop
commit "$t/seed" dev2 shared.txt
git -C "$t/seed" push -q origin develop

set +e
out=$(bash "$here/git-ac-update.sh" "$root" 2>"$t/log")
code=$?
set -e
printf '%s\n' "$out"

fail=0
expect() { # expect <RESULT> <BRANCH> <PATH の末尾> [NOTE の一部]
  printf '%s\n' "$out" | awk -F'\t' -v r="$1" -v b="$2" -v p="$3" -v n="${4:-}" \
    '$1 == r && $3 == b && $4 ~ (p "$") && (n == "" || index($5, n)) { found = 1 } END { exit !found }' ||
    { echo "NG: $*" >&2; fail=1; }
}
expect OK develop /app
expect OK feat-ok /app-feat-ok "force-with-lease"
expect CONFLICT feat-conflict /app-feat-conflict
expect SKIP feat-nopr /app-feat-nopr "開いた PR がなく"
expect SKIP - /app-detached "detached"
expect SKIP chore/x /other "develop / main / master ではない"
[ "$code" = 1 ] || { echo "NG: 終了コード $code（期待は 1）" >&2; fail=1; }
[ "$(git -C "$root/app" rev-parse HEAD)" = "$(git -C "$root/app" rev-parse origin/develop)" ] ||
  { echo "NG: develop が pull されていない" >&2; fail=1; }
git -C "$root/app" merge-base --is-ancestor origin/develop feat-ok ||
  { echo "NG: feat-ok が origin/develop へ rebase されていない" >&2; fail=1; }
[ "$fail" = 0 ] || { cat "$t/log" >&2; exit 1; }
echo "PASS"
