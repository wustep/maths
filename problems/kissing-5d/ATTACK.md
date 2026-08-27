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

## 2026-08-27 — continue (q1)

- Start from main. Folder `compute/q1/`. House rules unchanged: do not
  claim $\tau_5=40$; a numerical SDP without an exact positivity
  certificate is residue; the published record is still
  $40\le\tau_5\le 44$.
- Re-fetched tonight, all still $40\le\tau_5\le 44$:
  Tao $C_{29}$ <https://teorth.github.io/optimizationproblems/constants/29a.html>,
  Cohn table <https://cohn.mit.edu/kissing-numbers/> (dim 5: 40 / 44,
  refs [9] Korkine–Zolotareff and [17] Mittelmann–Vallentin),
  Cohn–Rajagopal arXiv:2412.00937v3, Mittelmann–Vallentin
  arXiv:0902.1105v3. A Zenodo note claiming a Cohn–Kumar LP number
  $44.0297$ is a lead, not a citation: unrestricted Delsarte is already
  $\approx 46.345$, and there is no exact dual.
- Plan: (1) exact polar vertices of $D_5,L_5,Q_5,R_5$ (maximality of
  $Q_5,R_5$ was only numerical on 17 August); (2) integer Delsarte boxes
  for $T_{L_5}$ and $T_{Q_5}$; (3) $A_4$-containing height and the
  discrete vertex-extra graph; (4) more interpolating duals; (5)
  Szöllősi $T^5$ candidate graph on the known angles.

## 2026-08-27 — polar vertices: all four codes are maximal

- $P(C)=\{x:\langle x,p\rangle\le 1\ \forall p\in C\}$ is a bounded
  rational polytope for each of $D_5,L_5,Q_5,R_5$ (no recession ray).
- Exhaustive 5-subset vertex enumeration, twice:
  `compute/q1/polar.c` and `polar_vertices.py --python`.
  Counts agree: $D_5$ 5504 vertices, $L_5$ 5440, $Q_5$ 4024, $R_5$ 3960.
- $\max|x|^2=5/4<2$ on every polar. Independent Fraction GE
  (`replay_max_vertex.py`) rebuilds the recorded vertex over $\mathbb Q$:
  $Q_5$ and $D_5$ attain $5/4$ at $\pm\frac12(1,1,1,1,1)$; $L_5$ and
  $R_5$ at a coordinate half-axis. All inequalities hold.
- So $Q_5$ and $R_5$ are maximal as spherical codes. That was numerical
  slack $\approx-0.2649$ on 17 August. $D_5$ and $L_5$ were already
  maximal by other exact arguments; the polar is a uniform proof.
- This excludes a 41st point *on these four codes*. It does not exclude
  an unrelated 41-point code. Unrestricted $\tau_5$ is unchanged.

## 2026-08-27 — $T_{Q_5}$ integer slice empty at $N=44$

- Real Delsarte on $T_{Q_5}$ is still $\approx 44.67$ (no interpolating
  dual below 44; several supports certified only in the 45–60 range).
- Integer pair-counts: $n_t=N A_t/2\in\mathbb Z$, $\sum n_t=C(44,2)=946$.
- `integer_q5_44.c` scans a box containing the HiGHS axis-aligned range
  by 15 in each coordinate ($n_{-1}$ in the full $0..22$). $14\,753\,818\,985$
  points, 0 hits. Tables match `delsarte.py`; the published $Q_5$
  histogram at $N=40$ passes every row.
- Dent in this class: no spherical code in $S^4$ with distinct inner
  products in $\{-1,-4/5,-1/2,-3/10,0,1/5,1/2\}$ has 44 points.
  Does *not* exclude 41, 42 or 43, and is not an unrestricted dual.

## 2026-08-27 — $T_{L_5}$ integer does not kill 41–43

- $N=44$ is already empty by the 17 August dual $239925/5456<44$.
- $N=41,42,43$ each have integer Delsarte-feasible distributions
  (first hits in `integer_restricted.json`), all with $n_{-1}=0$.
  Residue: integrality does not improve the $T_{L_5}$ dual.

## 2026-08-27 — $A_4$ extras and Szöllősi graph

