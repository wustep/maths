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

## 2026-08-22 — q1 Phase 1: the gcd branch was missing; T1(191) is false

Built `compute/q1/cover.c` (the set-cover decision from Phase 0) and
`compute/q1/check_unsaved.py` (independent single-vector replay, written
from the paper, not from the C). Gate first, then results.

**Correctness gate.** `check_unsaved.py --selftest` brute-forces *all* of
`N_k` and re-proves ST26 Proposition 4.1 at k=4 and k=6, and reproduces
the k=8 (m=9 composite) failure. `cover` agrees on all three and on k=13
p-independent. A search that cannot re-prove Prop 4.1 is not trusted.

**Dent-shaped finding — the recorded target statement is false.** Run
`cover --k 13 --p 191` against `N_13` and it returns SAT in 27 s:

    v = (2,4,6,8,10,12,0,2,4,6,8,10,12) = 2·(1,…,13) mod 14

`v ∈ N_13` (nonzero, `v_7 = 0`), and exhausting all 2674 pairs `(s,j)`
finds no witness. Independently confirmed:

    python3 check_unsaved.py --k 13 --p 191 \
        --v 2,4,6,8,10,12,0,2,4,6,8,10,12     ->  SAVED : False

So **T1(191) as stated in Phase 0 is false**, and the 2026-08-17 campaign
— which was searching for exactly that, and had reported "0 unsaved" over
the part of the space it had finished — could not have succeeded. The
vector sits in the `remain ≥ 5` range that was still running. This is a
residue turned into a decision, not a completed search.

**Why it does not matter, and what the correct statement is.** Re-reading
Prop 4.4's case split: ST26 dispose of `u' = 0` through the *gcd
condition* of Definition 2.1, `gcd(l, u_1,…,û_i,…,u_k) > 1` with
`l = k+1`. When `k+1` is prime that branch means "at most one nonzero
coordinate" and is nearly empty, so it is easy to read past. When
`k+1 = 14` it is a wide branch: some prime `q ∈ {2,7}` divides all but at
most one coordinate. And `2·(1,…,13)` is entirely even. It is unsaved and
*harmless*. The folder had been transcribing ST26 to composite `k+1`
with this term dropped. Restored, the statement to prove is

> **T2(p).** For every `v ∈ Z_14^13` with (i) at least one zero
> coordinate, (ii) at least two odd coordinates, (iii) at least two
> coordinates not divisible by 7, there are `s ∈ Z_14`, `j ∈ Z` with
> `s v + r_13(j/p) ∈ {1,…,12}^13 (mod 14)`.
>
> (ii)+(iii) is exactly "not gcd-proper": for prime `q | m`,
> "some `i` has `q | v_j` for all `j ≠ i`" ⟺ `#{j : q ∤ v_j} ≤ 1`.
> T2(p) ⇒ every `u ∈ Z^13_{>0}` with `gcd(u) = 1` and `u_i ≡ i (mod p)`
> has the LR property — the k=13 analogue of ST26 Proposition 1.4.

**Second correction: the 2026-08-17 obstruction was harmless.** The
vector cited that day to declare the p-independent statement false,
`v = (0,…,0,1,0)`, is gcd-proper (`2` divides all but one coordinate), as
is the k=8 example `(0,0,0,0,0,1,0,0)`. Neither is an obstruction to
Prop 4.4. The conclusion survives, but on the strength of the *mixed*
example `v = (1,0,0,12,6,10,0,1,0,4,0,10,0)`, which is confirmed not
gcd-proper and genuinely unsaved. `cover --k 13` (p-independent, gcd
branch on) returns SAT in 29 nodes with another genuine one,

    v = (1,1,1,0,1,1,1,5,1,6,1,2,1)      single zero coordinate, 10 odd

so **T2(13,14) is false** and p-dependence is genuinely required. That
part of the 2026-08-17 record is now on a correct witness.

**Status.** `cover --k 13 --p 191` under T2 is running; the cheap SAT
answer is gone, which is the outcome one wants. Not yet decided, so:
residue, and no bound is claimed.

## 2026-08-22 — q1: dent. T2(13,191) holds

`./cover --k 13 --p 191` returns UNSAT in 102,905,279 nodes / 240.7 s.
Certificate and the full verification chain: `compute/q1/certs/T2_p191.txt`.

