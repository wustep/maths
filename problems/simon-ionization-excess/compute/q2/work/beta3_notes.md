# β_3^{rad} leading coefficient

Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, Proposition 4.5:
β_3 ≥ min_t f(t) = 1/b(3) ≈ 0.894107, with f(t)=(1+t^3)/(1+t^2) and
b(3)<1.1185. Figure 2 says this is not sharp: power-law trials sit
about 3% below b(3). A certified γ > 1/b(3) is a new leading
coefficient in the same §5–§7 chain.

## Numerical target (upper bounds on β_3)

Replay: `explore_beta3.py`. These are the wrong direction for an
ionization *upper* bound.

- Power law m(dr) ∝ r^α dr on [1,n], HPS 3D density A|x|^{-p} with
  α=2-p. Best at α≈−2, n≈3.50, p≈4: I/D ≈ 0.920655, so
  β_3^{-1} ≈ 1.08618 (2.88% below b(3)=1.11843). Matches Figure 2.
- k-atomic: 1.000, 0.9433, 0.9310, 0.9265, 0.9244, 0.9232 for
  k=1…6, decreasing toward the power law.
- Piecewise-constant log-grid: I/D ≈ 0.921.

Apparent inf of β_3^{-1} ≈ 1.086. Apparent inf of β_3 ≈ 0.921.

b(s) for s>3 (what a theorem for s>3 would be worth):

- s=3.1: b≈1.11358
- s=3.5: b≈1.09761
- s=4:   b≈1.08302
- s=5:   b≈1.06393

s>3 is worth about 0.5–5% on the leading coefficient if radialization
survives. The two-shell dipole in `s_gt_3.py` makes I_s negative for
every s>3, so that path is closed.

## Certified lower bound

Scale so D=∫ r^2 dm = 1. Split (0,∞) at α=R^{-1/2} and 1/α, R=12.
The middle window scales to [1,12].

On a geometric n=26 grid, replace f by its minimum on each bin-pair
(unimodal: decreasing on [0,t_0], increasing on [t_0,1]). The
mid-radius Rayleigh φ(m)=(m^T A m)/(c·m) with
A_{ij}=F_{ij}(r_i^{*2}+r_j^{*2})/2, c_i=r_i^{*2} then differs from
the true F-average by at most [θ/(1-θ)](1-min f), θ=R^{1/n}−1,
because the D-weights ρ_i/r_i^{*2} lie in [1/q,q].

φ ≥ γ_target is equivalent to m^T M m ≥ 0 on the simplex,
M=A−γ_target(c 1^T+1 c^T)/2. Exhaustive face enumeration
(`verify_beta3.c`) finds every interior critical point (including
all-negative Lagrange vectors) and every vertex.

The tail polynomial h(D_L,D_R) lower-bounds I for D=1 after dropping
only nonnegative remainders. For a=1/12 and β≤0.896 the interval
minimum of h on the triangle is at the origin and equals β, so the
middle bound lifts to every Borel probability with finite D.

C face enumeration at γ_target=0.9072 (n=26, 2^{26}−1 faces):
min mᵀMm = 4.219×10^{-3}>0, so φ_mid≥0.9072. Interval error
err≤0.0118036978898114. Therefore

  γ ≥ 0.9072 − err ≥ 0.895396302110

and γ^{-1} ≤ 1.11682391099 < 1.1185, also strictly below the
exact b(3)∈(1.1184,1.1185). The tail polynomial’s minimum on
the (D_L,D_R) triangle sits at the origin and equals this γ,
so the middle bound lifts to every Borel probability with
finite D. Replay: `certs/beta3_rad.json`.

Independent second path: `verify_beta3.rs` rebuilds F and the
16-bin [1,4] Rayleigh from scratch (Gauss–Jordan plus Cramer
on 3-faces, residual rejected). That compact-support window
already beats 1/b(3) after the same mid-radius error, which is
a method check, not the production global bound.

## What is not claimed

The numerical 1.086 is not a lower bound on β_3^{-1}. The certified
γ is a lower bound on β_3, hence an *upper* bound on the ionization
coefficient. Remainder constants in HPS §7 are not recomputed here.
s>3 remains open.
