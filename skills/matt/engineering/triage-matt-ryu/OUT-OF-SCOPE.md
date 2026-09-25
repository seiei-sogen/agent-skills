# 範囲外ナレッジベース

リポジトリ内の `.out-of-scope/` ディレクトリは、却下された機能要求の永続的な記録を保存します。これは 2 つの目的で使用されます:

1. **組織の記憶**：なぜある機能が却下されたのか、問題がクローズされたときに理由が失われないようにするもの
2. **重複排除**：新しい問題が以前の却下と一致する場合、スキルは再度議論するのではなく、前回の決定を示すことができる

## ディレクトリ構造

```
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```

1つのファイルにつき**概念**ごとに作成し、問題ごとではない。同じことを要求する複数の問題は1つのファイルにまとめる。

## ファイル形式

ファイルは、データベースのエントリというよりも、短い設計文書のように、リラックスした読みやすいスタイルで書くべきです。段落、コードサンプル、例を使用して、初めてそれに触れる人にとっても理由付けが明確で役立つようにしてください。

```markdown
# Dark Mode

This project does not support dark mode or user-facing theming.

## Why this is out of scope

The rendering pipeline assumes a single color palette defined in
`ThemeConfig`. Supporting multiple themes would require:

- A theme context provider wrapping the entire component tree
- Per-component theme-aware style resolution
- A persistence layer for user theme preferences

This is a significant architectural change that doesn't align with the
project's focus on content authoring. Theming is a concern for downstream
consumers who embed or redistribute the output.

```ts
// 現在の ThemeConfig インターフェースはランタイムでの切り替え用に設計されていません:
interface ThemeConfig {
  colors: ColorPalette; // 単一のパレット、ビルド時に解決されます
  fonts: FontStack;
}
```

## Prior requests

- #42: "Add dark mode support"
- #87: "Night theme for accessibility"
- #134: "Dark theme option"
```

### ファイルの名前付け

コンセプトには短く、説明的なケバブケースの名前を使用してください: `dark-mode.md`, `plugin-system.md`, `graphql-api.md`。名前は、ディレクトリを閲覧している人がファイルを開かなくても何が却下されたのか理解できる程度に認識可能であるべきです。

### 理由の記述

理由は実質的であるべきです：「私たちはこれを望まない」というだけではなく、なぜなのかを示す必要があります。適切な理由の参考：

- プロジェクトの範囲や方針（「このプロジェクトはXに焦点を当てている。テーマ化は後の課題である」）
- 技術的制約（「これをサポートするにはYが必要であり、それは私たちのZアーキテクチャと矛盾する」）
- 戦略的決定（「Bの代わりにAを使用することにした理由は…」）

理由は持続可能であるべきです。一時的な状況（「今は忙しすぎる」など）を参照するのは避けてください。それらは本当の拒否ではなく、延期にすぎません。

## `.out-of-scope/` をいつ確認するか

トリアージ中（ステップ1：コンテキストを収集）、`.out-of-scope/`内のすべてのファイルを読みます。新しい問題を評価する際には：

- リクエストが既存の範囲外の概念と一致するか確認する
- マッチングはキーワードではなく概念の類似性によります：「夜のテーマ」が`dark-mode.md`にマッチします
- 一致がある場合は、メンテナーに提示してください：「これは`.out-of-scope/dark-mode.md`に似ています。以前に[理由]のため却下しました。まだ同じように感じますか？」

メンテナーは次のことができます:

- **確認**：新しい問題が既存ファイルの「以前のリクエスト」リストに追加され、その後閉じられる
- **再考**: 範囲外のファイルは削除または更新され、問題は通常のトリアージを通じて進行します
- **異議あり**: 問題は関連していますが別個のものであり、通常のトリアージを進めます

## いつ`.out-of-scope/`に書き込むか

**強化**（バグではなく）が`wontfix`として*却下*された場合のみです。これは、強化のPRにも問題と同様に適用されます：却下されたPRはここに記録され、同じリクエストが新しいコードとして戻ってこないようにします。

**`wontfix`**として何かがクローズされたときには、ここに書かないでください。なぜなら、それは**すでに実装されている**からです。それは拒否されたものではなく、組み込みの機能です。記録すると、重複排除チェックに偽の拒否として影響を与えてしまいます。代わりに、クローズ時のコメントはその機能がすでに存在する場所を示します。

フロー:

1. - メンテナーが機能要望が範囲外だと判断する
2. - 該当する**`.out-of-scope/`**ファイルがすでに存在するか確認する
3. もしはいの場合: 新しい問題を「以前のリクエスト」リストに追加する
4. もしいいえの場合: 概念名、決定、理由、および最初の以前のリクエストを含む新しいファイルを作成する
5. 問題にコメントを投稿して決定を説明し、`.out-of-scope/`ファイルに言及する
6. `wontfix`ラベルで問題をクローズする

## 範囲外のファイルを更新または削除する

メンテナーが以前に却下された概念に対して考えを変えた場合:

- `.out-of-scope/`ファイルを削除する
- スキルは古い問題を再度開く必要はありません; それらは履歴記録です
- 再検討を引き起こした新しい問題は通常のトリアージを通じて進行します
