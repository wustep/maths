#!/usr/bin/env bash
# Replay I_s(ν) for s>3 (HPS Lemma 4.3). Not a new bound.
set -euo pipefail
cd "$(dirname "$0")"
python3 s_gt_3.py
python3 - <<'PY'
import json
from pathlib import Path
blob = json.loads(Path("certs/s_gt_3.json").read_text())
v = blob["verdict"]
assert v["I_s_goes_negative_for_s_gt_3"] is True
assert v["certified_path_to_s_gt_3"] is False
assert v["I_3_stays_nonnegative_on_all_examples"] is True
b4 = float(v["b4"])
assert 1.08302 < b4 < 1.08303
assert v["b4_lt_1.1185"] is True
q4 = blob["exact_negative_Q"]["s4_t_1/8_alpha_16_beta_-1"]["Q"]
assert q4 == "-1025/2048"
signs = {ex["name"]: ex["sign"] for ex in blob["two_shell_certified"]}
assert signs["dipole_two_shell_s4"] == "negative"
assert signs["dipole_two_shell_s35"] == "negative"
assert signs["dipole_two_shell_s31"] == "negative"
assert signs["dipole_two_shell_s3_balanced"] == "positive"
assert signs["quad_two_shell_s4_opposite"] == "positive"
smeared = {row["s"]: row["sign"] for row in blob["smeared_two_shell_volume"]}
assert smeared[4.0] == "negative"
assert smeared[3.5] == "negative"
assert smeared[3.0] == "positive"
print("run_s_gt_3.sh cert checks OK")
PY
