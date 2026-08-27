# Lieb–Thirring constants (Simon 2000 #15)

- Slug: `simon-lieb-thirring`
- List: Simon 2000 #15
- Solver: Grok 4.6
- Status: open
- Area: Spectral theory / semiclassical inequalities
- Sources: Simon, *Mathematical Physics 2000*, pp. 283–288; Frank–Hundertmark–Jex–Nam arXiv:1808.09017 / *J. Eur. Math. Soc.* 23 (2021); Schimmer arXiv:2203.06051; Frank arXiv:2007.09326
- Started: 2026-08-27

## Statement

For a Schrödinger operator −Δ+V on L² of Euclidean space of dimension d,
write e_j(V) for the negative eigenvalues. The Lieb–Thirring constant
L(γ,d) is the smallest number such that the sum of |e_j(V)|^γ is at most
L(γ,d) times the integral of V_− to the power γ+d/2, whenever that
integral is finite. Here γ ≥ 1/2 in dimension 1, and γ ≥ 0 in dimension
at least 2. Two comparison constants are computable: the semiclassical
(phase-space) value Lcl(γ,d) and the one-bound-state / Sobolev value
L1(γ,d). Lieb and Thirring conjectured that L(γ,d) equals the max of
those two.

In dimension 1 that maximum is the one-bound-state constant on
1/2 ≤ γ ≤ 3/2 and the classical constant for γ ≥ 3/2. Simon's #15
asks for the remaining one-dimensional slot 1/2 < γ < 3/2.

The conjecture is known at the endpoints of that slot and above it.
Hundertmark–Lieb–Thomas give L(1/2,1) = 1/2 = L1(1/2,1).
Laptev–Weidl (after Aizenman–Lieb) give L(γ,d) = Lcl(γ,d) for every
dimension once γ ≥ 3/2. The open interval is the ask.

## Published record

Fetched and read this session (see RESEARCH.md). The best published
upper bound on the physically central case γ = 1 is

$$
L_{1,d}/L^{\mathrm{cl}}_{1,d}\le 1.456
$$

for every dimension d ≥ 1 (Frank–Hundertmark–Jex–Nam, arXiv:1808.09017,
*J. Eur. Math. Soc.* 23 (2021), 2583–2600, Theorem 1). The same paper
records the finer ratio 1.455786 coming from K1 / Kcl ≥ 0.471851.
The one-dimensional conjecture at γ = 1 would be the one-bound-state
ratio 2/√3 ≈ 1.1547.

Schimmer, arXiv:2203.06051 (Lieb 90th-birthday survey; this is the
paper at the id sometimes labelled as a Frank survey), and Frank,
arXiv:2007.09326, both still treat 1/2 < γ < 3/2 in dimension 1 as
open, and both still quote 1.456 as the best ratio for 1 ≤ γ < 3/2.
Aizenman–Lieb lifting extends the γ = 1 bound through that range.
No later paper opened this session improves 1.456.

The classical constant used for comparison is

$$
L^{\mathrm{cl}}_{\gamma,d}=2^{-d}\pi^{-d/2}\Gamma(\gamma+1)/\Gamma(\gamma+1+d/2).
$$

Independently recomputed values (compute/): Lcl(1,1) = 2/(3π) and
Lcl(3/2,1) = 3/16, matching the surveys.

## What would count as a new bound

A verified finite improvement of a documented record. Success is one of:

**(A)** A proof, or a checkable analytic certificate, that the ratio
L(1,d)/Lcl(1,d) is strictly smaller than 1.456 for some d ≥ 1, citing
Frank–Hundertmark–Jex–Nam as the beaten number.

**(B)** The conjecture in some open slot: L(γ,1) = L1(γ,1) for a
fixed γ in (1/2, 3/2), or L(1,d) equal to the conjectured max of
classical and one-bound-state constants.

**(C)** Any other published L(γ,d) strictly improved, with the paper
being compared opened and the new number independently checked.

A numerical Lieb–Thirring ratio for a handful of potentials is a
lower bound on L(γ,d) and is not an upper-bound improvement.
Replaying 1.456, or the classical Gamma formula, is not a new bound.
The full conjecture is not claimed by a finite table.
