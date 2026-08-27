# Line OO — five Abelian zeros of a cubic perturbation

Status: five zeros of $I(h)$, and $H(3)\ge 5$ as a dent of 13,
dropped. Kept: the degree-3 radial slice on the circle
Hamiltonian, and the named family on the cubic Hamiltonian of
a quadratic field. Not a dent of Li–Liu–Yang 13. Planar $H(n)$
did not move.

Imagined: an explicit cubic perturbation of a quadratic
Hamiltonian has five simple zeros of $I(h)$, attaining the
published local max (Han–Yang–Yu).

Two readings, both drop.

If “quadratic Hamiltonian” means $H$ of degree 2, the period
annulus is circles and a degree-3 1-form has
$Z(2,3)=\lfloor(3-1)/2\rfloor=1$. Five is impossible:
$\tilde I(h)=c\,\mu\,h\,p(2h)$ with $\deg p\le 1$ has at most
one positive zero.

If it means a quadratic field that is Hamiltonian ($H$ cubic),
then a cubic perturbation is degree 3 and five zeros of $I(h)$
would be $H(3)\ge 5$, not 14. Still not a dent of
Li–Liu–Yang 13. Scholarpedia records Han–Yang–Yu 2009 as a
local statement: a center of a Hamiltonian quadratic system
generates at most 5 cycles under cubic perturbations. That 5
is not 13, and the named closed forms below do not produce
5 zeros.

