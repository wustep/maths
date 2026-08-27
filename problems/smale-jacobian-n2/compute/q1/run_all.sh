#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
CERTIFICATE="$ROOT/certificate.json"
WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/jc2-q1.XXXXXXXX")
trap 'rm -rf "$WORK_DIR"' EXIT

python3 "$ROOT/verify_bridge.py" "$CERTIFICATE" > "$WORK_DIR/bridge-python.out"
rustc --edition=2021 -O "$ROOT/verify_bridge.rs" -o "$WORK_DIR/verify_bridge_rs"
"$WORK_DIR/verify_bridge_rs" "$CERTIFICATE" > "$WORK_DIR/bridge-rust.out"
diff -u "$WORK_DIR/bridge-python.out" "$WORK_DIR/bridge-rust.out"
cat "$WORK_DIR/bridge-python.out"
echo "BRIDGE_CROSS_IMPLEMENTATION_PASS"

ARCHIVE=${JC2_72_108_ARCHIVE:-}
if [[ -z "$ARCHIVE" ]]; then
  ARCHIVE="$WORK_DIR/jc2_72_108_exact_replay_v1.0.1.zip"
  URL=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["external_exact_certificate"]["url"])' "$CERTIFICATE")
  echo "Downloading the pinned 86 MB exact certificate archive..."
  curl --fail --location "$URL" --output "$ARCHIVE"
fi

python3 "$ROOT/verify_archive.py" "$CERTIFICATE" "$ARCHIVE" --extract "$WORK_DIR/unpacked"

CERT_PYTHON=${JC2_72_108_PYTHON:-}
if [[ -z "$CERT_PYTHON" ]]; then
  python3 -m venv "$WORK_DIR/venv"
  CERT_PYTHON="$WORK_DIR/venv/bin/python"
  "$CERT_PYTHON" -m pip install --quiet --requirement "$ROOT/requirements.txt"
fi

(
  cd "$WORK_DIR/unpacked/exact_replay"
  PYTHON="$CERT_PYTHON" bash ./verify_all.sh
) | tee "$WORK_DIR/replay.out"

python3 "$ROOT/verify_archive.py" "$CERTIFICATE" "$ARCHIVE" --output "$WORK_DIR/replay.out"
echo "Q1_DEGREE_125_CERTIFICATE_PASS"