- Height over a fixed $A_4$ equator: $|s|\ge 2$. Poles conflict with
  every other extra in the same hemisphere ($8/5>1$). Discrete
  two-level vertex extras: independence 10 per hemisphere, 20 total,
  so $A_4$ plus vertex extras is at most 40. Continuous extras with
  $|s|>2$ are not in that graph.
- Szöllősi $T^5$ pool: 355 equal-norm vectors. Exact clique on 355
  vertices was not run. Residue, not a 41-point code.

## 2026-08-27 — continue (q2)

- Start from current main (after q1). Folder `compute/q2/`. House rules
  unchanged: do not claim $\tau_5=40$; a numerical SDP without an exact
  positivity certificate is residue; do not regress the restricted
  certificates already in `compute/certs/` and `compute/q1/certs/`.
- Replayed first, all still pass:
  `compute/verify_certificates.py` (T_{D_5} bound 42; T_{L_5} bound
  $239925/5456<44$);
  `compute/q1/verify.py` / `replay_max_vertex.py` (polar $\max|x|^2=5/4$);
  `compute/q1/check_q5_44_empty.py` ($T_{Q_5}$ integer slice empty at 44).
- Re-fetched tonight, all still $40\le\tau_5\le 44$:
  Tao $C_{29}$ <https://teorth.github.io/optimizationproblems/constants/29a.html>,
  Cohn table <https://cohn.mit.edu/kissing-numbers/> (dim 5: 40 / 44,
  refs [9] and [17]),
  Mittelmann–Vallentin arXiv:0902.1105v3 ($s_{14}(5)=44.99899685\ldots$),
  Cohn–Rajagopal arXiv:2412.00937v3 (4 Mar 2026). The unaffiliated
  Zenodo note that claimed a Cohn–Kumar number $44.0297$ is now
  retracted (doi:10.5281/zenodo.18449600, removed 5 Feb 2026). Lead
  only; not a citation.
- Hunt: an exact dual that is nonpositive on the whole interval
  $[-1,1/2]$ and excludes some $k\in\{41,42,43\}$, or a new exact
  41-point code in $S^4$. Plan: (1) exact clique on the leftover $T^5$
  pool of 355; (2) exact kissing graph on
  $(1/2)\mathbb Z^5\cap\{\lvert x\rvert^2=2\}$ (200 points; contains
  $D_5$ and $L_5$); (3) other hyperplane layer-swaps; (4) low-degree
  unrestricted Delsarte with Sturm / real-root certification.

## 2026-08-27 — q2 results (no unrestricted move)

- Unrestricted numerical Delsarte at degree $\ge 10$ is $46.3368\ldots$,
  matching Odlyzko–Sloane. Grid-rationalised polynomials fail the exact
  Sturm test (they change sign on $[-1,1/2]$). An exact ansatz
  $f(t)=(t-1/2)q(t)^2$ with $q=P_0+(17/6)P_1+(8/3)P_2$ gives bound
  $53235/1109\approx 48.003$, just above Levenshtein 48. No certified
  unrestricted dual has bound $<44$. No $k\in\{41,42,43\}$ is excluded
  without a restricted angle set.
- $T^5$ pool, after including the basis: 360 rational vectors, all four
  published 40-point codes are cliques. Five basis vectors are adjacent
  to every other pool point, so a 41-clique exists iff the remaining
  355-point graph has a 36-clique. The 41-search on those 355 vertices
  is empty (`t5_clique.json`, 607171 nodes). The 36-search was started
  and stopped without a hit or an emptiness proof (`t5_36_residue.json`).
- Half-integer sphere $(1/2)\mathbb Z^5\cap\{\lvert x\rvert^2=2\}$: 200
  points, no 41-clique (`sphere_d2.json`). This class contains $D_5$
  and $L_5$.
- $(1/4)\mathbb Z^5$ sphere: 1480 points. 41-search incomplete
  (`sphere_d4.json`). Residue.
- Layer-swaps of $D_5$ and $L_5$ across 546 short integer normals:
  3148 swaps, kissing sizes $\{34,36,37,39,40\}$, none 41.
