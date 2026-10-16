# judge 統合テスト実行手順

`SKILL_JUDGE.md`（TASK-0017）と `tests/samples/*.md`（TASK-0016）を組み合わせて、7 サンプル × 8 観点 = **56 判定**を実行する手順。実機 LLM 推論を含むため、本ファイルはユーザーが手動実行する際の運用手順を整理したもの。

## 前提

- AI 実行コマンド: `claude --print --model claude-opus-4-6 --tools ""`（codd.yaml 由来）
- 配置: TASK-0019 / TASK-0020 で確定したパス（`.claude/skills/lakkhanadi-catukka/` または `.agents/skills/lakkhanadi-catukka/` 等）
- 実行ログ保存先: `/tmp/judge-run-<timestamp>/`（git 管理対象外。最終集計のみ docs にコミット）

## ステップ 1: Skill 推論実行

各サンプルの本文（フロントマター以下）を Skill に渡し、出力を保存する。

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
RUN_DIR="/tmp/judge-run-$TS"
mkdir -p "$RUN_DIR"

for sample in core-classical core-psychological core-technical \
              len-short len-detailed safety-medical norm-iast; do
  # フロントマターを除いた本文を抽出
  BODY=$(awk 'BEGIN{p=0} /^---$/{p++; next} p==2{print}' \
         "skills/lakkhanadi-catukka/tests/samples/${sample}.md")

  echo "$BODY" | claude --print --model claude-opus-4-6 --tools "" \
    --skill skills/lakkhanadi-catukka \
    > "$RUN_DIR/output-${sample}.md"
done
```

> 実コマンド形式（`--skill` フラグ等）は Claude Code / Codex CLI 仕様に応じて `docs/governance/adr_skill_platform.md` を参照のうえ調整すること。

## ステップ 2: judge 入力ペイロード作成

各 Skill 出力に「期待値」を添えて judge 入力を組み立てる。期待値はサンプルファイルのフロントマターから取得する。

```bash
for sample in core-classical core-psychological core-technical \
              len-short len-detailed safety-medical norm-iast; do
  # フロントマターから期待値を抽出
  MODE=$(awk -F': ' '/^expectedMode:/{print $2}' \
         "skills/lakkhanadi-catukka/tests/samples/${sample}.md")
  CANON=$(awk -F': ' '/^expectedCanonicality:/{print $2}' \
          "skills/lakkhanadi-catukka/tests/samples/${sample}.md")
  SAFETY=$(awk -F': ' '/^expectedSafety:/{print $2}' \
           "skills/lakkhanadi-catukka/tests/samples/${sample}.md")

  cat > "$RUN_DIR/judge-input-${sample}.md" <<EOF
## 評価対象

### sampleId
${sample}

### Skill 出力
$(cat "$RUN_DIR/output-${sample}.md")

### 期待モード
${MODE}

### 期待 canonicality
${CANON}

### 期待 safety
${SAFETY}
EOF
done
```

## ステップ 3: judge 実行

各 judge 入力に対し SKILL_JUDGE.md を適用し、JSON レポートを取得する。

```bash
for sample in core-classical core-psychological core-technical \
              len-short len-detailed safety-medical norm-iast; do
  cat skills/lakkhanadi-catukka/tests/judge/SKILL_JUDGE.md \
      "$RUN_DIR/judge-input-${sample}.md" \
    | claude --print --model claude-opus-4-6 --tools "" \
    > "$RUN_DIR/judge-result-${sample}.txt"

  # JSON コードブロックを抽出
  awk '/^```json$/{p=1; next} /^```$/{p=0} p' \
    "$RUN_DIR/judge-result-${sample}.txt" \
    > "$RUN_DIR/judge-result-${sample}.json"
done
```

## ステップ 4: JSON パース可能性の確認

`jq` または `serde_json` で全件パース可能であることを確認する（TASK-0018 単体テスト 1）。

```bash
for sample in core-classical core-psychological core-technical \
              len-short len-detailed safety-medical norm-iast; do
  if jq empty "$RUN_DIR/judge-result-${sample}.json" 2>/dev/null; then
    echo "OK: $sample"
  else
    echo "PARSE FAILED: $sample"
  fi
