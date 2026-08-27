# Walkthrough — the second term for Sidon subsets of [N]

Discovery notes, not a paper. Empty would mean not done.

## 0. What was actually missing

The missing degree of freedom was not a new Sidon set and not a new
energy identity. Hou–Zhao’s Lemma 2.1 already gives

    F(N) ≤ √N + √(ab) N^{1/4} + O(1)

for any covering-feasible (λ, p, w) on a boundary of length L kernel
widths. Their certificate fixes L=4. L is free. The same kernels with
w padded by ones are feasible for every L'>4, so the L' quadratic
program can only decrease b, and a is a function of (λ,p) alone.

The degree of freedom was **the boundary length on an already-optimal
kernel mix**.

## 1. Named false starts

**Finite F(N) tables.** Optimal Golomb rulers beat Singer’s second term
at small k (27 marks, length 553 is already √N + ~0.7 N^{1/4}). That is
a finite picture. It does not give an infinite family with
√N+ω(1). Rejected by the house rule.

**Singer plus extras.** Implemented the F_{p^3} discrete-log Singer set
for every prime p≤31. Size p+1 in [p²+p+1], second term climbing toward
½, and **zero** integers in the interval can be added while staying
Sidon. Obstruction: the unfolding already realises every difference in
range.

**Bose–Chowla plus extras.** Field implementation for primes 3≤p≤79.
Sidon of size p in [p²-1]. Greedy extras inside the native interval:
1,1, then 0 for all p≥7. One extra point far outside makes N grow faster
than |A|, so the second term vs √N gets worse. Bounded extras are still
O(1).

**1-kernel re-optimisation.** Symmetric cosine-mode search over (m,L)
reproduces Hou–Zhao’s R=1 value ~0.94615 and does not go below ~0.946.
The drop from 0.946 to 0.943 is a multi-kernel effect, not a grid
effect.

**m-refinement without changing shape.** Splitting each of the eight
histograms into 2, 3, or 4 equal sub-bins leaves a invariant and does
not move b. The published kernels are already at the continuous limit
of their shape class.

**CHO two-window replay.** Their hand parameters give b_∞ ≤ 1.99058
(C ≤ 0.99529). Real, weaker than 0.9435, not a new bound.

**Claiming 0.98183 as the record.** PROBLEM.md and Erdős #30 (edited
April 2026) still say 0.98183. Hou–Zhao is on arXiv 5 July 2026. After
the fetch, the record to beat is 0.9435 / γ0 = 0.943492590713545.

## 2. The useful failure

Singer extras = 0 is the useful failure on the lower side: you cannot
nibble a growing second term by adding points to a perfect difference
set inside its own interval. Green’s unwrap-with-a-gap produces another
O(1) unless the gap is ω(√q), which is Problem 32.

On the upper side, L-lifts **saturate**. L=4→5 saves ~8×10^{-8}; L=5→6
saves ~1×10^{-9}; L≥6 is flat to 12 digits. More boundary is not an
endless well. The published mix is already almost fully relaxed in L.

## 3. The click

Re-solve the published eight-kernel mix at L=6. a is the same rational
as Hou–Zhao Claim 4.1. b drops. The floating γ is 0.94349250848, below
their exact γ0 = 0.943492590713545. Round the new weights, add a common
η so every covering inequality holds over Q, and the exact γ stays
below γ0.

That is the whole new bound: **same lemma, same kernels, longer boundary,
exact arithmetic.**

## 4. The argument, in the order it was found

1. Fetch Green #31 and Erdős #30. Still open. Published C = 0.98183 on
   those pages.
2. Fetch CHO25. Then Hou–Zhao arXiv:2607.01169v2: C < 0.9435 with an
   eight-kernel rational certificate.
3. Independently rebuild their certificate from the integer tables.
   Hash matches Claim 4.1. Covering, a, b, and √(ab)<0.9435 all pass.
   (`compute/verify_houzhao.py`)
