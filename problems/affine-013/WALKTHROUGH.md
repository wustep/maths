# Walkthrough — A 1/2 upper bound for affine copies of {0,1,3}

- Problem: `problems/affine-013`
- Quest: SuperGrok 2026-08-17, Green 100 #24
- Model: grok-4.6 `--reasoning-effort xhigh`
- Date: 2026-08-17
- Argument status: elementary ordering + injection, machine-checked on
  the sum identity and on the fibres of many sets
- Problem status: open. The conjectured constant 1/3 is not proved.

## 0. What was actually missing

The missing degree of freedom was not a new family of sets. The
interval already gives T ∼ n²/3, and Green’s list (Dec 2025) still
says the constant is unknown because the matching upper bound is
missing. The published upper bound on Aaronson’s T is 3/4, coming
from a rearrangement comparison against a *different* equation
(x+y+z=0). That comparison throws away the fact that the three
sets in T_{1,1,1}(S, 2S, 3S) are dilates of each other, and it
throws away the ordering of ℤ.

Green–Sisask had already used the ordering of ℤ to get a sharp
⌈n²/2⌉ bound for 3-term APs. The same skeleton works for {0,1,3}
once the midpoint reflection y ↦ 2z−y is replaced by the weighted
map y ↦ 3z−2y. That map still sends the left of z into the right
and the right into the left, injectively. The resulting bound is
1/2 rather than 1/3, but 1/2 is already below 3/4.

## 1. False starts (named obstacles)

- **Periodic seeds.** Any P ⊂ ℤ/mℤ, lifted as
  S = {x ∈ [0, Lm): x mod m ∈ P}, is an infinite family. For m≤7
  and L=15 the best ratio was exactly 1/3, achieved by a single
  residue class (an AP, Freiman-isomorphic to an interval). The
  obstruction is modular: T ≤ A₀²+A₁²+A₂², and a balanced set
  saturates at n²/3; a biased seed either reduces to a smaller
  copy of the same problem (one class, divide by 3) or loses the
  extra congruence mass when z falls in a gap.
- **Two and three APs of difference 3.** The only way to beat n²/3
  is to be unbalanced mod 3. Placing two intervals in two residue
  classes, with a free shift, recovered only the +1 almost-interval
  (below). A 48-point grid gave T=769 versus T_I=768. Same
  constant.
- **Blow-ups of {0,1,3}.** Replacing each point of a small
  maximiser by a long cluster multiplies T by about m²/3 and n by
  m|S|, so the ratio is divided by 3. The integrality (i+2j)≡0
  (mod 3) inside clusters is the obstruction.
- **Energy ⇒ 1/√6.** Aaronson’s Lemma 2.3 says T² ≤ n E(S,2S).
  Interval energy is ∼ n³/6, which would give T ≤ n²/√6 ≈ 0.408 n²
  *if* the interval maximised E(S,2S). Search through n=15 found
  no counterexample, but the natural diameter-compression can
  *decrease* E, so it is not a proof. Not claimed.
- **Induction on n with a residue split.** If S lies in one class
  mod 3 then T(S)=T(S/3) and |S| does not drop. After translating
  and dividing out the gcd one may assume two classes, but the
  cross terms E_{A→B} ≤ ab overpower the inductive savings and the
  resulting bound is worse than 3/4.

## 2. The useful failure

The construction search was the useful failure. Two facts survived
every family:

1. T(S) ≤ A₀²+A₁²+A₂², with equality iff every pair with x≡y
   (mod 3) has (x+2y)/3 ∈ S. An interval saturates this among
   balanced sets, so anything beating 1/3 must be unbalanced
   mod 3.
2. Unbalancing does not pay asymptotically. One residue class
   reduces to the same problem. Two classes, placed as long APs,
   recapture some of the “lost” z-values and pick up at most +1
   (the almost-interval Sₙ = {0,…,n−2,n} for n=3m, proved by
   counting the unique pair whose z is the hole 3m−1).

So the lower-bound constant did not move, and the finite-n
maximisers (including the sporadic 7-set {0,3,6,8,9,12,18} with
T=18) are an incomplete search. That forced the work onto an upper bound that
uses the order of ℤ, which constructions never see.

## 3. The click

Green–Sisask, Theorem 1.2: if a₁ < ⋯ < aₙ then aⱼ is the midpoint
of at most min(j−1, n−j) increasing 3APs, and summing gives
⌈n²/2⌉. The only input is that the map y ↦ 2z−y swaps left and
right.

For x+2y=3z the analogous map is y ↦ 3z−2y. If y < z then
3z−2y − z = 2(z−y) > 0, so the image is strictly to the right of
z; if y > z the image is strictly to the left. Different y give
different images. Equivalently: z = (x+2y)/3 is a convex
combination of x and y, so z is always the median of {x,y,z}.
The j-th point of an ordered set can be the median of an affine
{0,1,3} at most min(L,R) times in each orientation. The fibre
over z=aⱼ still has size at most 1 + 2 min(j−1, n−j), and the
*same sum* bounds T.