> **Theorem.** Every `(u_1,…,u_13) ∈ Z^13_{>0}` with `gcd(u_1,…,u_13) = 1`
> and `u_i ≡ i (mod 191)` has the lonely runner property: there is `t`
> with `‖t u_i‖ ≥ 1/14` for all `i`.
>
> Equivalently `(1,2,…,13) ∉ J(13,191)` — the tight tuple that ST26 §5.2
> report as the sole survivor of the `×2` lifting ladder is eliminated at
> p=191 with no `×7` and no `×14` lift.

ST26 Proposition 1.4 proves the analogue only when `k+1` *and* `p` are
both odd primes. At k=13, `k+1 = 14` is composite, so their statement
does not apply and this one is not in the published record. Write the
comparison honestly: this is not a bound on `k`. LRC(13) is still open,
and the thing that keeps it open — computing `I(13,p,1)`, about `1.1e17`
tuples at p=191 under their §5.1 reduction — is untouched here.

Chain from T2(191) to the theorem, following Prop 4.4 with the case split
repaired for composite `k+1`. Let `u_i = a_i p + i`, `a_i ∈ Z_14`, and
`u' = u mod 14`, which ranges over all of `Z_14^13`.

1. `u'` gcd-proper — some `q ∈ {2,7}` divides all but at most one
   coordinate. Then `gcd(14, u_1,…,û_i,…,u_13) ≥ q > 1`, so `u` is
   `(13,p,14)`-proper by Definition 2.1's gcd condition. *(For prime
   `k+1` this branch is just `u' = 0`; at 14 it is wide, and it is the
   branch the folder had been dropping.)*
2. `u'` with no zero coordinate — take `t = 1/14`; then
   `{t u_i} = u'_i/14` with `u'_i ≠ 0`, so `‖t u_i‖ ≥ 1/14`.
3. otherwise — `u'` has a zero coordinate and is not gcd-proper, which is
   exactly T2's hypothesis. Take its `s, j` and `t = s/14 + j/191`; then
   `{t u_i} ∈ [C_i/14, (C_i+1)/14)` with `C_i ∈ {1,…,12}`, so again
   `‖t u_i‖ ≥ 1/14`. And `t ∈ (1/(14·191))Z`.

Then Prop 1.4's own last step: if the fiber element is proper by the gcd
condition, `gcd(u) = 1` plus the pre-jump technique gives the LR property;
otherwise the witness time is already there.

**Verification.** Four independent legs, and one that failed — recorded
because it did fail:

- the *reformulation* is checked against brute force at composite `m`.
  `check_unsaved.py` enumerates all of `Z_m^k` from the paper's
  definitions: k=5 (m=6) has 64 p-independent obstructions and **0** at
  p=31; k=7 (m=8) has 2596 and **0** at p=59. `cover` matches all four.
  Its `--selftest` also re-proves ST26 Prop 4.1 outright at k=4 and k=6.
- split and unsplit runs agree; unsplit is bit-reproducible at 102,905,279
  nodes.
- `spotcheck.c`, sharing no code with either search, finds **0**
  unsaved-and-needed vectors at p=191 across 23.2 million tuples needing a
  witness (sparse, arithmetic-progression plus 2-coordinate perturbations,
  Hamming balls about two known obstructions, and 20 M random). Positive
  control: the same sweep finds 24,300 obstructions at the p-independent
  grid, so it is not blind.
- **failed leg:** `cover_bdd.c`, the forward-sweep second decision
  procedure, agrees on all five small composite cases but state-explodes
  (>40 M states at depth 7) before reaching k=13. It does *not*
  independently confirm p=191. Adding subset dominance is the fix and it
  is not done. So the p=191 verdict rests on one exact search plus the
  three legs above, not on two exact searches.

**Sweep.** `T2(13,p)` fails at p=17,19 and holds at 191, so p is doing
real work and there is a threshold to locate. Sweeps over
p ∈ [17,181] and p ∈ [193,293] are running; results as they land.

## 2026-08-22 — q1: sweep, and shrinking the trusted base

**Sweep.** `T2(13,p)` decided for one prime is a fact about 191; decided
for a run of primes it starts to look like the composite-`k+1` analogue
of Prop 4.1 that shape A asked for.

| p | T2(13,p) |
|---|---|
| 17, 19, 23, 29, 31, 37, 41 | fails |
| 191, 193, 197, 199, 211, 223 | **holds** |

