#!/usr/bin/env bash
# Problem-level replay: q1 published-record checks.
set -euo pipefail
cd "$(dirname "$0")/q1"
exec ./run_all.sh
