# Research log — five-dimensional kissing number

## Status (accessed 2026-08-17)

The kissing number $\tau_5=A(5,1/2)$ is **open**. The published range
is still

$$
40\le\tau_5\le 44,
$$

and the value is widely expected to be 40. No accepted paper, arXiv
preprint, or living table consulted tonight improves either endpoint.

### Sources checked tonight

| Source | What it says | When |
| --- | --- | --- |
| [Tao constants $C_{29}$](https://teorth.github.io/optimizationproblems/constants/29a.html) | $40\le\tau_5\le 44$, conjectural value 40 | fetched 2026-08-17 |
| [Cohn, kissing-number table](https://cohn.mit.edu/kissing-numbers/) | dim 5: lower 40, upper 44, ratio 1.100 | crawled 2026-08-17 |
| [Boyvalenkov–Dodunekov–Musin, arXiv:1507.03631](https://arxiv.org/abs/1507.03631) | first open case; story $48\to 46.345\to 45\to 44.998$ | 2012/2015 survey |
| [Mittelmann–Vallentin, arXiv:0902.1105v3](https://arxiv.org/abs/0902.1105) / Exp. Math. 19 (2010) | $s_{14}(5)=44.99899685\ldots$, hence $\tau_5\le 44$ | the published upper bound |
| [Bachoc–Vallentin, JAMS 21 (2008)](https://arxiv.org/abs/math/0608426) | 3-point SDP, $\tau_5\le 45$ | precursor of MV |
| [Cohn–Rajagopal, arXiv:2412.00937v3](https://arxiv.org/abs/2412.00937) / DCG 2026 | “appears to be 40… best upper bound 44”; four 40-point geometries $D_5,L_5,Q_5,R_5$ | 4 Mar 2026 |
| [Szöllősi, MRL 30 (2023)](https://arxiv.org/abs/2301.08272) | third 40-point configuration $Q_5$ | 2023 |
| MathWorld / Wikipedia tables | 40 / 44 “as of August 2026” | fetched 2026-08-17 |
| Cohn table refs for later dimensions (de Laat–Leijenhorst 2024, Cohn–Li 2024, …) | new lower bounds in dims $\ge 10$ and better SDP in some high dims; **dim 5 untouched** | 2024–26 |

Odlyzko–Sloane 1979 is the continuum LP number $46.345$. Coxeter 1963
is 48. The $D_5$ lower bound is Korkine–Zolotareff 1873 (40 roots:
permutations of $(\pm 1,\pm 1,0,0,0)$).

## Independent checks (this folder)

- `compute/verify_configs.py` — PASS. $D_5,L_5,Q_5,R_5$ are 40-point
  kissing codes. Pair histograms match Cohn–Rajagopal Table 2.1 on the
  nose, including the non-$D_5$ angles $-4/5,-3/4,-3/10,-1/4,1/5$.
- `compute/levenshtein.py` — PASS. $L_5(5,1/2)=48$ from the BDM formula.
- `compute/extend_d5.py` — PASS. $4/5>1/2$, so $D_5$ is maximal.
- `compute/d4_equator.py` — PASS. $A(4,0)\le 8$ via $t^2+t$; 24-cell
  hole graph has independence number 8 and exactly three MIS
  (Cohn’s three cross-polytopes).
- `compute/verify_certificates.py` — PASS. Rebuilds Gegenbauer from the
  recurrence and checks the two duals in
  `compute/certs/restricted_delsarte.json`.
- `compute/integer_d5.py` — PASS. Integer $T_{D_5}$ distributions:
  42/43/44 empty; 41 only with 20 antipodes.

## What we certified

Restricted exact duals and one geometric lemma. **None of these changes
the unrestricted range $40\le\tau_5\le 44$.**

### 1. 24-cell lemma

A kissing code in $S^4$ that contains an isometric copy of the 24-cell
has at most 40 points. Proof: the 24-cell is equatorial; extra points
lie at $|h|\ge 1/\sqrt{2}$; each open hemisphere contributes at most
$A(4,0)\le 8$ extra points, via the exact polynomial $t^2+t$.
Consequently $k\in\{41,42,43,44\}$ is impossible in this class, and
the two 24-cell-containing 40-point codes $D_5$ and $L_5$ are
maximal.

This is the kind of fact experts use when they build $D_5$ and $L_5$
by filling holes of the 24-cell. We did not find it stated as a bound
on 41–44, so we wrote out the Rankin step and checked the discrete hole
graph. It is a restricted obstruction, not an unrestricted bound.

### 2. Leech-angle Delsarte dual

Any spherical code in $S^4$ whose distinct inner products lie in

$$
T_{L_5}=\{-1,-3/4,-1/2,-1/4,0,1/2\}
$$

(the exact angle set of Leech’s $L_5$) has size at most

$$
\frac{239925}{5456}=44-\frac{139}{5456}<44,
$$

hence at most 43. The dual is the Gegenbauer combination with
coefficients

$$
\Bigl(1,\ \tfrac{169541}{45136},\ \tfrac{28}{3},\ \tfrac{6095}{651},\ \tfrac{32}{3},\ 0,0,0,0,\ \tfrac{131072}{13299}\Bigr).
$$

Replay: `compute/verify_certificates.py`. This excludes $k=44$ in the
$T_{L_5}$ class. It does *not* exclude 44 for $Q_5$-type angles
(the corresponding interpolating dual has value $167076/3047\approx 54.8$).

### 3. $D_5$-angle codes

For $T_{D_5}=\{-1,-1/2,0,1/2\}$:

- real Delsarte gives $N\le 42$, by the dual
  $(1,49/45,28/3,0,32/3,896/45)$;
- integer pair-counts kill 42, 43, 44, and force any 41-point
  distribution to contain 20 antipodal pairs;
- those 40 points are an equal-length subset of a simply-laced root
  system of rank $\le 5$, hence a copy of $D_5$, which cannot be
  extended.

So $k\in\{41,42,43,44\}$ is impossible in the $T_{D_5}$ class. The
root-system step is classical (Cartan–Killing: the only 40-root
equal-length system in rank $\le 5$ is $D_5$); the integer slice
and the exact dual of bound 42 are computed here.

### 4. $Q_5$ has no extra equatorial point

On $\sum x_i=0$ the $A_4$ inequalities cut a polytope of maximal
squared norm $6/5<2$.

## What we did not beat

- The unrestricted upper bound 44. No continuum Delsarte or exact
  Bachoc–Vallentin dual below 44 was produced. A floating 3-point SDP
  would have been residue even if we had rerun one.
- The unrestricted lower bound 40. No exact 41-point spherical code.
  Algebraic ansätze (cube+axes, $D_5$ plus holes, $A_4$ completion)
  top out at 40. Numerical 41st-point slacks against $Q_5$ and $R_5$
  are $\approx-0.265$.
- Maximality of $Q_5$ and $R_5$ as spherical codes (they do not
  contain a 24-cell, so the lemma does not apply).
- An exact SOS certificate of Mittelmann–Vallentin’s $44.998\ldots$.

## How to replay

```bash
sh compute/run_all.sh
```

The duals alone:

```bash
compute/.venv/bin/python compute/verify_certificates.py
```

Expected last lines: `D5_inner_products: certified=True bound=42 … excludes=[43, 44]`
and `L5_inner_products: certified=True bound=239925/5456 … excludes=[44]`.

## 2026-08-27 — record still $40\le\tau_5\le 44$

Opened tonight:

- https://teorth.github.io/optimizationproblems/constants/29a.html —
  $40\le\tau_5\le 44$, conjectural value 40. Upper bound cited is
  Mittelmann–Vallentin.
- https://cohn.mit.edu/kissing-numbers/ — dim 5 lower 40, upper 44,
  ratio 1.100, citations [9] Korkine–Zolotareff and [17]
  Mittelmann–Vallentin. Later-dimension news (Cohn–Li, de Laat–
  Leijenhorst, Ma et al. 2511.13391, …) does not touch dim 5.
- https://arxiv.org/abs/2412.00937 — v3 (4 Mar 2026): “appears to be 40…
  best upper bound that has been proved is 44”. Four 40-point geometries.
- https://arxiv.org/abs/0902.1105 — $s_{14}(5)=44.998\ldots$, hence
  $\tau_5\le 44$. Still the published upper bound.
- https://arxiv.org/abs/1507.03631 — survey story $48\to 46.345\to 45\to 44.998$.
- https://arxiv.org/abs/2301.08272 — Szöllősi $Q_5$, third 40-point code.
- https://doi.org/10.5281/zenodo.18449600 — unaffiliated note claiming a
  degree-36 Cohn–Kumar number $44.0297$. Not a paper; not an exact dual;
  unrestricted Delsarte is already $\approx 46.345$. Lead only.

## 2026-08-27 — what we certified this run

Still **no** change to the unrestricted range $40\le\tau_5\le 44$.

### 5. Polar maximality of the four 40-point codes

`compute/q1/polar_vertices.json`, replayed by `replay_max_vertex.py`
(Fraction GE, not the Cramer path in `polar.c`). For each of
$D_5,L_5,Q_5,R_5$ the polar is bounded and $\max|x|^2=5/4<2$.
Python and C enumerations agree on the vertex counts. Consequently
none of these four codes admits a 41st kissing point. This is a
statement about those four codes, not about $\tau_5$.

### 6. Integer Delsarte on $T_{Q_5}$ excludes 44

`compute/q1/integer_q5_44.json`: $14\,753\,818\,985$ integer points in
a box containing the real AABB by 15, zero Delsarte-feasible. Tables
match `delsarte.py`; $Q_5$'s own $N=40$ histogram passes. So $k=44$
is impossible for inner products in
$T_{Q_5}=\{-1,-4/5,-1/2,-3/10,0,1/5,1/2\}$. Real Delsarte is still
$\approx 44.67$; this is integrality, not a dual below 44.

$T_{L_5}$ still has integer hits at $N=41,42,43$
(`compute/q1/integer_restricted.json`).

Replay:

```bash
sh problems/kissing-5d/compute/q1/run_all.sh
```
