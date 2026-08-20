# Attack log — five-dimensional kissing number

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House rules: write only here; no git; do
  not invent a dent; a restricted numerical SDP without an exact positivity
  certificate is residue.
- Tonight's target (house / PROBLEM.md): an exact dual certificate excluding
  some $k\in\{41,42,43,44\}$, or a new exact spherical code of size $>40$
  on $S^4$.

## Published record (fetched tonight)

Sources, all still stating $40\le\tau_5\le 44$:

- Tao constants page `C_{29}`
  <https://teorth.github.io/optimizationproblems/constants/29a.html>
  (accessed 2026-08-17): range $40\le\tau_5\le 44$, conjectural value 40.
- Cohn's living table
  <https://cohn.mit.edu/kissing-numbers/> (crawled 2026-08-17): dim 5 is
  40 / 44, ratio 1.100, citations [9] Korkine–Zolotareff and [17]
  Mittelmann–Vallentin.
- Boyvalenkov–Dodunekov–Musin survey, arXiv:1507.03631: “the first open
  case is in dimension five, where it is known that $40\le\tau_5\le 44$”
  (story: Levenshtein $L_5(5,1/2)=48$, Odlyzko–Sloane 46.345, Bachoc–
  Vallentin 45, Mittelmann–Vallentin 44.998).
- Mittelmann–Vallentin, arXiv:0902.1105v3 / Exp. Math. 19 (2010):
  $s_{14}(5)=44.99899685\ldots$, hence $\tau_5\le 44$. This is the
  published upper bound. High-accuracy SDP, not an exact SOS certificate
  in the paper.
- Cohn–Rajagopal, arXiv:2412.00937v3 (4 Mar 2026), published
  Discrete Comput. Geom. (doi 10.1007/s00454-026-00841-x): “the kissing
  number in five dimensions appears to be 40, although the best upper
  bound that has been proved is 44”. Four non-isometric 40-point codes:
  $D_5$, $L_5$ (Leech 1967), $Q_5$ (Szöllősi 2023 / Andreanov–Kallus),
  $R_5$ (Cohn–Rajagopal). None larger than 40.
- Wikipedia / MathWorld tables (MathWorld “as of August 2026”) still 40/44.
- No later accepted improvement of either endpoint found in arXiv search
  tonight (new work is lower bounds in high dimensions, or new 40-point
  geometries).

Independently I will re-verify the four 40-point Gram bounds and the
classical Levenshtein number 48 before claiming any comparison.

## Plan

1. Exact coordinates and Gram checks for $D_5,L_5,Q_5,R_5$.
2. Exact Delsarte / restricted-distance LPs (rational Gegenbauer).
3. Structural restrictions that can be certified exactly: codes containing
   a 24-cell, codes with only $D_5$ inner products, Q5-equator extensions.
4. Search for an exact 41-point spherical code (algebraic ansätze, layer
   replacement). Numerical SDP without a positivity certificate is residue.

## 2026-08-17 — replay of the four 40-point codes

- Implemented $D_5,L_5,Q_5,R_5$ from the geometric descriptions in
  Cohn–Rajagopal §2, not by typing Table 2.2.
- `compute/verify_configs.py`: all four have 40 points of squared norm 2,
  max normalised inner product exactly $1/2$, and the unordered-pair
  histograms match Cohn–Rajagopal Table 2.1 *exactly* (including the
  exotic angles $-4/5,-3/4,-3/10,-1/4,1/5$).
- Independently recomputed Levenshtein $L_5(5,1/2)=48$ from the BDM
  odd-bound formula (`compute/levenshtein.py`). Matches the survey.

## 2026-08-17 — false start: add a 41st point to $D_5$

- For unit $x\in S^4$, the $D_5$ inequalities are
  $|x_i|+|x_j|\le 1/\sqrt{2}$ for all $i\neq j$.
- On the unit sphere the min of the largest pair-sum is $2/\sqrt{5}$,
  with equality at the equal-coordinate points. Squares: $4/5>1/2$.
- So $D_5$ is maximal as a spherical code. Exact, not a 41-point lead.
  Script: `compute/extend_d5.py`.

## 2026-08-17 — false start: complete the $Q_5$ equator to a 24-cell

- $Q_5$ slices as $10+20+10$ along the all-ones direction, equator
  $=A_4$ (20 roots). The 4D kissing number is 24, so adding four
  equatorial points would give a 44-point candidate.
- Histogram check: $A_4$ is *not* isometric to any 24-cell minus two
  antipodal pairs (66 subsets, zero histogram matches).
- Stronger: on the equatorial 4-space $\sum x_i=0$, the $A_4$
  inequalities $x_i-x_j\le 1$ cut a polytope whose vertices are
  two-level and satisfy $|x|^2\le 6/5<2$. No new equatorial vector of
  squared norm 2 exists at all. Script: `compute/q5_extend.py`.

## 2026-08-17 — the D4-containing bound

- Any isometric 24-cell in $S^4$ spans a 4-space, so after rotation it
  is the $D_4$ equator $x_5=0$. Extra points
  $x=(\sqrt{1-h^2}\,u,\,h)$ must have
  $\varphi(u):=\max_{i\neq j}(|u_i|+|u_j|)\le 1/\sqrt{2(1-h^2)}$.
