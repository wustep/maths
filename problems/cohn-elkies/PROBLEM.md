# Exact Cohn–Elkies certificate for planar circle packing

- Slug: `cohn-elkies`
- List: P27
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Sphere packing / Fourier analysis
- Sources: Green 100 #42; Cohn–Elkies Annals 2003
- Started: 2026-08-17

## Statement

It is unknown whether the Cohn–Elkies linear-programming scheme itself can attain the sharp hexagonal circle-packing density in dimension 2: equivalently, whether an exact admissible auxiliary function with the required optimal ratio exists.

## Tonight

An exact admissible function (algebraic coefficients, independently checkable Fourier sign conditions) that meets or strictly improves a published Cohn–Elkies ratio, or a documented obstruction. Numerical LP output without exact certificates is an incomplete search. Fetch Green #42 and Cohn–Elkies before searching.

## Outcome (2026-08-17)

Exact Laguerre–Gaussian certificate in `compute/certs/ce_d2_m5.json`, replay `compute/verify.py`.

`R = 3627599/500000 = 7.255198` gives center density `≤ R/(8π) ≈ 0.28867515620`, ratio `1.00000007485` against hexagonal `√3/6`. Meets Cohn–Elkies 2003 Table 3 (`0.28868`) and is strictly below the printed Table 4 value `2πr² = 7.25520`. Not a magic function; Green #42 remains open.
