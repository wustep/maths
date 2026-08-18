#!/bin/sh
# q4 driver: run the orbit DFS over every generated group file at n=49.
# Deterministic per case; a case is only "exhausted" if it prints RESULT.
# Timeouts produce a TIMEOUT line instead; those cases prove nothing.
set -u
cd "$(dirname "$0")/../.." || exit 2
ENGINE=compute/q4/orbit_dfs
LOG=compute/q4/orbit_runs.log
touch "$LOG"
# flagship order-7 cases first, then everything else alphabetically
CASES="cyc_L7_t1_7_1__7_1__7_1 cyc_L7_t1_7_1__7_1__7_3 cyc_L7_t4_7_1__7_1 \
cyc_L7_t4_7_1__7_3 cyc_L7_t7_7_1"
for g in compute/q4/groups/*.grp; do
    base=$(basename "$g" .grp)
    case " $CASES " in
        *" $base "*) ;;
        *) CASES="$CASES $base" ;;
    esac
done
for base in $CASES; do
    g="compute/q4/groups/$base.grp"
    [ -f "$g" ] || continue
    if grep -q "RESULT group=$g " "$LOG"; then
        continue
    fi
    echo "=== $base $(date -u +%H:%M:%S)" >> "$LOG"
    timeout "${CASE_TIMEOUT:-1800}" "$ENGINE" --group "$g" --n 49 >> "$LOG" 2>&1
    status=$?
    if [ "$status" = 124 ]; then
        echo "TIMEOUT group=$g" >> "$LOG"
    elif [ "$status" != 0 ]; then
        echo "ERROR group=$g status=$status" >> "$LOG"
    fi
done
echo "=== driver done $(date -u +%H:%M:%S)" >> "$LOG"