Drop immediately. No numeric hunt for 5 zeros. A closed form
that does not produce 5 is a drop, not a search target.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/oo-five-zeros/run.sh
```

Python expands the identities sparsely; Rust expands them
again with a BTreeMap and evaluates the residuals on an
integer box. The two dumps are `diff`ed. Exit 0. Certs:
`certs/core.json`, `certs/identities.json`.

Opened this session:
[Scholarpedia, Han–Li–Li 2010](http://www.scholarpedia.org/article/Limit_cycles_of_planar_polynomial_vector_fields).
Weak Hilbert $Z(2,n)=\lfloor(n-1)/2\rfloor$ because $M(h)$ is
a polynomial; that is the $n=3$ pointer kept below. The same
article says it is proved in Han–Yang–Yu 2009 that a center
of a Hamiltonian quadratic system generates at most 5 limit
cycles under cubic perturbations (their [46],
*Hopf bifurcations for near-Hamiltonian systems*, IJBC 19).
Forum restatements are leads. Li–Liu–Yang 13 is still the
cubic record (full text still paywalled; see RESEARCH.md).

## Dropped — five zeros, and H(3) at least 5 as a dent of 13

A dent of the published cubic record would be a verified
family with more than 13 isolated cubic cycles. Five simple
zeros of $I(h)$ are not that. On the circle reading they
contradict $Z(2,3)=1$. On the cubic-$H$ reading they would
be $H(3)\ge 5$, which does not beat 13. Han–Yang–Yu’s 5 is
a local cyclicity bound at one Hamiltonian quadratic center,
via the expansion of $M$ at that center, not a construction
of 14 and not a beat of Li–Liu–Yang. The imagined five-zero
integral is not written. A numeric search of an elliptic
integral is not a lower bound.

## Kept — circles, degree 3, one positive zero

Take the quadratic Hamiltonian

$$H=\frac{x^2+y^2}{2}.$$

Its Hamiltonian field is $\dot x=y$, $\dot y=-x$. Formal
differentiation gives $d(x^2+y^2)/dt\equiv 0$, so every
regular level $H=h>0$ is a circle $x^2+y^2=2h$. This is
the $n=3$ slice of the radial family already replayed on
line JJ, not a second copy of that folder.

Perturb by $P=0$ and

$$Q=\mu\, y\bigl(\alpha-(x^2+y^2)\bigr).$$

Then $\deg Q=3$. On each oval, $x^2+y^2=2h$ is constant, so

$$I(h)=\mu\,(\alpha-2h)\oint_{H=h} y\,dx.$$

The reduced integral

$$\tilde I(h)=h\,(\alpha-2h)$$

is a polynomial in $Z[h,\alpha]$ with the same zeros on
$h>0$ as $I(h)$. The factor $h$ is the area scaling; it
vanishes only at the equilibrium $h=0$. The positive zeros
are exactly the positive zeros of $\alpha-2h$. For
$\alpha>0$ there is one, at $h=\alpha/2$. For $\alpha=1$,

$$\tilde I(h)=h(1-2h),$$

one positive zero at $h=1/2$. Matches $Z(2,3)=1$. The oval
reduction $(\alpha-x^2-y^2)-(\alpha-2h)=-(x^2+y^2-2h)$ is
the zero remainder.

Here $p(s)=\alpha-s$ has degree 1, so
$\tilde I(h)=h\,p(2h)$ has at most one positive zero. Five
positive zeros would need $\deg p\ge 5$ and
$\deg Q\ge 11$. That is a degree-11 1-form, the $n=11$
attaining example of $Z(2,11)=5$, not a beat of $Z(2,3)$.

## Kept — cubic Hamiltonian, quadratic field, named family

Now read “quadratic Hamiltonian” as a quadratic field that
is Hamiltonian. Take

$$H=\frac{y^2}{2}+\frac{x^3}{3}-\frac{x^2}{2}.$$

The Hamiltonian field is $\dot x=y$, $\dot y=x-x^2$,
degree 2. The certificate uses the cleared polynomial
$H_6=6H=3y^2+2x^3-3x^2$, so every identity stays in
$Z[x,y]$. Formal differentiation gives $dH_6/dt\equiv 0$.

Equilibria of $(y,\,x-x^2)$: $y=0$ and $x(1-x)=0$, hence
$(0,0)$ and $(1,0)$. The Jacobian is

$$\begin{pmatrix}0&1\\1-2x&0\end{pmatrix},$$

trace 0 everywhere, determinant $2x-1$. At $(0,0)$ the
determinant is $-1$ (saddle). At $(1,0)$ it is $1$ (linear
center, frequency $1$). Energy: $H(0,0)=0$ and
$H(1,0)=-1/6$. The potential identity

$$2x^3-3x^2+1=(x-1)^2(2x+1)$$

puts the well bottom at $H=-1/6$ and a second point
$(-1/2,0)$ of the same energy on the unbounded left
component, not a nest oval. The homoclinic through the
saddle is the level $H=0$, with right tip $V(3/2)=0$.
Nest ovals live in $H\in(-1/6,0)$.

Named perturbation, degree at most 3 (in fact linear):

$$P=0,\qquad Q=\mu y.$$

Along the perturbation, $dH/dt=\mu y^2$ and
$dH_6/dt=6\mu y^2$ (block `family`). One-signed for
$\mu\neq 0$: every oval is displaced in the same
direction. The first-order integral is

$$I(h)=\mu\oint_{H=h} y\,dx=\pm\mu\,\mathrm{Area}(\{H\le h\}\cap\mathrm{nest}).$$

Area vanishes only at the well bottom (the oval shrinks
to $(1,0)$). On a regular nest oval the area is positive:
the rectangle $[3/4,5/4]\times[-1/4,1/4]$ sits inside
$\{H_6\le-19/32\}\subset$ nest, because the far corner
is $-19/32<0$, so that one oval already has area at
least $1/4$. Scaling / monotonicity: the nest sublevels
are nested, so Area is strictly increasing from $0$ at
$h=-1/6$ to the homoclinic area at $h=0$. Thus $I$ has
no zero on the open period interval. After the shift
$\hat h=h+1/6\ge 0$, that is no positive zero, or exactly
the well-bottom zero $\hat h=0$. First-order cyclicity of
this family is at most 1, not 5. Regular zeros exhibited
on the nest: 0. The named field after perturbation is
still degree 2 ($\dot y=x-x^2+\mu y$), so it is not an
$H(3)$ construction in any case.

## What this is not

Not a dent of $Z(2,3)$. Not a dent of $H(3)$ or $H(n)$.
Not five zeros of an Abelian integral. Not a beat of
Han–Yang–Yu’s local 5, and not a replay of their
expansion of $M$ at a general quadratic Hamiltonian
center. Not a numeric search. The reusable lemmas are
the $n=3$ radial identity $\tilde I(h)=h(\alpha-2h)$ and
the one-signed $dH/dt=\mu y^2$ on the cubic Hamiltonian
nest. A stranger can run `run.sh` and read one circle
zero and zero regular nest zeros off the dump.
