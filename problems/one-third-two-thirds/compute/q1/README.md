# q1 — Gupta v2 replay and the first unused orders

SuperGrok (2026-08-17) cited Gupta arXiv:2607.23926 as Gold Partition
through 14, not a δ-census. Version 2 (30 Jul 2026) is a full balance
census of every unlabelled 14-element poset. This folder independently
replays the named witnesses and extends the broken-rung ladder table.

## Certified

- Gupta encodings: L_{14,1,9} has δ=254/725, e=725; the 37/106 witness
  has e=318; the width-3 6/17 row is an ordinal sum, e=561.
- Every non-sum broken-rung ladder at n=7..14 matches Gupta Table 1.
- Complete class minima at n=15..21, including exact fractions for
  Peczarski's named L_{15,1,5,6,10}=166/475 and L_{17,1,5,8,12}=1304/3737.
  At n=21 the minimum is 5402/15485.
- All 101 width-≤3 one-point extensions of W10 have δ≥6/17.

No width-3 poset with δ<6/17. The unrestricted conjecture is not claimed.
n=22 of the ladder enumerator is not a row.

## Replay

```
./run_all.sh
```

Re-enumerate n=19..21 from scratch:

```
gcc -O3 -o ladder_census ladder_census.c
./ladder_census 19 21
```
