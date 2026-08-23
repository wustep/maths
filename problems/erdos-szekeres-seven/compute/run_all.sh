#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

python3 "$here/verify_record.py"
"$here/q1/run_all.sh"
