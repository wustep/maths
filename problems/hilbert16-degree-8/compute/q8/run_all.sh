#!/bin/sh
# Exit zero only for the q8 existence claim, never for an empty search.
set -eu
cd "$(dirname "$0")"
python3 controls.py
python3 verify.py "$@"
