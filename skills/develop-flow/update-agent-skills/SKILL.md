---
name: update-agent-skills
description: agent-skills リポジトリの変更をコミット・push し、fish の skup、hs の順に実行して Claude Code と Codex への反映を確認する。ユーザーが自作スキルを公開し、Nix と両エージェントのスキルをまとめて更新したいときに使う。
---

# 自作スキルを公開して Claude Code と Codex に反映する

次の順番で実行する。前の工程が失敗した場合は、その時点の状態とエラーを報告して終了する。

1. agent-skills リポジトリの差分をコミット・push する。
2. fish の `skup` を実行する。
3. fish の `hs` を実行する。
4. インストール内容を確認し、Claude Code と Codex に反映する。

このスキルの実行依頼を、上記の公開・更新処理への依頼として扱う。
対象は `/home/agir_wsl/develop/ghq_repos/github.com/seiei-sogen/agent-skills` とする。
呼び出し元の作業ディレクトリが別リポジトリでも、Git 操作はこの対象で行う。

## 1. 取得対象を確認してコミット・push する

対象リポジトリの現在のブランチ、remote、upstream、差分を確認する。
未追跡ファイルも含め、今回公開するスキルと付属ファイル、削除するファイルを記録する。

`/home/agir_wsl/.config/fish/conf.d/alias.fish` の `skup` と `hs` の定義を読む。
`/home/agir_wsl/.config/home-manager/flake.nix` で `seiei-sogen-skills` の取得元を確認する。
現在の設定では `github:seiei-sogen/agent-skills` の既定ブランチを取得する。
既定ブランチは `git ls-remote --symref origin HEAD` で確認する。
取得元のリポジトリ・ブランチと push 先が異なる場合は、相違を伝え、公開先が確定するまでコミットへ進まない。
取得元の設定変更やブランチのマージは、別途依頼された場合に行う。

対象リポジトリ内の `skills/git/commit-push/SKILL.md` を読み、コミット・push の手順に従う。
差分がない場合はコミットを省略する。未 push のコミットがあれば、同スキルの公開範囲確認と push 手順に従う。
更新処理へ進む前に、対象の `HEAD` が実際のリモートの取得対象ブランチへ公開されていることを確認し、そのコミット hash を記録する。

## 2. skup でスキルを更新する

次のコマンドを1回実行し、終了コードを確認する。

```bash
fish -c 'source /home/agir_wsl/.config/fish/conf.d/alias.fish; and skup'
```

`skup` は Nix の取得元更新、Home Manager の適用、Claude Code と Codex のプラグイン更新を行う。
設定ファイル内の関数をそのまま利用し、同じ処理を別スクリプトへ複製しない。
失敗した場合は、完了済みの処理をログから確認し、`hs` へ進まず終了する。

## 3. hs で Nix の設定を適用する

`skup` が成功したら、指定どおり `hs` も1回実行する。

```bash
fish -c 'source /home/agir_wsl/.config/fish/conf.d/alias.fish; and hs'
```

`hs` は `home-manager switch` による設定適用であり、単独では取得元のバージョンを更新しない。
失敗した場合は、その状態を報告して終了する。
これらの処理で変更された Home Manager 側の `flake.lock` などを、追加でコミット・push するのは別途依頼された場合とする。

## 4. 配置されたスキルを確認する

`/home/agir_wsl/.config/home-manager/flake.lock` の `nodes["seiei-sogen-skills"].locked.rev` を取得する。
その rev が、手順1で公開したコミットと同一か、そのコミットを含む後続のコミットであることを確認する。
後続のコミットなら、必要に応じて対象リポジトリへ取得し、`git merge-base --is-ancestor` で確認する。
異なる履歴の場合は、今回の変更が取り込まれていないことを報告する。

`home.nix` のスキル取得元、フィルター、配布先を確認する。
通常の配布先は `~/.claude/skills/<skill-name>/` と `~/.codex/skills/<skill-name>/` である。
Codex アプリが使う一時的な `CODEX_HOME` と、Home Manager が管理する配布先を区別する。
今回追加・変更したスキルの `SKILL.md` と付属ファイルを、両方の配布先で公開した内容と照合する。
削除したファイルは配布先にも残っていないことを確認する。
フィルターによる除外やファイルの不一致があれば、未反映のスキルを報告する。

## 5. Claude Code と Codex のセッションに反映する

両エージェントのスキル変更の自動検知を確認する。
現在のセッションを操作できるツールがある場合は、次の確認とリロードをそのセッションで行う。
スラッシュコマンドをシェルで実行したり、別の CLI プロセスを起動しただけで既存セッションのリロード完了と扱ったりしない。

- Claude Code では `/reload-skills` を実行し、`/skills` で今回更新したスキルの認識を確認する。`skup` で更新されたプラグインも反映するため、`/reload-plugins` を実行する。
- Codex はスキル変更を自動検知する。`/skills` で認識を確認し、更新が現れない場合はセッションを再起動して再確認する。

起動していないエージェントは、次回起動時に更新済みの配布先からスキルを読み込む。
既存セッションを操作できない場合は、配置確認まで済ませ、上記の操作が必要なエージェントを明示する。
実行中の自分自身や他のセッションの強制終了で会話や作業を失わせない。
インストール済みでも、セッション内の認識を確認できなければリロードは未確認と報告する。

仕様を確認する場合は [Claude Code のスキル変更検知](https://code.claude.com/docs/en/skills) と [Codex のスキル更新](https://learn.chatgpt.com/docs/build-skills) を読む。

## 6. 結果を報告する

公開したコミットとブランチ、`skup` と `hs` の成否、取り込まれた rev を簡潔に報告する。
更新したスキルについて、両方への配置確認とセッション内の反映確認を分けて報告する。
残っている操作があれば、エージェント名と実行するコマンドを示す。
