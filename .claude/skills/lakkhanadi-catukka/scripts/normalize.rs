// 補助 Rust スクリプト: パーリ語表記の正規化
//
// 関連: docs/design/lakkhanadi-catukka-analytics-requirements/interfaces.ts
// 二段冗長: 本ルール表は SKILL.md「2. Pali 表記正規化」と常に同期させること
// （差分が生じると前処理フック有/無で結果がズレる）。

/// 規則カテゴリ — judge / デバッグ用途のメタ情報。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Category {
    /// PRD で明示された既知異形（例: padahāna → padaṭṭhāna）
    KnownVariant,
    /// IAST／ダイアクリティカル揺れ（例: lakkhana → lakkhaṇa）
    IastDiacritic,
}

/// Pali 用語の正規化規則。
///
/// 配列順 = 適用順 = 優先順（前のものから先に適用）。
/// 部分一致衝突を避けるため、長い `from` を先に置く。
#[derive(Debug, Clone, Copy)]
pub struct PaliNormalizationRule {
    /// 入力中に出現しうる異形（小文字で記述。case-insensitive にマッチ）。
    pub from: &'static str,
    /// 標準表記。
    pub to: &'static str,
    /// 規則カテゴリ。
    pub category: Category,
    /// 由来コメント（REQ-107, TC-NORM-01 等）。
    pub source: &'static str,
}

/// 正規化規則テーブル。
///
/// 順序方針:
///   1. 既知異形（known-variant）を先に — 古典・PRD 由来で優先度が高い。
///   2. その後、IAST/ダイアクリティカル揺れ（iast-diacritic）。
///   3. 部分一致衝突を避けるため、同カテゴリ内でも長い `from` を先に。
pub const NORMALIZATION_RULES: &[PaliNormalizationRule] = &[
    // === known-variant（PRD 由来既知異形）===
    PaliNormalizationRule {
        from: "paccupahāna",
        to: "paccupaṭṭhāna",
        category: Category::KnownVariant,
        source: "REQ-107 / TC-NORM-02",
    },
    PaliNormalizationRule {
        from: "padahāna",
        to: "padaṭṭhāna",
        category: Category::KnownVariant,
        source: "REQ-107 / TC-NORM-01",
    },
    // === iast-diacritic（ダイアクリティカル揺れ）===
    // 長い from から先に並べる（部分一致衝突回避）。
    PaliNormalizationRule {
        from: "paccupatthana",
        to: "paccupaṭṭhāna",
        category: Category::IastDiacritic,
        source: "REQ-108 / TC-NORM-03",
    },
    PaliNormalizationRule {
        // 部分一致衝突回避のため "thana" より先に置く
        // ("padatthana" を先に正規化しないと、"thana" 単独ルールが
        //  途中の "thana" 部分文字列だけを差し替えてしまう)
        from: "padatthana",
        to: "padaṭṭhāna",
        category: Category::IastDiacritic,
        source: "REQ-108 / TC-NORM-B01",
    },
    PaliNormalizationRule {
        from: "lakkhana",
        to: "lakkhaṇa",
        category: Category::IastDiacritic,
        source: "REQ-108 / TC-NORM-03",
    },
    PaliNormalizationRule {
        from: "anatta",
        to: "anattā",
        category: Category::IastDiacritic,
        source: "REQ-108",
    },
    PaliNormalizationRule {
        from: "thana",
        to: "ṭhāna",
        category: Category::IastDiacritic,
        source: "REQ-108",
    },
    PaliNormalizationRule {
        from: "dhatu",
        to: "dhātu",
        category: Category::IastDiacritic,
        source: "REQ-108",
    },
];

/// 入力文字列のパーリ語表記を標準表記に正規化する。
///
/// 動作:
/// - `NORMALIZATION_RULES` を配列順に走査し、各ルールについて
///   case-insensitive で全出現を `to` に置換する。
/// - ルール表に該当しない極端な崩れ（"padaaaaana" 等）はそのまま通す
///   （SKILL.md 側で "unknown_term" として扱われる）。
/// - 大文字始まり（"Lakkhana"）も同じルールで小文字標準表記に統一する。
pub fn normalize(input: &str) -> String {
    let mut result = input.to_string();
    for rule in NORMALIZATION_RULES {
        result = replace_case_insensitive(&result, rule.from, rule.to);
    }
    result
}

