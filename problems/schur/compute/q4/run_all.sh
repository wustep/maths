#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp_log=$(mktemp /tmp/schur-q4-local.XXXXXX)
tmp_templates=$(mktemp /tmp/schur-q4-templates.XXXXXX)
tmp_shift=$(mktemp /tmp/schur-q4-shift.XXXXXX)
tmp_coloring=$(mktemp /tmp/schur-q4-coloring.XXXXXX)
cleanup() {
  rm -f "$tmp_log" "$tmp_templates" "$tmp_shift" "$tmp_coloring"
}
trap cleanup EXIT HUP INT TERM

python3 "$here/../q3/audit_near.py" \
  "$here/../q3/near_1697_two_violations.txt"
python3 "$here/local_repair.py" \
  "$here/../q3/near_1697_two_violations.txt" \
  --sizes 0,16,32,64,128 --seconds 8 --log "$tmp_log"
python3 - "$here/local_repair.json" "$tmp_log" <<'PY'
import json
import sys

expected = json.load(open(sys.argv[1], encoding="utf-8"))
actual = json.load(open(sys.argv[2], encoding="utf-8"))
for report in (expected, actual):
    for run in report["runs"]:
        run.pop("elapsed_seconds", None)
if actual != expected:
    raise SystemExit("local repair replay differs from preserved report")
print("q4 local replay: five fixed-outside neighborhoods are UNSAT")
PY
python3 "$here/scan_templates.py" \
  "$here/../q3/near_1697_two_violations.txt" --log "$tmp_templates"
cmp "$here/template_scan.json" "$tmp_templates"
printf '%s\n' 'q4 transform replay: no coloring in either finite family'
shift_status=0
python3 "$here/search_shift537.py" \
  "$here/../q3/near_1697_two_violations.txt" --seconds 30 \
  --log "$tmp_shift" --output "$tmp_coloring" || shift_status=$?
if [ "$shift_status" -ne 1 ]; then
  printf '%s\n' "unexpected shift-search exit status: $shift_status" >&2
  exit 1
fi
python3 - "$here/shift537_glucose42.json" "$tmp_shift" <<'PY'
import json
import sys

expected = json.load(open(sys.argv[1], encoding="utf-8"))
actual = json.load(open(sys.argv[2], encoding="utf-8"))
for report in (expected, actual):
    report.pop("encoding_seconds", None)
    report.pop("solver_and_encoding_seconds", None)
if actual != expected or actual["result"] != "unsat":
    raise SystemExit("537-shift replay differs from preserved UNSAT result")
print("q4 symmetry replay: 537-step color-twisted translation is UNSAT")
PY