So `p` is doing real work — the statement is false for small `p` and true
for every large `p` tried so far. The threshold is somewhere in (41, 191);
p=43 did not resolve inside 40 minutes and was stopped, which is itself a
hint that it is near the boundary. Note this needs no `p > k(k+1) = 182`
hypothesis: `T2` is checked directly on the `j/p` grid, so ST26's Lemma
4.3 route through `r_13(1/14 Z) ⊆ r_13(1/p Z)` is bypassed, not used.
The obstructions at the failing primes are heavily zero-supported, e.g.
p=31 gives `(0,0,0,1,1,1,0,0,1,0,0,0,0)`, but no clean schema yet.

**Trusted base.** The only non-obvious step in `cover.c` is the counting
bound: with `X` the uncovered set, each free coordinate `i` contributes at
most `max_a |hit(i,a) ∩ X|`, so if the sum over free coordinates is below
`|X|` no completion can cover. Sound by inspection, but it is the one
place a wrong answer could hide, so it now has a `--nobound` switch.
Bound on and bound off agree on every decided case, including the two
composite-`m` UNSAT cases that brute force independently confirms:

    k=5 p=31  UNSAT / UNSAT      k=7 p=59  UNSAT / UNSAT
    k=5 p=6   SAT   / SAT        k=7 p=8   SAT   / SAT      k=13 p=14 SAT / SAT

`./cover --k 13 --p 191 --nobound` is running to remove the bound from
the trusted base at the headline case as well; result when it lands.

**Replay checked from a clean clone.** `git clone`, three `gcc` lines
with no `-march=native`, `check_unsaved.py --selftest`, and the four
gate runs all pass. `compute/q1/README.md` lists them.

## 2026-08-22 — q1 close of session

**Sweep, final state.** `T2(13,p)` holds at

    191, 193, 197, 199, 211, 223, 227, 229, 233, 239

and fails at 17, 19, 23, 29, 31, 37, 41. Ten consecutive primes from 191
up, none failing. Each is an independent instance of the theorem: for each
such `p`, every coprime `(u_1,…,u_13)` with `u_i ≡ i (mod p)` has the LR
property. The sweep is still running past 239.

**`--nobound` at p=191: unresolved.** Left running ~35 minutes without
terminating and was not waited out. Expected — 80 M of the 103 M nodes in
the bounded run were bound cuts, and each cut node's subtree comes back.
So the counting bound is *not* removed from the trusted base at p=191; it
is removed at k=5 p=31 and k=7 p=59, where brute force independently
confirms the same answers. Write it as it is: bounded and unbounded search
agree everywhere both finish, and p=191 is only in the bounded column.

**Where q1 stands against the Phase 0 tree.**

- A (p-uniform replacement for Prop 4.1 at composite `k+1`) — not proved,
  but its first check came back positive and then some: the statement is
  true at every large prime tried, at k=13 and at composite `m = 6, 8`.
  A proof for all `p > p_0` is the open end. Locating the threshold in
  (41, 191) is the next cheap step, then look for a schema.
- B (enough primes to clear `B_13`) — dead, on ST26 §7, not on arithmetic.
- C (finish the p=191 salvage) — done, but only after correcting what it
  was aimed at. The original target was false.
- D (new excluded family) — delivered; it is A/C restricted to one prime,
  ten times over.
- E (SAT on the missing `I(13,p,1)`) — dead at `1.1e17` representatives.
- F (outside ST26) — dropped, no certificate named.

**Not claimed.** LRC(13). The bottleneck ST26 name is untouched.

## 2026-08-22 — q2: the failing end has an exact schema

Two ends of the gap `(41, 191)`, attacked with tools that do not decide one
prime at a time. Code in `compute/q2/`.

**Housekeeping first.** `compute/q1/t2_sweep.log` as committed runs past where
the close-of-session note stopped reading it. `T2(13,p)` also holds at

    241, 251, 257, 263, 269, 271, 277, 281, 283, 293

so the sweep is twenty consecutive primes from 191 to 293, not ten. Same
binary, same certificate chain; nothing new was run for those, they were
already in the log.