- Signed-permutation orbit of a $Q_5$ cap vector: 320 points, no
  41-clique (`q5cap_clique.json`, 7 nodes).
- Unrestricted interval unchanged: $40\le\tau_5\le 44$. Did not beat
  Mittelmann–Vallentin. Did not produce a 41-point code.

## 2026-08-27 — continue (q3)

- Start from current main (after q2). Folder `compute/q3/`. House rules
  unchanged: do not claim $\tau_5=40$; a numerical SDP without an exact
  positivity certificate is residue; do not regress the restricted
  certificates already in `compute/certs/`, `compute/q1/`, `compute/q2/`.
- Re-fetched tonight, all still $40\le\tau_5\le 44$:
  Tao $C_{29}$ <https://teorth.github.io/optimizationproblems/constants/29a.html>
  (range $40\le\tau_5\le 44$, conjectural value 40; upper bound
  Mittelmann–Vallentin),
  Cohn table <https://cohn.mit.edu/kissing-numbers/> (dim 5: 40 / 44,
  ratio 1.100, citations [9] Korkine–Zolotareff and [17]
  Mittelmann–Vallentin),
  Mittelmann–Vallentin arXiv:0902.1105v3 ($s_{14}(5)=44.99899685\ldots$),
  Cohn–Rajagopal arXiv:2412.00937v3 (4 Mar 2026; title “Variations on
  five-dimensional sphere packings”: “appears to be 40… best upper bound
  that has been proved is 44”). The unaffiliated Zenodo $44.0297$ note
  remains retracted. Later-dimension news on Cohn’s table (Cohn–Li,
  Ho 2603.10425, Ma et al. 2511.13391, Takhanov et al. 2606.18984,
  Sun–Wang 2607.20359) does not touch dim 5.
- Hunt: an exact dual that is nonpositive on the whole interval
  $[-1,1/2]$ and excludes some $k\in\{41,42,43,44\}$, or a new exact
  41-point code. Leftover handles from q2, to verify independently:
  the 36-clique in the 355-point $T^5$ remainder, and the 1480-point
  $(1/4)\mathbb Z^5$ graph. Own route if better: type analysis of
  $(1/d)\mathbb Z^5$, a $T^5$ pool on a larger exact angle set, a
  $\mathbb Q(\sqrt5)$ orbit, continuous $A_4$ extras at $|s|>2$, and
  gapped duals that would need a geometric lemma to become unrestricted.

## 2026-08-27 — q3 results (no unrestricted move)

- Re-fetched Tao $C_{29}$, Cohn, Mittelmann–Vallentin, Cohn–Rajagopal:
  still $40\le\tau_5\le 44$. Pfender's kernel (arXiv:math/0501493) does
  not give an exact dual below 44 in dim 5. The Zenodo $44.0297$ note
  remains retracted.
- Unrestricted numerical Delsarte is still $46.3368\ldots$. Exact
  rationalizations fail the Sturm test. Gapped duals with
  $f\le 0$ only on $[-2/3,1/2]$ have a *numerical* value $\approx 37.46$,
  but there is no geometric lemma forbidding $t\in[-1,-2/3)$ (every
  published 40-point code has such an angle) and the rational
  polynomials did not certify. Not an unrestricted dual. No
  $k\in\{41,42,43,44\}$ is excluded on the whole interval $[-1,1/2]$.
- $(1/d)\mathbb Z^5$ type analysis (`sphere_types.py`,
  `complete_slices.py`): every extra vector kisses at most 36 of the
  40 $D_5$ roots, so a 41-set has $n_1\le 36$ and at least 5 extras.
  Complete enumeration of every $k$-superset of an actual missed-root
  set, $k\in\{4,5,6,7\}$, finds no extras-clique of size $k+1$.
  Therefore the 1480-point $d=4$ graph has no 41-clique that uses 33
  or more $D_5$-type points. Replay: `complete_slices.json`,
  `n1_ge_33_empty=true`. The $n_1\le 32$ slice (at least 9 extras) was
  not emptied. Residue for the whole 1480-graph, not a 41-code.
