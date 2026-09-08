#!/usr/bin/env bash
set -euo pipefail
unset PYTHONOPTIMIZE PYTHONPATH PYTHONHOME
export PYTHONDONTWRITEBYTECODE=1
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
upstream=${1:?usage: run_all.sh PINNED_UPSTREAM_CHECKOUT NEW_OUTPUT_DIRECTORY}
out=${2:?usage: run_all.sh PINNED_UPSTREAM_CHECKOUT NEW_OUTPUT_DIRECTORY}
if [[ -e "$out" ]]; then
  echo 'FAIL: output directory must be new; stored transcripts are not a fresh proof run' >&2
  exit 2
fi
mkdir -p "$out"
out=$(CDPATH= cd -- "$out" && pwd)
upstream=$(CDPATH= cd -- "$upstream" && pwd)
test "$(git -C "$upstream" rev-parse HEAD)" = a74738deb6d5e0f76887cb36901da08b68dca705
test -z "$(git -C "$upstream" status --porcelain --untracked-files=all)"
python3 -c 'import mpmath, sympy, flint'
bash "$here/build.sh" "$out/build" > "$out/build.txt"
python3 "$here/check_small.py" "$out/build/interpolate" > "$out/small-checks.txt"
python3 "$here/regenerate.py" "$upstream" "$out/build/original" "$out/finite" \
  > "$out/finite-driver.txt"
python3 "$here/run_independent.py" "$out/build" "$out/independent" \
  --lock "$out/finite/.lock" > "$out/independent-driver.txt"
extra=()
if [[ -n ${FLINT_PREFIX:-} ]]; then extra=(--flint-prefix "$FLINT_PREFIX"); fi
python3 "$here/replay_analytic.py" "$upstream" "$out/analytic" \
  --lock "$out/finite/.lock" "${extra[@]}" > "$out/analytic-driver.txt"
python3 "$here/verify_finite.py" "$out/finite" "$out/independent" \
  --summary "$out/finite-summary.json"
python3 "$here/verify_analytic.py" "$upstream" "$out/analytic"
echo 'PASS CLAIM: Lambda <= 893927/5000000 = 0.1787854 < 1/5'
