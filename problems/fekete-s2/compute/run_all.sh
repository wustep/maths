#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 known.py
python3 verify_replay.py
if [[ -d /tmp/fekete-data/rathbun ]]; then
  python3 replay_published.py
else
  echo "Rathbun cache absent; replay table is compute/replay_rathbun.json"
  echo "To refetch: unzip Zenodo 10.5281/zenodo.5595366 log.0-65.zip into /tmp/fekete-data/rathbun"
fi
echo
echo "To search (deterministic seeds):"
echo "  python3 optimize.py 7 8 9 10 14 19 24 32 33 46 48"
