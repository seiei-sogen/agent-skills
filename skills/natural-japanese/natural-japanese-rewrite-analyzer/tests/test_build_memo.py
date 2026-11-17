# /// script
# requires-python = ">=3.10"
# dependencies = ["rhoknp>=1.8", "pyyaml"]
# ///
"""usage: uv run tests/test_build_memo.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

here = Path(__file__).parent
with tempfile.TemporaryDirectory() as tmp:
    text = Path(tmp, "input.txt")
    text.write_text("dummy", encoding="utf-8")
    script = here.parent / "scripts" / "build_memo.py"
    out = subprocess.run([sys.executable, str(script), str(text), str(here / "sample.kwja.txt")], check=True, capture_output=True, text=True)
    memo = yaml.safe_load(Path(out.stdout.strip()).read_text(encoding="utf-8"))

assert memo["schema_version"] == 3
assert [s["sid"] for s in memo["sentences"]] == [1, 2]
first = memo["sentences"][0]
assert first["phrases"][0].startswith("0>7D 曖昧さを")

# 「曖昧さを … 整理したい」: ヲ格は係り受けのある明示項、ガ格は外界照応のゼロ項。
seiri = next(p for p in first["predicates"] if p["attrs"]["surface"] == "整理したい")
args = {a["role"]: a for a in seiri["arguments"]}
assert args["ヲ"] | {"surface": None} == {"role": "ヲ", "at": "1/0", "surface": None, "realization": "overt", "particle": "を"}
assert args["ガ"] == {"role": "ガ", "realization": "zero", "referent": "外界:不特定:人", "recoverability": "clear"}

# 文をまたぐゼロ項は、先行詞の位置を持つ。
kaezu = memo["sentences"][1]["predicates"][0]
wo = next(a for a in kaezu["arguments"] if a["role"] == "ヲ")
assert (wo["realization"], wo["at"], wo["recoverability"]) == ("zero", "1/3", "clear")
assert kaezu["attrs"]["polarity"] == "negative"

for key in ("source_alignment", "protected_ranges", "rewrite_targets", "issues", "ambiguities", "graph_invariants", "rewrite_policy"):
    assert memo[key] == []
print("ok")
