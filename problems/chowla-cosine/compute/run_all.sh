#!/bin/sh
# Replay every certificate in this folder. Expected: all OK, exit 0.
set -e
cd "$(dirname "$0")"
python3 verify_lemma72.py
python3 lemma71_bounds.py
python3 track_constants.py
python3 verify_certificate.py
echo "ALL OK"
