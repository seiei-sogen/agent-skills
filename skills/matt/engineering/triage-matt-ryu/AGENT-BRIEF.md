# エージェントブリーフの作成

エージェントブリーフとは、GitHubのイシューまたはPRが`ready-for-agent`に移動したときに投稿される構造化されたコメントです。これは、AFKエージェントが作業する際の権威ある仕様です。元の本文と議論はコンテキストとして扱われます：エージェントブリーフが契約です。

ブリーフには**エージェントが何をすべきか**が記載されており、両方の面に及びます：問題の場合、それは何もないところから変更を作り上げることです；PRの場合、それは*既存の差分に対して*残っている作業です：完了させる、ギャップを埋める、レビューの指摘に対応する。どちらの場合も原則は同じです；以下のPRの例がその違いを示しています。

## 原則

### 正確さよりも耐久性

この問題は`ready-for-agent`の中で数日から数週間残ることがあります。その間にコードベースは変更されます。ファイルが名前変更、移動、またはリファクタリングされても役立つようにブリーフを書いてください。

- **すべきこと** インターフェース、型、挙動の契約を説明する
- **すべきこと** エージェントが探すべき、または変更すべき特定の型、関数シグネチャ、設定の形を名前で示す
- **してはいけないこと** ファイルパスを参照しない: 時間が経つと古くなります
- **行番号を**参照しないでください
- **現在の実装構造が**そのまま維持されると仮定しないでください

### 手順的ではなく、振る舞いに関するものです

システムが**何をするべきか**を説明し、**どのように実装するか**は説明しないでください。エージェントはコードベースを新たに探索し、自分自身で実装方法を決定します。

- **良い例:** "`SkillConfig`型は、`CronExpression`型のオプションの`schedule`フィールドを受け入れるべきです"
- **悪い例:** 「src/types/skill.ts を開き、42行目に schedule フィールドを追加する」
- **良い例:** 「ユーザーが引数なしで `/triage-matt-ryu` を実行したとき、注意が必要な問題の概要が表示されるべきである」
- **悪い例:** 「メインハンドラ関数に switch 文を追加する」

### 受け入れ基準を完全にする

エージェントは、作業が完了した時を認識する必要があります。すべてのエージェントブリーフには具体的でテスト可能な受け入れ基準が必要です。各基準は独立して検証可能であるべきです。

- **良い例:** 「`gh issue list --label needs-triage`を実行すると、初期分類を経た問題が返される」
- **悪い例:** 「トリアージが正しく機能するべき」

### 明確な範囲の境界

範囲外のものを明示してください。これにより、エージェントが過剰に作り込んだり、隣接する機能について推測したりするのを防げます。

## テンプレート

```markdown
## Agent Brief

**Category:** bug / enhancement
**Summary:** one-line description of what needs to happen

**Current behavior:**
Describe what happens now. For bugs, this is the broken behavior.
For enhancements, this is the status quo the feature builds on.

**Desired behavior:**
Describe what should happen after the agent's work is complete.
Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName`: what needs to change and why
- `functionName()` return type: what it currently returns vs what it should return
- Config shape: any new configuration options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] Specific, testable criterion 3

**Out of scope:**
- Thing that should NOT be changed or addressed in this issue
- Adjacent feature that might seem related but is separate
```

## 例

### 良いエージェントブリーフ（バグ）

```markdown
## Agent Brief

**Category:** bug
**Summary:** Skill description truncation drops mid-word, producing broken output

**Current behavior:**
When a skill description exceeds 1024 characters, it is truncated at exactly
1024 characters regardless of word boundaries. This produces descriptions
that end mid-word (e.g. "Use when the user wants to confi").

**Desired behavior:**
Truncation should break at the last word boundary before 1024 characters
and append "..." to indicate truncation.

**Key interfaces:**
- The `SkillMetadata` type's `description` field: no type change needed,
  but the validation/processing logic that populates it needs to respect
  word boundaries
