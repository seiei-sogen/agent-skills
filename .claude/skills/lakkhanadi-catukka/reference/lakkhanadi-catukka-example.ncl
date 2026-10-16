# lakkhanadi-catukka-example.ncl
#
# 上座部アビダンマ「四相分析」（lakkhaṇādi-catukka / lakkhaṇa-rasa-paccupaṭṭhāna-padaṭṭhāna）
# のリファレンス例。Visuddhimagga と Atthasālinī の四相記述を、Skill が機械的に
# 参照しやすい形へ構造化したもの。
#
# 利用想定:
#   - lakkhanadi-catukka-analytics Skill が「古典明示トピック」かどうかを判定する根拠データ
#   - 出力テンプレート（要約表 + 詳説）の正解データ（古典トピックの場合）
#   - judge プロンプトが古典トピックの妥当性を評価する際のリファレンス
#
# 注意:
#   - 本ファイルは公的に利用できる Theravāda 注釈文献の四相分析を「再構造化」したものであり、
#     特定の出版物 PDF からの逐語転写ではない。Pali 語形は IAST + ダイアクリティカルで統一。
#   - 出力言語は日本語（Skill 出力規約 REQ-404）。Pali / English は参考併記。
#   - 例は代表 5 件のみを収録（28 種すべての色法を網羅する目的ではない）。
#     追加が必要になれば examples リストに同形式で追加する。
#
# 出典:
#   - Visuddhimagga (Vs.1.362, Vs.2.73–80) — Sixth Saṅgha Council Burmese edition
#   - Dhammasaṅgaṇī aṭṭhakathā / Atthasālinī (DhsA.349–368)

