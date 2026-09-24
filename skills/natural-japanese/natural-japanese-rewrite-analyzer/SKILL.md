---
name: natural-japanese-rewrite-analyzer
description: >-
  日本語のリライト前に、保護範囲、語義、述語、項、指示対象、付加部、
  曖昧さを KWJA の解析ファイルから述語項グラフに整理したいときに使う。
  natural-japanese-rewriter の前段として、原意・事実・仕様・技術的意味を
  変えずに書き換えるための意味不変条件と分析メモを作る。
---

# 述語項グラフによる日本語リライト前分析

日本語推敲を文字列の整形ではなく、述語項グラフの修復として扱うための前段分析スキルである。
述語を個別に列挙するだけでなく、同じ参加者を指す項、表面にないゼロ項、語義候補を文全体で関連づける。

このスキルは原則としてリライトしない。
`natural-japanese-rewriter` の前段では分析メモを内部入力として渡し、ユーザーが分析だけを求めた場合は問題と不確実性を簡潔に出力する。

## 解析元

[japanese-kwja-analyze](../japanese-kwja-analyze/SKILL.md) を読み、生成された KNP 形式の `.kwja.txt` を解析元にする。
同じ実行内で、現在の入力と内容が一致する解析用テキストと解析ファイルが渡された場合は、それらを読み取って再利用する。
それ以外は KWJA を実行する。過去のファイルを名前だけで再利用しない。
実行や読み取りに失敗した場合は分析を止め、原因を報告する。LLM による形態素解析、係り受け解析、項・照応関係の推測で代行しない。

KWJA の結果はモデルの予測として扱う。本文との矛盾は `ambiguities` に記録する。
KWJA が出力していない関係は未検出として残し、存在しないことの証明にはしない。
LLM が判断する修復案、語用論、文体と、KWJA の出力にある解析情報を区別する。

## 分析手順

### 1. 原文と解析用テキストを対応付ける

対象の日本語本文、見出し、箇条書き、コメント、UI 文言を確定する。
コード、コマンド、構造化データ、URL、ファイルパス、API 名、設定値、数値、固有名詞、引用などの保護範囲は、修正前の原文から記録する。

プレーンテキストのファイル全体が対象なら、そのファイルを KWJA に渡す。
Markdown、AsciiDoc、コードなどの一部が対象なら、対象の文章を出現順に抽出した UTF-8 の作業用 `.txt` を原文と同じディレクトリに作る。
文をまたぐ関係を解析できるよう、文脈と段落の順序を保ち、文ごとに独立実行しない。
応答本文などファイルのない入力も、作業ディレクトリにテキストファイルとして保存する。
作業ファイルは既存ファイルと衝突しない名前にし、原文用と候補文用を別々にする。

抽出した箇所と原文の行・範囲の対応を `source_alignment` に記録する。
タイポ修正・単語正規化によって表記や長さが変わるため、解析結果の文字位置をそのまま原文の編集位置にしない。

### 2. KWJA を実行し、解析ファイルを読む

`japanese-kwja-analyze` のスクリプトへ解析用テキストのパスを渡す。
同スキルの完了条件を確認し、出力された `.kwja.txt` の全文を読む。
必要なら同じディレクトリに作業メモを作ってよい。元の KNP ファイルは加工せず残す。

`analysis_source` に入力ファイルと解析ファイルのパスを記録する。
KWJA の文 ID、形態素、基本句、係り先、関係タグを使って、原文・解析用テキスト・解析結果を対応付ける。
タイポ修正・正規化前後で対応が不明な箇所は `ambiguities` に残す。解析表記を原文へ自動反映しない。

### 3. KWJA の結果を述語項グラフへ整理する

- 形態素と付与された素性から述語・項の候補を取り出す。
- 形態素・基本句と固有表現の出力から指示対象ノードを作り、共参照の出力で同じ対象を関連づける。
- 係り受け、述語項構造、橋渡し照応、共参照のタグは、種類を区別して対応するノードへ結ぶ。係り先だけから格関係や共参照を決めない。
- 言語素性と談話関係の出力を、該当する述語・基本句・節へ関連づける。
- `evidence` には、解析ファイルのパス、文 ID、基本句または形態素の位置、根拠となるタグと原文の対応箇所を残す。
- 外界照応など文書内の位置を持たない参照も、KWJA の参照先表現を保持する。人物などの具体的な対象を補わない。

以下のスキーマへ整理する際、KWJA にない語義候補、格フレーム、ドメイン役割、項の復元可能性は `unknown`、`uncertain`、空配列で表す。
参照用の `sense_id`、`frame_id`、`slot_id` はローカルに付けてよいが、KWJA が語義や格フレームを確定したと見なさない。
未確定の語義は `sense: unknown` とし、必要な候補枠の `gloss` も `unknown` とする。
出力された項スロットを記録し、未出力の項を LLM の知識から追加しない。
KWJA が検出したゼロ項と未検出の項を区別し、表面の助詞、統語関係、意味役割、談話上の役割を混同しない。

### 4. 原文と照合して修復案を作る

KWJA の根拠に基づき、項共有、主体切り替え、態、名詞化、軽動詞、曖昧な係り受けを確認する。
出力と原文が矛盾する場合は、関係を黙って変更せず、該当タグと問題を `ambiguities` に記録する。
`issues` には、スキーマの問題コードから該当するものを付ける。
`graph_invariants` と `rewrite_policy` は、原文と KWJA の結果を根拠に作る。
親スキルのデストロイモードで別の解釈を選ぶ場合も、生成時の判断として扱い、KWJA の解析結果を書き換えない。

## 出力契約

次の YAML 形式を基本とする。
該当項目がない配列もキーを保ち、同じ参加者は ID で共有する。

```yaml
schema_version: 2
analysis_source:
  input_file: 解析用テキストのパス
  result_file: KWJA の解析ファイルのパス
source_alignment: []
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
    predicate_type: verb | adjective | verbal-noun | event-noun | embedded | unknown
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
    polarity: positive | negative | unknown
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

- 対象範囲の全文に対応する KWJA の解析ファイルを読み、KWJA が検出した述語候補がノードになっている。
- 各解析情報に出力タグの根拠があり、未出力の項や関係を補っていない。
- 原文・解析用テキスト・解析結果の対応を確認し、不明な箇所を記録している。
- 各語義候補の重要な項が、指示対象、候補集合、または `unknown` のいずれかになっている。
- すべての項が実在する語義候補、格フレーム、項スロットを参照している。
- 複数述語の共有項と主体切り替えを検査している。
- 保護範囲、問題、曖昧さ、意味不変条件が記録されている。
- 原文にない情報を確定していない。

単独利用では、分析メモ全体を機械的に表示する必要はない。
問題のある述語、競合または不明な項、判断根拠を、ユーザーの求める粒度で提示する。
