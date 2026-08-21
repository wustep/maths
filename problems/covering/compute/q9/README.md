# q9 — trajectory of the r=10 record, and exact quotient-block replacement

Everything here is new in quest q9 (2026-08-21).  `result/` is read only.
No search from q2/q4 (SA, guided, lifted, k-swap, invariant orbit DFS) is rerun.

## 1. The record, recovered and re-verified

`build_kr51.py` reconstructs the Kaikkonen–Rosendahl 51-column seed from the
hexadecimal listing reprinted as display (4.9) of arXiv:2511.02542v1 (their
Theorem 4.3, citing Kaikkonen–Rosendahl, *New covering codes from an ADS-like
construction*, IEEE Trans. Inform. Theory **49**(7) 1809–1812, 2003, p. 1812).
Output `H_r10_n51_KR.txt`: rank 10, 51 distinct nonzero columns, 1024/1024.
`RESEARCH.md` had recorded this listing as not recovered; it is recovered now.

`trajectory.py` re-derives the documented upper-bound trajectory at r=10 from
the cited formulas and from the explicit matrices in this repository:

| year | n | density | step | how |
|---|---|---|---|---|
| 1992 | 53 | 179/128 ≈ 1.39844 | — | φ(10)=27·2^{t−4}−1: the r=8 value 26 lifted, 2(26+1)−1 |
| 2003 | 51 | 1327/1024 ≈ 1.29590 | −2 | Kaikkonen–Rosendahl, ADS-like, direct at r=10 |
| 2025 | 51 | 1327/1024 | ±0 | still the Table 5.1 entry of arXiv:2511.02542 |
| 2026 | 50 | 319/256 = 1.24609 | −1 | q1: targeted annealing seeded from the 51-set |
| open | 49 | 613/512 ≈ 1.19727 | −1 | this quest |

The volume bound only gives n ≥ 45, so nothing in the counting excludes 49.

## 2. What the trajectory actually says

`profiles.py` computes, for each of the 174251 two-dimensional quotients
q : F_2^10 → F_2^2, the block profile (|A|;|B|,|C|,|D|) of a column set, where
A = S ∩ ker q and B, C, D are the three nonzero fibres.

- **Since 2003 the record has not been a lift.**  φ(10)=53 is exactly the r=8
  record 26 pushed up by the even-r doubling.  The 51-set is not: **no** quotient
  of the 51-set, and **no** quotient of the certified 50-set, has its kernel
  block A covering ker q.  (Both do have quotients with |A| ≥ 25, which is large
  enough by cardinality — they just are not coverings.)  The 2003 gain of −2 and
  the 2026 gain of −1 both left the lift family behind.
- **The record is quotient-flat.**  Profiles concentrate near n/4 in every
  direction: |A| ranges only over 3..27 (51-set) and 3..26 (50-set) across all
  174251 quotients, against a mean of n/4 ≈ 12.5.
- q4 separately exhausted 79 subgroup classes of GL(10,2) at n=49 with zero
  invariant coverings, including every C_7×C_7 class.

Flat, asymmetric, not a lift, and (q4) provably ≥6-swap-deep at the 7-hole
floor.  That is a description of an object no *small* or *symmetric* move will
improve.  The move class left over is a **large exact rearrangement along a
quotient**, which is what §3 does.

## 3. The construction family: block replacement

Fix a quotient with kernel V and coset representatives t00=0, t01, t10,
t11 = t01+t10 (this choice makes the twist vanish).  Pulling every block back
into V, covering radius ≤ 2 is *equivalent* to four conditions inside V:

    (00)  {0} ∪ A ∪ Δ(A) ∪ Δ(B) ∪ Δ(C) ∪ Δ(D) = V        Δ(X) = {x+x' : x ≠ x'}
    (01)  (A ∪ {0}) + B  ∪  C + D = V
    (10)  (A ∪ {0}) + C  ∪  B + D = V
    (11)  (A ∪ {0}) + D  ∪  B + C = V

`verify_blocks.py` checks this equivalence both ways against a direct syndrome
sweep, on the 51-set, the 50-set and both 7-hole residues, matching the exact
hole *sets* and not merely their counts.