- $T^5$ remainder: exact repairs of the four published 35-cliques
  (remove 1 add 2; remove 2 add 3, candidate cap 28) are empty
  (`t5_repair.json`). Coloured B&B to 40 million nodes found no
  36-clique (`t5_36_c.json`). Incomplete, not an exclusion.
- Larger $T^5$ (published angles plus $\{\pm 1/3,\pm 2/5,\pm 3/5\}$):
  552-point pool, no 41-clique in 5 million nodes. Residue.
- $D_5$ plus the signed-permutation orbit of
  $(\varphi,1,1/\varphi,0,0)/\sqrt{2}$ and the half-spinor layers
  (552 points over $\mathbb Q(\sqrt2,\sqrt5)$): no 41-clique in 3
  million nodes. Residue.
- Continuous $A_4$ extras at exact rational heights, mesh
  denominators 2, 3, 4: 40 northern extras at den 4, independence 4,
  not 11. No 41-code.
- Unrestricted interval unchanged: $40\le\tau_5\le 44$. Did not beat
  Mittelmann–Vallentin. Did not produce a 41-point code.

## 2026-08-27 — q4 unrestricted dual hunt

- Folder `compute/q4/`. House rules unchanged: do not claim $\tau_5=40$;
  a numerical SDP without an exact positivity certificate is residue.
- Re-fetched tonight, all still $40\le\tau_5\le 44$:
  Tao $C_{29}$ <https://teorth.github.io/optimizationproblems/constants/29a.html>,
  Cohn table <https://cohn.mit.edu/kissing-numbers/> (dim 5: 40 / 44,
  refs [9] and [17]),
  Mittelmann–Vallentin arXiv:0902.1105v3 ($s_{14}(5)=44.99899685\ldots$),
  Bachoc–Vallentin arXiv:math/0608426v4 (3-point SDP, $\tau_5\le 45$
  before MV; exact $Y_k^n$ / $S_k^n$ formulas, Remark 3.4 monomial
  form),
  Cohn–Rajagopal arXiv:2412.00937v3. The unaffiliated Zenodo $44.0297$
  note remains retracted.
- Implemented exact $S_k^5$ over $\mathbb Q$ (`bv.py`). Self-tests:
  $Q_0=1$, $Q_1=t-uv$, $Q_k(u,u,1)=(1-u^2)^k$, $S_0(1,1,1)=J$,
  $S_k(1,1,1)=0$ for $k\ge 1$, $P_k^5$ matches `delsarte.py`.
- 1-point continuum Delsarte at degree 12 is $46.3368\ldots$. One
  rationalization (`den=1000`) gives $46.337$ and fails Sturm. Did not
  spend the session re-rationalizing Gegenbauer polynomials.
- Exact 3-point search, all residue or $\ge 48$:
  - constant-multiplier Putinar $d=1..4$: HiGHS infeasible;
  - diagonal grid LP: infeasible at $d\le 3$, grid value $85.56$ at
    $d=4$ (matches 1-point Delsarte $\approx 90$ at degree 4);
  - exact $p_4$-span kernel at $d=3,4,5$: 34 / 81 / 148 nonnegative
    kernel vectors, none make $h\le 0$ on $[-1,1/2]$;
  - square-dictionary LP: infeasible at $d=5$; numerical $40.38$ at
    $d=6$ does not snap to an identity over $\mathbb Q$;
  - floating Putinar SDP at $d=5$ (Clarabel / SCS): solver values
    below 40 or on the dummy cut $40$, `grid_ok=false`. Discarded.
- Best certified unrestricted dual remains Levenshtein
  $L_5(5,1/2)=48$ (the $F_k=0$ case of BV). No $k\in\{41,42,43,44\}$
  is excluded on the whole interval. Mittelmann–Vallentin
  $s_{14}(5)=44.998\ldots$ is still the published upper bound; that
  hierarchy cannot go below its own optimum at $d=14$, so a dual
  $<44$ would need $d>14$ or a different hierarchy *and* an exact
  SOS certificate.
- Wrote `compute/q4/dual_exact.json`. No `certs/unrestricted_delsarte.json`
  or `certs/bv_dual.json`.

## 2026-08-27 — q4 leftover graphs (no unrestricted move)

