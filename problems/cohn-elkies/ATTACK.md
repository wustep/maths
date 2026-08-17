# Attack log — Exact Cohn–Elkies certificate, planar packing

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House rules: write only here; no git; cite what we beat; floating-point LP without exact coefficients is residue.
- Green 100 #42 (Dec 2025 update of `open-problems.pdf`, fetched tonight from https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf): *Can the Cohn–Elkies scheme be used to prove the optimal bound for circle-packings?* Comments: CE conjectured sharpness in dimensions 1, 2, 8, 24; proved for d=1; Viazovska d=8; Cohn–Kumar–Miller–Radchenko–Viazovska d=24. The case d=2 is the remaining magic-function problem. Green writes it as: a radial admissible f : R² → R with f(x) ≤ 0 for |x| ≥ 2, ˆf ≥ 0 everywhere, ˆf(0) > 0, and f(0)/ˆf(0) = √3/6. Related discussion: Sardari, arXiv:2102.08753 ([274] in Green).
- Cohn–Elkies 2003 (Annals 157, 689–714; arXiv:math/0110009), fetched tonight:
  - Theorem 3.1 / 3.2 is the LP scheme.
  - Conjecture 7.3: there exist functions solving the packing problem in dimensions 2, 8, 24.
  - Numerical method (§7): odd/even Laguerre–Gaussian eigenfunctions, m forced double roots, last sign change r, exact rational arithmetic + Sturm. For n=2 they use m=5.
  - Table 3, n=2: best packing 0.28868, new upper bound 0.28868 (center density). That is the hexagonal value 1/(2√3) = √3/6 printed to five decimals.
  - Table 4, n=2: 2π r² = 7.25520 and forced double roots 21.77, 29.02, 50.79, 65.34, 90.19. They do **not** print the Laguerre coefficients. They say 2π z_i² are taken rational and 2π r² is a nearby rational slightly larger than the true last sign change.
- Hexagonal target in Theorem 3.2 normalisation: 2π r² = 4π/√3 ≈ 7.255197456936. The printed 7.25520 is already a 3.5·10⁻⁷ relative excess.
- Status tonight (literature screen, not a claim of completeness):
  - Viazovska / CKMRV solve d=8,24. Nobody claims a magic function for d=2.
  - Sardari (arXiv:2102.08753) proves a Fourier interpolation formula on the A2 nodes and settles CKMRV Conjecture 7.5; it does not produce the CE auxiliary function.
  - Mo–Wen–Xia (arXiv:2410.04800v2) write down a *periodic* trigonometric polynomial on R²/2A2 matching the hexagonal ratio. That is not an admissible function on R², and they explicitly leave the CE-SA function open.
  - Jumagulov (arXiv:2607.11319, Jul 2026) and Salmon (arXiv:2607.25254) still call the planar magic function unknown. Salmon: “no sharp planar magic function is known.”
  - Dual-LP work (Cohn–Triantafillou, Li 2022) shows the CE bound is *not* sharp in dimensions 3–7, 12, 16; d=2 is not on that list.
- Tonight’s quest, as written: an exact admissible function whose Fourier sign conditions can be independently checked, meeting or beating a **published** Cohn–Elkies ratio. The published d=2 CE number is Table 3’s 0.28868 (equivalently Table 4’s 2π r² = 7.25520). Reconstructing CE’s Laguerre method over Q, with a Sturm verifier, is the finite handle. A float LP dump is residue.

## 2026-08-17 — first false start: treat Mo–Wen–Xia g₂ as a CE certificate

- Their Proposition 3.8 is a 4-term cosine sum, periodic modulo 2A2, with g₂# = √3/2. That lives in their SSA class, not in CE’s SA. Poisson summation on R² does not apply. Abandoned as a claimed dent.

## 2026-08-17 — second false start: chase a closed modular-form magic function

- The d=8,24 proofs use integral transforms of (quasi)modular forms. The d=2 analogue is Green’s problem, and Sardari’s interpolation is the documented obstruction: the A2 node set does not determine a radial Schwartz function from first-derivative data. A one-night modular-form hunt is not a certificate. Abandoned as the main line.

## 2026-08-17 — the working line: exact CE Laguerre–Gaussians

- Reproduce §7 over Q. Radial Fourier eigenfunctions in dimension 2:
  g_k(x) = L_k(2π |x|²) exp(−π |x|²), ˆg_k = (−1)^k g_k.
