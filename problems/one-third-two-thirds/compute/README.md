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
