---
name: natural-japanese-rewriter
description: >-
  日本語テキストを自然で読みやすく修正・リライト・校正したいときに使う。
  LLMくさい日本語、翻訳調、硬すぎる日本語、文意の取りづらい悪文が対象。
  README、仕様書、技術記事、Zenn記事、コードコメント、docstring、
  エラーメッセージ、UI文言、issue、PR説明文、職務経歴書などの日本語を、
  原意・事実・仕様・技術的意味を保ったまま整える。
  「自然にして」「翻訳調を直して」「読みやすくして」「LLMっぽさを消して」
  「リライトして」「校正して」などの依頼で起動する。
---

# 述語項グラフを修復する日本語リライト

日本語推敲を文字列の整形ではなく、述語項グラフの修復として実行する親スキルである。
原文の語義、述語、項、指示対象を意味の不変条件として固定し、その上に談話、情報構造、語用論、敬語、文体を重ねて自然な日本語を生成する。

すべての省略項を表面化することが目的ではない。
読み手が意味関係を復元できない箇所だけを修復し、自然に復元できる省略は残す。

## 子スキルと優先順位

Phase 1 で `natural-japanese-rewrite-analyzer` の `SKILL.md` を最後まで読み、同スキルの出力契約で述語項グラフを作る。
見つからない場合はパイプラインを止めず、同じ出力契約で分析を自前実行する。
平坦な述語一覧だけで Phase 1 を完了してはならず、代替した事実を Phase 6 で報告する。

指示が衝突する場合は、現在のユーザー指示、この親スキルの Phase 固有の指示、子スキルの通常指示の順に優先する。

## 入力と出力モード

入力は、リライト対象の日本語テキスト、またはファイルパスとする。
複数ファイルは1件ずつ独立したパイプラインとして扱う。
対象を特定できない場合は Phase 1 を始めず、対象を1件だけ確認する。

開始時に次を確定する。

- 対象範囲: 本文、見出し、箇条書き、コメント、UI 文言など
- 出力先: ファイル編集または応答本文
- 媒体と文体: Slack、メール、技術文書、です・ます調、である調など
- 出力モード

出力モードは次の2つとする。

- `polish`: 既定。修正後の本文を中心に出力し、内部分析を表示しない
- `diagnostic`: ユーザーが分析、理由、問題箇所を求めた場合だけ、本文に加えて問題のある述語、不明または競合する項、修復した関係を簡潔に示す

1〜2文や UI 文言でも Phase の順序は変えない。
分析メモの必須トップレベルキーは空配列でも保持し、必要なノードと制約だけに内部内容を簡略化できる。

## 最優先の意味保持

- 原意、事実、仕様、技術的意味を変えない。
- 原文にない主体、対象、原因、目的、時刻、確実性を作らない。
- コード、コマンド、ファイルパス、API 名、設定値、数値、固有名詞、引用、リンク、構造化データは、明確な誤りがない限り保護する。
- 否定、条件、例外、因果、時系列、範囲を変えない。
- 可能性、義務、許可、推量、断定の強さを変えない。
- 発話行為、相手に求める行動、敬語の方向を変えない。
- 技術用語を一般語へ薄めない。
- 問題のない文はそのまま残す。

自然さより意味保持を優先する。
判断材料が不足する場合は、文脈から一意に復元できる直しだけを行う。
一意に決まらない箇所は候補を保持し、安全な候補すべてに共通する変更だけを行う。
それでも誤解を避けられない場合は原文を保持し、必要なときだけ `要確認` とする。

## Phase 1: 述語項グラフを構築する

`natural-japanese-rewrite-analyzer` を使い、次を含む分析メモを作る。

- `protected_ranges` と `rewrite_targets`
- 語義候補を持つ述語ノード
- ID を持つ語義候補、格フレーム、項スロット
- 共有可能な指示対象ノード
- 述語と指示対象を結ぶ項スロット
- 項の表面助詞、統語関係、意味役割、実現形式、復元可能性、根拠
- 付加部、問題コード、曖昧さ
- `graph_invariants` と安全な `rewrite_policy`

子スキルを利用できない場合も、少なくとも次のスキーマと列挙値を保つ。