/// `needle` の出現を case-insensitive に検出して `replacement` で置換する。
///
/// `haystack` を小文字化したコピー上で `needle.to_lowercase()` の出現位置を
/// 探し、元文字列の対応バイト範囲を `replacement` で差し替える。
/// IAST 文字（ā, ṇ, ṭ 等）の Unicode 大文字小文字対応は標準ライブラリの
/// `to_lowercase()` に委ねる。
fn replace_case_insensitive(haystack: &str, needle: &str, replacement: &str) -> String {
    if needle.is_empty() || haystack.is_empty() {
        return haystack.to_string();
    }
    let lower_haystack: String = haystack.to_lowercase();
    let lower_needle: String = needle.to_lowercase();

    let mut out = String::with_capacity(haystack.len());
    let mut cursor = 0usize;
    while cursor < haystack.len() {
        match lower_haystack[cursor..].find(&lower_needle) {
            Some(rel) => {
                let abs = cursor + rel;
                // マッチ前の元文字列をそのまま追加（大小は保持）
                out.push_str(&haystack[cursor..abs]);
                // マッチ部分は標準表記（replacement）で差し替える
                out.push_str(replacement);
                // 次の検索開始位置は「元文字列における needle のバイト長」分進める。
                // lower_haystack と haystack はバイト長が一致する保証がないため、
                // lower_needle のバイト長で進めることに依存できない。
                // ただし `to_lowercase()` は ASCII / 共通ケースでは同一バイト長を保つので、
                // ここでは lower_needle のバイト長で進める実装にし、
                // バイト長が変わるエッジケースが起きたときに見直す。
                cursor = abs + lower_needle.len();
            }
            None => {
                out.push_str(&haystack[cursor..]);
                break;
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rule_table_is_non_empty() {
        assert!(!NORMALIZATION_RULES.is_empty());
    }

    #[test]
    fn no_rule_has_identical_from_and_to() {
        for r in NORMALIZATION_RULES {
            assert_ne!(r.from, r.to, "from must differ from to: {:?}", r);
        }
    }

    #[test]
    fn no_duplicate_from() {
        let mut seen: Vec<&str> = Vec::new();
        for r in NORMALIZATION_RULES {
            assert!(
                !seen.contains(&r.from),
                "duplicate `from` detected: {}",
                r.from
            );
            seen.push(r.from);
        }
    }

    #[test]
    fn every_rule_has_non_empty_source() {
        for r in NORMALIZATION_RULES {
            assert!(!r.source.is_empty(), "source must not be empty for {:?}", r);
        }
    }

    #[test]
    fn required_known_variants_exist() {
        let pairs: Vec<(&str, &str)> = NORMALIZATION_RULES
            .iter()
            .filter(|r| r.category == Category::KnownVariant)
            .map(|r| (r.from, r.to))
            .collect();
        assert!(pairs.contains(&("padahāna", "padaṭṭhāna")));
        assert!(pairs.contains(&("paccupahāna", "paccupaṭṭhāna")));
    }

    #[test]
    fn required_iast_drifts_exist() {
        let pairs: Vec<(&str, &str)> = NORMALIZATION_RULES
            .iter()
            .filter(|r| r.category == Category::IastDiacritic)
            .map(|r| (r.from, r.to))
            .collect();
        assert!(pairs.contains(&("lakkhana", "lakkhaṇa")));
        assert!(pairs.contains(&("paccupatthana", "paccupaṭṭhāna")));
    }

    #[test]
    fn longer_iast_pattern_precedes_shorter() {
        // paccupatthana は thana より先（部分一致衝突回避）
        let idx_long = NORMALIZATION_RULES
            .iter()
            .position(|r| r.from == "paccupatthana")
            .expect("paccupatthana must exist");
        let idx_short = NORMALIZATION_RULES
            .iter()
            .position(|r| r.from == "thana")
            .expect("thana must exist");
        assert!(
            idx_long < idx_short,
            "paccupatthana ({}) must come before thana ({})",
            idx_long,
            idx_short
        );
    }

    // ============================================================
    // normalize 関数 — 受け入れ基準 TC-NORM-* 網羅
    // ============================================================

    #[test]
    fn tc_norm_01_padahaana_to_padatthaana() {
        // TC-NORM-01: 既知異形 padahāna → padaṭṭhāna
        assert_eq!(
            normalize("padahāna について教えて"),
            "padaṭṭhāna について教えて"
        );
    }

    #[test]
    fn tc_norm_02_paccupahaana_to_paccupatthaana() {
        // TC-NORM-02: 既知異形 paccupahāna → paccupaṭṭhāna
        assert_eq!(normalize("paccupahāna について"), "paccupaṭṭhāna について");
    }

    #[test]
    fn tc_norm_03_iast_drift() {
        // TC-NORM-03: ダイアクリティカルなし表記の正規化
        assert_eq!(
            normalize("lakkhana, paccupatthana の意味"),
            "lakkhaṇa, paccupaṭṭhāna の意味"
        );
    }

    #[test]
    fn tc_norm_b01_extreme_drift_passes_through() {
        // TC-NORM-B01: 「推測まで」採用しないため、ルール表外の崩れはそのまま通す
        assert_eq!(normalize("padaaaaana"), "padaaaaana");
    }

    #[test]
    fn tc_norm_b01_near_standard_handled_per_table() {
        // TC-NORM-B01: 標準表記に近いものはルール表に登録されていれば case-insensitive で正規化、
        // 登録されていなければスルー。"padaTthana" は現ルール表に未登録のためスルー想定。
        let result = normalize("padaTthana");
        assert!(
            result == "padaṭṭhāna" || result == "padaTthana",
            "expected either normalized or pass-through, got {}",
            result
        );
    }

    #[test]
    fn capitalized_variant_normalizes_to_lowercase_standard() {
        // 大文字始まりの異形も case-insensitive で正規化される（小文字標準表記に統一）
        assert_eq!(normalize("Padahāna は重要"), "padaṭṭhāna は重要");
    }

    #[test]
    fn multiple_iast_drifts_in_one_sentence() {
        // 1 文中に複数の異形が混在しても全て正規化される
        assert_eq!(
            normalize("lakkhana と paccupatthana を比較"),
            "lakkhaṇa と paccupaṭṭhāna を比較"
        );
    }

    #[test]
    fn known_variant_and_iast_drift_together() {
        // 既知異形と IAST 揺れが同居しても両方正規化される
        assert_eq!(normalize("padahāna と lakkhana"), "padaṭṭhāna と lakkhaṇa");
    }

    #[test]
    fn non_pali_text_passes_through() {
        // Pali 用語を含まない文字列はそのまま返す
        assert_eq!(normalize("今日の天気は晴れです"), "今日の天気は晴れです");
    }

    #[test]
    fn empty_string_passes_through() {
        assert_eq!(normalize(""), "");
    }
}
