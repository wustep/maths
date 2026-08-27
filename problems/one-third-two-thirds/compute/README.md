# Compute

Exact linear-extension counts for the 1/3–2/3 attack.

## Replay the records

```
python3 verify_W10.py     # the n=10 width-3 witness, four counters
python3 verify_records.py
```

Two counters (order-ideal DP; remaining-set recursion) and two pair counters
(forward–backward; add the relation). Checks `T`, Saks `M7`, Chen `P(5,5)`,
hook-length rectangles, and small 3-chain boxes.

## Width-3 census

```
gcc -O3 -march=native -o census census.c
./census 9    # replays Olson–Sagan / TGF through 9
./census 10   # first unpublished width-3 order
```

Python twin through n=8: `python3 width3_census.py 8`.

## 3-chain boxes

```
python3 box_dp.py           # atom-pair table
python3 box_allpairs.py     # full δ on the dangerous boxes
python3 plot_thickening.py  # figures/thickening.png
```

`posetlib.py` is the shared Python library. `three_chains.py` is the first
bitmask pass (n≤24).

## q1 (2026-08-27)

Gupta v2 replay and the broken-rung table past order 14:

```
cd q1
./run_all.sh
```

The committed ladder minima through order 21 are `q1/ladder_census.json`.
Re-enumerating orders 19 through 21 from scratch is
`gcc -O3 -o ladder_census ladder_census.c && ./ladder_census 19 21`.

## q2 (2026-08-27)

Leftover class tables: ladders through 22, three-rail through 15,
naturally labelled interval orders through 9.

```
cd q2
./run_all.sh
```

The $n=22$ ladder is $1065/3049$. Re-enumerating from scratch:

```
gcc -O3 -o ladder_census ladder_census.c && ./ladder_census 22 22
gcc -O3 -o three_rail_census three_rail_census.c && ./three_rail_census 8 15
gcc -O3 -o interval_census interval_census.c && ./interval_census 3 9
```
