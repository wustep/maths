# Line HH — first Melnikov on the quasi-homogeneous center

Status: 14 zeros of I(h), and the H(3) beat, dropped. Scaling
and first-order cyclicity at most 1 for a named cubic family
kept. Not a dent of H(3).

Imagined: a cubic (or degree-4) perturbation of the
quasi-homogeneous center ẋ = 2y, ẏ = −x³ has 14 isolated
zeros of the first Melnikov function I(h) on the period
annulus H = x⁴ + 4y², hence H(3) ≥ 14.

Drop immediately. The unperturbed degree is already 3.
A cubic perturbation stays in degree 3, so 14 zeros would
be a dent of Li–Liu–Yang’s H(3) ≥ 13. Scaling on this
annulus forbids it. For any cubic perturbation the first
Melnikov function is of the form

$$I(h)=h^{3/4}\bigl(c_0+c_1\sqrt{h}+c_2 h\bigr),$$

which has at most two positive zeros. The named one-parameter
family below has c₂ = 0 and at most one. Gavrilov–He–Xiao,
arXiv:2606.22137v1, already bound the zeros of every Melnikov
order for one-parameter polynomial perturbations of a
quasi-homogeneous center; their §5 application is this same
annulus (H = x⁴/4 + y²/2, a constant multiple of ours after
rescaling y) and concludes cyclicity one for a linear
unfolding. This line does not beat that paper, and it does
not beat H(3) ≥ 13.

Replay:

```
problems/hilbert16-limit-cycles/compute/q3/hh-qh-melnikov/run.sh
```

Python expands the identities sparsely; Rust expands them
again and evaluates the residuals on an integer box. The two
dumps are `diff`ed. Exit 0. Cert: `certs/identities.json`.

Opened this session: the abs and HTML of
Gavrilov–He–Xiao, arXiv:2606.22137v1.

## Dropped — 14 zeros, and H(3) at least 14

The fiction needs fourteen isolated zeros of I(h), or some
other construction of fourteen isolated cubic cycles. First
order on this single annulus cannot supply them. A quadratic
in √h has at most two positive roots. Higher-order Melnikov
functions are a different problem; Gavrilov–He–Xiao already
treat that unfolding and do not produce 14. Li–Liu–Yang’s 13
is still the published cubic record (full text still
paywalled; see RESEARCH.md). This line does not invent a
14-cycle cubic.

## Kept — unperturbed field, degenerate center, period annulus

The field ẋ = 2y, ẏ = −x³ is Hamiltonian for

$$H=x^4+4y^2$$

(equal to 4 times x⁴/4 + y²). Formal differentiation gives
dH/dt ≡ 0 (certificate block `unperturbed`). The only
equilibrium is the origin: 2y = 0 and −x³ = 0 force (x, y) =
(0, 0). The identity Q₀² + (P₀/2)² = x⁶ + y² is a sum of
even powers and vanishes only there.

The linearization at the origin is ẋ = 2y, ẏ = 0. The
Jacobian is [[0, 2], [0, 0]]: trace 0, determinant 0,
characteristic polynomial t². This is not a linear center.
It is a nilpotent / degenerate quasi-homogeneous center.
The Hessian of H at the origin is [[0, 0], [0, 8]], also
degenerate.

Regular levels H = h > 0 are compact ovals. H vanishes only
at the origin, H → +∞ at infinity, and ∇H = (4x³, 8y)
vanishes only at the origin, so those ovals are smooth. Each
is a periodic orbit. A continuum; the unperturbed field has
zero isolated cycles. This is the unperturbed half already
kept on line F, recorded again because the Melnikov count
sits on it.

The same field is quasi-homogeneous of weighted degree 2 for
weights (1, 2):

$$P_0(\lambda x,\lambda^2 y)=\lambda^2 P_0,\qquad
Q_0(\lambda x,\lambda^2 y)=\lambda^3 Q_0,\qquad
H(\lambda x,\lambda^2 y)=\lambda^4 H.$$

Each level H = c maps to the distinct level H = λ⁴ c
(block `weight`).

## Kept — first Melnikov formula

Perturb by a polynomial field of degree at most 3:

$$\dot x=2y+\varepsilon P,\qquad \dot y=-x^3+\varepsilon Q.$$

The first Melnikov function used here is

$$I(h)=\oint_{H=h}Q\,dx-P\,dy.$$

That is the standard line integral of the perturbation
1-form ω = Q dx − P dy, matching Gavrilov–He–Xiao’s ωᵢ.
Green’s theorem, counterclockwise, rewrites it as a
divergence integral on the disk H ≤ h:

$$I(h)=-\iint_{H\le h}(P_x+Q_y)\,dx\,dy.$$

The energy increment along the unperturbed orbit is a
constant multiple of the same integral. Along the
unperturbed field, dt = dx / (2y) and

$$\nabla H\cdot(P,Q)=4x^3 P+8y Q.$$

When P = 0 this collapses by the polynomial identity
(8y Q)/(2y) = 4Q (cleared: 8y Q − 8y Q ≡ 0), so

$$\oint\nabla H\cdot(P,Q)\,dt=4\oint Q\,dx=4I(h).$$

