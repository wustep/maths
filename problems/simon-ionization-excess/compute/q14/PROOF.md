# A rational certificate for the leading coefficient 1.1005

For the fermionic Hamiltonian in PROBLEM.md, we obtain

$$
N_c(Z)<1.1005Z+3.933Z^{1/3}\qquad(Z\ge4).
$$

The finite calculation proves $\beta_3\ge9087/10000$ in the notation
of [Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1](https://arxiv.org/html/2504.18487v1).
This note supplies the passage from the matrices to that variational
constant and then to the electron bound. The analytic inputs are
HPS Theorem 4.2 and their Section 7 argument, together with Lieb's
$N_c<2Z+1$. No earlier notebook face enumeration is an input.

## 1. The radial quotient

HPS Theorem 4.2 permits radialization at $s=3$. Write $m$ for the
probability distribution of the radius. Newton's theorem gives

$$
Q(m)=\frac{I(m)}{D(m)},\qquad
I(m)=\iint g(r,u)\,dm(r)dm(u),\qquad
D(m)=\int r^2\,dm(r),\qquad
g(r,u)=\frac{r^3+u^3}{2\max(r,u)}.
$$

For positive radii, setting $t=\min(r,u)/\max(r,u)$ gives

$$
g(r,u)=\frac{r^2+u^2}{2}f(t),\qquad
f(t)=\frac{1+t^3}{1+t^2},\quad 0\le t\le1.
$$

Both verifiers establish the rational global floor $f(t)\ge l$,
where $l=8941/10000$. Indeed, the numerator of $f(t)-l$ is
$t^3-lt^2+1-l$. Its minimum for $t\ge0$ is
$1-l-4l^3/27>0$, as checked exactly in Python and outwardly in Rust.
Also $f(t)\le1$. Its derivative has the sign of $t^3+3t-2$
for $t>0$. This polynomial is strictly increasing and has its sole
positive root between $0.5960$ and $0.5961$; both checks certify
the endpoint signs.

## 2. Compact support and the matrix witnesses

Scale the radii into $[1,10]$. `certificate.json` specifies 38
strictly increasing rational edges, with first edge 1 and last edge
10. They determine 37 bins. Assign shared endpoints to either
neighboring bin, using half-open bins to make the assignment unique.

For bin $i$ with endpoints $a_i,b_i$, put
$c_i=a_i b_i$ and $d_i=(a_i+b_i)/2$. On each bin pair, the extreme
values of $t$ are its corner ratios, with upper endpoint 1 whenever
the bins overlap. The rational lower bound $F_{ij}$ is obtained by
evaluating $f$ at the appropriate endpoint if the whole ratio interval
lies below $0.5960$ or above $0.5961$. Otherwise use the global floor
$l$. Thus $l\le F_{ij}\le f(t)\le1$ throughout the bin pair.

The matrix to be certified is

$$
M_{ij}=(F_{ij}-\varphi)\frac{c_i+c_j}{2d_i d_j},
\qquad \varphi=114/125=0.912.
$$

The certificate has two separate witnesses. Python checks
$M=P+E$ with $E$ entrywise positive. Exact rational elimination
gives positive Schur-complement pivots for the symmetric matrix
$P$, proving that it is positive definite. Rust instead checks
$M=BB^{\mathsf T}+E'$ with $E'$ entrywise positive. The entries of
$B$ are explicitly stored rational numbers, so its Gram matrix is
positive semidefinite by the sum-of-squares identity. Both residuals
are greater than $10^{-5}$ entry by entry. The witnesses need not
be equal and are verified independently.

It follows for every nonnegative vector $x$ that $x^{\mathsf T}Mx\ge0$.
Let $m_i$ be the probability in bin $i$, and substitute $x_i=d_i m_i$.
Since the total mass is one, this proves

$$
\frac{\sum_{i,j}F_{ij}(c_i+c_j)m_i m_j/2}
     {\sum_i c_i m_i}\ge\varphi.
$$

## 3. The reweighting error

Set $C=\sum_i c_i m_i$ and let $D_i$ be the integral of $r^2$ over
bin $i$. Define probability vectors $p_i=c_i m_i/C$ and
$w_i=D_i/D$. If $m_i>0$, the ratio $D_i/(c_i m_i)$ lies in
$[a_i/b_i,b_i/a_i]$. Let $q=\max_i(b_i/a_i)$. Reweighting a
probability by factors in $[1/q,q]$ changes it in total variation
by at most $(q-1)/(q+1)$.

For completeness, if a random reweighting factor $X$ lies in
$[a,b]$ and has mean $s$, convexity of $|X-s|$ gives

$$
\frac{\mathbb E|X-s|}{2s}
\le\frac{(b-s)(s-a)}{(b-a)s}
\le\frac{\sqrt b-\sqrt a}{\sqrt b+\sqrt a}.
$$

The last maximum occurs at $s=\sqrt{ab}$. Taking $a=1/q,b=q$
gives the stated bound. Zero-mass bins can be discarded.

By symmetry of $F$, the compact matrix quotient is
$\sum_i p_i\sum_jF_{ij}m_j$. The true quotient is at least
$\sum_i w_i\sum_jF_{ij}m_j$. The inner sums lie in $[l,1]$,
so their difference is bounded by $(1-l)$ times total variation.
Therefore every measure supported in $[1,10]$ satisfies

$$
Q(m)\ge\gamma:=\varphi-\frac{q-1}{q+1}(1-l)
=\frac{5799575951378799}{6382236648346000}
>\frac{9087}{10000}.
$$

Python obtains the displayed rational exactly; Rust independently
encloses the same expression and verifies the final strict inequality.

## 4. Removing the support restriction

For a fixed finite set of positive radii, minimize $Q$ over the
probability simplex. The denominator is bounded away from zero,
so a minimizer exists. On its used support, with
$V(r)=\int g(r,u)\,dm(u)$, mass stationarity yields

$$
2V(r)=Q(r^2+D).
$$

This follows by differentiating $I/D$ and then integrating the
stationarity equation to determine its Lagrange multiplier. Scale
the smallest used radius to 1 and denote the largest by $R$.
At these endpoints the identity reads

$$
\int u^{-1}\,dm(u)=Q+(Q-1)D>0,\qquad
\int u^3\,dm(u)=(Q-1)R^3+QDR>0.
$$

If $Q\ge1$ the desired lower bound is immediate. Otherwise these
positive moments imply

$$
\frac{1-Q}{Q}R^2<D<\frac{Q}{1-Q},
\qquad Q>\frac{R}{R+1}.
$$

If $R\ge10$, this exceeds $10/11>9087/10000$. If $R<10$, the
compact certificate applies. The original finite measure has a
quotient at least as large as its mass minimizer. Hence every finite
probability on positive radii satisfies the claimed lower bound.

On a compact interval bounded away from zero, finite radial measures
approximate any radial probability, and both integrals defining $Q$
converge. For an arbitrary admissible radial measure, truncate to
$[\epsilon,L]$ and renormalize. The bound
$0\le g(r,u)\le(r^2+u^2)/2$ and the finite second moment give
convergence by dominated convergence. An atom at the origin is
excluded by the HPS $H^{-1}$ condition. Thus the bound extends to
the entire radial variational domain, and Theorem 4.2 gives
$\beta_3\ge9087/10000$.

## 5. The HPS constants

Put $b=10000/9087$. The constant called $c$ in HPS (7.34), denoted
here by $C_0$, simplifies to

$$
C_0=\frac4{\sqrt3}\left(\frac{2\cdot1.456}{9}\right)^{1/3}.
$$

The powers of $\pi$ cancel. Python encloses its sixth root with
exact rational bisection. Rust checks $C_0<1.5855$ by a sixth-power
comparison and uses that slightly larger upper bound throughout.

Under the contradiction assumption for our target inequality,
$N\ge bZ$, so $N\beta_3\ge Z\ge4$. HPS's smoothing radius has
cube at most $5/48<1/8$, as required. Equations (7.26)–(7.33)
then apply. Lieb gives $N/Z<9/4$. For a fixed variational constant
$\beta$, the function to maximize is

$$
A\beta^{-2/3}x^{1/3}+C_0\beta^{-1}x^{-2/3},
\qquad A=3(3/10)^{1/3}.
$$

Its derivative changes sign only from negative to positive, so its
maximum on $[1/\beta,9/4]$ is at an endpoint. Both endpoint values
decrease as $\beta$ increases. Substituting our lower bound for
$\beta$ therefore bounds the maximum by

$$
a_1=\max\left\{Ab+C_0b^{1/3},\;
A(9b^2/4)^{1/3}+C_0(16b^3/81)^{1/3}\right\}.
$$

HPS (7.29) gives the remaining upper bounds

$$
a_2=b/84,\qquad a_3=(C_0/5)(25b/144)^{1/3},
\qquad a_4=(C_0/84)b^{1/3}.
$$

The same contradiction argument yields the corresponding electron
bound with these coefficients. After dividing the remainder by
$Z^{1/3}$, its maximum for $Z\ge4$ is at $Z=4$. Both verifiers prove

$$
b<1.1005<1.1006,\qquad
a_1+a_2\,4^{-1/3}+a_3\,4^{-2/3}+a_4/4<3.933.
$$

The strict slack in the final printed constants yields the strict
inequality in CLAIM.md. Both verifiers also replay the published
$1.1184<b(3)<1.1185$ enclosure using the increasing cubic
$t^3+3t-2$ and $b(3)=2/(3t)$. The bounded-excess conjecture remains
open.
