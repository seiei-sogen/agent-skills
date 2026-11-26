#!/usr/bin/env bash
# AICROSS 配下の各リポジトリを更新する。先に、日報に載っている開いた PR のうちワークツリーがないものを git-wt で作る。
# そのうえで元のワークツリー（develop / main / master）は fish の gp で pull し、git-wt のワークツリーは fish の gur で rebase する。
# 最後に結果を TSV で標準出力へ出す。
#   使い方: git-repo-update.sh [root] [nippo]
#     root の既定は ~/develop/github.com/AICROSS、nippo の既定は enterprise-agent-ssot の ai-cross-memo/nippo/nippo.adoc
#   終了コード: 0 = OK と SKIP だけ、1 = CONFLICT か FAIL がある、2 = root がない、または gp / gur / git-wt を読み込めない
set -u

root=${1:-$HOME/develop/github.com/AICROSS}
nippo=${2:-$HOME/develop/github.com.sogen/seiei-sogen/enterprise-agent-ssot/enterprises/ai-cross-memo/nippo/nippo.adoc}
[ -d "$root" ] || { echo "$root がありません。" >&2; exit 2; }
fish -c 'functions -q gp gur' || { echo "fish の gp / gur を読み込めません。" >&2; exit 2; }
command -v git-wt >/dev/null || { echo "git-wt がありません。" >&2; exit 2; }
owner=$(basename "$root") # 日報の PR の URL https://github.com/<owner>/<repo>/pull/<n> の <repo> を root/<repo> で探す

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

has_worktree() { git -C "$1" worktree list --porcelain | grep -qxF "branch refs/heads/$2"; }

# 自動の後片付けでワークツリーだけ消えた、開いた PR のブランチを作り直す。作ったものは下のループで gur の対象になる。
if [ ! -f "$nippo" ]; then
  add SKIP create - "$nippo" "日報がない"
else
  for url in $(grep -oE "https://github\.com/$owner/[^/]+/pull/[0-9]+" "$nippo" | sort -u); do
    name=${url#https://github.com/$owner/}
    name=${name%%/*} # リポジトリ名
    dir=$root/$name
    [ -d "$dir/.git" ] || { add SKIP create - "$dir" "ローカルにリポジトリがない（$url）"; continue; }
    info=$(gh pr view "$url" --json state,headRefName --jq '.state + "\t" + .headRefName') ||
      { add FAIL create - "$dir" "gh pr view に失敗（$url）"; continue; }
    state=${info%%$'\t'*} branch=${info#*$'\t'}
    [ "$state" = OPEN ] || continue
    # ディレクトリだけ消えたワークツリーの登録が残っていると、ブランチが使用中とみなされて作れないので片付ける。
    git -C "$dir" worktree prune
    has_worktree "$dir" "$branch" && continue
    git -C "$dir" fetch -q origin "+refs/heads/$branch:refs/remotes/origin/$branch" ||
      { add FAIL create "$branch" "$dir" "git fetch に失敗（$url）"; continue; }
    # 消し残りのローカルブランチが古いままだと、gur のローカル rebase が origin の新しいコミットを押し戻すので、
    # origin まで進める。push 前のコミットがあればそのまま使い、分岐していれば作らずに人へ任せる。
    if git -C "$dir" show-ref -q --verify "refs/heads/$branch"; then
      if git -C "$dir" merge-base --is-ancestor "$branch" "origin/$branch"; then
        git -C "$dir" branch -qf "$branch" "origin/$branch"
      elif ! git -C "$dir" merge-base --is-ancestor "origin/$branch" "$branch"; then
        add SKIP create "$branch" "$dir" "ローカルのブランチが origin/$branch と分岐している（$url）"
        continue
      fi
    fi
    echo "== git wt: $dir ($branch)" >&2
    # 置き場所は各リポジトリの wt.basedir。名前にリポジトリ名を付け、別リポジトリの同じブランチ名とぶつけない。
    path=$(cd "$dir" && git wt --nocd -b "$branch" "$name-${branch//\//-}")
    code=$?
    path=${path##*$'\n'} # git-wt は作ったパスを標準出力の最後の行に出す
    if ! has_worktree "$dir" "$branch"; then
      add FAIL create "$branch" "$dir" "git wt に失敗（$url）"
    elif [ "$code" -ne 0 ]; then
      add OK create "$branch" "$path" "作成。wt.hook が終了コード $code で失敗（$url）"
    else
      add OK create "$branch" "$path" "作成（$url）"
    fi
  done
fi

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
