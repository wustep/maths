#!/bin/sh
set -eu
cd "$(dirname "$0")/../../"
python3 compute/verify_certificate.py
python3 compute/q14/verify_best.py
cc -O3 -Wall -Wextra -o /tmp/q14_switch compute/q14/switch_2to1.c
cc -O3 -Wall -Wextra -o /tmp/q14_switch3 compute/q14/switch_3to2.c
two=$(/tmp/q14_switch compute/H_r10_n50.txt)
three=$(/tmp/q14_switch3 compute/H_r10_n50.txt)
printf '%s\n%s\n' "$two" "$three"
printf '%s\n' "$two" | grep -Fx 'pairs=1225 candidates=1194375 base_holes_min=27 best_holes=9 rank_bad_zero_hole=0'
printf '%s\n' "$three" | grep -Fx 'NO_COVER triples=19600 first_insertions=19129600 second_candidates=937350400 min_base_holes=45 min_after_first=27'
