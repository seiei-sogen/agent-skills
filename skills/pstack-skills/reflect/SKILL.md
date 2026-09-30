---
name: reflect
description: 現在のトランスクリプトに対して 3 つのレビューサブエージェントを並列に起動し、学びを掘り起こし、それぞれを既存スキルへの具体的な編集にルーティングする。ユーザーが reflect と言ったときに使う。
---

# Reflect

現在の会話から長持ちする学びを掘り起こし、スキルの編集へルーティングする。

**ディスパッチ契約。** 設定済みのすべてのロールを [`provider-dispatch.md`](../poteto-mode/references/provider-dispatch.md) を通じて解決する。レビュアーは親のライブな MCP サーフェスを必要とするので、既定でありサポートされる可搬なルートは `inherit-parent`（またはそのエイリアス `auto`）である。トランスクリプトまたはダイジェストと、必要な証拠パスを渡す。Codex では、残りの Claude ツール名を [`codex-tools.md`](../poteto-mode/references/codex-tools.md) を通じて解決する。

## 起動する場面

ユーザーが「reflect」または「/reflect」と言ったときに起動する。会話が些細なもの、本題から外れたもの、または親が正しく従った既存スキルですでにカバーされているものであれば省略する。一度きりの出来事は学びではない。

## プロセス

### 1. 現在のトランスクリプトを特定する

親はファンアウトする前に自身のトランスクリプトファイルを見つける。システムプロンプトには Claude Code のプロジェクトごとのトランスクリプトディレクトリが `~/.claude/projects/<encoded-cwd>/` として記されている。そのパスを使う。`~/.claude/projects/` 全体に glob をかけてはならない。それはワークスペースの境界を越え、無関係なプロジェクトの私的なチャットを読むことになる。

```bash
ls -t ~/.claude/projects/<encoded-cwd>/*.jsonl 2>/dev/null | head -10
```

トランスクリプトのレイアウトは 3 種類ある。旧式のフラット（`<id>.jsonl`）、現行のネスト（`<id>/<id>.jsonl`）、サブエージェント（`<parent>/subagents/<child>.jsonl`）である。

候補ごとに JSONL の最初の行を読み、`message.content[0].text` に会話の最初のユーザープロンプトが含まれることを確認する。一致したパスを採用する。どのパスも解決できなければ、セッションの簡潔なダイジェストを書き、代わりにそれを渡す。

### 2. 3 つのレビュアーを並列に起動する

プロバイダディスパッチを通じて、読み取り専用の 3 レーンをすべて 1 回のファンアウトフェーズで開始する。レビュアーはコンテキストの参照（トランスクリプトで言及されたチケット、チャットスレッド、オブザーバビリティのトレース）のために MCP アクセスを必要とするので、親にネイティブなまま保つ。プロンプトはファイル書き込みを禁じる。編集を適用するのは親である。

| レンズ | モデルディスクリプタ | プロンプトテンプレート |
|---|---|---|
| Judgment | 設定済みの reflect-judgment の選択（既定 `inherit-parent`） | `references/judgment-reviewer.md` |
| Tooling | 設定済みの reflect-tooling の選択（既定 `inherit-parent`） | `references/tooling-reviewer.md` |
| Divergent | 設定済みの reflect-judgment の選択（既定 `inherit-parent`） | `references/divergent-reviewer.md` |

各テンプレートを一字一句そのまま渡し、印のある箇所にトランスクリプトのパスまたはダイジェストを差し込む。レビュアーは `Agent` の応答本文で指摘を返す。

### 3. 統合する

設定済みの reflect-judgment ディスクリプタ（既定 `inherit-parent`）で 1 レーンをディスパッチする。シンセサイザー（統合役）は引用を抜き取り検証するので、関連する MCP アクセスを保つ。`references/synthesizer.md` を一字一句そのまま使い、印のある箇所に各レビュアーの全出力をインラインで差し込む。シンセサイザーは構造化された Accepted / Rejected / Backlog のリストを返す。

### 4. 構造的な強制のチェック

シンセサイザーの Accepted リストを健全性チェックする。リントルール、スクリプト、メタデータフラグ、または実行時チェックのほうが確実に強制できる項目があれば、Accepted から Backlog へ移す。**encode-lessons-in-structure** 原則スキルを参照する。

### 5. 適用する

Accepted の編集を適用する前に、シンセサイザーの Accepted/Rejected/Backlog の全出力をユーザーに提示し、明示的な承認を待つ。ユーザーが適用するサブセットを選び、ルーティングを変更することもある。スキルの変更は組織内の将来のすべてのエージェントに影響する。自動で適用してはならない。

Backlog 項目は、チームが使っている devex / バックログトラッカーへ自動で起票する。承認を待つのは Accepted リストだけである。

承認された Accepted 項目ごとに、Routing フィールドに正確に従う。

- 既存スキルへの些細な編集（1 行の箇条書き、文の引き締め、古くなった事実の修正）: 親が直接行う。
- 既存スキルへの実質的な編集（新しいセクション、新しいパターン表、およそ 10 行を超えるもの）: **plugin-dev:skill-development** スキルに引き渡し、その起草 / テスト / 反復のループを実行する。
- `tune description: <skill path>`（スキルは存在するが、トリガーすべきときにトリガーしなかった）: `plugin-dev:skill-development` に引き渡し、その description 最適化ループを実行する。
- `new skill via plugin-dev:skill-development: <kebab-name>`: 作成を `plugin-dev:skill-development` に引き渡す。形をその場ででっち上げてはならない。

環境に SKILL.md バリデータが同梱されているなら、完了を宣言する前に、触ったすべてのスキルに対して実行する。同梱されていなければこのステップは省略する。

### 6. ユーザーへ要約する

前置きなしの短いリスト。

- 適用した編集: `<skill path>`。何が変わったか、それぞれ 1 行。
- 作成した新スキル: `<skill path>`。それぞれ 1 行（まれ）。
- devex トラッカーへ起票した Backlog: `<issue title>`（`<tags>`）。それぞれ 1 行。
- 却下: 却下された指摘ごとに 1 行と、シンセサイザーからの理由。