done
```

## ステップ 5: 8 観点完備の確認

各 JSON の `aspects` 配列に 8 観点すべてが含まれることを確認する（TASK-0018 単体テスト 2）。

```bash
EXPECTED_ASPECTS='four-sections-coverage detail-sentence-count concrete-examples modern-paraphrase observational-tone applied-marker summary-table-rows safety-advisory'

for sample in core-classical core-psychological core-technical \
              len-short len-detailed safety-medical norm-iast; do
  for asp in $EXPECTED_ASPECTS; do
    if jq -e ".aspects[] | select(.aspect==\"$asp\")" \
       "$RUN_DIR/judge-result-${sample}.json" >/dev/null 2>&1; then
      :
    else
      echo "MISSING ASPECT: $sample / $asp"
    fi
  done
done
```

## ステップ 6: 集計表の作成

`summary-template.md` のテーブルを埋めて `$RUN_DIR/summary.md` を作成。集計結果は最終的に `docs/release/v0.1.0-checklist.md`（TASK-0021）へ反映。

```bash
cp skills/lakkhanadi-catukka/tests/judge/summary-template.md \
   "$RUN_DIR/summary.md"
# 各サンプルの judge-result-*.json から verdict を抜き出してテーブルを埋める（手動 or 簡易スクリプト）
```

## ステップ 7: フィードバックループ（fail があった場合）

`overallPass: false` のサンプルがあれば、以下のマップで該当する SKILL.md セクションに修正を加える:

| fail 観点 | 主な修正対象 SKILL.md セクション |
|---|---|
| `four-sections-coverage` / `summary-table-rows` | 「出力テンプレート」（TASK-0005 起源） |
| `detail-sentence-count` | 「3. 長さモード判定」「6. 四相生成チェックリスト §6.2」（TASK-0007） |
| `concrete-examples` | 「6. 四相生成チェックリスト §6.1」（TASK-0011） |
| `modern-paraphrase` | 「全体方針」「6.3」（TASK-0011） |
| `observational-tone` | 「全体方針」「6.6」「4.5」（TASK-0008, 0011） |
| `applied-marker` | 「5. 古典 vs 応用判定」（TASK-0009） |
| `safety-advisory` | 「4. 安全性判定 + 観察的捉え直し」（TASK-0008） |

修正後は対象サンプルを再実行 → 再判定 → pass を確認し、リグレッション防止のため他 6 サンプルも再判定する。

## ステップ 8: judge ばらつき確認

同じ Skill 出力（例: `core-classical`）に対して judge を 3 回実行し、`aspects[].verdict` が一貫することを確認する。揺らぎが出る観点があれば `SKILL_JUDGE.md` の判定指示を強化する（TASK-0017 へフィードバック）。

```bash
for run in 1 2 3; do
  cat skills/lakkhanadi-catukka/tests/judge/SKILL_JUDGE.md \
      "$RUN_DIR/judge-input-core-classical.md" \
    | claude --print --model claude-opus-4-6 --tools "" \
    > "$RUN_DIR/judge-stability-run${run}.txt"
done

# 3 回の verdict を比較
diff <(jq -r '.aspects[]|"\(.aspect):\(.verdict)"' "$RUN_DIR/judge-stability-run1.txt") \
     <(jq -r '.aspects[]|"\(.aspect):\(.verdict)"' "$RUN_DIR/judge-stability-run2.txt")
```

## ステップ 9: 故意違反サンプルでの自己テスト

`tests/judge/fixtures-bad/*.md` の故意違反サンプルを judge にかけ、期待される観点で `fail` が返ることを確認する（TC-NFR-302-02）。

```bash
for bad in missing-section missing-examples summary-3-rows imperative-tone; do
  cat skills/lakkhanadi-catukka/tests/judge/SKILL_JUDGE.md \
      skills/lakkhanadi-catukka/tests/judge/fixtures-bad/${bad}.md \
    | claude --print --model claude-opus-4-6 --tools "" \
    > "$RUN_DIR/judge-bad-${bad}.txt"
done
```

期待値の対応は `fixtures-bad/README.md` を参照。
