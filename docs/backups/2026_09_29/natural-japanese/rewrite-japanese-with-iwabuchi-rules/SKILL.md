---
name: rewrite-japanese-with-iwabuchi-rules
description: >-
  岩淵「悪文」メモ由来の、文の組み立て・語の選び方・敬語・行配置に関する
  全48規則を照合し、原意・事実・仕様・技術的意味・文書構造を保って日本語を
  診断・推敲する。「岩淵ルールで直して」「この48規則で悪文をチェックして」
  「ルールID付きで推敲して」「文の組み立て・用語・敬語を網羅的に点検して」
  など、規則準拠のリライト、校正、監査、違反理由の報告を求められたときに使う。
  一般的な「悪文をチェックして」「校正して」「自然にして」「読みやすくして」
  だけの依頼には使わない。
---

# Rewrite Japanese with Iwabuchi Rules

日本語文章を48個の規則で点検し、問題のある箇所だけを最小限に推敲する。
各規則の意味IDを、診断、修正理由、要確認事項の共通識別子として使う。

## 最優先原則

- 原意、事実、仕様、技術的意味を変えない。
- 数値、固有名詞、引用、専門用語、否定、条件、例外、因果関係、時制、確実性、義務・許可の強さ、敬意の向きを保つ。
- 原文から一意に判断できない情報を補わない。必要なら規則ID付きの `要確認` にする。
- 規則を機械的に適用せず、読みやすさや正確さが実際に上がる変更だけを採用する。
- 問題のない文は変更しない。

判断が衝突する場合は、次の順序を優先する。

1. 原意・事実・仕様・技術的意味の保持
2. 文脈、係り受け、否定範囲、用語の正確さ
3. 読み手にとっての明確さ
4. 語感、敬語、簡潔さ
5. 行配置

## IDの扱い

- このスキルに記載したIDを安定した公開識別子として扱う。
- IDを省略、改名、再利用しない。元メモの不確かな通し番号は使わない。
- 一つの問題に複数の規則が関係する場合は、主となるIDを先に示し、関連IDを続ける。
- 全規則を内部で照合するが、通常は `actionable` と `needs-confirmation` のIDだけを報告する。

各状態を次の意味で使う。

- `pass`: その規則を適用でき、問題がない。
- `not-applicable`: 媒体、文体、文章の内容などから、その規則が対象外である。
- `actionable`: 規則に反する問題があり、原意を変えず安全に修正または修正提案できる。
- `needs-confirmation`: 問題または適用可能性を判断するには、原文にない情報やユーザーの意図が必要である。

## 作業手順

1. 推敲、レビューのみ、ファイル編集のどのモードかを確認する。ユーザーが「レビューだけ」と指定した場合は本文を変更しない。
2. 文章の用途、読み手、媒体、書き言葉か話し言葉か、文体、敬意を向ける相手を把握する。
3. コード、コマンド、URL、ファイルパス、API名、設定値、front matter、構造化データ、表、引用など、保護する範囲を確定する。
4. 主体、対象、述語、条件、例外、因果、否定範囲、段落ごとの論点を把握する。
5. 以下の48規則をすべて確認し、各IDを内部で `pass`、`not-applicable`、`actionable`、`needs-confirmation` のいずれかに分類する。
6. `actionable` の問題だけを、最小限の変更で修正する。
7. 修正後に全48規則を再確認し、新しい問題を作っていないか検証する。
8. 原文と比較し、保護対象、条件、例外、否定、因果、モダリティ、敬意の向きが変わっていないか確認する。

このスキルは単独で実行する。
一般的な自然化スキルや箇条書き化スキルは、ユーザーが併用を求めた場合だけ使う。

## 出力・行配置

| ID | 規則 |
|---|---|
| `output.line-break-each-line` | 元メモの「一行ごとに改行する」をそのまま規則として扱う。何を一行と数えるかが指定されている場合だけ、その単位ごとに改行する。指定がなければ `needs-confirmation` とし、現在の行配置を保つ。表、箇条書き、コード、front matter、詩など、行自体に意味がある構造は崩さない。Markdownの `<br>` や AsciiDoc の ` +` など、表示上の強制改行は明示された場合だけ追加する。 |

