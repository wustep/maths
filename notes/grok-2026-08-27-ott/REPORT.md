# 1/3–2/3 posets, 2026-08-27

Grok 4.6 on SuperGrok's `one-third-two-thirds` folder.

## q1

The 17 August note cited Gupta arXiv:2607.23926 as Gold Partition
through 14, not a δ-census. Version 2 is a full balance census.
Independently replayed the named witnesses, then extended
Peczarski's broken-rung table.

Certified:

- L_{14,1,9} has δ=254/725, e=725.
- Gupta's width-3 6/17 tail row is an ordinal sum (W10 padded).
- Non-sum broken-rung minima through n=21, matching Gupta through 14.
  At n=21: 5402/15485. All still above 1/3.
- 101 width-≤3 one-point extensions of W10, none below 6/17.

Replay: `cd problems/one-third-two-thirds/compute/q1 && ./run_all.sh`.

## q2

The leftover handles after q1: n=22 ladders, three-rail past 12,
interval orders past 8. Stamp-based C (no 2^n memset) finishes them.

Certified:

- L_{22,1,5,6,9,12,13,17} has δ=1065/3049, e=54882. 524288 non-sum
  ladders, none below 1/3. The n=22 value is larger than n=21.
- Three-rail exhaustive through n=15. At 15: 30572/78185, width 3,
  2097152 non-sums, none below 6/17.
- Naturally labelled interval orders through n=9: 9062503 posets,
  matching OEIS A367494. Minimum 1/3. Non-semiorder minimum 8/21.

No δ < 1/3. No width-3 example below 6/17. Conjecture still open.

Replay: `cd problems/one-third-two-thirds/compute/q2 && ./run_all.sh`.
