#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
build_dir=$(mktemp -d /tmp/schur-q3-build.XXXXXX)
cleanup() {
  rm -f "$build_dir/search_unrestricted"
  rmdir "$build_dir"
}
trap cleanup EXIT HUP INT TERM

python3 "$here/../verify_coloring.py" "$here/rowley_1696.txt" --expect-length 1696
python3 "$here/analyze_rowley_extension.py" "$here/rowley_1696.txt"
python3 "$here/audit_near.py" "$here/near_1697_two_violations.txt"
lean "$here/../../lean/Schur1697SymmetryObstruction.lean"
gcc -O3 -std=c11 -Wall -Wextra -Werror \
  -o "$build_dir/search_unrestricted" "$here/search_unrestricted.c"
printf '%s\n' 'q3 replay: valid Rowley base; exact two-violation residue; Lean and C compile'
