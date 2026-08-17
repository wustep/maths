# Research log — Exact Cohn–Elkies certificate for planar packing

## 2026-08-17

- [Ben Green, *100 Open Problems*, Problem 42](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf) (Dec 2025 update, fetched tonight). Statement: can the Cohn–Elkies scheme prove the optimal circle-packing bound? Comments: sharpness conjectured in dimensions 1, 2, 8, 24; d=1 elementary; d=8 Viazovska; d=24 Cohn–Kumar–Miller–Radchenko–Viazovska. The d=2 case is written as a radial admissible `f : R² → R` with `f ≤ 0` for `|x| ≥ 2`, `ˆf ≥ 0`, `ˆf(0) > 0`, and `f(0)/ˆf(0) = √3/6`. Related discussion: [274] = Sardari.
- [Cohn and Elkies, *New upper bounds on sphere packings I*, Ann. of Math. 157 (2003), 689–714](https://doi.org/10.4007/annals.2003.157.689), arXiv:[math/0110009](https://arxiv.org/abs/math/0110009). Fetched tonight (arXiv v3 and the Annals PDF). Theorem 3.1 / 3.2 is the LP scheme. §7 is the Laguerre–Gaussian method with exact rational arithmetic and Sturm. Conjecture 7.3: magic functions exist in dimensions 2, 8, 24. Table 3, n=2: packing and bound both printed `0.28868`. Table 4, n=2: `2πr² = 7.25520` and five forced double roots `21.77, 29.02, 50.79, 65.34, 90.19`. Coefficients are not printed.
- [Cohn, *New upper bounds on sphere packings II*, Geom. Topol. 6 (2002), 329–353](https://arxiv.org/abs/math/0110010). Theta-series derivation of Theorem 3.1; no extra d=2 function.
- [Sardari, *Higher Fourier interpolation on the plane*, arXiv:2102.08753](https://arxiv.org/abs/2102.08753). Green’s [274]. Interpolation formulas on A2-type nodes; proves CKMRV Conjecture 7.5. Does not produce a CE auxiliary function.
- [Viazovska, *The sphere packing problem in dimension 8*, Ann. of Math. 185 (2017)](https://doi.org/10.4007/annals.2017.185.3.7). Magic function in d=8.
- [Cohn, Kumar, Miller, Radchenko, Viazovska, *The sphere packing problem in dimension 24*, Ann. of Math. 185 (2017)](https://doi.org/10.4007/annals.2017.185.3.8). Magic function in d=24.
- [Cohn, *From sphere packing to Fourier interpolation*, Bull. Amer. Math. Soc. 61 (2024), 3–22](https://arxiv.org/abs/2407.14999). Survey. d=2 remains the open magic-function case among `{1,2,8,24}`.
- [Mo, Wen, Xia, *A new linear programming method in sphere packing*, arXiv:2410.04800v2](https://arxiv.org/abs/2410.04800). Periodic trigonometric polynomials on `R²/2A2`. Their `g₂` is not an admissible function on `R²`. They leave the CE-SA function open.
- [Li, *Dual linear programming bounds for sphere packing*, arXiv:2206.09876](https://arxiv.org/abs/2206.09876). Dual bounds show the CE LP is not sharp in dimensions 3–7 and several higher dimensions. d=2 is not on the non-sharpness list.
- [Jumagulov, *A dual linear programming bound for sphere packing in dimension 36*, arXiv:2607.11319](https://arxiv.org/abs/2607.11319) (Jul 2026). Still treats the planar magic function as unknown; dual work is about high-dimensional *lower* bounds on `δ_LP`.
- [Salmon, *Linear programming bounds for fibered sphere packings*, arXiv:2607.25254](https://arxiv.org/abs/2607.25254). Quote: “no sharp planar magic function is known.” Conjecture 17 is exactly Green #42.
- [Gonçalves, Oliveira e Silva, Steinerberger / related sign-uncertainty papers](https://arxiv.org/abs/2003.10771). Record the CE conjecture `A_LP(2) = (4/3)^{1/4}`, equivalent to `2πr² = 4π/√3` in Theorem 3.2 normalisation.
- Henry Cohn’s sphere-packing page, <https://cohn.mit.edu/sphere-packing/>, fetched tonight: no downloadable d=2 magic function or updated exact primal certificate.

No source fetched tonight prints an exact admissible d=2 polynomial (with coefficients) that we failed to meet. The 2003 paper is the published primal record we compare against.

## Normalisations used

- Fourier transform: `ˆf(t) = ∫ f(x) e^{2πi ⟨x,t⟩} dx` (Cohn–Elkies).
- `t = 2π |x|²`. Radial eigenfunctions `g_k(x) = L_k(t) exp(−π |x|²)`, `ˆg_k = (−1)^k g_k`.
- Theorem 3.2: if `f(0)=ˆf(0)>0`, `f ≤ 0` for `|x| ≥ r`, `ˆf ≥ 0`, then center density `δ ≤ (r/2)^n`. For `n=2` this is `δ ≤ R/(8π)` with `R = 2π r²`.
- Green’s `|x| ≥ 2` form is the same bound after a factor-of-two rescaling: `δ ≤ f(0)/ˆf(0)`.
