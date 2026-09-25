# エンジニアリング

コード作業で日常的に使用するスキル。

## ユーザー起動

ユーザーが入力したときのみ利用可能（Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`）。

- **[ask-matt-matt-p](./ask-matt-matt-p/SKILL.md)**: 自分の状況に合うスキルやフローを問い合わせます。このリポジトリのユーザー起動スキル上のルーター。
- **[grill-with-docs-matt-p](./grill-with-docs-matt-p/SKILL.md)**: プロジェクトのドメインモデルを構築しながらグリルするセッションで、専門用語を磨き、`CONTEXT.md` および ADR をインラインで更新します。
- **[triage-matt-p](./triage-matt-p/SKILL.md)**: 課題をトリアージの役割の状態機械を通じて移動させます。
- **[improve-codebase-architecture-matt-p](./improve-codebase-architecture-matt-p/SKILL.md)**: コードベースをスキャンして改善の機会を深め、視覚的な HTML レポートとして提示し、その中から選んだものをグリルします。
- **[setup-matt-pocock-skills-matt-p](./setup-matt-pocock-skills-matt-p/SKILL.md)**: このリポジトリをエンジニアリングスキル用に設定します（課題トラッカー、トリアージラベル、ドメインドキュメントの配置）。リポジトリごとに一度実行してください。
- **[to-spec-matt-p](./to-spec-matt-p/SKILL.md)**: 現在の会話を仕様に変換し、課題トラッカーに公開します。
- **[to-tickets-matt-p](./to-tickets-matt-p/SKILL.md)**: 任意のプラン、仕様、または会話を一連のトレイサーブレットチケットに分解し、それぞれが依存関係を宣言します。これは、ローカルファイル内のテキストとしてでも、実際のトラッカー上のネイティブブロッキングリンクとしてでもかまいません。
- **[implement-matt-p](./implement-matt-p/SKILL.md)**: 仕様または一連のチケットによって記述された作業を構築し、事前に合意された継ぎ目で`/tdd-matt-p`を推進し、コミット前に`/code-review-matt-p`を完了させます。
- **[wayfinder-matt-p](./wayfinder-matt-p/SKILL.md)**: 問題トラッカー上での意思決定チケットの共有マップとして、1つのエージェントセッションで処理できる以上の大規模な作業を計画し、目的地への道が明確になるまで1つずつ解決します。

## モデル呼び出し可能

モデルまたはユーザーが到達可能（モデルがアクセスできるように豊富なトリガーフレーズを使用）

- **[prototype-matt-p](./prototype-matt-p/SKILL.md)**: デザインの質問に答えるための使い捨てプロトタイプを作成する：状態/ロジック用の単一の共有可能なHTMLファイル、または複数の切り替え可能なUIバリエーション。

- **[diagnosing-bugs-matt-p](./diagnosing-bugs-matt-p/SKILL.md)**: 難しいバグやパフォーマンス低下のための規律ある診断ループ：このバグで赤になるフィードバックループを作る → 最小化 → 仮説立て → 計測 → 修正 → リグレッションテスト。
- **[research-matt-p](./research-matt-p/SKILL.md)**: 高信頼の一次情報源に対して質問を調査し、調査結果を引用付きのMarkdownファイルとしてリポジトリに保存し、バックグラウンドエージェントとして実行します。
- **[tdd-matt-p](./tdd-matt-p/SKILL.md)**: レッド・グリーン・リファクタリングのループによるテスト駆動開発。機能の構築やバグ修正を垂直方向に一切れずつ行います。
- **[domain-modeling-matt-p](./domain-modeling-matt-p/SKILL.md)**: 用語に挑戦し、シナリオでストレステストを行い、`CONTEXT.md`やADRをインラインで更新することで、プロジェクトのドメインモデルを積極的に構築・洗練する。
- **[codebase-design-matt-p](./codebase-design-matt-p/SKILL.md)**: 小さなインターフェース、クリーンな境界、インターフェースを通じてテスト可能なモジュール設計のための共有規律と語彙。
- **[code-review-matt-p](./code-review-matt-p/SKILL.md)**: 固定ポイント以降の差分に対する二軸レビュー：**Standards**（リポジトリのコーディング規約に従っているか、さらにFowlerのスメルベースラインも含む）および**Spec**（元の課題/仕様を忠実に実装しているか）、並列サブエージェントとして実行。
- **[resolving-merge-conflicts-matt-p](./resolving-merge-conflicts-matt-p/SKILL.md)**: 進行中の git マージまたはリベースの競合をハンクごとに処理し、それぞれのサイドの主要なソースに追跡された意図に基づいて解決し、その後操作を完了します、決して `--abort` しない。
- **[wizard-matt-p](./wizard-matt-p/SKILL.md)**: インタラクティブなBashウィザードを生成し、人間が実行できるステップ（インフラのプロビジョニング、資格情報やCIシークレットの設定、慣れていないサードパーティのダッシュボードの操作、または一度限りのマイグレーションやカットオーバーの実行）を案内します。
