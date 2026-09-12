#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
q15_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ion-q15-replay.XXXXXXXX")
trap 'rm -rf -- "$q15_tmp"' EXIT
"${PYTHON:-python3}" verify.py certificate.json
rustc --edition=2021 -O -C overflow-checks=on verify.rs -o "$q15_tmp/verify"
"$q15_tmp/verify" certificate.json
echo 'q15 CLAIM verified by both implementations.'
