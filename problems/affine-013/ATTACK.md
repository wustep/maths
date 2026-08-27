# Attack log — extremal affine copies of {0,1,3}

## 2026-08-17 — literature (fetch Green #24 first)

Fetched:

- Green, *100 Open Problems* (Dec 2025 update), Problem 24:
  > If A is a set of n integers, what is the maximum number of affine
  > translates of the set {0,1,3} that can A contain?
  Comments: raised by Ganguly, heard from Pemantle; “it seems likely
  that the answer is (1/3+o(1))n², but this is not known. Aaronson’s
  paper [2] should be consulted.” No later update on this problem.
  SHA-256 of the PDF: `e06971245914947f152550dee59bbb29fe0e798f0c51b2bc2557f824c2f9a44a`.

- Aaronson, *Maximising the number of solutions to a linear equation
  in a set of integers*, arXiv:1801.07135v4 (3 May 2019) = Bull. Lond.
  Math. Soc. 51 (2019), 577–594. The list’s `1805.01980` is the wrong
  paper (a scattering inverse-problem). SHA-256:
  `f0da178874c50f7653d87271d86fae036abb5d19e9b83b17503251424f2e2ef2`.

An affine copy of {0,1,3} is {a, a+d, a+3d} with d≠0, equivalently a
solution of x+2y=3z with not all three equal. Aaronson’s T(S) counts
*all* ordered triples in S³ with x+2y=3z, including the n trivials
x=y=z. Those are o(n²), so the asymptotic constant is the same.

Published record on γ_{1,2,-3} := limsup T(S)/|S|², after the fetch:

- Lower: 1/3, from a centred (or any) interval. For S={0,…,n−1} one
  has T(S) = #{(x,y)∈S² : x≡y (mod 3)}, because z=(x+2y)/3 lands in
  S automatically; that count is n²/3+O(1). Aaronson conjectures this
  is the truth.
- Upper: 3/4, from Hardy–Littlewood / Gabriel / Lev rearrangement:
  T_{1,2,-3}(S) ≤ T_{1,1,1}(S′) where S′ is a centred interval of the
  same size, and T_{1,1,1}(S′) = (3/4+o(1))n². Aaronson Lemma 2.6 is
  the same 3/4 with an explicit +1/4.

Exact values of γ_{a,b,c} are known only for |abc|≤2
(γ_{1,1,±1}=3/4, γ_{1,−2,±1}=1/2, γ_{1,2,1}=1/2). Green–Sisask and
Lev–Pinchasi handle the 3-AP equation; {0,1,3} is the first open
pattern. No later paper I found moves γ_{1,2,-3}. Green’s Dec 2025
list still treats it as open.

A dent is a construction with limsup T/n² > 1/3, an upper bound
< 3/4, or a small-n table that *implies* one of those on an infinite
family. Isolated small-n counts are residue.

## 2026-08-17 — tonight’s handle

Three live handles:

1. **Construction.** Interval is *not* finite-n optimal ({0,1,3} has
   T=4 > T({0,1,2})=3). Any set beating 1/3 must be unbalanced mod 3,
   because T ≤ A₀²+A₁²+A₂² and a balanced set has A₀²+A₁²+A₂²=n²/3+O(n),
   with interval saturating the congruence. Search: two/three intervals,
   periodic lifts of a subset of ℤ/mℤ, {0,1,3}-configurations of APs,
   ×(−2)-orbits (the representation graph of x+2y=c).
2. **Upper bound < 3/4.** The 3/4 slack is that rearrangement compares
   against T_{1,1,1}(I,I,I), but T = T_{1,1,1}(S,2S,3S) and 2S, 3S
   cannot be the same interval. Residue-class Lemma 2.6 recovers 3/4
   again when S lies in one class (and that case reduces to the same
   problem by dividing by 3). Need a genuine new inequality.
3. **Small-n table.** Exhaust n-element sets up to affine normalisation
   (min=0, gcd=1, bounded diameter). Only a dent if the table implies
   an infinite-family bound (e.g. a periodic seed with c>1/3, or a
   compression that upgrades finite maxima to γ≤c<3/4).

Starting with (1) and a certified interval formula, then (3), then (2).

## 2026-08-17 — interval formula, independently checked

`compute/count.py` / `verify_interval.py`: for S={0,…,n−1}, z=(x+2y)/3 lands
in S automatically, so T(S)=A₀²+A₁²+A₂² with Aᵢ=⌈(n−i)/3⌉. Closed form

- n=3m:     T=3m²
- n=3m+1:   T=3m²+2m+1
- n=3m+2:   T=3m²+4m+2

matches brute force through n=79. Centred [−M,M] has the same T as some
translate of an n-interval (same residue profile). HL/Aaronson
T≤(3n²+1)/4 holds on these. {0,1,3} has T=4>T({0,1,2})=3, as Aaronson
remarks: the interval is *not* finite-n optimal.

## 2026-08-17 — constructions do not move 1/3

Periodic lifts S={x∈[0,Lm): x mod m ∈ P}, all nonempty proper P⊂ℤ/mℤ,
m=2..7, L=15: best ratio is exactly 1/3, achieved by a single residue
class (an AP ≅ interval). Nothing above the interval.

Two APs of difference 3 (the unbalanced-mod-3 family) and three APs:
through n=12 they recover only the +1 almost-interval, and a 48-point
grid search gave T=769 vs T_I=768. Ratio 0.3338.

Two intervals, {0,1,3}-placed blocks, residue-restricted intervals,
local search n≤30: the only infinite family that beats the interval is

    Sₙ = {0,1,…,n−2,n}          (n ≡ 0 (mod 3)),
    T(Sₙ) = T_interval(n) + 1 = n²/3 + 1.