**The failing end: a family that needs no search.** Every witness the alphabet
prober returns has one shape — two coordinates equal to 1, the rest 0. That
shape has a closed form. Take `v = e_a + e_b`, `Z = {1,…,13} \ {a,b}`. At a
given `j`, a coordinate in `Z` (value 0) hits `(s,j)` iff `B^{(j)}_i ∈ {0,13}`,
which does not depend on `s` at all; a coordinate in `T = {a,b}` (value 1) hits
only the two values `s = -B_i` and `-B_i-1`. So if some `j` has no `i ∈ Z` with
`B^{(j)}_i ∈ {0,13}`, then at that `j` the two coordinates of `T` reach at most
4 of the 13 nonzero `s`, and `v` is saved. Hence

> **Lemma.** For `k ≥ 5`, `v = e_a + e_b` is unsaved at `p` ⟺ no `j ∈ Z_p` has
> `‖i j/p‖ ≥ 1/14` for every `i ∈ Z`. So `T2(13,p)` FAILS whenever some pair of
> speeds can be deleted and still leave the remaining eleven with no witness
> time *on the grid* `(1/p)Z`.

Two deletions make the tight tuple slack, so `G(Z) = {t : ‖i t‖ ≥ 1/14 ∀ i∈Z}`
has positive length — it is a union of closed intervals with endpoints over
`D = 14·lcm(1..13) = 5045040`. `schema.py` computes it exactly and decides the
whole family for every `p` at once, no search:

| | |
|---|---|
| `T2(13,p)` fails at | 2..52, 55..62, 64,65,66, 70..76, 78, 82, 85,86,87, 89,90, 95, 99, 105, **116** |
| primes among these | …, 41, **43, 47, 59, 61, 71, 73, 89** |
| shortest longest-interval | pair `{6,10}`, `31680/5045040 = 1/159.25` |

so this family produces no failure at any `p ≥ 160`. The last failing prime in
the record moves from 41 to **89**, and the last failing integer to **116**.

Independently confirmed. `compute/q2/probe.c` exhausts `A^13` for
`A = {0,1,7}` and finds the same witnesses at 43, 47, 59, 61, 71, 73, 89 and
nothing at 53, 67, 79, 83 — exactly the schema's pattern — and
`q1/check_unsaved.py`, written from the paper and sharing no code with either,
returns `genuine obstruction` for the p=43, p=61 and p=89 witnesses. The prober
also returns nothing at every prime from 97 to 181, but that is one-sided and
proves nothing: `NONE in this alphabet` is not `T2 holds`.

**The family is not the whole story, and k=5 says so.** Brute force over all of
`Z_6^5` gives the exact failure set for `k=5`: `p = 6..14, 19, 21, 22, 24, 26,
27, 39, 42, 57`. The pair family accounts only for `p ≤ 13`. Everything above
comes from a single richer obstruction, `v = (1,5,0,1,5) = (1,-1,0,1,-1)`, the
balanced lift of `i mod 3` with `3 = m/2`. Its `m=14` analogue,
`v_i = ` balanced lift of `i mod 7`, is **saved at every prime tried from 17 to
293**, so it does not transfer — but the lesson does. 89 and 116 are lower
bounds on where `T2(13,·)` stops failing, not the threshold.

Also worth recording: the pass/fail set is not an interval. At `k=5` the prime
19 fails while 17 holds. So "the first `p` that holds" is not a well-posed
quantity, and the sweep column should not be read as a threshold.

**The holding end: one search for every large `p`.** `compute/q2/cells.c`.
`B_i(t) = ⌊14·frac(i t)⌋` jumps only on `(1/(14 i))Z`, so the 812 breakpoints
`⋃_i (1/(14 i))Z` cut the circle into half-open cells on which the entire
hitting structure is constant. Every half-open interval of length `1/p`
contains a point of `(1/p)Z`. So for `p ≥ q`, an unsaved `v` must hit, for
every `s` and every cell start `c_r`, at least one of the cells meeting
`[c_r, c_r + 1/q)`. That is a set-cover feasibility question again — same DFS,
same counting bound, same gcd branch, only the constraints change — and

> no eligible `v` covers all of it ⟹ `T2(13,p)` holds for **every** integer
> `p ≥ q`.

The constraints strengthen as `q` grows, so one run certifies an infinite tail,
and the lemma above forces `q ≥ 117`. Calibration at small `k`, where brute
force decides everything: `k=5` certifies `p ≥ 90` against a true last failure
of 57; `k=7` certifies `p ≥ 84`. The first version of the reduction, keeping
only cells longer than `1/q` and no window union, gave 91 and 121 — the window
union is what makes it sharp, and it is kept as `--strictcell` for comparison.