- Since $\varphi\ge 1$ on $S^3$, one needs $h^2\ge 1/2$ (or a pole).
- Two extra points in the same open hemisphere then have 4D blocks $y,y'$
  with $\langle y,y'\rangle\le 0$, so their directions form a code in
  $S^3$ of max inner product $\le 0$.
- Rankin's $A(4,0)\le 8$ is the exact Delsarte polynomial
  $f(t)=t^2+t=(1/4)P_0^{(4)}+P_1^{(4)}+(3/4)P_2^{(4)}$,
  $f\le 0$ on $[-1,0]$, $f(1)/f_0=8$.
- Poles conflict with every non-polar extra point in the same hemisphere
  ($h\ge 1/\sqrt{2}>1/2$).
- Therefore a $D_4$-containing 5D kissing code has size at most
  $24+8+8=40$. This excludes $k=41,42,43,44$ in that class.
- Discrete check (`compute/d4_equator.py`): the 24 holes of the 24-cell
  realise $\varphi=1$, their $1/2$-graph has independence number 8,
  and there are exactly three maximum independent sets — Cohn's three
  inscribed cross-polytopes (one axis, two tesseract).
- $D_5$ and $L_5$ contain a 24-cell, so they are covered. $Q_5$ and
  $R_5$ do not.

## 2026-08-17 — restricted Delsarte, then exact duals

- Unrestricted Delsarte cannot beat $\sim 46.3$ (Odlyzko–Sloane) and
  the 3-point SDP of Mittelmann–Vallentin is $44.998$. A floating SDP
  without a positivity certificate is residue; we did not rerun SDPA-GMP.
- For a *finite* inner-product set $T$ the dual only needs $f\le 0$
  on $T$, not on the whole interval $[-1,1/2]$. That *can* go below 44.
- Numerical LP (`compute/restricted_lp.py`):
  - $T_{D_5}=\{-1,-1/2,0,1/2\}$: bound $42$
  - $T_{L_5}=\{-1,-3/4,-1/2,-1/4,0,1/2\}$: bound $43.9745\ldots$
  - $T_{Q_5}$: bound $44.67$ (does not exclude 44)
  - union of all known 40-point angles: bound $45.66$
- The $L_5$ dual uses only $c_0,c_1,c_2,c_3,c_4,c_9$ and vanishes on
  $T_{L_5}\setminus\{-1\}$. Solving that interpolation over $\mathbb Q$
  (`compute/exact_duals.py`) gives the exact polynomial in
  `compute/certs/restricted_delsarte.json`:
  $$
  f=\sum c_k P_k^{(5)},\quad
  c=\Bigl(1,\tfrac{169541}{45136},\tfrac{28}{3},\tfrac{6095}{651},\tfrac{32}{3},0,0,0,0,\tfrac{131072}{13299}\Bigr),
  $$
  $f(1)=239925/5456=44-139/5456<44$. All $c_k\ge 0$, $f\le 0$ on
  $T_{L_5}$. Replay: `compute/verify_certificates.py`.
- Same method for $T_{D_5}$: $c=(1,49/45,28/3,0,32/3,896/45)$,
  $f(1)=42$, excludes 43 and 44 in that class.

## 2026-08-17 — integer distance distributions for $T_{D_5}$

- Real Delsarte allows $N=42$ with fractional $A_t=12.8,14.4,12.8$.
- Unordered pair counts $n_t=N A_t/2$ must be integers.
- Exhaustive search at Gegenbauer degree 8 (`compute/integer_d5.py`):
  - $N=40$: feasible (including $D_5$ and nearby)
  - $N=41$: feasible, but *every* hit has $n_{-1}=20$
    (the slice $n_{-1}\le 19$ is empty)
  - $N=42,43,44$: empty
- The $N=41$ witness survives degree 20 (`compute/check_integer_hits.py`),
  so Delsarte+integrality alone does not kill 41. Combined with the root
  system of 20 antipodal pairs (a 40-point $T_{D_5}$ code, necessarily
  $D_5$) and the $\varphi$-obstruction, 41 dies too.

## 2026-08-17 — construction residue

- Cube vertices $+$ axes: 16+10=26.
- $D_5$ minus neighbourhoods plus even-sign holes: best size 40
  (`compute/construct_search.py`).
- Numerical 41st-point slack against $L_5,Q_5,R_5$: all
  $\approx -0.2649$, the optimiser sitting on a deep hole
  (inner product $2/\sqrt{5}$). Residue, not a certificate of
  maximality for $Q_5,R_5$.
- Enlarging $T$ by $Q_5$'s extra angles lifts the exact dual back
  above 44 (`compute/more_duals.py`). No unrestricted dual below 44.

## Published record we compare against

- Lower bound 40 (Korkine–Zolotareff $D_5$; also $L_5,Q_5,R_5$).
  We did not produce a spherical code of size $>40$.
- Upper bound 44 (Mittelmann–Vallentin $s_{14}(5)=44.99899685\ldots$).
  We did not produce an unrestricted dual below 44.
- What we *did* certify is restricted: see RESEARCH.md.