{
  meta = {
    title = "Lakkhaṇādi-catukka Reference Examples",
    framework_pali = "lakkhaṇādi-catukka",
    framework_ja = "四相分析",
    pali_orthography = "IAST_with_diacritics",
    output_language = "ja",
    license_note =
      "Restructured restatement of public-domain Theravāda commentary content for "
      ++ "machine reference; not a verbatim PDF excerpt.",
    sources = [
      "Visuddhimagga (Vs.1.362, Vs.2.73–80), Sixth Saṅgha Council Burmese edition",
      "Dhammasaṅgaṇī aṭṭhakathā / Atthasālinī (DhsA.349–368)"
    ],
    schema_version = "1.0.0",
  },

  # 四相分析の枠組みそのもの（Skill のトーンと整合する形で記述）
  framework = {
    name_pali = "lakkhaṇādi-catukka",
    name_ja = "四相分析",
    summary_ja =
      "任意の対象を、その特相・作用・現れ方・近因の 4 つの観察軸で記述する Theravāda の "
      ++ "定義法。各軸は責任追及ではなく観察のためのレンズである。",
    devices = [
      {
        key = "lakkhaṇa",
        abbr = "C",
        ja_label = "特相",
        en_label = "characteristic",
        gloss_ja =
          "対象が他と区別される本質的な特徴。動的な作用ではなく「変わらない芯」を言い当てる。",
        gloss_en =
          "The salient defining quality of the phenomenon — what makes it itself.",
      },
      {
        key = "rasa",
        abbr = "F",
        ja_label = "作用",
        en_label = "function",
        gloss_ja =
          "対象が果たす働き。具体的な職分（kicca-rasa）または成就（sampatti-rasa）。",
        gloss_en =
          "Performance of a concrete task (kicca-rasa) or achievement of a goal (sampatti-rasa).",
      },
      {
        key = "paccupaṭṭhāna",
        abbr = "M",
        ja_label = "現れ方",
        en_label = "manifestation",
        gloss_ja =
          "経験のなかにそれがどう立ち現れるか（upaṭṭhānākāra）、または何の効果として表れるか（phala）。"
          ++ "身体感覚 / 思考・感情・イメージ / 世界の見え方 の三面で記述する。",
        gloss_en =
          "The way it presents itself within experience (upaṭṭhānākāra-paccupaṭṭhāna) "
          ++ "or its mode of effect (phala-paccupaṭṭhāna).",
      },
      {
        key = "padaṭṭhāna",
        abbr = "P",
        ja_label = "近因",
        en_label = "proximate cause",
        gloss_ja =
          "それを「いま」支えている近接条件。根本原因や責めるべき犯人ではなく、観察的に並べる支柱。",
        gloss_en =
          "The principal proximate condition upon which it depends (not a root cause to be blamed).",
      },
    ],
    notes_ja = [
      "padaṭṭhāna は近接条件であり、根本原因ではない。観察的・非難しないトーンで記述する。",
      "paccupaṭṭhāna は単一観点で書かない。心理対象なら身体感覚 / 思考・感情 / 世界の見え方の三面を網羅する。",
      "古典に明示されている対象（地水火風など）はそのまま記述する。古典に明示されていない応用対象は『四相分析の枠組みを応用すると』マーカーを冒頭に付ける。",
    ],
  },

  # 古典明示トピックの代表 5 例（Skill が「canonical」と判定する基準データ）
  examples = [
    # ---- 1. 地大 ----
    {
      pali_term = "pathavī-dhātu",
      ja_label = "地大",
      en_label = "earth-element",
      category = "mahābhūta",
      category_ja = "四大（基本物質要素）",
      canonical = true,
      applied_marker_required = false,
      source_refs = [ "DhsA.368", "Vs.1.362", "Vs.2.73" ],
      pali_compact = "kakkhaḷatta-lakkhaṇā, patiṭṭhāna-rasā, sampaṭicchana-paccupaṭṭhānā, avasesa-dhātuttaya-padaṭṭhānā.",
      analysis = {
        lakkhana = {
          pali = "kakkhaḷatta",
          ja = "硬さ",
          en = "hardness",
          gloss_ja = "他の倶生諸大と区別される、抵抗・固さの性質。",
        },
        rasa = {
          pali = "patiṭṭhāna",
          ja = "他の倶生諸大の基盤となること",
          en = "to act as a foundation for the other coexisting primary elements and derived materialities in its own kalāpa",
          gloss_ja = "同じ kalāpa 内の水・火・風および派生色の支えとして働く。",
        },
        paccupatthana = {
          pali = "sampaṭicchana",
          ja = "受け取りとして現れる",
          en = "as receiving the coexisting materialities in its own kalāpa",
          gloss_ja = "他の倶生諸大を受け取り保持するさまとして経験に立ち現れる。",
        },
        padatthana = {
          pali = "avasesa-dhātuttaya",
          ja = "残りの三大（水・火・風）",
          en = "the other three great primary elements (water, fire, air) in its own kalāpa",
          gloss_ja = "同じ kalāpa 内の水・火・風が、地大を「いま」支えている近接条件。",
        },
      },
    },

    # ---- 2. 水大 ----
    {
      pali_term = "āpo-dhātu",
      ja_label = "水大",
      en_label = "water-element",
      category = "mahābhūta",
      category_ja = "四大（基本物質要素）",
      canonical = true,
      applied_marker_required = false,
      source_refs = [ "DhsA.368", "Vs.1.362", "Vs.2.73" ],
      pali_compact = "paggharaṇa-lakkhaṇā, brūhana-rasā, saṅgaha-paccupaṭṭhānā, avasesa-dhātuttaya-padaṭṭhānā.",
      analysis = {
        lakkhana = {
          pali = "paggharaṇa",
          ja = "流れる・滲み出る性質",
          en = "flowing or trickling or oozing",
          gloss_ja = "粘性・湿潤として現象する、流れていく芯。",
        },
        rasa = {
          pali = "brūhana",
          ja = "倶生の物質を強める作用",
          en = "to intensify the coexisting materialities in its own kalāpa",
          gloss_ja = "同じ kalāpa 内の他の物質を増勢する。",
        },
        paccupatthana = {
          pali = "saṅgaha",
          ja = "結合・凝集として現れる",
          en = "as the holding together or cohesion of material phenomena in its own kalāpa",
          gloss_ja = "ばらばらになりかねない他要素をまとめて保つさまとして現れる。",
        },
        padatthana = {
          pali = "avasesa-dhātuttaya",
          ja = "残りの三大（地・火・風）",
          en = "the other three great primary elements (earth, fire, air) in its own kalāpa",
          gloss_ja = "同 kalāpa 内の地・火・風が水大を支えている近接条件。",
        },
      },
    },

    # ---- 3. 火大 ----
    {
      pali_term = "tejo-dhātu",
      ja_label = "火大",
      en_label = "fire-element",
      category = "mahābhūta",
      category_ja = "四大（基本物質要素）",
      canonical = true,
      applied_marker_required = false,
      source_refs = [ "DhsA.368", "Vs.1.362", "Vs.2.73" ],
      pali_compact = "uṇhatta-lakkhaṇā, paripācana-rasā, maddavānuppadāna-paccupaṭṭhānā, avasesa-dhātuttaya-padaṭṭhānā.",
      analysis = {
        lakkhana = {
          pali = "uṇhatta",
          ja = "熱（および冷）",
          en = "heat (or coldness)",
          gloss_ja = "温度として経験される、熱と冷の両極を含む芯。",
        },
        rasa = {
          pali = "paripācana",
          ja = "他の物質を成熟・熟成させる作用",
          en = "to mature or ripen other material phenomena in its own kalāpa",
          gloss_ja = "同 kalāpa 内の他物質を熟させ変容させる。",
        },
        paccupatthana = {
          pali = "maddavānuppadāna",
          ja = "柔らかさを供給し続けるさまとして現れる",
          en = "as a continuous supply of softness",
          gloss_ja = "硬直を解き、柔軟さを保たせるはたらきとして経験に現れる。",
        },
        padatthana = {
          pali = "avasesa-dhātuttaya",
          ja = "残りの三大（地・水・風）",
          en = "the other three great primary elements (earth, water, air) in its own kalāpa",
          gloss_ja = "同 kalāpa 内の地・水・風が火大を支えている近接条件。",
        },
      },
    },

    # ---- 4. 眼浄色（眼の透明性） ----
    {
      pali_term = "cakkhu-pasāda",
      ja_label = "眼浄色",
      en_label = "eye-transparent-element",
      category = "pasāda-rūpa",
      category_ja = "五浄色（感官の透明性物質）",
      canonical = true,
      applied_marker_required = false,
      source_refs = [ "DhsA.349", "Vs.2.74" ],
      pali_compact =
        "rūpābhighātāraha-bhūta-ppasāda-lakkhaṇaṃ "
        ++ "(daṭṭhukāmatā-nidāna-kamma-samuṭṭhāna-bhūtappasāda-lakkhaṇaṃ vā), "
        ++ "rūpesu āviñchana-rasaṃ, "
        ++ "cakkhu-viññāṇassa ādhāra-bhāva-paccupaṭṭhānaṃ, "
        ++ "daṭṭhu-kāmatā-nidāna-kammaja-bhūta-padaṭṭhānaṃ.",
      analysis = {
        lakkhana = {
          pali = "rūpābhighātāraha-bhūta-ppasāda",
          ja = "色境（見られる対象）の刺激を受けるに耐える、倶生四大の透明性",
          en = "the sensitivity of primary elements (in its own kalāpa) that is ready for the impact of visible data; or that originated by kamma sourcing from craving to see",
          gloss_ja = "見ることへの渇愛から生じた業によってもたらされた、四大の感受性ともいえる。",
        },
        rasa = {
          pali = "rūpesu āviñchana",
          ja = "色境への認識過程を引き寄せる作用",
          en = "to pick up / fetch the cognitive-process to a visible object — to pull the mind toward the visible",
          gloss_ja = "心を色境（見られる対象）の方へ向けさせる。",
        },
        paccupatthana = {
          pali = "cakkhu-viññāṇassa ādhāra-bhāva",
          ja = "眼識および相応心所の足場・基盤として現れる",
          en = "as the footing or foundation of eye-consciousness and the mental factors associated with it",
          gloss_ja = "眼識が成立する場として経験に立ち現れる。",
        },
        padatthana = {
          pali = "daṭṭhu-kāmatā-nidāna-kammaja-bhūta",
          ja = "見たいという渇愛に由来する業より生じた、倶生四大",
          en = "the primary elements (in its own kalāpa) born of kamma sourcing from craving to see",
          gloss_ja = "業生四大が眼浄色を支えている近接条件。",
        },
      },
    },

    # ---- 5. 色境（見られる対象） ----
    {
      pali_term = "rūpa",
      ja_label = "色境",
      en_label = "colour / visible data",
      category = "gocara-rūpa",
      category_ja = "五境（感官の対象物質）",
      canonical = true,
      applied_marker_required = false,
      source_refs = [ "DhsA.355", "Vs.2.76" ],
      pali_compact =
        "cakkhu-paṭihanana-lakkhaṇaṃ, "
        ++ "cakkhu-viññāṇassa visaya-bhāva-rasaṃ, "
        ++ "tasseva gocara-paccupaṭṭhānaṃ, "
        ++ "catu-mahābhūta-padaṭṭhānaṃ.",
      analysis = {
        lakkhana = {
          pali = "cakkhu-paṭihanana",
          ja = "眼浄色に衝突するという特相",
          en = "impinging on the eye-transparent-element",
          gloss_ja = "見られる対象が眼浄色に当たる、その当たりこそが色境の芯。",
        },
        rasa = {
          pali = "cakkhu-viññāṇassa visaya-bhāva",
          ja = "眼識および相応心所の対象となる作用",
          en = "to be the object of eye-consciousness and the mental factors associated with it",
          gloss_ja = "認識の対象として立てられる。",
        },
        paccupatthana = {
          pali = "tasseva gocara",
          ja = "そのもの（眼識）の所行領域として現れる",
          en = "as the resort / objective field of that very (eye-)consciousness",
          gloss_ja = "眼識が遊行する領域として経験に立ち現れる。",
        },
        padatthana = {
          pali = "catu-mahābhūta",
          ja = "（その自 kalāpa における）四大",
          en = "the four great primary elements in its own kalāpa",
          gloss_ja = "色境を「いま」支えている近接条件は、その自 kalāpa の四大。",
        },
      },
    },
  ],

  # Skill 実装からの参照ポイント
  usage_hints = {
    canonical_lookup =
      "examples[].pali_term と examples[].ja_label をキーに、入力対象が古典明示トピックか判定する。"
      ++ "ヒットすれば canonical = true として applied_marker_required = false で扱う。",
    output_table_mapping =
      "出力の要約表（4 行）は analysis.lakkhana / rasa / paccupatthana / padatthana の "
      ++ "{ ja, pali } を 3 列（項目 / パーリ語 / 要約）に展開する。",
    paraphrase_rule =
      "Pali 語が出現する箇所では必ず ja を併記する（REQ-006 / NFR-202）。"
      ++ "本ファイルの examples[].analysis.<key>.{ja, pali} がそのまま併記の根拠になる。",
    detail_seed =
      "詳説 4 セクションは gloss_ja を出発点として、長さモード（short / normal / detailed）に応じ "
      ++ "3〜5 文または 5〜8 文に展開する。",
  },
}