- Odd combination G of {L_1, L_3, …, L_{4m+3}} with G(0)=0 and m double roots at rational t_i = 2π z_i². Even combination H of {L_0, …, L_{4m+2}} with the same double roots and a double root of G+H at a rational R ≥ last sign change of G.
- Then f = (−G+H) exp(−π |x|²) and ˆf = (G+H) exp(−π |x|²). Sign conditions reduce to Sturm queries on two polynomials in Q[t]. Theorem 3.2 gives center density ≤ R/(8π).
- Published comparison points (recomputed tonight, `compute/CONSTANTS.md`):
  - Levenshtein / CE Proposition 6.1: δ ≤ j_1²/(16π) = 0.292088525253…, ratio 1.01182433….
  - CE Table 3: 0.28868 (ratio 1.00000 at five decimals). Met by any certified R ≤ 7.25545.
  - CE Table 4: R = 7.25520 ⇒ δ ≤ 0.28867523578…, ratio 1.0000003505….
  - Hexagonal: R_* = 4π/√3. We will not claim a function with R = R_*.

## 2026-08-17 — third false start: float SVD of the raw Laguerre matrix

- High-degree `L_k(t)` at `t ≈ 90` is `10^18`. The `G(0)=∑ a_j` row is lost. Float kernel of the unscaled matrix is not a kernel. Exact Q linear algebra is mandatory even for discovery.

## 2026-08-17 — fourth false start: Sturm on the unreduced degree-23 `hatF`

- `hatF` has 1835-bit coefficients and five forced double roots plus a double root at `R`. Naive `sqf_part` / Sturm hung. Useless as a verifier.

## 2026-08-17 — the click

- Divide first. `G` vanishes simply at `0` and at the last sign-change, and doubly at the five Table-4 nodes. `hatF = (t-R)^2 ∏(t-t_i)^2 S(t)` and `F = ∏(t-t_i)^2 P(t)` are exact divisions in `Q[t]`. `S` has degree 11, `P` degree 13. `count_roots` on those two quotients finishes in seconds.
- The two-decimal Table-4 nodes already place the last odd root of `G` in
  `(1267758233/174737932, 878736008/121118135) ≈ (7.2551976464961250, 7.2551976464961259)`,
  just above `4π/√3 ≈ 7.255197456936871`. The printed `7.25520` is a coarse upward rounding of that isolation.

## 2026-08-17 — certificate

- `compute/make_certificate.py` builds `G,H` over `Q` from
  `t_i ∈ {2177/100, 2902/100, 5079/100, 6534/100, 9019/100}`
  and `R = 3627599/500000 = 7.255198`.
- `compute/verify.py` rebuilds `G,H` from the stored Laguerre coefficients (does not re-solve the interpolation system) and replays the divisions + `count_roots`. Exit 0.
- Theorem 3.2 bound:
  - `δ ≤ R/(8π) = 0.2886751562026082…`
  - ratio vs hex `= 1.0000000748515987…`
- Published comparisons (independently recomputed):
  - Meets CE Table 3 printed `0.28868`.
  - Strictly below CE Table 4 printed `R = 7.25520` (their implied ratio `1.0000003505…`).
  - Beats Levenshtein `1.01182…` by a mile, as expected: this is their improved ansatz, not the compactly-supported Bessel function.
- Replay: `compute/run_all.sh`.
- What this does **not** do: produce a magic function with `R = 4π/√3`; vanish on every later A2 shell; prove Green #42.

## Published record we compare against

- Best published *printed* Cohn–Elkies d=2 ratio in the 2003 paper: Table 3 lists `0.28868/0.28868 = 1` at five decimals; Table 4 prints `2πr² = 7.25520`, which is a ratio `1.0000003505…`.
- Best published *exact closed-form* CE-scheme bound in d=2: Levenshtein / CE Prop. 6.1, ratio `1.01182433…`.
- No later source fetched tonight prints an exact d=2 admissible polynomial (with coefficients) beating `7.25520`. Mo–Wen–Xia 2024 is periodic, not admissible on `R²`. Viazovska / CKMRV are d=8,24. Dual-LP papers do not give a primal d=2 function.

The dent is the exact function, independently checkable, meeting Table 3 and beating the printed Table 4 `R`. It is not a solution of Green #42.
