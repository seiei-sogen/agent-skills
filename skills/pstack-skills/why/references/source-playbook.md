# ソースプレイブック

why スキルは利用可能な証拠カテゴリごとに調査役を 1 人起動し、それぞれが下記のソース固有のプレイブック 1 つを読む。プレイブックは一般的な MCP 向けの具体例である。同じカテゴリの別の MCP には適応させて使う。

| カテゴリ | プレイブック | 文書化している MCP の例 |
|---|---|---|
| ソース管理の履歴 | [`code-archaeology.md`](./sources/code-archaeology.md) | git、`gh` |
| issue / チケットトラッカー | [`linear.md`](./sources/linear.md) | Linear（Jira、GitHub Issues、Plane、Shortcut には適応させる） |
| 長文ドキュメント | [`notion.md`](./sources/notion.md) | Notion（Confluence、Google Docs、Coda には適応させる） |
| リアルタイムのチームチャット | [`slack.md`](./sources/slack.md) | Slack（Discord、Microsoft Teams、Mattermost には適応させる） |
| インフラ可観測性 | [`datadog.md`](./sources/datadog.md) | Datadog（New Relic、Honeycomb、Grafana、Splunk には適応させる） |
| エラー / 例外トラッキング | [`sentry.md`](./sources/sentry.md) | Sentry（Rollbar、Bugsnag、Airbrake には適応させる） |
| プロダクト分析ウェアハウス | [`databricks.md`](./sources/databricks.md) | Databricks SQL（Snowflake、BigQuery、ClickHouse、dbt には適応させる） |

横断的:

- [`incident-postmortem.md`](./sources/incident-postmortem.md)。対象コードが防御的に見える場合（null チェック、リトライ、タイムアウト、レート制限、フィーチャーフラグ、egress ガード、OOM ハンドラ）に追加する。