4. Re-implement the fixed-kernel QP. Table 1 replays.
5. Notice Lemma 2.1 does not prefer L=4. Run the same (λ,p) at L=4,…,12.
6. Certify L=6: `compute/certs/hz_kernels_L6.json`.
7. Two verifiers that do not import each other both accept
   √(ab) < 0.94349251 < γ0.

Hou–Zhao Lemma 2.1 (scalar form, L free): kernels p^{(r)} are symmetric
probabilities on m bins; weights w^{(r)} live on n=Lm bins and equal 1
after that; covering

    ∑_r λ_r ∑_i p_i^{(r)} W_{q+i}^{(r)} ≥ 1    (q = 0,…,n)

with W_j = w_j (j<n) and 1 (j≥n);

    a = m ∑_r λ_r ‖p^{(r)}‖²
    b = 1 + 2( (1/m) ∑_r λ_r ‖w^{(r)}‖² − L )

and if b>0 then F(N) ≤ √N + √(ab) N^{1/4} + O(1). The O(1) may depend
on the finite certificate (hence on L) but not on N. For L=6 one needs
N ≥ 12H with H ≍ N^{3/4}, which holds for large N.

## 5. Computer search

- `figures/published_C.png` — published C against year.
- `figures/table1_replay.png` — independent QP vs R.
- `figures/L_lift.png` — γ against L for the published mix; the L=4
  certificate sits above the L≥6 plateau.
- `compute/search_results.jsonl` — every floating experiment.
- `compute/bose_greedy.json`, `compute/singer_greedy.json` — extras = 0
  (Singer always; Bose for p≥7).
- `compute/certs/hz_kernels_L6.json` — the exact L=6 certificate.
- grid1 aborted on an infeasible covering row from a degenerate seed.
- Multi-scale (different m_r) and coordinate descent on the eight
  histograms were still at the L=6 plateau when this was written.

Replay:

```bash
python3 compute/verify_houzhao.py
python3 compute/verify_certificate.py compute/certs/hz_kernels_L6.json --beat 0.94349259
python3 compute/verify_beat_hz.py
```

## 6. What is proved vs still open

**Proved here.** For all sufficiently large N,

    F(N) ≤ N^{1/2} + 0.94349251 N^{1/4} + O(1),

with an explicit rational certificate whose a is Hou–Zhao’s a and whose
√(ab) is 8.22×10^{-8} below their γ0. Independently, Hou–Zhao’s own
L=4 certificate is valid, so C < 0.9435 was already in the literature.

**Still open (2026-08-17).** Erdős–Turán (do not claim it). A lower bound
F(N) ≥ √N+ω(1) for infinitely many N. Any constant at the 0.9434 level
or a new method. The $1000 form h(N)=N^{1/2}+O_ε(N^ε).

The L=6 lift is a strict numerical improvement of a published
certificate. It is not a new proof idea. If a later reader wants only
improvements that change the four-decimal statement 0.9435, the 17
August search is incomplete.

## 7. 2026-08-27: the six-mode cage

Hou–Zhao’s Table 1, rows R=4 through R=8, add one *six-mode* cosine
profile at a time. The 17 August coordinate descent and Powell
searches stayed inside that cage, or never returned. The 27 August
search used L-BFGS on the eight kernels as free symmetric histograms
(16 half-bin logits, no mode cutoff) at L=6.

The floating γ dropped by 2.5×10^{-4}, from 0.94349251 to
0.94324253. Adding R=9..12 twelve-mode kernels on top of the
*published* mix only reached 0.94326. The degree of freedom was the
shape class of the existing eight kernels, not a ninth kernel and
not a longer boundary.

Rounded, η-shifted, and checked over Q: √(ab) = 0.9432425309706136,
so F(N) ≤ √N + 0.94325 N^{1/4} + O(1). That does change the
four-decimal statement 0.9435. Same lemma. New histograms.

**Still open.** Erdős–Turán. A lower bound F(N) ≥ √N+ω(1) infinitely
often. The $1000 form. A constant at the 0.9431 level, or a method
that is not Lemma 2.1.
