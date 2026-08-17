# Attack log — Lonely runner for 14 runners

## 2026-08-17 — start

- Folder created. Quest: a certified finite-reduction or modular-sieve
  certificate for 14 runners (LRC(13)), a new excluded speed configuration
  with an independently checkable witness, or a documented residue.
  Isolated floating-point scans are not a dent.
- Fetched Sungkawichai–Trakulthongchai, *Eleven, twelve, and thirteen lonely
  runners*, arXiv:2604.23906 (26 Apr 2026), and Trakulthongchai, *Nine and
  ten lonely runners*, arXiv:2511.22427 / E-JC 33 (2026).
- Notation: LRC(k) is the integer-speed statement for k nonzero relative
  speeds, i.e. k+1 runners. The published computer-assisted frontier is
  LRC(k) for k≤12 (13 runners). The open case is k=13 (14 runners).
- ST26 Theorem 1.3 proves LRC(k) for k∈{10,11,12}. The paper title counts
  runners; the theorems count relative speeds. Section 7 names k=13 as the
  next bottleneck and isolates I(k,p,1) as the obstruction.
- Companion code: `vzsky/13-lonely-runners` (ST26) and
  `t-tanupat/nine-and-ten-lonely-runners` (Tra25). Their `main.cpp` already
  has `LrcVerifier<13>` / `<14>` templates; `results/` stops at k=12.
  `sat/README.md` estimates ~1.5 machine-years for their k=14 find-cover.
  `raw_log_13/` is the k=12 (13-runner) campaign, not 14 runners.
- Dent path: ST26 Proposition 1.4 / §4 shows that (1,…,k) is eventually
  (k,p)-proper when k+1 and p>k(k+1) are odd primes, by a polynomial-method
  identity in the field F_{k+1}. For 14 runners one has k=13 and k+1=14,
  which is composite, so the field argument is unavailable. The *application*
  (Lemma 4.2–4.3 and Proposition 4.4) only needs a finite statement: every
  v∈(Z/14Z)^{13} that is nonzero and has a zero coordinate admits s,r with
  s v + r(1,…,13) ∈ {1,…,12}^{13}. That is independently checkable. The
  transfer r_{13}(1/14 Z) ⊆ r_{13}(1/p Z) is a second finite check, and
  does not use primality of 14.

## 2026-08-17 — finite AP-fiber check

- Implementing an exact (s,r)-obstruction search and the r_k inclusion
  check, with a replay of ST26’s k=10 and k=12 inclusion footnotes as a
  self-test. Isolated floating-point scans are out of scope.

## 2026-08-17 — p-independent statement fails; p-dependent salvage

- ST26 Lemma 4.3’s inclusion `r_k(1/(k+1)Z) ⊆ r_k(1/p Z)` is field-free.
  Replay: k=10 holds at 103,107,109; k=12 at 149,151; k=13 holds at
  173,179,181 and every prime p>182. Threshold k(k+1)=182. Script:
  `compute/rk_inclusion.py --selftest`.
- The p-independent (s,r) covering statement (ST26 Prop 4.1 / Lemma 4.2)
  is **false** for k=13. Independently checked obstruction
  `v=(0,0,0,0,0,0,0,0,0,0,0,1,0)` has no (s,r) in (Z/14Z)^2. Mixed
  obstruction `v=(1,0,0,12,6,10,0,1,0,4,0,10,0)` likewise. Same phenomenon
  already at k=8 (m=9 composite): `v=(0,0,0,0,0,1,0,0)`.
- Classification of unsaved v: 62 zero-sets cover the (s,r)-torus alone.
  These are exactly “all odd speeds zero, at least one even speed zero”
  (2^6−1=63 including the excluded all-zero vector). Cardinality of that
  family in N_13: 14^6−13^6−1=2,702,726. Plus mixed patterns with leftover
  r-columns.
- Those unsaved v are **p-saved** for p=191 (and the listed smaller
  inclusion primes). Exact witnesses, e.g.
    - family: v=(0..0,1,0), (s,j)=(1,16), t=415/2674, lift u reconstructed
      by a_i ≡ (v_i−i)p^{-1} (mod 14), min ||t u_i||·2674 = 205 ≥ 191.
    - mixed: v=(1,0,0,12,6,10,0,1,0,4,0,10,0), (s,j)=(1,12), t=359/2674,
      min d=230≥191.
  Checker: `compute/verify_witness.py`.
- Exhaustive p=191 salvage so far (0 unsaved):
    - family 2,702,726 / 2,702,726
    - leftover r-columns ≤2: 3,464,589 mixed
    - leftover r-columns =3: 5,350,341 mixed
  `leftover_csp` still running on remain 4–12.

## 2026-08-17 — MSS bound replay

- B_k = (binom(k+1,2)^{k-1}/k)^k. ln B_13 = 13(12 ln 91 − ln 13) =
  670.349741. ST26 Table 1: ln B_10=337.634<338, ln B_11=434.485<435,
  ln B_12=545.267<546. Primes in [191,800] give ln prod=591.6 < 670.3,
  so one modular constraint cannot finish LRC(13).