The 3/4 bound never used the order. Once the order is used, 1/2
is immediate.

## 4. The argument, in the order it was found

Write T(S) for the number of ordered triples (x,y,z)∈S³ with
x+2y=3z (Aaronson’s count). Let S={a₁ < ⋯ < aₙ} ⊂ ℤ and fix
z=aⱼ. For each y∈S there is at most one x=3z−2y, and this x
lies in S if and only if (y,z) extends to a solution.

- If y=z then x=z: the one trivial solution at this z.
- If y < z then x−z = 2(z−y) > 0, so x > z. The map
  y ↦ 3z−2y is injective on the left of z, and lands strictly
  to the right. At most min(j−1, n−j) such y work.
- If y > z then x < z, injectively into the left. Again at most
  min(j−1, n−j).

Hence the fibre at aⱼ has size at most 1+2 min(j−1, n−j), and

```
T(S)  ≤  ∑_{j=1}^{n} (1 + 2 min(j-1, n-j)).
```

The sum is n + 2 ∑ min(j−1, n−j). For n=2t even this is
2t + 2·t(t−1) = 2t² = n²/2. For n=2t+1 it is
2t+1 + 2(t²) = 2t²+2t+1 = ⌈n²/2⌉. (Green–Sisask evaluate the
same sum for a different fibre.) Therefore

```
T(S)  ≤  ⌈n²/2⌉
```

for every n-element integer set S. In particular

```
γ_{1,2,-3}  :=  limsup_{|S|→∞} T(S)/|S|²   ≤   1/2.
```

The published upper bound was 3/4 (Aaronson (1.2), from
T_{1,2,-3}(S) ≤ T_{1,1,1}(S′) and the Hardy–Littlewood /
Gabriel / Lev evaluation T_{1,1,1}(centred interval) ∼ 3n²/4).
1/2 < 3/4, so the asymptotic constant has moved.

The bound is not sharp. An interval has T = n²/3+O(1). The
almost-interval {0,…,n−2,n} for n=3m has T = n²/3+1, still 1/3.
Green–Sisask’s 3AP-extremisers E(k,m), F(k,m) do not beat 1/3
for this equation either (they are almost-intervals of even
difference, or they lose the factor-of-two spacing).

## 5. Computer search

- Interval closed form, brute-forced through n=79:
  `compute/verify_interval.py`.
- Fibre injection and the sum identity: `compute/verify_half.py`.
  Identity through n=399; every n-subset of {0..dmax} for
  (n,dmax) in {(3,12),(4,12),(5,12),(6,12),(7,14)}; 2360 random
  sets with n≤60; named witnesses including the n=7 sporadic.
  Output: `compute/certs/half_bound.json`.
- Small-n maxima found by exact search / local search (not needed
  for the bound; they do not move 1/3):

  | n | T_interval | T_found | ⌈n²/2⌉ | a maximiser |
  |--:|--:|--:|--:|---|
  | 3 | 3 | 4 | 5 | {0,1,3} |
  | 4 | 6 | 6 | 8 | interval |
  | 5 | 9 | 9 | 13 | interval |
  | 6 | 12 | 13 | 18 | {0,1,2,3,4,6} |
  | 7 | 17 | 18 | 25 | {0,3,6,8,9,12,18} |
  | 8 | 22 | 22 | 32 | interval |
  | 9 | 27 | 28 | 41 | {0,…,7,9} |

  For every n=3m the almost-interval {0,…,n−2,n} has T = T_I+1
  (proved, not just tabulated). The 18 triples of the n=7 set are
  in `compute/certs/n7_triples.json`.
- Periodic / two-AP / three-AP / local search: no family with
  limsup T/n² > 1/3. Logs in `compute/periodic.json`,
  `compute/two_ap.json`, `compute/local.json`.
- Figure: `figures/constants.png`.

## 6. What is proved vs still open

Proved: T(S) ≤ ⌈n²/2⌉ for every finite S ⊂ ℤ, hence
γ_{1,2,-3} ≤ 1/2. This is a strict improvement on the published
3/4 and is not a restatement of Green–Sisask (different equation,
different injection).

Still open: the conjecture γ_{1,2,-3} = 1/3. The gap between 1/3
and 1/2 is exactly the slack in the fibre bound — for a typical
z only about a third of the candidate y with the right side of z
have 3z−2y *equal* to an existing point, not merely to *some*
point on the correct side. Closing that slack is the original
problem. Isolated small-n counts, including the +1 almost-interval
and the n=7 sporadic, do not close it.
