# 生産性

一般的なワークフローツール、コード固有ではありません。

## ユーザー起動型

入力したときのみアクセス可能（Claudeコード: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`）。

- **[grill-me-matt-ryu](./grill-me-matt-ryu/SKILL.md)**: 計画や設計について徹底的にインタビューされ、設計ツリーのすべての枝が解決されるまで質問される。
- **[handoff-matt-ryu](./handoff-matt-ryu/SKILL.md)**: 現在の会話をコンパクトな引き継ぎ文書にまとめ、別のエージェントが作業を続けられるようにする。
- **[teach-matt-ryu](./teach-matt-ryu/SKILL.md)**: 現在のディレクトリを状態を保持する教育用ワークスペースとして使用し、ユーザーに複数回のセッションを通じて新しいスキルまたは概念を教えます。
- **[to-questionnaire-matt-ryu](./to-questionnaire-matt-ryu/SKILL.md)**: 自分一人では答えられない決定を、その答えを知っている唯一の人のためのMarkdownアンケートに変換します（非同期で記入するか、会議で一緒に行います）。
- **[wait-what-matt-ryu](./wait-what-matt-ryu/SKILL.md)**: メッセージが届かない瞬間にこれを発動してください。そのエージェントは、あなたが欠けているコンテキストを、あなたの`CONTEXT.md`の語彙を使って、平易な英語で再提示します。

## モデル起動

モデルまたはユーザーが到達可能（モデルが参照できるように豊富なトリガーフレーズ）。

- **[grilling-matt-ryu](./grilling-matt-ryu/SKILL.md)**: 計画、決定、またはアイデアについて、デザインツリーのすべての枝が解決されるまで、ユーザーに徹底的にインタビューする。
- **[writing-for-agents-matt-ryu](./writing-for-agents-matt-ryu/SKILL.md)**: エージェント向けのドキュメント作成：スキル、AGENTS.md/CLAUDE.md、およびエージェントがポインタを通じてアクセスする任意のドキュメント。
