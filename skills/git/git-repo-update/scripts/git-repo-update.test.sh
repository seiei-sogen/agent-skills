#!/usr/bin/env bash
# git-repo-update.sh を一時ディレクトリのリポジトリで動かす。gp は本物の fish 関数を使い、gh だけを差し替える。
# 差し替えた gh は feat-ok だけ GitHub 側のマージを再現し、ほかの PR では失敗させて手元でのマージの経路を通す。
#   使い方: bash git-repo-update.test.sh
set -eu

here=$(cd "$(dirname "$0")" && pwd)
t=$(mktemp -d)
trap 'rm -rf "$t"' EXIT
# 普段の ~/.gitconfig（commit.gpgsign やフックなど）で一時リポジトリのコミットが失敗しないようにする。
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.com

mkdir -p "$t/bin"
export GH_FAKE_TMP=$t
cat >"$t/bin/gh" <<'EOF'
#!/usr/bin/env bash
# 開いた PR は feat-ok・feat-conflict・fix/gone・feat-stale・feat-diverged・feat-pruned・feat-dirty で、base はどれも develop。feat-merged はマージ済み。
# pr update-branch は、feat-ok なら別の clone で origin/develop をマージして push し、GitHub 側のマージを再現する。
if [ "$1 $2" = "pr update-branch" ]; then
  b=$(git branch --show-current)
  [ "$b" = feat-ok ] || exit 1
  s=$(mktemp -d "$GH_FAKE_TMP/server.XXXX")
  git clone -q "$(git remote get-url origin)" "$s" && git -C "$s" switch -q "$b" &&
    git -C "$s" merge -q --no-edit origin/develop && git -C "$s" push -q origin "$b"
  exit
fi
# pr view は日報の URL（https://github.com/root/app/pull/<n>）の番号から、--jq を当てた後の「状態<TAB>ブランチ」を返す。
if [ "$1 $2" = "pr view" ]; then
  case ${3##*/} in
    1) printf 'OPEN\tfeat-ok\n' ;; 2) printf 'OPEN\tfix/gone\n' ;; 3) printf 'OPEN\tfeat-stale\n' ;;
    4) printf 'OPEN\tfeat-diverged\n' ;; 6) printf 'OPEN\tfeat-pruned\n' ;; 5) printf 'MERGED\tfeat-merged\n' ;; *) exit 1 ;;
  esac
  exit
fi
[ "$1 $2" = "pr list" ] || exit 1
while [ $# -gt 0 ]; do [ "$1" = --head ] && head=$2; shift; done
case $head in feat-ok | feat-conflict | fix/gone | feat-stale | feat-diverged | feat-pruned | feat-dirty) echo develop ;; esac
EOF
chmod +x "$t/bin/gh"
export PATH="$t/bin:$PATH"

commit() { echo "$2" >"$1/$3"; git -C "$1" add "$3"; git -C "$1" commit -qm "$2"; }

git init -q --bare -b main "$t/origin.git"
git clone -q "$t/origin.git" "$t/seed" 2>/dev/null
commit "$t/seed" base shared.txt
git -C "$t/seed" push -q origin main
git -C "$t/seed" switch -qc develop
commit "$t/seed" dev1 dev.txt
git -C "$t/seed" push -q origin develop
for b in feat-ok feat-conflict feat-nopr fix/gone feat-stale feat-diverged feat-merged feat-pruned feat-dirty; do
  git -C "$t/seed" switch -qc "$b" develop
  commit "$t/seed" "$b" "$([ $b = feat-conflict ] && echo shared.txt || echo ${b//\//-}.txt)"
  git -C "$t/seed" push -q origin "$b"
done