## 文の組み立て

| ID | 規則 |
|---|---|
| `sentence.split-overlong-sentences` | 長すぎる文は、意味関係を保ったまま適切に区切る。 |
| `sentence.keep-one-topic-per-sentence` | 一文に異なる事項を詰め込みすぎず、原則として一文一事項にする。 |
| `sentence.preserve-context-consistency` | 文と文、前提と結論、指示語と対象の食い違いをなくす。 |
| `sentence.limit-suspensive-clause-chains` | 中止法を長く連ねない。複雑な内容では文を分ける。 |
| `sentence.avoid-ambiguous-suspensive-clauses` | 複数の意味に取れる中止法を避ける。 |
| `sentence.clarify-suspensive-clause-attachment` | 中止した部分が、後続するどの語句や述語につながるかを明確にする。 |
| `sentence.use-punctuation-to-clarify-attachment` | `sentence.clarify-suspensive-clause-attachment` の具体策として句読点を工夫し、中止した部分の接続先を明確にする。 |
| `sentence.clarify-subject-predicate-correspondence` | 主語と述語の照応関係を明確にする。 |
| `sentence.retain-required-predicates` | 文の意味に必要な述語を省略しない。 |
| `sentence.keep-subject-and-predicate-close` | 主語と述語を、理解を妨げない範囲で近くに置く。 |
| `sentence.state-changed-subject-explicitly` | 文の途中で主語を変える場合は、新しい主語を明示する。主語を特定できない場合は捏造しない。 |
| `sentence.clarify-parallel-elements` | 何と何が並列なのかを、文法形式も含めて明確にする。 |
| `sentence.avoid-repeating-equivalent-particles` | 同じ形で同じ意味の助詞を、一文に二つ以上使わない。助詞を落とすと意味が壊れる場合は、文を分けて解消する。 |
| `sentence.retain-required-particles` | 意味関係を示すために必要な助詞を落とさない。 |
| `sentence.ensure-adverb-predicate-concord` | 「決して〜ない」など、副詞と後続表現の呼応を明確にする。 |
| `sentence.keep-modifier-and-modified-word-close` | 修飾語と被修飾語を、なるべく近くに置く。 |
| `sentence.clarify-modifier-scope` | 修飾語がどの語句にかかるかを明確にする。 |
| `sentence.clarify-negation-scope` | 打消しの語が何を否定しているかを明確にする。 |
| `sentence.avoid-overlong-modifiers` | 長すぎる修飾語を避ける。 |
| `sentence.split-overlong-modifiers-into-sentences` | 修飾語が長くなる場合は、内容を別の文に分ける。 |
| `sentence.minimize-passive-voice` | 受身形は、能動形の方が自然で動作主も明確な場合に減らす。未知または不要な動作主は補わない。 |

## 語の選び方

