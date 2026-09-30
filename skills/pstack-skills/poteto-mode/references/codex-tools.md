# pstack 向け Codex ツール対応表

pstack のスキルは共有の文章の中で Claude Code のツール用語（`Skill`、`Agent`、`AskUserQuestion`）を保っている。Codex でもファイルは同じで、それらのツール名の解決先だけが異なる。モデルの実行についてはここでは変換しない。親が所有する Claude/Codex/Grok のルート表とプロバイダ修飾付きディスクリプタは [`provider-dispatch.md`](provider-dispatch.md) を読む。

## ツールの操作

| pstack / Claude の操作 | Codex での対応物 |
|------------------------|------------------|
| ファイルを読む | `shell`（`cat`、`head`、`tail`） |
| ファイルを作成／編集／削除する | `apply_patch` |
| シェルコマンドを実行する | `shell` |
| ファイル内容を検索する／ファイルを探す | `shell`（`rg`、`grep`、`find`、`ls`） |
| URL を取得する | `curl` / `wget` を使った `shell` |
| Web を検索する | `web_search` |
| スキルを呼び出す（`Skill` ツール、`/command`） | スキルはネイティブに読み込まれる。提示された指示に従う。 |
| `paths` フロントマターによる自動読み込みの範囲指定 | Claude Code のみ。Codex では `pstack:typescript-best-practices` を名前で呼び出す。 |
| サブエージェントをディスパッチする（`Agent`/`Task` ツール） | `spawn_agent` |
| 1 ターンで N 個のサブエージェントを並列ディスパッチする | 1 回の応答で N 回の `spawn_agent` 呼び出し |
| サブエージェントの結果を待つ | `wait_agent` |
| 終了したサブエージェントのスロットを解放する | `close_agent` |
| タスクを追跡する（TODO リスト / `TodoWrite`） | `update_plan` |
| 人間に選択肢固定の質問をする（`AskUserQuestion`） | 平文で尋ね、ユーザーに答えさせる。Codex には構造化選択のツールがない。 |

サブエージェントのディスパッチには `multi_agent` の有効化が必要である。`~/.codex/config.toml` に追加する:

```toml
[features]
multi_agent = true
```

それがないと、ネイティブの Codex レーンは名前付きのドロップアウトになる。独立した外部レーンは引き続き動き、親は減ったプロバイダ数を記録する。パネルを逐次の単一モデルのパスに畳んではならない。

## サブエージェント方針

poteto-mode の「サブエージェント」セクションは Claude 固有の既定（`subagent_type: "poteto-agent"`、`run_in_background: true`）を定めている。Codex では:

- `poteto-agent` というサブエージェント種別はない。即席のサブエージェントを poteto-mode のスタイルに通すには、まず `poteto-mode` スキルを全文読むよう指示した `spawn_agent` をディスパッチする。
- `spawn_agent` の呼び出しはすでに自分のターンと並行して動くので、`run_in_background: true` に相当する別フラグはない。ディスパッチを発行して続ける。
- `comment-sicko` というサブエージェント種別もない。**no-comments** スキルは Claude Code ではそれを生成する。Codex では、まず `agents/comment-sicko.md` を全文読むよう指示した `spawn_agent` をディスパッチする。
- Claude Code はすべてのサブエージェントをこのマシン上で動かすので、**swarm** スキルのワーカーとファンアウト系プレイブック（`orchestrate`、`autopilot-full`、`autopilot-stack`）は書き込み側をワークツリーで分離する。Codex でも同じことが成り立つ。
- 方針の残りは変えない。インライン展開した文脈ではなくファイルポインタを渡し、書き込みを行う各ワーカーに専用のワークツリーかブランチを与え、すべてのサブエージェントの差分を自分でレビューする。

## モデルとプロバイダ

設定済みのすべての項目を Codex のモデルで置き換えてはならない。`/setup-pstack` は `claude:fable@max`、`codex:gpt-5.6-sol@max`、`grok:grok-4.6@xhigh` のような移植可能なディスクリプタを書き込む。Codex が親のとき、ネイティブなのは `codex:*` だけである。Claude と Grok のディスクリプタは、`provider-dispatch.md` が指定するとおりに外部ランチャーを通してルーティングする。現在の既定パネルは意図的に 4 プロバイダのフロンティアの多様性を保っており、古い GPT や Claude の代替は含まない。

## pstack が参照する Claude の組み込みスキル

一部のトリガーは pstack ではなく Claude Code に同梱されるスキルを挙げている。それらは Codex には存在しない。挙動を代替する:

| pstack で挙げられる Claude 組み込み | Codex では |
|---------------------------------|----------|
| `run`（CLI/TUI を動かして変更が機能するのを見る） | `shell` で自分でアプリを実行し、実際の出力を観察する。 |
| `verify`（UI を動かして修正を確認する） | 手元にある自動化手段で UI を操作するか、ユーザーに具体的な手動確認を渡す。成果物を観察せずに完了を主張しない。 |
| `plugin-dev:skill-development`（Claude の SKILL.md 執筆ガイダンス） | 自分のプラットフォームのスキル執筆ガイダンスに従う。あれば `writing-skills` スキル。`name` + `description` のフロントマターと段階的開示を保つ。 |
| `loop`（`babysit` が使う、定期的または自己ペースの再呼び出し） | Codex に `loop` スキルはない。自分で一定の間隔でステップを再実行するか、利用できるなら Codex のスケジュールされたタスクを使う。 |

## 同梱スクリプト

`skills/poteto-mode/scripts/` には PR 監視の `watch-pr`、ストア CLI の `orch`、`worktree-audit.sh`、`runner/pstack-runner` が同梱されている。これらは素の bun と bash なので Codex でも同じように動く。`shell` を通して呼び出す。外部ランナーはさらに、割り当てられた `claude`、`codex`、`grok` の実行ファイルがすでに認証済みであることを必要とする。Codex が親のときは Codex プロバイダを拒否する。そのレーンはネイティブの `spawn_agent` に属するからである。他のスクリプトには `bun`、`gh`、（スタック作業には）`gt`、（`worktree-audit.sh` には）`jq` と `rg` が必要である。`worktree-audit.sh` は `~/.claude/projects/` 配下の Claude Code トランスクリプトを読む。別の場所で実行するときは、代わりに自分のランタイムのトランスクリプトディレクトリを指すようにする。

## 指示ファイル

pstack のスキルが「自分の指示ファイル」と言う箇所は、Codex では `AGENTS.md`（プロジェクトルート、加えてグローバルの `~/.codex/AGENTS.md`）である。Claude Code では `CLAUDE.md` である。
