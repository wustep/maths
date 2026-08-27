# q2 — leftover class censuses past q1

q1 left three named handles unfinished: the n=22 broken-rung ladder
row, three-rail past n=12, and naturally labelled interval orders
past n=8. This folder finishes those as complete class searches
with the same pair counters.

No certified δ < 1/3. No certified width-3 example below 6/17.

## Replay

```
./run_all.sh
```

Re-enumerate from scratch (not required for the certificate check):

```
gcc -O3 -o ladder_census ladder_census.c
./ladder_census 22 22

gcc -O3 -o three_rail_census three_rail_census.c
./three_rail_census 8 15

gcc -O3 -o interval_census interval_census.c
./interval_census 3 9
```
