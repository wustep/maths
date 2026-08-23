#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
python3 "$here/audit_encoding.py"
python3 "$here/encode.py" --n 33 --k 7 --count-only

solver="${KISSAT:-}"
if [ -z "$solver" ] && command -v kissat >/dev/null 2>&1; then
  solver="$(command -v kissat)"
fi
if [ -z "$solver" ]; then
  echo "q2 small SAT regression skipped: set KISSAT or install kissat"
  exit 0
fi

build_dir="$(mktemp -d)"
trap 'rm -rf "$build_dir"' EXIT

python3 "$here/encode.py" --n 8 --k 5 --out "$build_dir/n8.cnf"
set +e
"$solver" -n "$build_dir/n8.cnf" > "$build_dir/n8.log"
status=$?
set -e
test "$status" -eq 10
grep -q '^s SATISFIABLE' "$build_dir/n8.log"

python3 "$here/encode.py" --n 9 --k 5 --out "$build_dir/n9.cnf"
set +e
"$solver" -n --no-binary "$build_dir/n9.cnf" "$build_dir/n9.drat" > "$build_dir/n9.log"
status=$?
set -e
test "$status" -eq 20
grep -q '^s UNSATISFIABLE' "$build_dir/n9.log"

checker="${DRAT_TRIM:-}"
if [ -z "$checker" ] && command -v drat-trim >/dev/null 2>&1; then
  checker="$(command -v drat-trim)"
fi
if [ -n "$checker" ]; then
  "$checker" "$build_dir/n9.cnf" "$build_dir/n9.drat" > "$build_dir/check.log"
  grep -q 's VERIFIED' "$build_dir/check.log"
  echo "q2 proof regression: n=9 DRAT verified"
fi
echo "q2 SAT regression: n=8 SAT and n=9 UNSAT for k=5"
