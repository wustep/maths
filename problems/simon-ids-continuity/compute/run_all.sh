#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
replay_tmp="$(mktemp -d)"
trap 'rm -rf -- "$replay_tmp"' EXIT

python3 "$script_dir/q1/verify_frontier.py" "$script_dir/q1" \
  > "$replay_tmp/python.txt"
rustc --edition=2021 -O "$script_dir/q1/verify_frontier.rs" \
  -o "$replay_tmp/verify_frontier"
"$replay_tmp/verify_frontier" "$script_dir/q1" \
  > "$replay_tmp/rust.txt"

diff -u "$replay_tmp/python.txt" "$replay_tmp/rust.txt"
sed -n '1,200p' "$replay_tmp/python.txt"