root=$t/root
mkdir -p "$root/notes"
git clone -q "$t/origin.git" "$root/app"
git -C "$root/app" switch -q develop
git -C "$root/app" config wt.basedir ../.worktrees
# 後片付けでワークツリーだけ消え、ローカルブランチが残った状態。feat-stale は origin より古く、feat-diverged は origin と分岐している。
git -C "$root/app" branch -q feat-stale origin/develop
git -C "$root/app" branch -q feat-diverged origin/develop
# feat-pruned はディレクトリだけ消え、ワークツリーの登録が残った状態。
git -C "$root/app" worktree add -q "$root/.worktrees/app-feat-pruned" feat-pruned && rm -rf "$root/.worktrees/app-feat-pruned"
commit "$root/app" local-only develop-local.txt && git -C "$root/app" branch -qf feat-diverged HEAD && git -C "$root/app" reset -q --hard origin/develop
for b in feat-ok feat-conflict feat-nopr feat-dirty; do git -C "$root/app" worktree add -q "$root/.worktrees/app-$b" "$b"; done
touch "$root/.worktrees/app-feat-dirty/untracked.txt"
# マージなら、元のコミットは SHA を変えずに残る。
orig_ok=$(git -C "$t/seed" rev-parse feat-ok) orig_gone=$(git -C "$t/seed" rev-parse fix/gone)
git -C "$root/app" worktree add -q --detach "$root/.worktrees/app-detached" develop
git clone -q "$t/origin.git" "$root/other"
git -C "$root/other" switch -qc chore/x

nippo=$t/nippo.adoc
printf -- '- https://github.com/root/app/pull/%s\n' 1 2 3 4 5 6 >"$nippo"
echo '- https://github.com/root/nope/pull/9' >>"$nippo"

# 元のワークツリーより origin/develop を先へ進め、feat-conflict と同じ行を変える。
git -C "$t/seed" switch -q develop
commit "$t/seed" dev2 shared.txt
git -C "$t/seed" push -q origin develop

set +e
out=$(bash "$here/git-repo-update.sh" "$root" "$nippo" 2>"$t/log")
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
expect OK feat-ok /app-feat-ok
expect CONFLICT feat-conflict /app-feat-conflict
expect SKIP feat-nopr /app-feat-nopr "開いた PR がなく"
expect SKIP feat-dirty /app-feat-dirty "未追跡"
expect SKIP - /app-detached "detached"
expect SKIP chore/x /other "develop / main / master ではない"
expect OK fix/gone /app-fix-gone "作成"
expect OK fix/gone /app-fix-gone "git push が必要"
expect OK feat-stale /app-feat-stale "作成"
expect SKIP feat-diverged /app "分岐"
expect OK feat-pruned /app-feat-pruned "作成"
expect SKIP - /nope "ローカルにリポジトリがない"
[ ! -e "$root/.worktrees/app-feat-merged" ] || { echo "NG: マージ済みの PR のワークツリーを作った" >&2; fail=1; }
[ "$(printf '%s\n' "$out" | awk -F'\t' '$2 == "create" && $3 == "feat-ok"' | wc -l)" -eq 0 ] ||
  { echo "NG: ワークツリーがある feat-ok を作り直した" >&2; fail=1; }
[ -f "$root/.worktrees/app-feat-stale/feat-stale.txt" ] ||
  { echo "NG: 古いローカルの feat-stale を origin まで進めずに作った" >&2; fail=1; }
[ "$code" = 1 ] || { echo "NG: 終了コード ${code}（期待は 1）" >&2; fail=1; }
[ "$(git -C "$root/app" rev-parse HEAD)" = "$(git -C "$root/app" rev-parse origin/develop)" ] ||
  { echo "NG: develop が pull されていない" >&2; fail=1; }
for b in feat-ok fix/gone; do
  git -C "$root/app" merge-base --is-ancestor origin/develop "$b" ||
    { echo "NG: $b に origin/develop が取り込まれていない" >&2; fail=1; }
done
git -C "$root/app" merge-base --is-ancestor "$orig_ok" feat-ok && git -C "$root/app" merge-base --is-ancestor "$orig_gone" fix/gone ||
  { echo "NG: 元のコミットの SHA が変わった（rebase された）" >&2; fail=1; }
[ "$(git -C "$root/app" rev-parse feat-ok)" = "$(git -C "$root/app" rev-parse origin/feat-ok)" ] ||
  { echo "NG: GitHub 側でマージした feat-ok を手元へ取り込んでいない" >&2; fail=1; }
git -C "$root/.worktrees/app-feat-conflict" rev-parse -q --verify MERGE_HEAD >/dev/null ||
  { echo "NG: feat-conflict がマージの途中で止まっていない" >&2; fail=1; }
! git -C "$root/app" merge-base --is-ancestor origin/develop feat-dirty ||
  { echo "NG: 未追跡のファイルがある feat-dirty をマージした" >&2; fail=1; }
[ "$fail" = 0 ] || { cat "$t/log" >&2; exit 1; }
echo "PASS"
