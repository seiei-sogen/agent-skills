---
name: natural-japanese-rewrite-analyzer
description: >-
  日本語のリライト前に、保護範囲、語義、述語、項、指示対象、付加部、
  曖昧さを述語項グラフとして分析したいときに使う。
  natural-japanese-rewriter の前段として、原意・事実・仕様・技術的意味を
  変えずに書き換えるための意味不変条件と分析メモを作る。
---

# 述語項グラフによる日本語リライト前分析

日本語推敲を文字列の整形ではなく、述語項グラフの修復として扱うための前段分析スキルである。
述語を個別に列挙するだけでなく、同じ参加者を指す項、表面にないゼロ項、語義候補を文全体で関連づける。

このスキルは原則としてリライトしない。
`natural-japanese-rewriter` の前段では分析メモを内部入力として渡し、ユーザーが分析だけを求めた場合は問題と不確実性を簡潔に出力する。

## 基本原則

- 項は、述語の語義が意味を成立させるために用意する参加者スロットとして扱う。
- 表面にない項もスロットとして保持する。省略されていることと、存在しないことを混同しない。
- 表面の助詞、統語関係、意味役割、談話上の役割、項の実現形式を別々に記録する。
- `は` と `も` を自動的に主語とみなさない。
- 項と付加部は助詞や省略可能性だけで決めず、語義ごとの格フレームで判断する。
- 語義や指示対象を一意に決められない場合は、複数候補または `unknown` を保持する。
- 原文にない主体、対象、原因、目的、時刻、確実性を作らない。

## 分析手順

### 1. 対象と保護範囲を確定する

日本語本文、見出し、箇条書き、コメント、UI 文言、エラーメッセージなど、分析対象を特定する。
コードブロック、コマンド、JSON / YAML / TOML、表、URL、ファイルパス、API 名、設定値、数値、固有名詞、引用を `protected_ranges` に記録する。

### 2. 述語候補と語義候補を抽出する

次を述語候補として拾う。

- 動詞
- 形容詞述語
- サ変名詞
- 出来事を表す名詞
- 埋込み節の述語

表記が同じでも語義が複数あり得る場合は、各語義候補、格フレーム候補、項スロットへ ID を付けて保持する。
格フレームの異なる語義候補を、一つの無修飾な項一覧へ統合しない。
文脈だけで一つに決められなければ確定しない。

### 3. 指示対象ノードを作る

人物、組織、成果物、環境、データ、出来事、命題など、述語の参加者になり得る対象へ ID を付ける。
表記が違っても同じ対象を指す根拠があれば同じノードへ関連づける。
指示語やゼロ項に複数候補がある場合は、候補を残したままにする。

### 4. 項スロットを指示対象へ結ぶ

各述語について、語義が選択する項を列挙し、明示された項または指示対象候補へ結ぶ。
各項は `sense_id`、`frame_id`、`slot_id` で一つの語義候補、格フレーム、項スロットを参照する。
同じ表面の句が複数の語義候補に対応する場合も、語義ごとに項を分け、互換性のない意味役割を一つの項へ統合しない。
各項では次を分離する。

- `kind`: `core`、`selected-oblique`、`adjunct`、`uncertain`
- 表面の句と助詞
- 統語関係
- 意味役割と、必要な場合のドメイン役割
- `realization`: `overt`、`zero`、`relative-gap`、`nominalized`、`generic`、`unresolved`
- `discourse_role`: `topic`、`topic-continuation`、`focus`、`contrast`、`none`、`unknown`
- 指示対象または候補集合
- `recoverability`: `clear`、`probable`、`ambiguous`、`unknown`
- 判断根拠

ゼロ項の候補は、同一節、同一文の別述語、直前文、現在の主題、書き手、読み手、一般主体の順に探す。
候補が競合する場合は `ambiguous`、根拠がなければ `unknown` とする。
数値の確信度を擬似的に精密化しない。

### 5. 日本語特有の対応を検査する

- 主題化: `は` や `も` で提示された要素が、どの述語のどの項を満たすか確認する。
- 項共有: 並列述語が主体や対象を共有するか、途中で主体が切り替わるか確認する。
- 態: 受け身、使役、使役受け身、可能、授受、敬語表現の表面格と意味役割を分ける。
- 名詞化: `NのN`、サ変名詞、出来事名詞の動作主、対象、内容、結果を区別する。
- 軽動詞: `確認を行う` などでは、項構造を `行う` だけでなく内容名詞側から復元する。
- 係り受け: 一つの句が複数の述語へ係り得る場合は候補を保持する。

