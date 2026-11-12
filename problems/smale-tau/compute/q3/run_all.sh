#!/usr/bin/env bash
# Exit 0 means CLAIM.md holds, including both exhaustive enumerations.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 replay.py "$@"
