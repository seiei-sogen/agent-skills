# 故意違反サンプル（fixtures-bad）

`SKILL_JUDGE.md` の自己テスト用に、特定の観点で必ず `fail` が返るよう設計された出力サンプル群（TC-NFR-302-02）。`run.md` ステップ 9 で使用。

各ファイルは「judge 入力ペイロード」の形式をとっており、`SKILL_JUDGE.md` と連結して LLM に渡すと、対応する観点で `fail` が返ることが期待される。

| ファイル | 期待 fail 観点 | 違反内容 |
|---|---|---|
| `missing-section.md` | `four-sections-coverage` | 詳説から `padaṭṭhāna（近因）` セクションを意図的に欠落 |
| `missing-examples.md` | `concrete-examples` | 詳説 4 セクションを定義の言い換えだけで埋め、具体例を一切含まない |
| `summary-3-rows.md` | `summary-table-rows` | 要約表が 3 行しかない（「近因」行欠落） |
| `imperative-tone.md` | `observational-tone` | 命令形（「〜すべき」「〜してはいけない」）と非難語を多用 |

## 検証手順

```bash
RUN_DIR="/tmp/judge-bad-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN_DIR"

for bad in missing-section missing-examples summary-3-rows imperative-tone; do
  cat skills/lakkhanadi-catukka/tests/judge/SKILL_JUDGE.md \
      skills/lakkhanadi-catukka/tests/judge/fixtures-bad/${bad}.md \
    | claude --print --model claude-opus-4-6 --tools "" \
    > "$RUN_DIR/result-${bad}.txt"
done
```

期待結果: 各 `result-*.txt` 内の JSON で、対応する観点が `verdict: "fail"` となり、`overallPass: false`。期待観点以外も巻き添えで fail になる場合があるが、**期待観点が fail であれば本テストは pass** とする（過剰検出は許容範囲）。
