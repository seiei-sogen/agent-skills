# /// script
# requires-python = ">=3.10"
# dependencies = ["rhoknp>=1.8"]
# ///
"""KWJA の KNP ファイルから、分析メモの KWJA 由来部分を作る。

usage: uv run build_memo.py <解析用テキスト> <KNP ファイル>
出力: <解析用テキスト>.memo.yaml（保存先を標準出力に返す）
"""
import json
import sys
from pathlib import Path

from rhoknp import Document

# LLM が判断して埋めるキー。スクリプトは空で出す。
LLM_KEYS = ("source_alignment", "protected_ranges", "rewrite_targets", "issues", "ambiguities", "graph_invariants", "rewrite_policy")
PREDICATE_TYPE = {"動": "verb", "形": "adjective", "判": "copula"}
# 行数の多い割にリライトの判定で使わない素性。KNP ファイルには残る。
NOISY_FEATURES = {"談話関係", "体言", "動態述語", "状態述語", "節-主辞", "レベル"}
VOICE_HINT = {"れる": "passive-or-potential", "られる": "passive-or-potential", "せる": "causative", "させる": "causative"}


def flow(value):
    return json.dumps(value, ensure_ascii=False)


def number(sid):
    return int(sid.rsplit("-", 1)[1])


def build(doc):
    phrases = {(number(s.sid), bp.index): bp for s in doc.sentences for bp in s.base_phrases}

    def at(key):
        return f"{key[0]}/{key[1]}"

    def rels(bp):
        for rel in bp.rel_tags:
            target = (number(rel.sid), rel.base_phrase_index) if rel.sid else None
            yield rel.type, rel.target, target if target in phrases else None

    # 共参照（= で始まる関係）でつながる基本句を、同じ entity にまとめる。
    root = {}

    def find(key):
        while root.setdefault(key, key) != key:
            key = root[key]
        return key

    for key, bp in phrases.items():
        for kind, _, target in rels(bp):
            if kind.startswith("=") and target:
                root[find(key)] = find(target)
    clusters = {}
    for key in sorted(root):
        clusters.setdefault(find(key), []).append(key)
    entity_of = {key: f"e{i}" for i, members in enumerate(clusters.values(), 1) for key in members}
    entities = [
        {"id": entity_of[members[0]], "mentions": [f"{at(k)} {phrases[k].text.strip()}" for k in members]}
        for members in clusters.values()
    ]

    def argument(sid, bp, case, target_text, target):
        if target is None:
            return {"role": case, "realization": "zero", "referent": f"外界:{target_text}"}
        arg = {"role": case, "at": at(target), "surface": target_text}
        if target in entity_of:
            arg["entity"] = entity_of[target]
        target_bp = phrases[target]
        if target[0] == sid and target_bp.parent_index == bp.index:
            particles = [m.text for m in target_bp.morphemes if m.pos == "助詞"]
            arg |= {"realization": "overt", "particle": particles[-1] if particles else None}
        elif target[0] == sid and bp.parent_index == target[1]:
            arg["realization"] = "relative-gap"
        else:
            arg["realization"] = "zero"
        return arg

    sentences, bridging, discourse = [], [], []
    for s in doc.sentences:
        sid = number(s.sid)
        lines, predicates = [], []
        for bp in s.base_phrases:
            feats = [k if v is True else f"{k}:{v}" for k, v in bp.features.items() if k not in NOISY_FEATURES]
            conj = [m.conjform for m in bp.morphemes if m.conjform != "*"]
            feats += [f"活用:{conj[-1]}"] if conj and conj[-1] != "基本形" else []
            parent = -1 if bp.parent_index is None else bp.parent_index
            lines.append(f"{bp.index}>{parent}{bp.dep_type.value} {bp.text.strip()}" + (f" | {' '.join(feats)}" if feats else ""))
            if "談話関係" in bp.features:
                discourse.append(f"{sid}/{bp.index} {bp.text.strip()} -> " + str(bp.features["談話関係"]).replace(s.sid.rsplit("-", 1)[0] + "-", ""))

            args = []
            for kind, target_text, target in rels(bp):
                if kind.startswith("="):
                    continue
                if kind.startswith("ノ"):
                    bridging.append(f"{sid}/{bp.index} {bp.text.strip()} -[{kind}]-> " + (f"{at(target)} {target_text}" if target else f"外界:{target_text}"))
                else:
                    args.append(argument(sid, bp, kind, target_text, target))
            if "用言" not in bp.features and not args:
                continue
            # KWJA が同じ格に先行詞を1つ出せば clear、複数なら ambiguous。
            per_case = {}
            for arg in args:
                per_case[arg["role"]] = per_case.get(arg["role"], 0) + 1
            for arg in args:
                if arg["realization"] != "overt":
                    arg["recoverability"] = "clear" if per_case[arg["role"]] == 1 else "ambiguous"
            attrs = {
                "id": f"p{sid}.{bp.index}",
                "surface": bp.text.strip(),
                "type": PREDICATE_TYPE.get(bp.features.get("用言"), "event-noun"),
                "polarity": "negative" if "否定表現" in bp.features else None,
                "tense": bp.features.get("時制"),
                "voice_hint": next((VOICE_HINT[m.lemma] for m in bp.morphemes if m.pos == "接尾辞" and m.lemma in VOICE_HINT), None),
            }
            # 既定値（肯定、時制なし、態の手がかりなし）のキーは出さない。
            predicates.append({k: v for k, v in attrs.items() if v is not None} | {"arguments": args})
        sentences.append({"sid": sid, "text": s.text.strip(), "phrases": lines, "predicates": predicates})
    return sentences, entities, bridging, discourse


def render(input_file, result_file, sentences, entities, bridging, discourse):
    out = [
        "schema_version: 3",
        f"analysis_source: {flow({'input_file': input_file, 'result_file': result_file})}",
        "# ここから discourse までは build_memo.py が KWJA の出力から作った。編集しない。",
        "# phrases の書式: 基本句番号>係り先番号+係り種別 表層 | KWJA の素性。参照先は 文番号/基本句番号。",
        "sentences:",
    ]
    for s in sentences:
        out += [f"- sid: {s['sid']}", f"  text: {flow(s['text'])}", "  phrases:"]
        out += [f"  - {flow(line)}" for line in s["phrases"]]
        out.append("  predicates:" if s["predicates"] else "  predicates: []")
        for p in s["predicates"]:
            args = p.pop("arguments")
            out.append(f"  - attrs: {flow(p)}")
            out.append("    arguments:" if args else "    arguments: []")
            out += [f"    - {flow(a)}" for a in args]
    for name, items in (("entities", entities), ("bridging", bridging), ("discourse", discourse)):
        out.append(f"{name}:" if items else f"{name}: []")
        out += [f"- {flow(item)}" for item in items]
    out.append("# ここから下は LLM が原文と上の解析結果を照合して埋める。")
    out += [f"{key}: []" for key in LLM_KEYS]
    return "\n".join(out) + "\n"


def main():
    if len(sys.argv) != 3:
        sys.exit(f"usage: {Path(sys.argv[0]).name} <解析用テキスト> <KNP ファイル>")
    input_file, result_file = sys.argv[1:]
    doc = Document.from_knp(Path(result_file).read_text(encoding="utf-8"))
    if not doc.sentences:
        sys.exit(f"{result_file} に文がない")
    memo = Path(f"{input_file}.memo.yaml")
    memo.write_text(render(input_file, result_file, *build(doc)), encoding="utf-8")
    print(memo)


if __name__ == "__main__":
    main()