- Any function that reads SKILL.md frontmatter and extracts the description

**Acceptance criteria:**
- [ ] Descriptions under 1024 chars are unchanged
- [ ] Descriptions over 1024 chars are truncated at the last word boundary
      before 1024 chars
- [ ] Truncated descriptions end with "..."
- [ ] The total length including "..." does not exceed 1024 chars

**Out of scope:**
- Changing the 1024 char limit itself
- Multi-line description support
```

### 良いエージェントブリーフ（機能追加）

```markdown
## Agent Brief

**Category:** enhancement
**Summary:** Add `.out-of-scope/` directory support for tracking rejected feature requests

**Current behavior:**
When a feature request is rejected, the issue is closed with a `wontfix` label
and a comment. There is no persistent record of the decision or reasoning.
Future similar requests require the maintainer to recall or search for the
prior discussion.

**Desired behavior:**
Rejected feature requests should be documented in `.out-of-scope/<concept>.md`
files that capture the decision, reasoning, and links to all issues that
requested the feature. When triaging new issues, these files should be
checked for matches.

**Key interfaces:**
- Markdown file format in `.out-of-scope/`: each file should have a
  `# Concept Name` heading, a `**Decision:**` line, a `**Reason:**` line,
  and a `**Prior requests:**` list with issue links
- The triage workflow should read all `.out-of-scope/*.md` files early
  and match incoming issues against them by concept similarity

**Acceptance criteria:**
- [ ] Closing a feature as wontfix creates/updates a file in `.out-of-scope/`
- [ ] The file includes the decision, reasoning, and link to the closed issue
- [ ] If a matching `.out-of-scope/` file already exists, the new issue is
      appended to its "Prior requests" list rather than creating a duplicate
- [ ] During triage, existing `.out-of-scope/` files are checked and surfaced
      when a new issue matches a prior rejection

**Out of scope:**
- Automated matching (human confirms the match)
- Reopening previously rejected features
- Bug reports (only enhancement rejections go to `.out-of-scope/`)
```

### 良いエージェントブリーフ（プルリクエスト）

プルリクエストの場合、「現在の動作」は差分の状態を示し、ブリーフはエージェントに最初から作るのではなく、完成させるまたは修正するよう依頼します。

```markdown
## Agent Brief

**Category:** enhancement
**Summary:** Finish the contributor's `--json` output flag for `triage list`

**Current behavior:**
The PR adds a `--json` flag that serializes the issue list to JSON. The happy
path works and the diff matches the project's command structure. Two gaps
remain: errors are still printed as human text (not JSON), and the new flag has
no test coverage.

**Desired behavior:**
With `--json`, all output (including errors) is well-formed JSON on stdout,
and the command's exit codes are unchanged. The existing human-readable output
is untouched when the flag is absent.

**Key interfaces:**
- The command's error path should emit `{ "error": string }` under `--json`
  instead of the plain-text error
- Reuse the existing serializer the PR already added; don't introduce a second

**Acceptance criteria:**
- [ ] `triage list --json` emits valid JSON for both success and error cases
- [ ] Exit codes match the non-JSON command
- [ ] A test covers the `--json` success output and one error case
- [ ] Default (non-JSON) output is byte-for-byte unchanged

**Out of scope:**
- Adding `--json` to any other command
- Changing the JSON shape of the success payload the PR already defined
```

### 悪いエージェントブリーフ

```markdown
## Agent Brief

**Summary:** Fix the triage bug

**What to do:**
The triage thing is broken. Look at the main file and fix it.
The function around line 150 has the issue.

**Files to change:**
- src/triage/handler.ts (line 150)
- src/types.ts (line 42)
```

これは悪い理由:
- カテゴリなし
- あいまいな説明（「トリアージの仕組みが壊れている」）
- 古くなる参照ファイルパスと行番号
- 受け入れ基準なし
- スコープの境界なし
- 現行の動作と希望する動作の説明なし
