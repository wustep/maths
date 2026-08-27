# Line JJ — weak Hilbert number on a quadratic period annulus

Status: beat-the-formula dent dropped. Kept as a replay of the
published $Z(2,n)$. Planar $H(n)$ did not move. This is the
cyclicity of one Hamiltonian period annulus, not a dent of $H(2)$.

Imagined: an explicit Abelian integral with
$\lfloor(n-1)/2\rfloor+1$ real zeros on the period interval,
beating Scholarpedia / Han–Li–Li 2010.

Dropped: that formula is a theorem, not a conjecture. $M(h)$ is
a polynomial, so the count cannot be beaten.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/jj-weak-hilbert/run.sh
```

Python expands the Hamiltonian identity, the oval reduction, and
the reduced integral $\tilde I(h)=h\,p(2h)$ as sparse monomials.
Rust expands the same rings with a BTreeMap and evaluates the
residuals on an integer box. The two dumps are `diff`ed. Exit 0.
Cert: `certs/family.json`.

Opened this session:
[Scholarpedia, Han–Li–Li 2010](http://www.scholarpedia.org/article/Limit_cycles_of_planar_polynomial_vector_fields).
Weak Hilbert $Z(m,n)$ is the maximum number of isolated zeros of
the first Melnikov function

$$M(h)=\oint_{L_h}P\,dy-Q\,dx$$

over polynomial Hamiltonians of degree $m$ and polynomial
perturbations of degree $n$. The article states that
$Z(2,n)=\lfloor(n-1)/2\rfloor$ because $M(h)$ is a polynomial.
That is the record replayed here. Forum restatements are leads.

## Dropped — one more zero than the formula

A dent would be a verified family with
$\lfloor(n-1)/2\rfloor+1$ isolated zeros of $M(h)$ on the period
interval. For a quadratic Hamiltonian the first-order integral is
a polynomial (times a density that does not vanish for $h>0$).
A polynomial of that degree cannot have more real zeros than the
published count. The imagined extra zero is not a search target;
it contradicts the theorem. The formula was not beaten.

## Kept — $H=(x^2+y^2)/2$ and a radial 1-form

Take the quadratic Hamiltonian

$$H=\frac{x^2+y^2}{2}.$$

Its Hamiltonian field is $\dot x=y$, $\dot y=-x$. Formal
differentiation gives $d(x^2+y^2)/dt\equiv 0$, so every regular
level $H=h>0$ is a circle $x^2+y^2=2h$. That is the period
annulus. The flow is clockwise:
$x=\sqrt{2h}\,\sin t$, $y=\sqrt{2h}\,\cos t$.

Perturb by $P=0$ and

$$Q=\mu\, y\, p(x^2+y^2),$$

where $p$ is a univariate polynomial of degree $k$ and $\mu\neq 0$.
Then $\deg Q=2k+1$. The first-order integral (either orientation)
factors on each oval, because $x^2+y^2=2h$ is constant:

$$I(h)=\mu\, p(2h)\oint_{H=h} y\,dx.$$

Along the Hamiltonian orientation,
$\oint y\,dx=2\pi h$. The code never computes $\pi$. The reduced
integral

$$\tilde I(h)=h\, p(2h)$$

is a polynomial in $Z[h]$ with the same zeros on $h>0$ as $I(h)$.
The factor $h$ is the area scaling; it vanishes only at the
equilibrium $h=0$, which is not in the period interval. The
positive zeros are exactly the positive zeros of $p(2h)$.

If $p(s)=\prod_{j=1}^{k}(s-\alpha_j)$ with distinct $\alpha_j>0$,
then $\tilde I$ has exactly $k$ positive zeros. The degree budget
is $n=2k+1$, so

$$k=\frac{n-1}{2}=\Bigl\lfloor\frac{n-1}{2}\Bigr\rfloor$$

when $n$ is odd. The family attains the published $Z(2,n)$. It
does not beat it.

For even $n=2k$ the same radial form cannot use a degree-$k$
factor $p$ (that would make $\deg Q=2k+1=n+1$). Taking $p$ of
degree $k-1$ gives $\deg Q=2k-1\le n$ and $k-1$ positive zeros,
which is again $\lfloor(n-1)/2\rfloor$. Equivalently: for every
$n\ge 1$ the radial 1-form of degree $2\lfloor(n-1)/2\rfloor+1\le n$
attains exactly $Z(2,n)$ zeros and uses at most degree $n$.

A mixed term $Q=\mu\,xy\,q(x^2+y^2)$ integrates to zero on every
circle (the integrand is odd in the angle). It does not add zeros
and does not beat the odd-degree radial count.

### Degree 3

$Z(2,3)=1$. Take $p(s)=1-s$, so
$Q=\mu y\bigl(1-(x^2+y^2)\bigr)$ has degree 3. Then

$$\tilde I(h)=h(1-2h).$$

One positive zero, at $h=1/2$. Matches $Z(2,3)$. The oval
reduction $p(x^2+y^2)-p(2h)=-(x^2+y^2-2h)$ is the zero remainder.

### Degree 5

$Z(2,5)=2$. Take $p(s)=(s-1)(s-4)=s^2-5s+4$, so
$Q=\mu y(x^2+y^2-1)(x^2+y^2-4)$ has degree 5. Then

$$\tilde I(h)=h(2h-1)(2h-4)=4h^3-10h^2+4h.$$

Two positive zeros, at $h=1/2$ and $h=2$. Matches $Z(2,5)$.
The oval reduction is
$p(x^2+y^2)-p(2h)=(x^2+y^2-2h)(x^2+y^2+2h-5)$.

An extra positive zero would need $\deg\tilde I\ge 4$, hence
$\deg p\ge 3$ and $\deg Q\ge 7$. That is a degree-7 1-form, which
is the $n=7$ attaining example, not a beat of $Z(2,5)$.

### Family upper bound, same family

On this annulus, $\tilde I(h)=h\,p(2h)$ has at most $\deg p$
zeros in $h>0$. For $Q=\mu y\,p(x^2+y^2)$ of degree at most $n$
one has $\deg p\le\lfloor(n-1)/2\rfloor$. Upper and lower match
the formula on this family. That is a replay of the small-$n$
case, not an independent proof that every degree-$n$ 1-form
(non-radial included) has at most that many zeros. Scholarpedia
already records the general fact because $M(h)$ is a polynomial.

Enumeration $n=1,\ldots,10$ (both languages, same dump):
$Z(2,n)=\lfloor(n-1)/2\rfloor$ equals the radial zero count, and
the radial degree $2Z(2,n)+1$ never exceeds $n$.

## Kept — this annulus is not $H(2)$

$Z(2,n)$ bounds the number of zeros of the first Melnikov
function on a period annulus of a quadratic Hamiltonian. It is
not a bound on the planar Hilbert number $H(2)$. The published
$H(2)\ge 4$ uses a order-3 weak focus plus a surrounding cycle
(Shi; Chen–Wang), or graphics, not this Hamiltonian annulus.
For quadratic perturbations one has $Z(2,2)=0$: the first-order
integral of this family has no positive zero. That is consistent
with four quadratic cycles needing a non-Hamiltonian mechanism.

## What this is not

Not a dent of $Z(2,n)$. Not a dent of $H(2)$ or $H(n)$. Not a
field with $\lfloor(n-1)/2\rfloor+1$ Abelian zeros. Not a bound
on cyclicity of an arbitrary quadratic period annulus beyond the
published theorem. The reusable lemma is the radial attaining
family: a stranger can run `run.sh` and read $n=3$ and $n=5$ off
the dump.
