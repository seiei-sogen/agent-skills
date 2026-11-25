#!/usr/bin/env bash
# AICROSS 配下の各リポジトリを更新する。元のワークツリー（develop / main / master）は fish の gp で pull し、
# git-wt のワークツリーは fish の gur で rebase する。最後に結果を TSV で標準出力へ出す。
#   使い方: git-ac-update.sh [root]（既定は ~/develop/github.com/AICROSS）
#   終了コード: 0 = OK と SKIP だけ、1 = CONFLICT か FAIL がある、2 = root がない、または gp / gur を読み込めない
set -u

root=${1:-$HOME/develop/github.com/AICROSS}
[ -d "$root" ] || { echo "$root がありません。" >&2; exit 2; }
fish -c 'functions -q gp gur' || { echo "fish の gp / gur を読み込めません。" >&2; exit 2; }

summary=$'RESULT\tKIND\tBRANCH\tPATH\tNOTE\n'
status=0
add() { # add <RESULT> <KIND> <BRANCH> <PATH> [NOTE]
  summary+="$1"$'\t'"$2"$'\t'"$3"$'\t'"$4"$'\t'"${5:-}"$'\n'
  case $1 in CONFLICT | FAIL) status=1 ;; esac
}

# rebase / merge の途中か、未解消のファイルが残っていれば成功を返す。
stuck() {
  local gd
  gd=$(git -C "$1" rev-parse --absolute-git-dir) || return 1
  [ -d "$gd/rebase-merge" ] || [ -d "$gd/rebase-apply" ] || [ -f "$gd/MERGE_HEAD" ] ||
    [ -n "$(git -C "$1" diff --name-only --diff-filter=U)" ]
}

for repo in "$root"/*/; do
  repo=${repo%/}
  [ -d "$repo/.git" ] || continue # git-wt のワークツリー（.git がファイル）と Git 管理外を除く
  base=
  # worktree list の先頭が元のワークツリー。ブランチ名は - で始まれないので、detached HEAD を - で表す。
  while IFS=$'\t' read -r -u 3 kind path branch prunable; do
    if [ "$kind" = base ]; then
      base=$branch
      case $branch in
        develop | main | master) cmd=gp ;;
        *) add SKIP base "$branch" "$path" "develop / main / master ではない"; continue ;;
      esac
    else
      cmd=gur
      if [ "$prunable" = 1 ]; then add SKIP worktree "$branch" "$path" "ディレクトリがない（git worktree prune の対象）"; continue; fi
      if [ "$branch" = - ]; then add SKIP worktree - "$path" "detached HEAD"; continue; fi
    fi
    if stuck "$path"; then add SKIP "$kind" "$branch" "$path" "rebase / merge が途中で止まっている"; continue; fi
    if [ "$cmd" = gur ]; then
      # gur は開いた PR がないと origin/HEAD へ rebase する。元のブランチが develop のリポジトリでは main へ載せ替えてしまう。
      pr_base=$(cd "$path" && gh pr list --head "$branch" --state open --json baseRefName --jq '.[0].baseRefName // empty') ||
        { add FAIL worktree "$branch" "$path" "gh pr list に失敗"; continue; }
      default=$(git -C "$path" symbolic-ref --quiet --short refs/remotes/origin/HEAD)
      default=${default#origin/}
      if [ -z "$pr_base" ] && [ "$default" != "$base" ]; then
        add SKIP worktree "$branch" "$path" "開いた PR がなく、gur の rebase 先 origin/${default:-?} が元のブランチ $base と違う"
        continue
      fi
    fi
    echo "== $cmd: $path ($branch)" >&2
    (cd "$path" && fish -c "$cmd") >&2
    code=$?
    if stuck "$path"; then
      add CONFLICT "$kind" "$branch" "$path" "$cmd が競合で止まった"
    elif [ "$code" -ne 0 ]; then
      add FAIL "$kind" "$branch" "$path" "$cmd が終了コード $code で失敗"
    else
      counts=$(git -C "$path" rev-list --left-right --count "origin/$branch...HEAD" 2>/dev/null)
      case $counts in
        [1-9]*$'\t'[1-9]*) add OK "$kind" "$branch" "$path" "origin/$branch から分岐。git push --force-with-lease が必要" ;;
        *) add OK "$kind" "$branch" "$path" ;;
      esac
    fi
  done 3< <(git -C "$repo" worktree list --porcelain | awk '
    /^worktree / { path = substr($0, 10); branch = "-"; prunable = 0 }
    /^branch /   { branch = substr($0, 19) }
    /^prunable/  { prunable = 1 }
    /^$/         { print (n++ ? "worktree" : "base") "\t" path "\t" branch "\t" prunable }')
done

printf '%s' "$summary"
exit "$status"
