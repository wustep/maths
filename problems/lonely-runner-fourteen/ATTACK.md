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

## 2026-08-22 — q1 Phase 0: what a solution could look like

Replayed ST26 end to end before planning (`compute/refs/st26.txt`,
extracted from the arXiv PDF). Three facts from that replay reframe the
problem, and one of them contradicts how this folder had been reading it.

**The F_{k+1} identity is not the obstruction.** Proposition 4.1 exists
only to dodge the `c = k+1` lift when `k+1` is *prime*. §5.2 gives the
k=11 lifting diagram — `k+1 = 12` is composite and ST26 simply lift
through its prime factors, `S1 ×2 ×2 ×2 ×2 ×3 ×3 → S7`, with no
polynomial method anywhere. So compositeness of 14 is not by itself a
wall; it is a change of route. For k=13, `k+1 = 14 = 2·7`, and Remark
3.2 forces `14 | l`, so the cheap `×2` ladder can never finish alone —
a `×7` lift costs `7^13 ≈ 9.7e10` per surviving tuple. That is the real
cost, and it is what an analogue of Prop 4.4 would buy back.

**What the p=191 salvage actually is.** Reading Prop 4.4's proof, the
only step that uses primality of `k+1` is Lemma 4.2 (via Prop 4.1).
Every other step is field-free: `u' = 0` lands in the gcd condition,
`u'` with no zero coordinate takes `s=1, r=0`. So the salvage in this
folder is exactly a p-specific replacement for Lemma 4.3 at k=13, and
finishing it proves a named statement of the same shape as Prop 1.4:

> **T1(p).** For every `v ∈ N_13` there are `s ∈ Z_14` and `j ∈ Z` with
> `s v + r_13(j/p) ∈ {1,…,12}^13 (mod 14)`.
>
> T1(p) ⇒ every `u ∈ π^{-1}_{14p→p}(1,…,13)` is `(13,p,14)`-proper ⇒
> every `u ∈ Z^13_{>0}` with `gcd(u)=1` and `u_i ≡ i (mod p)` has the LR
> property.

**§7 names the actual bottleneck, and it is not this.** ST26's closing
section says the primary obstruction at k=13 is computing `I(13,p,1)`.
Under their §5.1 reduction that is `~ p^13 / (2^13 · 12!)` tuples; at
p=191 that is about `1.1e17`. So T1(191) is a component, not LRC(13),
and this folder must not claim otherwise.

### The possibility tree

**A. p-uniform replacement for Prop 4.1 at k+1 = 14.** *Object:* a proof
of T1(p) for every prime `p > 182`, i.e. Prop 1.4 with the odd-prime
hypothesis on `k+1` dropped. *Why it wins:* it is the exact statement
ST26 could not reach for composite `k+1`, and it removes the `×7` lift
from any future k=13 campaign. *First check:* the p-independent version
is already known false here, so a uniform proof must use `p`. The 62
bad zero-sets are "all odd coordinates zero, at least one even
coordinate zero"; for those, the odd coordinates need only a `j` with
`‖i j/p‖ ≥ 1/14` for `i ∈ {1,3,…,13}` — the LR property for seven
speeds at gap 1/14, which is far weaker than LRC(7). If that `j` always
exists and the even coordinates can be fixed by choice of `s`, A closes
by hand. *Not doing:* re-deriving Prop 4.1 over `Z_14`; the ring has
zero divisors and the leading-coefficient step dies.

**B. Enough primes to clear B_13.** *Object:* `J(13,p) = ∅` for a set of
primes with `Σ ln p ≥ ln B_13 = 670.35`. *Why it wins:* Prop 2.7 then
gives LRC(13) outright. *First check:* `θ(x)` arithmetic — the earlier
note that primes in [191,800] give 591.6 is right but the conclusion
drawn from it was too strong; the requirement is not one prime but a
long enough list, and the list needs to run to roughly p ≈ 880. *Kill:*
each `J(13,p) = ∅` needs `I(13,p,1)`, which is the 1.1e17 wall of §7. B
is dead at this budget, not by arithmetic but by §7. Record and move on.

**C. Finish the p=191 salvage exhaustively.** *Object:* T1(191),
certified. *Why it wins:* it is A restricted to one prime, and it is the
one shape already half-built here. *First check:* the existing
`leftover_csp` enumerates *vectors* (millions per pattern) and was left
unfinished on remain 4–12. That is the wrong shape of search — see the
reformulation below, which decides T1(p) without enumerating any vector.
*Not doing:* resuming `leftover_csp` on remain 4–12.

**D. New excluded infinite family.** *Object:* a witness schema, one `t`
covering an unbounded set of speed tuples. *Why it wins:* it is a bound
statement independent of the lifting machinery. *First check:* T1(p) is
already of this shape — it excludes the whole residue class
`u ≡ (1,…,13) (mod p)`, infinitely many tuples, from being a
counterexample. So D is subsumed by A/C rather than separate. Keep as
the framing for writeup, not as separate work.

**E. Turn the missing `I(13,p,1)` cases into a finite SAT/CSP.** *Object:*
a replayable UNSAT log. *First check:* count the instance. `1.1e17`
representatives is beyond SAT by many orders. Dead at this budget.

**F. Outside ST26 entirely** (Bohr sets, view obstruction, Wills–Cusick).
*First check:* name the certificate. None of these currently produce a
finite object a stranger can replay at k=13. Dropped, not disproved.

### The reformulation that makes C (and the check for A) cheap

T1(p) is a *covering* question with 13 variables, not an enumeration over
`|N_13| ≈ 7.9e14` vectors. Write `B^{(j)}_i = ⌊14·{ij/p}⌋`. Call the pair
`(s,j) ∈ Z_14 × Z_p` a *constraint*, and say coordinate `i` taking value
`a` *hits* it when `s a + B^{(j)}_i ≡ 0` or `13 (mod 14)`. Then

> `v` is **unsaved** ⟺ `⋃_i hit(i, v_i)` is *all* `14p` constraints.

So T1(p) holds iff that covering is infeasible over `v ∈ N_13`. That is
13 variables of 14 values against `14p` constraints — a set-cover
feasibility question, decidable by DFS on "cover the lowest uncovered
constraint", with no vector enumeration at all. Two free reductions:
every `s = 0` constraint is hit by every `v` (it does not involve `a`),
so all `p` of them drop; and `(s,j)` and `(-s, p-j)` induce the same
hitting set, so the rest halve.

Ranking, cheapest real win first: **C** (reformulated) → **A** (its first
check is the same code at many `p`) → **D** (writeup of A) → B, E, F
recorded as dead or dropped.

### First check, run before ranking was written

Prototype of the reformulation (`/tmp/probe3.py`, superseded by
`compute/q1/`) reproduces both known SAT facts instantly, which is the
self-test this reformulation had to pass:

- k=8, m=9: 8 nodes, witness `v = (0,0,0,0,0,*,0,0)` — the obstruction
  already recorded in this folder on 2026-08-17.
- k=13, m=14: 9 nodes, witness "odd coordinates zero, even coordinates
  free" — exactly the 62 zero-sets, recovered from scratch.

The UNSAT direction (k=10 and k=12 p-independent, both *theorems* by
Prop 4.1) did not close in Python at 3e6 nodes. Those two are the
correctness gate for the C solver: a search that cannot re-prove Prop
4.1 at k=10 and k=12 is not trusted at k=13.