```yaml
schema_version: 2
protected_ranges: []
rewrite_targets: []
entities:
  - id: entity-1
    text: 表面に現れた表現または null
    candidates: []
predicates:
  - id: predicate-1
    surface: 原文の述語
    verb: 原文の述語
    args: {}
    omitted_args: []
    lemma: 見出し語
    predicate_type: verb | adjective | verbal-noun | event-noun | embedded
    sense_candidates:
      - id: sense-1
        gloss: 語義候補
        case_frames:
          - id: frame-1
            slots:
              - id: slot-1
                role: 意味役割
                domain_role: ドメイン固有役割または null
                kind: core | selected-oblique | adjunct | uncertain
                legacy_label: 旧 args で使う単一ラベルまたは null
                surface_particles: []
    sense: sense-1 | unknown
    voice: active | passive | causative | causative-passive | potential | not-applicable | unknown
    polarity: positive | negative
    tense: 原文の時制または unknown
    aspect: 原文のアスペクトまたは unknown
    modality: {}
    arguments:
      - sense_id: sense-1
        frame_id: frame-1
        slot_id: slot-1
        role: 意味役割
        domain_role: ドメイン固有役割または null
        kind: core | selected-oblique | adjunct | uncertain
        surface: 原文の項または null
        surface_particle: 表面の助詞または null
        syntactic_relation: 統語関係または unknown
        realization: overt | zero | relative-gap | nominalized | generic | unresolved
        discourse_role: topic | topic-continuation | focus | contrast | none | unknown
        referent: 指示対象IDまたは null
        candidates: []
        recoverability: clear | probable | ambiguous | unknown
        evidence: 判断根拠
adjuncts: []
issues:
  - code: UNRESOLVED_CORE_ARGUMENT | AMBIGUOUS_ANTECEDENT | CASE_FRAME_MISMATCH | SUBJECT_DRIFT | ATTACHMENT_AMBIGUITY | NOMINAL_ROLE_AMBIGUITY | VAGUE_PREDICATE | OVEREXPLICIT_ARGUMENT | SEMANTIC_DRIFT
    predicate_ids: []
    evidence: 原文上の根拠
    repairability: safe | contextual | blocked
ambiguities: []
graph_invariants: []
rewrite_policy: []
```

`surface` と `arguments` を正規フィールドとする。
各 `argument` の `sense_id`、`frame_id`、`slot_id` は、同じ predicate の `sense_candidates` 内に実在する ID を参照し、役割と種別は参照先スロットと一致させる。
`verb`、`args`、`omitted_args` は旧契約向けの互換ビューであり、正規フィールドから毎回導出する。
`legacy_label` は v1 へ投影するときの単一キーであり、表面助詞や語義別の意味役割を完全には表さない。
確定語義があればその格フレーム、確定していなければ残っているすべての語義候補と格フレームを投影元とする。
`args` は、各 `legacy_label` について、すべての投影元に同ラベルのスロットがあり、その項が同じ非 null の `referent` を指し、`candidates` に競合候補がない場合だけ、そのラベルと指示対象を1回記録する mapping として v1 のコンテナ型を維持する。
`omitted_args` は、その合意に加えて、対応するすべての項が `realization: zero` と `recoverability: clear` を満たす場合だけ、同じラベルと指示対象を1回記録する sequence とする。
`probable`、`ambiguous`、`unknown` の項、または投影元の間でラベル、指示対象、実現形式が一致しない項は旧ビューへ投影せず、正規の `arguments` と `ambiguities` に残す。
`args` と `omitted_args` は lossy view であり、語義別の意味判断には使用しない。
正規フィールドと互換ビューが矛盾する場合は正規フィールドを優先し、矛盾自体を `ambiguities` へ記録する。

ゼロ項、主題化、並列述語の項共有と主体切り替え、態、名詞化、軽動詞を検査する。
語義や指示対象を確定できなければ、複数候補、`ambiguous`、`unknown` のまま保持する。

完了条件: 全述語候補がグラフにあり、重要な項が指示対象、候補集合、`unknown` のいずれかになり、原文にない情報を確定していない。

## Phase 2: 上位レイヤーの制約を固定する

Phase 1 の意味グラフを土台に、下位から上位へ次を分析する。

1. 談話構造
   - 指示語とゼロ項の候補
   - 現在の主題と文間の主体・対象の継続
2. 情報構造
   - 原文の topic、focus、対比
   - `は`、`が`、`も` を変えたときの焦点の変化
3. 語用論
   - 報告、依頼、質問、提案、謝罪、予定通知、警告などの発話行為
   - 読み手へ求める行動
4. 対人関係
   - 書き手、読み手、第三者
   - 尊敬語、謙譲語、丁寧語の主体と方向
5. 文体
   - 媒体、文末、簡潔さ、丁寧さ

