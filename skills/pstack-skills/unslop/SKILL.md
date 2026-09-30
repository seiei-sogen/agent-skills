---
name: unslop
description: あらゆる文章から AI の痕跡を削る。常に適用しなければならない。
---

# Unslop

テキストを編集して AI のパターンを取り除く。

## プロセス

1. 下のパターンを走査する。
2. 書き直す。意味を保ち、意図されたトーンに合わせる。
3. 自己監査する。「何がこれを明らかに AI 生成だと分からせるか」。残った痕跡を直す。

## 検出して直すパターン

ルール番号は、他のスキルが引用する安定した ID である。削除されたルールは欠番として残る。

### 内容

3. **表面的な -ing 句。** 「highlighting...」「ensuring...」「reflecting...」「showcasing...」「fostering...」。削除するか、実際の出典で展開する。
5. **曖昧な帰属。** 「Experts believe」「Industry reports suggest」「Some critics argue」。出典を名指しするか削除する。

### 言語

7. **AI 語彙。** Additionally、crucial、delve、enduring、enhance、fostering、garner、interplay、intricate、landscape（抽象的な用法）、pivotal、showcase、tapestry（抽象的な用法）、testament、underscore、vibrant。平易な語に置き換える。
8. **「is」の気取った言い方。** 「serves as」「stands as」「boasts」「features」。単に「is」か「has」と言う。
9. **「Not just X, but Y.」** 代わりに要点を直接述べる。
10. **三の法則。** 考えを無理に 3 つの組にする。自然な数を使う。
11. **同義語の取り替え。** Protagonist、main character、central figure、hero が 1 つの段落に全部ある。1 つ選んで繰り返す。
12. **偽の範囲。** X と Y が意味のある尺度上にないのに「from X to Y」と言う。トピックを直接列挙する。

### スタイル

13. **em ダッシュの乱用。** em ダッシュは完全に避ける。ピリオドかコンマだけを使う（括弧なし、en ダッシュなし、ダッシュ代わりのハイフンなし）。思考を区切る必要があるなら、文を終えるかコンマを使う。
14. **コロンの乱用。** コロンはリストや例の前なら問題ない。文中の接続語としては使わない。「If you're coming from traditional automation: instead of registering event handlers, you describe conditions」は、コロンによって何も足していない。比較の枠組みなしに要点が自立するよう書き直す。「Describing when the scheduler should fire works best as plain English.」同じ意味で、支えの句読点なし。
15. **太字の乱用。** すべての固有名詞や頭字語を太字にしない。
16. **インラインヘッダーのリスト。** 痕跡は、行を言い直す太字のラベルとコロンである。「**Performance:** Performance improved...」。これらは文章に変換する。ピリオドで終わり、項目を名指しし、本当に新しい詳細が続く太字の導入（「**Schema in TypeScript.** Tables live in one file.」）は問題なく、痕跡ではない。
17. **タイトルケースの見出し。** センテンスケースを使う。
18. **装飾的な絵文字。** 見出しと箇条書きから取り除く。
19. **カーリークォート。** ストレートクォートに置き換える。

### コミュニケーションの産物

20. **チャットボット句。** 「I hope this helps!」「Let me know if...」「Of course!」「Certainly!」「Found the smoking gun!」。取り除く。
22. **迎合的なトーン。** 「Great question! You're absolutely right!」。直接応答する。

### フィラー

23. **フィラー句。** 「In order to」は「To」になる。「Due to the fact that」は「Because」になる。「It is important to note that」は削除される。
24. **保険のかけすぎ。** 「could potentially possibly be argued that it might」は「may」になる。
25. **一般的な結論。** 「The future looks bright.」。具体的な計画や事実を述べる。

### 専門用語

26. **抽象的なメタファー名詞。** Substrate、wedge、vector、locus、vantage、nexus、primitive（名詞として）、harness（メタファーとして）、surface（「API surface」のような用法）、bedrock、scaffolding（メタファーとして）、modality、paradigm、gold-plating、ratchet（メタファーとして）、evacuate（コードの移動の意味で）、endgame、north star、flywheel。これらは技術的に読めるが、たいていはもっと平易で具体的な語がある。「Substrate」は「base」になる。「Wedge in」は「add」になる。「Vector」は「way」か「method」になる。「Gold-plating」は「more than the job needs」になる。「Ratchet」は仕組みの実際の名前か「a limit that only tightens」になる。「Evacuate」は「move out」になる。「Endgame」は「the last phase」になる。具体的な語を選ぶ。

### 平易な話し方

27. **どう感じるかではなく、何をするかを言う。** 「the database stays close at hand」「SQL you can read」「types that follow your schema」は感覚を名指ししている。修正は仕組みか数値を名指しする。「`.toSQL()` returns the exact string sent to the database」「a column rename fails the build」。その文が読者に何をせよ、何を知れと伝えているかを問い、それを書く。具体的な指示、事実、数値として言い直せないなら、削る。もう 1 つの確認。その文が他のプロジェクトの文書にそのまま載せられるなら、このプロジェクトについて何も言っていない。削る。
28. **密な文を短くするか分割する。** 読者が文を解析するために戻り読みしなければならないなら、2 つに分けるか節を落とす。1 文につき 1 つの考え。
29. **能動態。** 能動態を優先する。「is/are/was/were + 過去分詞」を捕まえて行為者を名指しする。「queries are validated」は「the compiler validates queries」になり、「the file is parsed by the loader」は「the loader parses the file」になる。受動態は、行為者が不明か本当に重要でないときだけ許される。
30. **副詞を削るか、より強い動詞を使う。** 「runs quickly」は「is fast」か数値になる。「significantly improves」は測定された差分になる。弱い動詞を副詞で支えているなら、動詞が間違っている。
31. **平易な語を優先する。** 「utilize」は「use」に、「leverage」は「use」に、「facilitate」は「help」に、「numerous」は「many」に、「in the event that」は「if」になる。気取った同義語のほうが明快であることはまれである。
32. **凝った文章。** 文字どおりの句があるところでのメタファーや装飾。格言（「wire it or delete it」）、効果を狙った修辞的な断片、人格化されたコード（「the plan holds it」）、比喩的な動詞（「rides along」「stands on」）、定型の前置き句。「A dial worth turning」は「a parameter worth varying」になる。言いたいことを言う。ルール 26 がメタファー名詞を扱う。
33. **過度な圧縮。** 落とされた冠詞、動詞のない断片、記号語、略語は、読者に読むのではなく解読を強いる。「Parser rejects bad date → exit 2, no write」は「The parser rejects a bad date, exits with code 2, and writes nothing.」になる。冠詞と動詞を備えた完全な文を書き、矢印と略語は省略せずに言葉で書く。
