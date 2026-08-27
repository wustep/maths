#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OLC_REPO=${1:?usage: replay_olc.sh /path/to/olc}
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

python3 "$SCRIPT_DIR/audit_olc.py" \
  --repo "$OLC_REPO" \
  --rows-output "$TMP_DIR/olc_rows.tsv.gz" \
  --summary-output "$TMP_DIR/olc_public_audit.json"
cmp "$TMP_DIR/olc_rows.tsv.gz" "$SCRIPT_DIR/certs/olc_rows.tsv.gz"
cmp "$TMP_DIR/olc_public_audit.json" "$SCRIPT_DIR/certs/olc_public_audit.json"
python3 "$SCRIPT_DIR/verify_olc_audit.py" \
  --rows "$SCRIPT_DIR/certs/olc_rows.tsv.gz" \
  --summary "$SCRIPT_DIR/certs/olc_public_audit.json"
echo "PASS olc_upstream_replay commit=5cdaa95f0a4b1428a05480cc1c69d556a8f9517a"