不明な属性は推測せず `unknown` とする。
文体の都合で下位レイヤーの語義、指示関係、発話行為を変更してはならない。

完了条件: 原文に存在する topic / focus、発話行為、requested action、敬語の方向、文体が、保持する制約または `unknown` として整理されている。

## Phase 3: 修復箇所を決める

次に該当し、原文の情報だけで安全に改善できる箇所を修復対象にする。

- 主体または対象に複数候補があり、文脈で安全に絞れる
- 重要な項の指示対象が不明で、原文内の明示で解消できる
- 助詞や構文が誤った意味役割を示す
- 一つの句が複数の述語へ係り得る
- 並列中の主体切り替えが不明瞭である
- 名詞化によって動作主と対象を区別できない
- `する`、`なる`、`対応する`、`もの`、`こと` などが意味関係を隠す
- 重要な項と述語が離れ、誤読が起こり得る
- 意味関係は明確だが、翻訳調、冗長、過度に硬い表現、周囲と不整合な文体が読みやすさを損なう
- 意味役割を変えずに直せる、不自然な語順、助詞、重複がある

次の場合は修復せず、項を無理に補わない。

- 書き手、読み手、直前の主題から一意に復元できる
- 項が複数述語間で自然に共有されている
- 省略しても誤読の可能性が低い
- 明示すると不自然または冗長になる
- 文体上自然な主題化や対比である
- 原文に問題がない

長文、複数述語、名詞化、技術的曖昧さ、既存ルールとの照合が必要な場合は、ここで `references/detailed-rules.md` を読む。
確定不能な曖昧さは修復対象にせず、原文保持または `要確認` とする。

完了条件: 各 `rewrite_target` が「修復する」「意図的に残す」「要確認」のいずれかになり、修復理由と変更禁止の制約が対応している。

## Phase 4: 制約に沿って生成する

上位レイヤーから下位レイヤーへ制約を適用し、語順、助詞、文分割、冗長表現、硬さを整える。
生成時の優先順位は次のとおりとする。

1. 語義、指示対象、意味役割、極性、条件、因果、時系列、範囲、モダリティ
2. 発話行為、requested action、topic、focus、対比
3. 敬語の主体、方向、対人関係
4. 媒体に合う文体と自然さ
5. 編集距離の小ささ

Markdown の見出し、箇条書き、表、コードブロック、JSON / YAML / TOML、コマンド例などの構造を壊さない。

完了条件: 修復対象が処理され、保護範囲と変更禁止の制約が候補文に保持されている。

## Phase 5: 意味回帰を検査する

候補文へ Phase 1 と Phase 2 を再実行し、原文と意味的に比較する。
語順、助詞、態、項の明示または省略は一致しなくてもよいが、次は一致しなければならない。

- 述語の語義と出来事
- 指示対象と項の意味役割、ドメイン役割
- 否定、条件、例外、因果、時系列、範囲
- 時制、アスペクト、モダリティ、断定の強さ
- topic、focus、対比
- 発話行為と requested action
- 敬語の主体、方向、対人関係
- 保護範囲
- Markdown / AsciiDoc などの見出し、リスト項目、表の行、コードブロックについて、原文と候補文の要素数、順序、階層、入れ子、境界、対応関係

不一致は `SEMANTIC_DRIFT` として候補を棄却し、修正して同じ検査を再実行する。
最大3巡で解消しない場合は、文の分割・結合や共有指示対象で結び付く編集を含む最小の原子的修復単位を原文へ戻す。
原文へ戻した後の候補文全体へ Phase 1 と Phase 2 を再実行し、意味不変条件と文書構造をもう一度比較する。
不一致が残る場合は復元単位を段落または構造ブロックへ広げ、同じ再検査を行う。

完了条件: 最終候補全体で意味不変条件と文書構造の不一致が0件であり、必要な `要確認` が記録されている。原文へ戻したことだけを不一致解消の根拠にしない。

## Phase 6: 出力する

ファイルが対象なら必要最小限の変更だけを反映し、変更概要と `要確認` を短く報告する。
応答本文が対象なら修正後の本文を先に出し、必要な場合だけ `要確認` を続ける。

`diagnostic` モードでは、次を簡潔に追加する。

1. 問題のある述語
2. 不明または競合していた項
3. 修復で明確になった関係

分析メモ全体、内部手順、問題のない箇所の説明は出さない。
子スキルを利用できず自前分析へ縮退した場合は、その事実を報告する。

リライト本文が出力され、意味不変条件の不一致が0件で、`要確認` がすべて報告済みなら完了とする。