Now fix A, B, C and ask for D.  Every condition involving D becomes either a
hitting-set constraint or a pair constraint:

    u ∉ (A⁺+B) ⟹ D ∩ (u+C)  ≠ ∅
    u ∉ (A⁺+C) ⟹ D ∩ (u+B)  ≠ ∅
    u ∉ (B +C) ⟹ D ∩ (u+A⁺) ≠ ∅
    h ∉ {0} ∪ A ∪ Δ(A) ∪ Δ(B) ∪ Δ(C) ⟹ h ∈ Δ(D)

so *"is there **any** block of size ≤ k completing A, B, C to a covering?"* is a
finite exact question.  `block_solve.c` decides it by constraint-directed DFS
with sound sibling exclusion on the hitting branches (where the branches really
are "d ∈ D" and so partition the search), non-excluding branching on the pair
constraints (where the branches overlap and exclusion would be unsound), and
counting prunes on all four families.

Two modes:

- `--shrink`  replace a block of size m by one of size ≤ m−1: n → n−1.
  Run on the certified 50-set this asks directly for a 49; run on the 51-set it
  asks for a 50.
- `--resolve` replace a block of size m by any block of size ≤ m: same n, and on
  a 7-hole residue it asks for a 49-covering.

**This is not a k-swap.**  A block has up to 20 columns and they are all
re-chosen simultaneously and exactly.  q4 proved the 7-hole optima admit no
swap of ≤ 5 columns; the planted controls below reconstruct a 14-column block
from scratch.

## 4. Controls

- **Encoding, positive**: `--resolve` on the certified 50-set returns a valid
  50-set on the first instance, re-verified 1024/1024 by an independent flat
  sweep in the same binary.
- **Reduction, both directions**: `verify_blocks.py`, 160 quotient instances
  over four column sets, exact hole sets agree.
- **Search depth, planted**: `plant.py`-style controls replace an entire block
  of the 50-set by uniformly random elements of V and ask the solver to
  reconstruct one.  7/7 recovered, block sizes 8, 8, 10, 11, 12, 13, 14, each
  re-verified 1024/1024.  A planted needle at depth 14 is found.
- **Independent oracle**: `--selftest k` cross-checks the DFS verdict against
  brute-force enumeration of every candidate block of size ≤ k, scored only by
  the flat covering test, sharing no code with the constraint encoding.

Node cap per instance is reported as `capped`; a capped instance is *unknown*,
not a negative.  Blocks larger than `--maxblock` are reported as `skipped`.
Nothing is silently dropped.

## 5. Sweep results (2026-08-21)

All numbers over all 174251 quotients x 3 non-kernel blocks = 522753 instances.
`capped` = node cap hit, which is unknown and not a negative.

| sweep | cap | maxblock | instances | decided | capped | skipped | result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `--shrink` certified 50-set | 20000 | 18 | 509468 | 220118 | 289350 | 13285 | no 49 |
| `--resolve` best_sa (7 holes) | 20000 | 18 | 514224 | 156264 | 357960 | 8529 | no 49 |
| `--resolve` best_lifted (7 holes) | 20000 | 18 | 514160 | 164382 | 349778 | 8593 | no 49 |
| `--shrink` KR 51-set | 20000 | 18 | 507792 | 159279 | 348513 | 14961 | no 50 |
| `--shrink` certified 50-set | 200000 | 12 | 279034 | 271127 | 7907 | 243719 | no 49 |

The last row is the sharp one: narrow blocks are decided 97.2% of the time.
The KR row is calibration -- the historical 51 -> 50 step is not a single-block
shrink, so this move class does not contain what annealing did in q1.

## 6. Replay

    gcc -O2 -o block_solve block_solve.c
    python3 build_kr51.py H_r10_n51_KR.txt
    python3 trajectory.py
    python3 profiles.py H_r10_n51_KR.txt ../H_r10_n50.txt ../q4/best_sa_config.cols
    python3 verify_blocks.py ../H_r10_n50.txt 40
    ./block_solve --input ../H_r10_n50.txt --shrink --all --maxblock 20 \
                  --nodes 2000000 --shard 0/6
