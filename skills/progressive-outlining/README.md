# po — Progressive Outlining for Claude Code

Andrew Ng の Progressive Outlining（アウトライン → 批評 → 箇条書き → 本文）をコードに移した、段階制のスキル群。

| 文章 | コード | スキル |
|---|---|---|
| 章立て・要件 | ディレクトリ構成・モジュール境界・EARS 要件 | `/po:outline` |
| 批評 | 別コンテキストでのルーブリック審査 | `/po:critique` |
| 箇条書き | 型・シグネチャ・テスト名（型検査は通す） | `/po:skeleton` |
| 本文 | 実装 | `/po:implement` |

設計原則:

- 段階ごとの成果物を `docs/po/<slug>/` にファイルとして残す
- 段階遷移は人間が決める（全スキル `disable-model-invocation: true`）
- 批評は会話履歴を持たない別コンテキスト（`context: fork`）で行う
- outline / critique 段階では `docs/po/` 以外への Write / Edit をフックで決定論的にブロックする

## 導入

```bash
# 前提: フックの JSON 解析に jq（無ければ python3 にフォールバック）

# A) 個人用として常時ロード（次回セッションから po@skills-dir として自動ロード）
cp -r po ~/.claude/skills/po
chmod +x ~/.claude/skills/po/scripts/*.sh

# B) 試すだけ
claude --plugin-dir ./po

# 検証
claude plugin validate ./po
```

プロジェクトで共有したい場合は `<repo>/.claude/skills/po/` に置く（ワークスペースの信頼確認後にロードされる）。

## 使い方

```
/po:outline auth-refactor     # 議論を何往復か。成果物: docs/po/auth-refactor/01-outline.md
/po:critique auth-refactor    # 別コンテキストで批評 → 02-critique.md
/po:outline auth-refactor     # 批評を反映（再入可）
/po:skeleton auth-refactor    # 型・シグネチャ・テスト名。型検査を通す → 03-skeleton.md
/po:critique auth-refactor    # スケルトンの批評 → 04-critique.md
/po:implement auth-refactor   # 本体を埋める → 05-implement-notes.md
/code-review
```

段階は `docs/po/.stage` に記録される。ガードを外すには:

```bash
echo off > docs/po/.stage    # または rm docs/po/.stage
```

## 構成

```
po/
├── .claude-plugin/plugin.json
├── skills/
│   ├── outline/SKILL.md
│   ├── critique/
│   │   ├── SKILL.md
│   │   └── rubric.md          # ← 自分の設計原則に合わせて編集する
│   ├── skeleton/SKILL.md
│   └── implement/SKILL.md
├── agents/critic.md           # 読み取り中心（Read, Grep, Glob, Write）
├── hooks/hooks.json           # PreToolUse: Write|Edit|MultiEdit|NotebookEdit
└── scripts/
    ├── po-stage.sh            # 各スキル冒頭で `!` 注入により段階を書き込む
    └── po-guard.sh            # 段階外の書き込みを exit 2 でブロック
```

## カスタマイズ

- **rubric.md**: 批評の質はここで決まる。「判定できる問い」の形を保つ。
- **批評モデル**: `agents/critic.md` の frontmatter に `model: opus` などを足すと、批評だけ強いモデルで回せる。
- **ガード対象**: `po-guard.sh` は「outline / critique では docs/po/ 以外禁止」という単純な規則。src/ のパターン指定より言語・レイアウトに依存しない。

## 既知の制約

- ガードは Write / Edit 系ツールのみ対象。Bash の `cat > file` は素通りする。塞ぐなら `hooks.json` の matcher に `Bash` を足し、コマンド文字列をリダイレクトで検査する。
- `skeleton` 段階で「本体を書かない」ことは決定論的に検査できない（言語依存）。指示と批評で担保する。
- `agent: po:critic` の名前解決がうまくいかない場合は `agent: critic` を試す。`claude --debug` でエージェント登録名を確認できる。
- `context: fork` / `disable-model-invocation` / `arguments` / `!` 注入は Claude Code 拡張。Agent Skills 仕様準拠の他ツール（Amp 等）へ持っていく場合は、frontmatter を name / description / allowed-tools に絞り、段階制御を本文の指示に書き直す必要がある。
- `po-stage.sh` は `${CLAUDE_PROJECT_DIR}` を引数で受け取る。この置換は Claude Code v2.1.196 以降。