Proved: for n=3m, Sₙ=[0,3m]\{3m−1} has residue sizes (m+1,m,m−1), so
A₀²+A₁²+A₂²=3m²+2, and exactly one of those pairs has z equal to the
hole 3m−1, namely (x,y)=(3m−3, 3m). Same constant 1/3.

Sporadic n=7 set {0,3,6,8,9,12,18} has T=18=T_I+1 (18 triples listed in
`certs/n7_triples.json`). Diameter 18. Not an infinite-family seed:
periodizing or blowing it up dilutes the ratio.

Exact search (C, subsets of {0..4n} containing 0) for n≤9 agrees:
maxima are the interval, the +1 almost-interval, or the n=7 sporadic.
Ratios fall toward 1/3 (0.444, 0.375, 0.360, 0.361, 0.367, 0.344, …).

Residue: constructions do not beat the published lower-bound constant.

## 2026-08-17 — energy side-quest (not a bound)

Aaronson Lemma 2.3: T² ≤ n E(S,2S), with E(S,2S)=∑_d r_{S−S}(d) r_{S−S}(2d).
If E were maximised by an interval then T ≤ √(n E(I,2I)) ∼ n²/√6 ≈ 0.408 n².
Local/exhaustive search through n=15 found no set with E > E(I,2I)
(APs match the interval by affine invariance). Diameter-compression
can *decrease* E, so that particular compression is not a proof.
Left as residue; not claimed.

## 2026-08-17 — the 1/2 bound (dent)

Green–Sisask (arXiv:0709.4432, Thm 1.2) bound the number of 3APs in an
n-element integer set by ordering: the j-th point is the midpoint of at
most min(j−1,n−j) increasing 3APs. The same ordering works for
x+2y=3z, because for fixed z=aⱼ the map y ↦ 3z−2y sends the left of z
injectively into the right and the right injectively into the left.

So the fibre at aⱼ has size ≤ 1+2 min(j−1,n−j), and

    T(S) ≤ ∑ⱼ (1 + 2 min(j−1,n−j)) = ⌈n²/2⌉.

Hence γ_{1,2,−3} ≤ 1/2. This is strictly below the published 3/4
(Hardy–Littlewood / Aaronson Lemma 2.6 / rearrangement against
T_{1,1,1}). It does not reach the conjectured 1/3.

Verified: the sum identity through n=399; the fibre injection on every
n-subset of {0..dmax} for (n,dmax)∈{(3,12),(4,12),(5,12),(6,12),(7,14)}
and on 2360 random sets, n≤60; every construction above sits under the
bound (`compute/verify_half.py`, `certs/half_bound.json`).

## 2026-08-27 — literature (Green #24 and Aaronson again)

Refetched Green, *100 Open Problems* (Dec 2025 update). Problem 24 is
unchanged. SHA-256 still
`e06971245914947f152550dee59bbb29fe0e798f0c51b2bc2557f824c2f9a44a`.
Aaronson arXiv:1801.07135v4 is still the paper; the list id `1805.01980`
is still the wrong paper. No later paper found tonight moves
γ_{1,2,−3}. The DeepMind formal-conjectures file for Green #24 still
records the published upper bound as Hardy–Littlewood 3/4.

Parent replay `compute/run_all.sh` exited 0.

## 2026-08-27 — q1, endpoint induction (residue)

Green–Sisask remark that the 3AP bound also follows by induction:
an endpoint cannot sit in too many 3APs. For x+2y=3z the triples
that use min(S) as x or y are

    N2 = #{d>0: min+d, min+3d ∈ S},
    N1 = #{d>0: min+2d, min+3d ∈ S}.

If min(N1+N2 at left, N1+N2 at right) ≤ 2(n−1)/3 always, then
T(n) ≤ T(n−1)+1+2(n−1)/3 and γ ≤ 1/3. The interval meets 2/3 with
equality. The budget already fails:

    {0,2,3,4,6}           n=5, ends 3,3 > 8/3, T=9 = T_I
    {0,2,3,6,7,9}         n=6, ends 4,4 > 10/3, T=12 < T_I+1
    {0,3,4,6,8,9,12}      n=7, ends 5,5 > 4,    T=17 = T_I
    {0,2,3,4,6,8,9,10,12} n=9, ends 7,7 > 16/3, T=27 = T_I

Those sets do not beat the interval. Both-end scores can be larger:
the 11-set {0,18,27,36,48,54,60,72,81,90,108} has ends 9,9, ratio
9/10, and T=39 < T_I=41. Periodizing the n=9 seed (difference 12)
keeps the end-score ratio near 5/6 and drops T/n² toward 0.30.
A uniform α<1 for the endpoint recurrence is not certified, so this
handle does not move 1/2.

A second count T = n + ∑_a (N1(a)+N2(a)) (hooks from every point,
not fibres at z) agrees with `count.t_count` on the named witnesses
and still sits under ⌈n²/2⌉. Almost-interval for n=3m: residue
sizes (m+1,m,m−1), A₀²+A₁²+A₂² = 3m²+2, unique hole pair
(x,y)=(n−3,n), hence T = n²/3+1, checked through m=40.

Families tonight (Green–Sisask E/F, two intervals, interval+3-tail,
double GP, Beatty, 3-scale IFS of the n=5 seed) stay at or below
1/3 + O(1/n). No construction dent.

`compute/q1/certs/q1.json`. Replay `compute/q1/run_all.sh`.
