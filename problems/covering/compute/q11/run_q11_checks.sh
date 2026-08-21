#!/bin/sh
# q11 replay.  Rebuilds every claim in README.md that runs in minutes.
# The r=10 sweeps and the r=9 n=38 residue are annealing runs; they are
# reported as residue and are not re-decided here.
set -e
cd "$(dirname "$0")"
GS=${GS:-/tmp/gs}; GEN=${GEN:-/tmp/gen}; SA=${SA:-/tmp/sa}; VH=${VH:-/tmp/vh}
gcc -O3 -o "$GS" graph_search.c
gcc -O2 -o "$GEN" gen_asets.c
gcc -O3 -o "$SA" sa_graph.c -lm
gcc -O2 -o "$VH" verify_H.c

echo "== independent replay of the emitted matrices =="
for h in H_*.txt; do "$VH" "$h"; done

echo
echo "== line-colouring reformulation agrees with the flat sweep =="
python3 lines.py 2 2 "SOLUTION A=00000006 g=0,0,3"
python3 lines.py 3 3 "SOLUTION A=0000007e g=0,0,0,0,0,0,7"
python3 lines.py 3 4 "SOLUTION A=0000001e g=0,0,0,0,1,2,7,0,2,3,5,6,1,3,0"
python3 lines.py 4 4 "SOLUTION A=00000ffe g=0,0,12,0,12,13,2,0,13,12,2,13,3,3,14"
python3 lines.py 4 5 "SOLUTION A=0000ff00 g=15,14,3,4,11,15,7,12,6,3,15,14,6,4,15,12,2,1,10,12,7,7,14,4,14,9,5,7,13,10,0"
python3 lines.py 5 5 "SOLUTION A=5ffafa5e g=22,7,12,3,10,1,10,14,29,1,5,16,14,16,12,15,9,2,28,30,13,9,26,28,23,4,21,13,28,26,6"

echo
echo "== r=6: n=11 and n=12 exhausted, n=13 found =="
"$GS" -F 3 -M 3 -a 4 --quiet | tail -1
"$GS" -F 3 -M 3 -a 5 --quiet | tail -1
"$GS" -F 3 -M 3 -a 6 --quiet --first | tail -1

echo
echo "== r=8: n=23 and n=24 exhausted over every A =="
"$GS" -F 4 -M 4 -a 8 --quiet --strong | tail -1
"$GS" -F 4 -M 4 -a 9 --quiet --strong | tail -1

echo
echo "== r=8: n=25 exhausted over the GL(4,2)-reduced A list =="
"$GEN" 4 10 > /tmp/a_F4_a10.txt
"$GS" -F 4 -M 4 --alist /tmp/a_F4_a10.txt --quiet --strong | tail -1

echo
echo "== control: the reduction does not change the n=23 verdict =="
"$GEN" 4 8 > /tmp/a_F4_a8.txt
"$GS" -F 4 -M 4 --alist /tmp/a_F4_a8.txt --quiet --strong | tail -1

echo
echo "== r=8: n=26 found (matches the Table 5.1 entry) =="
"$GS" -F 4 -M 4 -a 11 --quiet --strong --first | tail -2

echo
echo "== r=7: n=19 found (matches GDT f(7)=19); n=18 needs a non-saturating A =="
"$GS" -F 3 -M 4 -a 4 --quiet --strong --first --rand 7 --restarts 20 --nodes 200000 | tail -1
"$GS" -F 3 -M 4 -a 3 --quiet | tail -1

echo
echo "== annealer reproduces the family optima at r=6, r=8, r=9 =="
"$SA" -F 3 -M 3 -k 1 --iters 200000 --tries 5  | tail -1
"$SA" -F 4 -M 4 -k 4 --iters 500000 --tries 10 | tail -1
"$SA" -F 4 -M 5 -k 7 --iters 400000 --tries 20 | tail -1