| ID | 規則 |
|---|---|
| `word-choice.remove-redundancy-and-clarify-ambiguity` | 意味の重複を削り、曖昧な用語を文脈から判断できる範囲で明確にする。 |
| `word-choice.avoid-roundabout-phrasing` | 持って回った言い方を避け、意味を保って簡潔にする。 |
| `word-choice.use-precise-nonmisleading-terms` | 読み手の誤解を招かず、対象を正確に表す語を選ぶ。 |
| `word-choice.avoid-idiosyncratic-neologisms-and-phrasing` | 読み手に通じない独りよがりな新造語や言い回しを避ける。 |
| `word-choice.maintain-terminology-register-consistency` | 文章全体の調子や用語体系から浮く、ちぐはぐな表現を避ける。 |
| `word-choice.choose-reader-appropriate-terms` | 読み手の知識、立場、目的に合う用語を選ぶ。 |
| `word-choice.handle-directive-language-carefully` | 読み手へ指示する表現は、必要な強さを保ちながら威圧的または不明確にならないようにする。 |
| `word-choice.match-expression-to-facts` | 入力内で確認できる事実に合う表現を使う。根拠なく断定を強めない。 |
| `word-choice.verify-metaphor-appropriateness` | 比喩が内容、読み手、文体に合っているか確認する。 |
| `word-choice.follow-established-usage` | 一般に定着した自然な語法を優先する。固有の用語法は保護する。 |
| `word-choice.avoid-translationese` | 日本語として不自然な直訳調を避ける。 |
| `word-choice.simplify-overly-formal-literary-or-technical-terms` | 堅すぎる漢語、文語、専門用語は、正確さを失わない場合だけ平易にする。 |
| `word-choice.limit-loanwords-and-foreign-words` | 外来語や外国語を乱用しない。固有名称や技術的に必要な語は保持する。 |
| `word-choice.use-immediately-understandable-spoken-words` | 話し言葉では、聞いただけですぐ理解できる語を選ぶ。 |
| `word-choice.avoid-confusing-homophones-in-speech` | 話し言葉では、文脈だけで区別しにくい同音異義語を避けるか言い換える。 |
| `word-choice.avoid-unfamiliar-abbreviations` | 読み手や聞き手になじみのない略語は使わない。 |

## 敬語

| ID | 規則 |
|---|---|
| `honorific.prefer-plain-simple-forms` | できるだけ平明で簡素な敬語を使う。 |
| `honorific.avoid-archaic-reverential-sino-japanese-terms` | 古い候文体などに由来する、特殊な敬意を表す漢語を乱用しない。 |
| `honorific.avoid-unnecessary-o-prefix` | 「お」を必要のない語にむやみにつけない。 |
| `honorific.avoid-repeated-o-prefixes` | 同じ文章で「お」を過度に続けて使わない。 |
| `honorific.do-not-use-humble-forms-as-respectful` | 「お〜する」などの謙譲語を、尊敬語として誤用しない。 |
| `honorific.avoid-double-respectful-forms` | 尊敬語を二重に使わない。 |
| `honorific.retain-required-forms` | 読み手、相手、場面に必要な敬語を落とさない。 |
| `honorific.keep-forms-consistent` | 同じ文章内で敬語の形と敬意の向きを一貫させる。 |
| `honorific.avoid-mixing-polite-and-plain-styles` | 原則として「です・ます」調と「だ・である」調を混用しない。 |
| `honorific.allow-deliberate-style-mixing-for-effect` | 明確な効果を意図している場合だけ、文体の混用を認める。この規則は `honorific.avoid-mixing-polite-and-plain-styles` の例外とする。 |

## 出力形式

推敲する場合は、原則として次の順で出力する。

```markdown
## 推敲後

{推敲後の文章}

## 適用ルール

- `{ID}`: {対象箇所と修正内容}

## 要確認

- `{ID}`: {原文だけでは判断できない点}
```

`要確認` がなければ、その見出しを省略する。
ユーザーが「最終版だけ」と指定した場合は、推敲後の文章だけを出す。

レビューのみの場合は、本文を変更せず、`ID / 対象箇所 / 問題 / 修正案` を示す。
`needs-confirmation` の項目は、修正案の代わりに判断に必要な情報を示す。
ファイルを編集した場合は本文を再掲せず、変更ファイルと適用したIDを報告する。
どのモードでも `needs-confirmation` は省略しない。
`actionable` がなければ、「適用ルール: なし」と報告する。

全48規則の判定一覧は、ユーザーが監査結果を求めた場合だけ、規則の定義順に次の形式で出力する。

```markdown
| ID | status | 根拠または対象箇所 |
|---|---|---|
| `{ID}` | `pass / not-applicable / actionable / needs-confirmation` | {短い根拠、対象箇所、または判断に必要な情報} |
```

## 完了条件

- 48個のIDをすべて照合している。
- `actionable` と判断した問題を修正済み、またはレビューとして報告している。
- `needs-confirmation` と判断した点を省略せず報告している。
- 修正後に全規則を再確認している。
- 原意、事実、仕様、技術的意味、文書構造を保持している。
- 報告に使うIDが、このスキルの定義と完全に一致している。