- Same house rules. Re-fetched Tao $C_{29}$, Cohn, Mittelmann–Vallentin
  $s_{14}(5)=44.99899685\ldots$, Cohn–Rajagopal arXiv:2412.00937v3:
  still $40\le\tau_5\le 44$. Did not claim $\tau_5=40$.
- The 240 missed-set seeds on the 40 $D_5$ roots split as 160
  four-seeds and 80 six-seeds. The ten special octads are the
  coordinate-stars $\{x_i=\pm 4\}\cap D_5$. Every four-seed lives in
  exactly one star, as the $2^4$ sign choices on the other four axes
  (`analyze_stars.py`). Independent Rust rebuild (`verify_n1.rs`):
  each star has 16 four-seeds, extras pool 80, $\omega=8$.
- Same-missed extras are edgeless, so a clique takes at most one extra
  per seed. A 41-set with $n_1=40-k$ needs an extras-clique of size
  $k+1$ whose missed sets sit in some $k$-set $U$.
- $n_1=32$ ($k=8$): complete $k$-superset scan, C and Python agree
  ($n_U=7\,407\,770$, 10 promising octads, best extras 8, total 40).
  $n_1=31$ ($k=9$): C empty (`n1_le32_k9.json`).
- Seed-union BFS through $|U|\le 12$ is complete and empty of a 41-set
  (`n1_complete_k12.json`, Python `replay_unions.py`). Promising
  unions only at $k=7$ (80 heptads), $k=8$ (10 stars), $k=11$ (960),
  $k=12$ (4640); each has $\omega=k$, total 40.
- Hash-free canonical DFS (`n1_dfs.c`) continues the same family
  without a table: each union has a unique parent (all but the last
  irredundant seed). Through $k=12$ the counts match the BFS. Through
  $k=18$ the scan is complete and empty of a 41-set
  (`n1_dfs_k18.json`): $933{,}648{,}919$ unions. Promising pools at
  $k=13$ through $18$ have extras $\omega=k$, total 40. Independent
  Python BFS matches the union census through $k=13$
  (`replay_unions_k13.json`). Therefore there is no 41-set that uses
  22 or more $D_5$-type points. The $n_1\le 21$ slice remains residue
  for the whole 1480-graph, not a 41-code.
- 40-colouring of the 1480-graph is UNSAT (Cadical and Glucose). That
  does not produce a 41-clique.
- $T^5$ remainder: no 35-colouring. Cadical and Glucose return no
  36-clique (`t5_omega.json`). UNSAT without a stored DRAT is not an
  emptiness proof. Share $\ge 30$ with each published 35 is empty
  (Python). Share 30 down to 24 are empty in C (`t5_share30_c.json`
  through `t5_share24_c.json`). Any remaining 36-clique shares at most
  23 with every published 35.
- Construction hunts outside these two graphs (other $(1/d)\mathbb Z^5$,
  $A_5$ hyperplane, $D_6$ projections, QR reflections) produced no
  41-code.
- Unrestricted interval unchanged: $40\le\tau_5\le 44$. Did not beat
  Mittelmann–Vallentin. Did not produce a 41-point code.

## 2026-08-27 — continue (q5)

- Start from the q4 branch (`cursor/kissing-5d-q4-cd01`, PR #91 not on
  main). Folder `compute/q5/`. House rules unchanged: do not claim
  $\tau_5=40$; a numerical SDP without an exact positivity certificate
  is residue; do not regress the restricted certificates already in
  `compute/certs/`, `compute/q1/`–`q4/`. Covering stays frozen.
- Hunt: finish the two leftovers (a 41-set in the 1480-graph with
  $n_1\le 21$, or a $T^5$ 36-clique sharing $\le 23$ with every
  published 35), or produce an exact 41-point code, or an exact
  unrestricted dual below 44. Residue if the interval does not move.

## 2026-08-27 — q5 leftovers (interval unchanged so far)

- Re-fetched Tao $C_{29}$, Cohn, Mittelmann–Vallentin
  $s_{14}(5)=44.99899685\ldots$, Cohn–Rajagopal arXiv:2412.00937v3:
  still $40\le\tau_5\le 44$. Did not claim $\tau_5=40$.
