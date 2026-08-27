# q2 — leftover class censuses past q1

q1 left three named handles unfinished: the n=22 broken-rung ladder
row, three-rail past n=12, and naturally labelled interval orders
past n=8. This folder finishes those as complete class searches
with the same pair counters.

Certified:

- L_{22,1,5,6,9,12,13,17} has δ=1065/3049, e=54882. Every non-sum
  broken-rung ladder at n=7..22 is above 1/3. Through 21 this
  independently matches q1.
- Three-rail exhaustive through n=15. Minimum at 15 is 30572/78185,
  width 3. None below 6/17.
- Naturally labelled interval orders through n=10: 197,409,097 at
  n=10, matching OEIS A367494. Minimum δ=1/3. Non-semiorder minimum
  8/21 through n=9 and 47/130 at n=10.

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
./interval_census 3 10
```
