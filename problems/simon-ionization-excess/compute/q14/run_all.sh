#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
q14_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ion-q14-replay.XXXXXXXX")
trap 'rm -rf -- "$q14_tmp"' EXIT
"${PYTHON:-python3}" verify.py certificate.json
rustc --edition=2021 -O -C overflow-checks=on verify.rs -o "$q14_tmp/verify"
"$q14_tmp/verify" certificate.json
echo 'q14 CLAIM verified by both implementations.'
