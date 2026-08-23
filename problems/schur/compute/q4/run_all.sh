#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp_log=$(mktemp /tmp/schur-q4-local.XXXXXX)
cleanup() {
  rm -f "$tmp_log"
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