- Extra types on the 1480-graph: 160 four-seeds (1 type A
  $(4,2,2,2,2)$ + 4 type B $(5,2,1,1,1)$) and 80 six-seeds (8 type C
  $(3,3,3,2,1)$). A type-A 20-clique exists with $|U|=34$, total 26,
  not a 41-set (`type_a_clique.json`). Type-A leftover hunt
  (`type_a_small_U.json`) is complete: no type-A clique $C$ with
  $|C|\ge 20$ and $|U|\le|C|-1$ (196{,}750 nodes).
- Seed compatibility graph is 240-vertex 231-regular
  (`seed_graph.json`). The 80 six-seeds form an 80-clique of union 40.
  Every 3-star union is leftover-tight: 80 pools $(22,21)$ and 40
  pools $(23,22)$. A seed-clique is a pool, not a 41-code.
- Extras B&B on all 120 three-star pools is complete and empty of a
  leftover 41-set (`triple_star_extras.json`): extras $\omega\le 18$
  on the 80 unions of size 21, $\omega\le 19$ on the 40 unions of
  size 22. With q4's $|U|\le 18$ empty, no 41-set has $U$ contained
  in three coordinate-stars. The leftover $n_1\le 21$ slice, if
  nonempty, has star-cover at least 4.
- Part-count MILP on $|U|\in\{19,20,21\}$ hits cutoff with verified
  incumbents $42,47,50$ contained seeds (`n1_partcount.json`). The
  leftover is not empty by part-count. Cutoff is not a proof of the
  maximum.
- $n_1$ leftover SAT $k=19$ (30{,}678 vars) is running; no model yet.
  Extras B&B 200M nodes: no 41-set, incomplete (`extras_clique.json`).
- $T^5$ remainder: PySAT Cadical195 returns UNSAT for a 36-clique
  (`t5_36_proof.json`, 16{,}548{,}926 proof lines). Heule `drat-trim`
  on that ASCII file ended `s NOT VERIFIED` (no conflict). Native
  CaDiCaL 3.0.1 on the same CNF is UNSAT in 573s (9{,}921{,}324
  conflicts) and writes a 671{,}198{,}215-byte binary DRAT.
  `drat-trim` on that file: `s VERIFIED` (756s; 4{,}787{,}602 of
  10{,}804{,}713 lemmas in core; 0 RAT). There is no 36-clique in
  the 355-point remainder, so the Szöllősi $T^5$ pool has no 41-point
  kissing code. Share 23 is empty as well (`t5_share23.json`):
  $C(35,12)$ neighbourhoods of each published remainder 35 have
  extras $\omega\le 12$ (need 13). Restricted finite-graph facts.
  Not an unrestricted bound.
- No unrestricted dual below 44 (`dual_more.json`: 1-point Delsarte
  still $\approx 46.337$; best certified ansatz $64715/1243\approx 52.06$).
  No 41-code in the finished construction pools (`construct_more.json`).
- Unrestricted interval unchanged: $40\le\tau_5\le 44$. Did not beat
  Mittelmann–Vallentin. Did not produce a 41-point code.

## 2026-08-27 — continue (q6)

- Start from the leftover branch after q5 (`cursor/kissing-5d-q4-cd01`,
  PR #97 merged there). Folder `compute/q6/`. House rules unchanged:
  do not claim $\tau_5=40$; a numerical SDP without an exact positivity
  certificate is residue; covering stays frozen.
- Re-fetched tonight, all still $40\le\tau_5\le 44$:
  Tao $C_{29}$ <https://teorth.github.io/optimizationproblems/constants/29a.html>,
  Cohn table <https://cohn.mit.edu/kissing-numbers/> (dim 5: 40 / 44,
  ratio 1.100, refs [9] and [17]; later-dimension news does not touch
  dim 5),
  Mittelmann–Vallentin arXiv:0902.1105v3 ($s_{14}(5)=44.99899685\ldots$),
  HTML <https://ar5iv.labs.arxiv.org/html/0902.1105v3> Table 1,
  Bachoc–Vallentin arXiv:math/0608426v4,
  Cohn–Rajagopal arXiv:2412.00937v3 (“appears to be 40… best upper
  bound that has been proved is 44”).
