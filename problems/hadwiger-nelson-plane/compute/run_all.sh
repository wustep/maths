#!/bin/sh
set -eu
cd "$(dirname "$0")"
./q1/run_all.sh &
hn_q1_pid=$!
./q2/run_all.sh &
hn_q2_pid=$!
./q3/run_all.sh &
hn_q3_pid=$!
hn_failed=0
wait "$hn_q1_pid" || hn_failed=1
wait "$hn_q2_pid" || hn_failed=1
wait "$hn_q3_pid" || hn_failed=1
if [ "$hn_failed" -ne 0 ]; then
    exit 1
fi
echo "all Hadwiger–Nelson compute replays complete"