Gates. `cells --p P` reproduces `q1/cover.c` on all five gate cases with
identical witnesses. `check_cells.py --selftest` checks the reduction itself
from the definitions: `B` constant on every half-open cell at `k=5,7,13`; every
window meets `(1/p)Z` inside its own cell set, over 43 values of `p` at each of
`q = 90, 84, 200, 300`; and brute force over `Z_6^5` for `p ∈ 6..399` never
contradicts the certified `k=5` threshold.

`cells --k 13 --q 200` and `--q 300` are running. Status: **residue** until one
returns. No bound is claimed from q2 yet.

**`--nobound` at p=191.** Still running, 11 h 45 m at the time of writing, no
output past the header. Unchanged from the close-of-session note: bounded and
unbounded agree everywhere both finish, and p=191 is only in the bounded
column.

## 2026-08-22 — q2: calibration, and the residue family is empty at k=13

**Calibration.** Run both ends at every composite `m` small enough to decide
outright, `cells --k K --q q` upward for the certificate and `cover --k K --p p`
across `p ∈ [6,400]` for the truth:

| k | m | certified `T2(k,p)` for all `p ≥` | largest `p ≤ 400` that actually fails | loss |
|---|---|---|---|---|
| 5 | 6 | 90 | 57 | 1.58× |
| 7 | 8 | 84 | 44 | 1.91× |
| 9 | 10 | 180 | 125 | 1.44× |
| 13 | 14 | *running* | ≥ 116 (schema) | — |

So the certificate is sound and roughly `1.5×` loose everywhere it can be
checked. Note `k=9` fails as far as `p=125`, past the `k=13` schema bound of
116 — a warning that 116 is unlikely to be the end at `k=13` either.

**What the last failures look like.** Take the obstruction `cover` returns at
the largest failing `p` for each `k`:

    k=5  p=57   v = (5,1,0,5,1)             v_i = -i mod 3
    k=7  p=44   v = (3,2,5,0,3,2,5)         v_i = -i mod 4
    k=9  p=125  v = (2,4,1,3,0,7,4,1,8)     v_i = 2i mod 5

One family, and it is `v_i ≡ λ i (mod m/2)` with the lift to `Z_m` free — not
`v_i ≡ λ i (mod m)`, which is the thing ST26's `×2` ladder already handles.
`probe --fam Q L` was added for it: coordinate `i` gets the alphabet
`{x ∈ Z_m : x ≡ L·i mod Q}`, so `2^k` lifts per `λ`, instant. It recovers all
three obstructions above from scratch.

**At k=13 that family is empty.** All six `λ`, all `2^13` lifts, at
`p = 43, 89, 97, …, 293` — 30 values of `p`, nothing unsaved anywhere,
including at primes where `T2(13,p)` is *known* to fail. So the vector that
carries failure furthest at `k = 5, 7, 9` has no `k = 13` counterpart. (The
balanced lift of `i mod 7`, tested earlier, is the `λ=1` member of this family
and is one of the 8192 lifts it just swept.)

Combined with the flat-alphabet sweeps — `{0,1,7}`, `{0,1,13}` and the
eight-letter `{0,1,2,3,7,11,12,13}`, all exhaustive in their alphabet, all
empty at every prime from 97 to 181, all firing correctly on the positive
controls at 71, 73, 89, 90, 95, 99, 105, 116 — the evidence that `T2(13,p)`
already holds well below 191 is now fairly wide. None of it is a proof. An
alphabet-restricted `NONE` is a residue, not a bound.

## 2026-08-22 — q2: `q = 200` is SAT, so the certificate needs a larger q

`cells --k 13 --q 200` returned SAT in 216,477,912 nodes / 2749 s:

    v = (2,4,6,1,10,5,0,2,4,6,8,10,12)

That is a statement about the *relaxation*, not about `T2`. Checked against
`q1/check_unsaved.py`, this `v` is **saved** at 191, 193, 197, 199, 211, 223,
239, 257, 293, 401 and 601 — every prime tried. The window construction is
one-sided by design: SAT means the constraints kept at `q = 200` are too few
to rule `v` out, not that any `p` fails. So the certificate holds at some
`q > 200`; `q = 300` and `q = 500` are running.