### 6. 問題と意味不変条件を記録する

次のコードを必要な箇所へ付ける。

| コード | 判定 |
| --- | --- |
| `UNRESOLVED_CORE_ARGUMENT` | 重要な項の指示対象が不明 |
| `AMBIGUOUS_ANTECEDENT` | ゼロ項や指示表現の候補が複数ある |
| `CASE_FRAME_MISMATCH` | 助詞や構文と述語の語義が整合しない |
| `SUBJECT_DRIFT` | 並列述語または文間で主体が不明瞭に切り替わる |
| `ATTACHMENT_AMBIGUITY` | 句が複数の述語へ係り得る |
| `NOMINAL_ROLE_AMBIGUITY` | 名詞化内部の役割を区別できない |
| `VAGUE_PREDICATE` | 曖昧な述語や形式名詞が意味関係を隠す |
| `OVEREXPLICIT_ARGUMENT` | 項の明示が不自然または冗長 |
| `SEMANTIC_DRIFT` | リライト前後で意味不変条件が変化 |

`graph_invariants` には、リライト後にも保つ述語の語義、指示対象、意味役割、極性、モダリティを列挙する。
条件、例外、因果、時系列、範囲も、該当する述語または付加部と関連づける。

## 出力契約

次の YAML 形式を基本とする。
該当項目がない配列もキーを保ち、同じ参加者は ID で共有する。

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
        referent: entity-1 | null
        candidates: []
        recoverability: clear | probable | ambiguous | unknown
        evidence: 判断根拠
adjuncts: []
issues:
  - code: 問題コード
    predicate_ids: []
    evidence: 原文上の根拠
    repairability: safe | contextual | blocked
ambiguities: []
graph_invariants: []
rewrite_policy: []
```

`modality` は、可能性、義務、許可、推量、断定の強さなど、原文に存在する属性だけを持つ。
`rewrite_policy` は修復案であり、確定不能な情報の補完を指示してはならない。
各 `argument` の `sense_id`、`frame_id`、`slot_id` は、同じ predicate の `sense_candidates` 内に実在する ID を参照し、役割と種別は参照先スロットと一致させる。
`verb`、`args`、`omitted_args` は旧契約向けの互換ビューであり、正規の `surface` と `arguments` から導出する。
`legacy_label` は v1 へ投影するときの単一キーであり、表面助詞や語義別の意味役割を完全には表さない。
確定語義があればその格フレーム、確定していなければ残っているすべての語義候補と格フレームを投影元とする。
`args` は、各 `legacy_label` について、すべての投影元に同ラベルのスロットがあり、その項が同じ非 null の `referent` を指し、`candidates` に競合候補がない場合だけ、そのラベルと指示対象を1回記録する mapping として v1 のコンテナ型を維持する。
`omitted_args` は、その合意に加えて、対応するすべての項が `realization: zero` と `recoverability: clear` を満たす場合だけ、同じラベルと指示対象を1回記録する sequence とする。
`probable`、`ambiguous`、`unknown` の項、または投影元の間でラベル、指示対象、実現形式が一致しない項は旧ビューへ投影せず、正規の `arguments` と `ambiguities` に残す。
`args` と `omitted_args` は lossy view であり、語義別の意味判断には使用しない。
両者が矛盾する場合は正規フィールドを優先し、矛盾自体を `ambiguities` へ記録する。

## 完了条件

次のすべてを満たした場合だけ分析完了とする。

- 対象範囲のすべての述語候補がノードになっている。
- 各語義候補の重要な項が、指示対象、候補集合、または `unknown` のいずれかになっている。
- すべての項が実在する語義候補、格フレーム、項スロットを参照している。
- 複数述語の共有項と主体切り替えを検査している。
- 保護範囲、問題、曖昧さ、意味不変条件が記録されている。
- 原文にない情報を確定していない。

単独利用では、分析メモ全体を機械的に表示する必要はない。
問題のある述語、競合または不明な項、判断根拠を、ユーザーの求める粒度で提示する。