- Hunt: empty the leftover $n_1\le 21$ slice of the 1480-point
  $(1/4)\mathbb Z^5$ graph (star-cover $\ge 4$), or produce an explicit
  41-set; in parallel an exact unrestricted dual below 44. Residue if
  the interval does not move.
- First measurement: greedy colouring of extras in every 4-star pool
  (`four_star_color.json`) uses 20 to 32 colours. So the 3-star
  colouring bound $\omega\le 19$ does not lift. Pools are 320 extras
  ($k=28$, two full axes), 384 ($k=27$), or 434 ($k=26$).
- C leftover-tight B&B on all 210 four-star pools is complete and
  empty (`four_star_extras.json`, 26{,}857{,}470 nodes, `best=19`
  is the start value). Independent Python leftover-tight replay of
  38 pools (every $k=28$ two-axis pool and a stride of the rest)
  matches: 38/38 complete empty, no 41-set (`replay_four_star.json`).
  Restricted: no leftover 41-set has $U$ contained in four
  $D_5$ coordinate-stars. Not extras $\omega$, not an unrestricted
  bound. The leftover $n_1\le 21$ slice, if nonempty, has star-cover
  at least 5.
- Minimum $|U|$ with star-cover $\ge 5$ is 5 (`star_cover_min.json`,
  Cadical hitting-set of the 210 four-star complements; witness
  $\{12,15,19,21,28\}$ independently checked). So $|U|=19$ is not
  empty by combinatorics.
- Five-star colouring uses 28 to 39 colours; none $\le 19$
  (`five_star_color.json`). Four $k=32$ five-star C pools hit a 20M
  node cutoff incomplete (`five_star_sample.json`).
- No unrestricted dual below 44 (`dual_more.json`): 1-point Delsarte
  still $\approx 46.33687$; rationalizations fail Sturm; 51 certified
  $(t-1/2)q^2$ ansätze, best $221991/3733\approx 59.47$. Did not beat
  Mittelmann–Vallentin. Did not claim $\tau_5=40$.
- Two-axis leftover SAT: all ten $k=28$ pools are SAT-unsat
  (`two_axis_extras.json`). Nine of ten Python B&Bs were already
  complete empty. SAT-unsat without a stored DRAT is residue for
  those CNFs; the C / leftover-tight Python emptiness is the
  certificate.
- Global leftover-tight extras B&B with the 4-star grow-prune
  (`leftover_global.json`, `n_four_star=210`) ran 200M nodes, no
  41-set, incomplete. Same leftover as q5 extras B&B, plus the prune.
- Leftover-tight SAT on the four $k=32$ five-star pools that hit the
  C 20M cutoff is SAT-unsat (`five_star_sat.json` snapshot). Two
  more pools in that sample were still running. SAT-unsat without
  DRAT is residue.
- Global leftover SAT $k=19$ with star-cover $\ge 5$ (30{,}678 vars,
  Cadical195 and Kissat404 in parallel) had no model after half an
  hour (`leftover_sat_status.json`). Incomplete. Residue, not a
  lower bound.
- Unrestricted interval unchanged: $40\le\tau_5\le 44$. Did not beat
  Mittelmann–Vallentin. Did not produce a 41-point code. Did not
  claim $\tau_5=40$. Residue.

## 2026-08-27 — continue (q7)

- Start from main after PR #101 (`809cdad`). Folder `compute/q7/`.
  House rules unchanged: do not claim $\tau_5=40$; a numerical SDP
  without an exact positivity certificate is residue; covering and
  `share/2026-08-16` stay frozen.
- Re-fetched tonight, all still $40\le\tau_5\le 44$:
  Tao $C_{29}$ <https://teorth.github.io/optimizationproblems/constants/29a.html>
  (range $40\le\tau_5\le 44$, conjectural value 40; upper bound
  Mittelmann–Vallentin),
  Cohn table <https://cohn.mit.edu/kissing-numbers/> (dim 5: 40 / 44,
  ratio 1.100, citations [9] Korkine–Zolotareff and [17]
  Mittelmann–Vallentin; dim 6 is 72 / 77; later-dimension news does
  not touch dim 5),
  Mittelmann–Vallentin arXiv:0902.1105v3
  ($s_{14}(5)=44.99899685\ldots$), HTML
  <https://ar5iv.labs.arxiv.org/html/0902.1105v3> Table 1,
  Bachoc–Vallentin arXiv:math/0608426v4,
  Cohn–Rajagopal arXiv:2412.00937v3 (“the kissing number in five
  dimensions appears to be 40, although the best upper bound that
  has been proved is 44”). Survey arXiv:1507.03631.