Zeros of I and of the first-order energy increment coincide.
The factor 4 is recorded; it is not a new parameter.

## Kept — Q = μ y produces no positive zero

Take P = 0, Q = μ y. Then I(h) = μ ∮ y dx. Green gives
∮ y dx = −A(h), where A(h) is the area of {H ≤ h}. The
change of variables x = h^{1/4} s, y = (√h / 2) t has
Jacobian (1/2) h^{3/4} and sends the disk to s⁴ + t² ≤ 1.
That model region has area

$$4\int_0^1\sqrt{1-s^4}\,ds=B\bigl(\tfrac14,\tfrac32\bigr)
=\frac{\Gamma(1/4)\Gamma(3/2)}{\Gamma(7/4)},$$

so

$$A(h)=\tfrac12 h^{3/4}\,B\bigl(\tfrac14,\tfrac32\bigr).$$

(The factor is 1/2, not 2: Jacobian (1/2) h^{3/4} times
Beta, not four times Beta.) Hence

$$I(h)=-\mu A(h)=-\frac{\mu}{2}B\bigl(\tfrac14,\tfrac32\bigr)\,h^{3/4}.$$

This is monotone in h and vanishes only at h = 0. There is
no positive zero. First-order Melnikov predicts no limit
cycle from this perturbation: dH/dt = 8μ y² is one-signed
for μ ≠ 0, so every oval is displaced in the same direction.
The verifier does not call Gamma or Beta. It certifies the
scaling A(λ⁴) = λ³ A(1) from the Jacobian identity, and
that A(1) ≠ 0 by a rectangle sitting inside s⁴ + 4u² ≤ 1
(corner 5/16 < 1).

A cousin with no y-factor, Q = μ(a + b x² + c y) and P = 0,
is no better. The 1-forms dx and x² dx are exact, so
∮ dx = ∮ x² dx = 0 and I(h) = μ c ∮ y dx, again either
identically zero or never zero.

## Kept — named family, scaling law, cyclicity at most 1

Named family, still degree 3:

$$P=0,\qquad Q=\mu(\alpha-x^2)y.$$

Then div(P, Q) = μ(α − x²) and

$$I(h)=\mu\bigl(\alpha J_0(h)-J_2(h)\bigr)
=-\mu\bigl(\alpha M_0(h)-M_2(h)\bigr),$$

where Jₖ(h) = ∮ xᵏ y dx and Mₖ(h) = ∬_{H≤h} xᵏ dx dy,
so Jₖ = −Mₖ. The extra term in dH/dt is the polynomial
8μ(α − x²) y² (block `family`).

Scaling, with x = λ s, y = λ² u and h = λ⁴: the chart
identity is H(λs, λ²u) = λ⁴(s⁴ + 4u²), and the Jacobian
determinant is λ³ (block `scale`). The integrand xᵏ times
that Jacobian is λ^{k+3} sᵏ. Therefore

$$M_k(\lambda^4)=\lambda^{k+3}M_k(1).$$

In particular M₀(h) scales as h^{3/4} and M₂(h) as h^{5/4},
so the ratio is a constant times a square root:

$$\frac{J_2(h)}{J_0(h)}=\frac{M_2(h)}{M_0(h)}=C\sqrt{h},\qquad
C=\frac{M_2(1)}{M_0(1)}=\frac{B(3/4,3/2)}{B(1/4,3/2)}.$$

The constant C is positive: the rectangle
[1/2, 3/4] × [0, 1/8] lies in s⁴ + 4u² ≤ 1 because the far
corner is 97/256 < 1, and s² ≥ 1/4 there, so M₂(1) ≠ 0;
the area rectangle [0, 1/2] × [0, 1/4] has far corner
5/16 < 1, so M₀(1) ≠ 0. The verifier checks those two
rational comparisons and the monotonicity derivatives
4s³ and 2u. It does not evaluate C.

Thus I(h) = 0 if and only if α = C √h. For fixed α that is
at most one h > 0 (none if α ≤ 0). The first-order
Melnikov function of this family is not identically zero
unless μ = 0, because J₂/J₀ is not constant. First-order
cyclicity of the period annulus, for this named family, is
at most 1. That is a certified upper bound for the family,
not a bound on H(3).

The same scaling, applied to a general cubic (P, Q), keeps
only three even moments of the quadratic divergence:
∬ 1, ∬ x², and ∬ y² (the region is symmetric in x and in
y; odd monomials integrate to zero). Those scale as
λ³, λ⁵, and λ⁷, so

$$I(h)=h^{3/4}\bigl(c_0+c_1\sqrt{h}+c_2 h\bigr)$$

and a general cubic has at most two positive zeros of I at
first order. The named family is the slice c₂ = 0.

## What this is not

Not a bound on H(3). Not fourteen zeros of I(h). Not a beat
of Gavrilov–He–Xiao’s application (they get cyclicity one
for a linear unfolding of this annulus; we get at most one
at first order for one cubic family). Not a closed-form
evaluation of the Beta values in the verifier — those sit
in this note as a closed form, and the replay is the
scaling exponents and the two rectangle inclusions. A
stranger can run `run.sh` and read the exponents 3, 5, 2
and the cyclicity 1 off the dump.
