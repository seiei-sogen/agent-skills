# judge 集計テンプレート

7 サンプル × 8 観点 = 56 判定の結果を以下の表で集計する。各セルは `pass` / `fail` / `n/a` のいずれか。

## 結果表

| サンプル | 4-sec | sent-cnt | examples | paraphrase | tone | marker | summary | safety | overallPass | failureCount |
|---|---|---|---|---|---|---|---|---|---|---|
| core-classical | _ | _ | _ | _ | _ | _ | _ | n/a | _ | _ |
| core-psychological | _ | _ | _ | _ | _ | _ | _ | n/a | _ | _ |
| core-technical | _ | _ | _ | _ | _ | _ | _ | n/a | _ | _ |
| len-short | _ | _ | _ | _ | _ | _ | _ | n/a | _ | _ |
| len-detailed | _ | _ | _ | _ | _ | _ | _ | n/a | _ | _ |
| safety-medical | _ | _ | _ | _ | _ | _ | _ | _ | _ | _ |
| norm-iast | _ | _ | _ | _ | _ | _ | _ | n/a | _ | _ |

凡例:
- 4-sec: `four-sections-coverage`
- sent-cnt: `detail-sentence-count`
- examples: `concrete-examples`
- paraphrase: `modern-paraphrase`
- tone: `observational-tone`
- marker: `applied-marker`
- summary: `summary-table-rows`
- safety: `safety-advisory`

## 主要 TC の judge 経由網羅状況

| TC | 紐付くサンプル | 主に確認する観点 | 結果 |
|---|---|---|---|
| TC-CORE-01 | core-classical | four-sections-coverage / summary-table-rows / applied-marker | _ |
| TC-CORE-02 | core-psychological | applied-marker / observational-tone | _ |
| TC-LEN-01 | len-short | detail-sentence-count | _ |
| TC-LEN-02 | len-detailed | detail-sentence-count | _ |
| TC-SAFE-01 | safety-medical | safety-advisory / observational-tone | _ |
| TC-NORM-03 | norm-iast | modern-paraphrase + 出力中の標準表記確認 | _ |

## judge ばらつき確認

同一サンプル `core-classical` で judge を 3 回実行した結果:

| 観点 | run1 | run2 | run3 | 一貫性 |
|---|---|---|---|---|
| four-sections-coverage | _ | _ | _ | _ |
| detail-sentence-count | _ | _ | _ | _ |
| concrete-examples | _ | _ | _ | _ |
| modern-paraphrase | _ | _ | _ | _ |
| observational-tone | _ | _ | _ | _ |
| applied-marker | _ | _ | _ | _ |
| summary-table-rows | _ | _ | _ | _ |
| safety-advisory | _ | _ | _ | _ |

## 修正履歴（fail → pass）

修正が必要だった観点と SKILL.md への修正内容を記録:

| サンプル | fail 観点 | 修正対象 SKILL.md セクション | 修正内容 | 再判定結果 |
|---|---|---|---|---|

## 備考

- 実行日時: <YYYY-MM-DD HH:MM:SS UTC>
- 実行モデル: claude-opus-4-6
- judge コマンド: `claude --print --model claude-opus-4-6 --tools ""`
- ログ保存先: `/tmp/judge-run-<timestamp>/`
