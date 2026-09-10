# po: Progressive Outlining for Claude Code と Codex

Andrew Ng の Progressive Outlining（アウトライン → 批評 → 箇条書き → 本文）をコードに移した、段階制のスキル群。

| 文章 | コード | Claude Code | Codex |
|---|---|---|---|
| 章立て・要件 | ディレクトリ構成・モジュール境界・EARS 要件 | `/po:outline-01` | `$outline-01` |
| 批評 | 別コンテキストでのルーブリック審査 | `/po:critique-02` | `$critique-02` |
| 箇条書き | 型・シグネチャ・テスト名（型検査は通す） | `/po:skeleton-03` | `$skeleton-03` |
| 本文 | 実装 | `/po:implement-04` | `$implement-04` |

設計原則:

- 段階ごとの成果物を `docs/progressive-outlining/<slug>/` にファイルとして残す
- 段階遷移は人間が決める。各スキルはユーザーが名前を明示した場合だけ使い、Codex は `agents/openai.yaml` でも暗黙起動を無効にする
- 批評は会話履歴を持たない別コンテキストで行う。Claude Code は `po:critic`、Codex は `fork_turns: "none"` のサブエージェントを使う
- Claude Code は outline と critique の間、`docs/progressive-outlining/` 以外への Write と Edit をフックでブロックする

## 導入

### Claude Code

```bash
# 前提: フックの JSON 解析に jq（無ければ python3 にフォールバック）

# A) 個人用として常時ロード（次回セッションから po@skills-dir として自動ロード）
cp -r skills/progressive-outlining ~/.claude/skills/po
chmod +x ~/.claude/skills/po/scripts/*.sh

# B) 試すだけ
claude --plugin-dir ./skills/progressive-outlining

# 検証
claude plugin validate ./skills/progressive-outlining
```

プロジェクトで共有する場合は `<repo>/.claude/skills/po/` に置く。

### Codex

Codex は4スキルを個別に読み込む。リポジトリルートで次を実行する。

```bash
mkdir -p ~/.codex/skills
cp -r skills/progressive-outlining/skills/{outline-01,critique-02,skeleton-03,implement-04} ~/.codex/skills/
```

次回の Codex セッションから各スキルを `$skill-name <slug>` で実行できる。

## 使い方

```
# Claude Code
/po:outline-01 auth-refactor     # 議論を何往復か。成果物: docs/progressive-outlining/auth-refactor/01-outline.md
/po:critique-02 auth-refactor    # 別コンテキストで批評 → 02-critique.md
/po:outline-01 auth-refactor     # 批評を反映（再入可）
/po:skeleton-03 auth-refactor    # 型・シグネチャ・テスト名。型検査を通す → 03-skeleton.md
/po:critique-02 auth-refactor    # スケルトンの批評 → 04-critique.md
/po:implement-04 auth-refactor   # 本体を埋める → 05-implement-notes.md
/code-review

# Codex
$outline-01 auth-refactor
$critique-02 auth-refactor
$outline-01 auth-refactor
$skeleton-03 auth-refactor
$critique-02 auth-refactor
$implement-04 auth-refactor
```

段階は `docs/progressive-outlining/.stage` に記録される。ガードを外すには:

```bash
echo off > docs/progressive-outlining/.stage    # または rm docs/progressive-outlining/.stage
```

## 構成

```
po/
├── .claude-plugin/plugin.json
├── skills/
│   ├── outline-01/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── critique-02/
│   │   ├── SKILL.md
│   │   ├── rubric.md          # ← 自分の設計原則に合わせて編集する
│   │   └── agents/openai.yaml
│   ├── skeleton-03/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   └── implement-04/
│       ├── SKILL.md
│       └── agents/openai.yaml
├── agents/critic.md           # 読み取り中心（Read, Grep, Glob, Write）
├── hooks/hooks.json           # PreToolUse: Write|Edit|MultiEdit|NotebookEdit
└── scripts/
    └── po-guard.sh            # 段階外の書き込みを exit 2 でブロック
```

## カスタマイズ

- **rubric.md**: 批評の質はここで決まる。「判定できる問い」の形を保つ。
- **批評モデル**: `agents/critic.md` の frontmatter に `model: opus` などを足すと、批評だけ強いモデルで回せる。
- **ガード対象**: `po-guard.sh` は「outline / critique では docs/progressive-outlining/ 以外禁止」という単純な規則。src/ のパターン指定より言語・レイアウトに依存しない。

## 既知の制約

- ガードは Write / Edit 系ツールのみ対象。Bash の `cat > file` は素通りする。塞ぐなら `hooks.json` の matcher に `Bash` を足し、コマンド文字列をリダイレクトで検査する。
- `skeleton` 段階で「本体を書かない」ことは決定論的に検査できない（言語依存）。指示と批評で担保する。
- `agent: po:critic` の名前解決がうまくいかない場合は `agent: critic` を試す。`claude --debug` でエージェント登録名を確認できる。
- Codex は Claude Code のフックを実行しない。outline と critique の書き込み範囲は各 `SKILL.md` の指示で制限する。
- Codex のサブエージェント機能が無効な場合、`critique-02` は別コンテキストで批評できない。
