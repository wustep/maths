#!/bin/bash
# Exhaust exactly the subgroup classes left open after q4 and q6a.
#
# A timeout proves nothing.  Completed cases are skipped only when this
# dedicated log already contains their full RESULT line.
set -u

cd "$(dirname "$0")/../.." || exit 2

ENGINE=compute/q4/orbit_dfs
LOG="${LOG:-compute/q7a/orbit_leftovers.log}"
CASE_TIMEOUT="${CASE_TIMEOUT:-43200}"
OPEN_GROUPS=(
    cyc_L21_t5_3_1__7_1
    cyc_L15_t4_3_1__5_1
    cyc_L15_t6_15_1
    cyc_L7_t4_7_1__7_1
    cyc_L7_t4_7_1__7_3
    cyc_L7_t7_7_1
    cyc_L5_t6_5_1
    cyc_L3_t2_3_1__3_1__3_1__3_1
    cyc_L3_t4_3_1__3_1__3_1
    cyc_L3_t6_3_1__3_1
    cyc_L3_t8_3_1
)

touch "$LOG"
for base in "${OPEN_GROUPS[@]}"; do
    group="compute/q4/groups/$base.grp"
    if grep -Fq "RESULT group=$group n=49 " "$LOG"; then
        continue
    fi
    printf '=== %s %s\n' "$base" "$(date -u +%FT%TZ)" >>"$LOG"
    timeout "$CASE_TIMEOUT" "$ENGINE" --group "$group" --n 49 >>"$LOG" 2>&1
    status=$?
    if [[ $status -eq 124 ]]; then
        printf 'TIMEOUT group=%s\n' "$group" >>"$LOG"
    elif [[ $status -ne 0 ]]; then
        printf 'ERROR group=%s status=%d\n' "$group" "$status" >>"$LOG"
    fi
done
printf '=== leftovers driver done %s\n' "$(date -u +%FT%TZ)" >>"$LOG"