- Hunt: empty leftover $|U|=19$ with star-cover at least 5, or empty
  the 5-star leftover hosts (252 pools, three Aut($D_5$) orbits),
  with stored native CaDiCaL DRAT; leftover-tight extras B&B past
  the q6 200M-node cutoff by dropping the $|P|\le 160$ grow cap;
  exact unrestricted dual below 44. Residue if the interval does
  not move.
- Plan: (1) classify 5-star hosts by signed-permutation orbits and
  SAT leftover-tight CNFs on one representative of each type plus
  the four q6 $k=32$ cutoff pools; (2) global leftover SAT $k=19$
  star-cover $\ge 5$ with native CaDiCaL / Kissat; (3) always-on
  grow prune in `leftover_global.c`; (4) one more $(t-1/2)^p q^2$
  dual grid, then drop that line if it stays above 44.
- Signed permutations act transitively on each 5-star type
  (`orbits.json`: 60 of type $(2,1)$ $k=32$, 160 of type $(1,3)$
  $k=31$, 32 of type $(0,5)$ $k=30$; Aut order $3840$).
- Minimum $|U|$ with star-cover $\ge 5$ is 5; with star-cover
  $\ge 6$ is 8 (`star_cover_min.json`). Neither empties $|U|=19$.
- Dual line dropped (`dual_more.json`): 1-point Delsarte still
  $\approx 46.33687$; exact $(t-1/2)^p q^2$ duals that certify sit
  at best $221991/3733\approx 59.47$. Did not beat
  Mittelmann–Vallentin.
- Native leftover-tight SAT on the $k=32$ orbit representative
  (stars $(0,1,2,3,4)$) is UNSAT: CaDiCaL 3.0.1, $1{,}857{,}657$
  conflicts, binary DRAT $211{,}850{,}438$ bytes, Heule
  `drat-trim` `s VERIFIED` (`five_star_sat.json`). Combined with
  Aut transitivity this empties all 60 type-$(2,1)$ five-star
  leftover hosts. The q6 cutoff pool $(0,1,2,3,5)$ is likewise
  UNSAT with a verified DRAT ($3{,}325{,}416$ conflicts).
- All four q6 $k=32$ cutoff pools are UNSAT with verified native
  DRATs (`five_q6_01235`, `five_q6_01236`, `five_q6_01237`, and
  the orbit representative). Combined with Aut transitivity the
  type-$(2,1)$ leftover hosts are empty.
- Leftover-tight extras B&B with always-on grow prune ran 400M
  nodes in about 90 seconds, no 41-set, incomplete
  (`leftover_global_400m.json`). The $|P|\le 160$ cap was the
  cost; remaining missed-union is cheap. With the type-$(2,1)$
  5-star prune (`five_mode=2`) the same search ran $20{,}000{,}000{,}001$
  nodes in $3594$ seconds, no 41-set, incomplete
  (`leftover_global.json`). Past the q6 200M cutoff; still residue.
- $k=31$ leftover-tight SAT is UNSAT with a verified native DRAT
  (`five_k31_n1_3`: $40{,}611{,}860$ conflicts, DRAT
  $4{,}134{,}873{,}401$ bytes, `drat-trim` $15{,}253{,}402$ of
  $46{,}128{,}907$ lemmas, $1{,}635{,}820{,}812$ resolution
  steps). Combined with Aut transitivity this empties all 160
  type-$(1,3)$ five-star leftover hosts. Remaining 5-star leftover
  hosts are the 32 type-$(0,5)$ pools.
- $k=30$ and global leftover SAT $k=19$ are still running. Residue
  until those certificates land. Did not claim $\tau_5=40$.
