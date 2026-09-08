# Analytic review of the pinned candidate

This review checks the mathematical transfer separately from its numerical
obligations. `CLAIM.md` gives the current certification status. The candidate
and its new lemmas belong to Jude Gomila; this folder is a reproduction and
audit with a new independent finite algorithm.

The source is commit `a74738deb6d5e0f76887cb36901da08b68dca705` of
[the candidate repository](https://github.com/judegomila/dbn-lambda-01787854-candidate-audit).
The published inputs are Polymath 15, Theorems 1.2 and 1.3,
[arXiv:1904.12438v2](https://arxiv.org/abs/1904.12438v2), and
Platt–Trudgian, Theorem 1 and Corollary 2,
[arXiv:2004.09765v1](https://arxiv.org/abs/2004.09765v1).
Both PDFs were fetched and their statements read again for this campaign.

## The theorem's domains

For the exact parameters in `CLAIM.md`, the criterion needs the following:

1. No zeta zero with real part at least $(1+y_0)/2$ and ordinate from zero
   through $X/2$.
2. At time $t_0$, no zero of the deformed function to the right of
   $X+\sqrt{1-y_0^2}$ and between heights $y_0$ and $\sqrt{1-2t_0}$.
3. At each time from zero through $t_0$, no zero between horizontal positions
   $X$ and $X+\sqrt{1-y_0^2}$ and heights
   $\sqrt{y_0^2+2(t_0-t)}$ and $\sqrt{1-2t}$.

The candidate transcribes these domains correctly. The published height
exceeds $X/2$ by $350479773/2$. Since $y_0>0$, critical-line zeros cannot
enter the first domain. The real axis endpoint is also safe: the alternating
eta series is positive for real arguments strictly between zero and one,
while its factor $1-2^{1-s}$ is negative. Zeta therefore has no zero there;
at one it has a pole. This proves the first input using the published theorem.

## The closed zero-time endpoint

The positive-time restriction in Polymath Theorem 1.3 does not, by itself,
invalidate this candidate. Here is the needed compact-set argument.

Let $R=[X,X+1]+i[1809/10000,1]$. For $z\in R$, $u\ge0$, and
$0\le t\le t_0$, the integrand defining the heat-deformed function obeys

$$
|e^{tu^2}\Phi(u)\cos(zu)|\le e^{t_0u^2+u}|\Phi(u)|.
$$

The series defining $\Phi$ has super-exponential decay as $u$ tends to
infinity, so the right side is integrable. Dominated convergence gives
continuity in both time and position, including time zero.

The normalizing factor in the paper is

$$
B_t(z)=M_t((1-iz)/2),\qquad
M_t(s)=e^{t\alpha(s)^2/4}M_0(s).
$$

On this rectangle the argument stays away from the branch cut and from
zero and one. The explicit factors of $M_0$ and the exponential never
vanish. Thus $B_t$ and its reciprocal are continuous on the compact time
rectangle. The candidate checks that the integer Riemann–Siegel index stays
equal to 690988 throughout it. Its approximation $f_t$ is consequently
a fixed finite sum of continuous functions, without an index jump.

If the positive-time error has the uniform upper bound $E$ on this box,
then for each fixed $z$ one may pass to the limit in
$|H_t(z)/B_t(z)-f_t(z)|\le E$ as time decreases to zero. The same estimate
holds at zero. A common constant $E$ gives the result for every point of
the rectangle. No uniform asymptotic limit as $x$ tends to infinity is
used. The identical reasoning applies to the finite-sum derivative bounds.

This resolves the specific zero-time scope note in q1 at the level of
analysis. It does not verify the numerical value of $E$ by itself.

## Horizontal window transfer

At fixed positive time, the windows have endpoints
$x_N=4\pi(N^2-t_0/16)$. They increase strictly and their half-open
assignment matches the floor defining the index. The first required
point lies inside the first window; the last finite window overlaps the
tail, which starts at index 3840000.

The bounds for $|\gamma|$ and $|\kappa|$ decrease with horizontal position.
For the real-part minorant, write

$$
h(x,y)=1-3y+4y(1+y)/x^2.
$$

For nonnegative height, both $h_+$ and $x^{-2}$ are nonnegative and
nonincreasing in $x$. Their product is nonincreasing. The logarithmic
term in the minorant increases, so the whole minorant increases even at
the kink. Freezing all three quantities at the left endpoint is therefore
conservative. This argument was checked against the producer's formulas.

## Native convolution and the sign of the numerator

The real Euler coefficients must be products of the individual prime heat
weights, with Möbius signs. Using the heat weight at the composite divisor
instead would change the functional. The producer uses the products.

Multiplying the first Dirichlet sum by $E(s_*)$ and the second by its
complex conjugate gives two real-coefficient convolutions. The second
conjugate is necessary; the candidate includes it. If $Q$ denotes one
minus the gamma bound and the two absolute convolution masses, then
the triangle inequality gives

$$
|E|\,|f_t|\ge Q-|E|\,gC,
$$

where $gC$ bounds the kappa correction. A positive candidate row says
$Q/M-gC>0$ with $M>0$ and $gC\ge0$. Thus $Q>0$. The displayed inequality
first excludes $E=0$, and then division and $|E|\le M$ imply

$$
|f_t|\ge Q/|E|-gC\ge Q/M-gC.
$$

This checks the normalization and the otherwise delicate inequality
direction. The Rust implementation recomputes this native functional
directly, without frozen weights or Taylor moments.

## Height transfer

The height transfer cannot be replaced by a statement that each signed
coefficient has a fixed sign. An absolute value can have a kink. For an
analytic real function $A$, the upper right derivative of $|A|$ at a zero
is $|A'|$. Away from a zero it is $\operatorname{sgn}(A)A'$. These facts
justify the candidate's upper Dini estimate, including its negative
gamma-derivative term. The composite divisor kernel retains the sum of
the squares of the individual prime logarithms.

The divisor-pattern reduction has $3^k$ cells for $k$ primes: for each
gcd mask, the active divisors form a suffix of its sorted divisor list.
The empty suffix contributes zero. The candidate's source checks
outward coverage of its logarithmic endpoints and both height endpoints,
and splits closed rectangles without gaps.

The local-to-global argument is valid conditional on every numerical cell
gate: absolute values of analytic functions and the clipped exponent are
locally Lipschitz; on the compact interval they are absolutely continuous.
A nonpositive derivative almost everywhere then gives nonincrease.
The normalizer decreases with height, and the candidate separately bounds
the correction's logarithmic derivative. These are distinct obligations.

The source-level reduction has been reviewed here. A stored cell summary
or a repeated precision of that source is not a second implementation of
the complete reduction.

## The barrier polynomial represents the required finite sum

This is a separate algebraic check from reproducing the coefficient file.
Set $a=\log(N/2)$, $\beta=(1-i(X+1/2))/2$, and $\ell_n=\log n-a$.
The regenerated matrix entries are exactly the finite sums

$$
c_{e,j}=\sum_{n=1}^N n^{-\beta}
\frac{\ell_n^e}{e!}\frac{(\ell_n^2/4)^j}{j!}.
$$

After the two exponential series are restored, evaluating this matrix at
$(w,t)$ represents

$$
P(w,t)=\sum_{n=1}^N n^{-\beta}
\exp(w\ell_n+t\ell_n^2/4).
$$

For any argument $u$ used by the code, put
$v=\beta-u-t\alpha(u)/2$. Expanding the square and collecting the
$\log n$ and $a$ terms gives the exact identity

$$
e^{a(v+ta/4)}P(v+ta/2,t)
=\sum_{n=1}^N b_t(n)n^{-u-t\alpha(u)/2}.
$$

This checks the outer powers as well as both shifts in the polynomial
argument. In the source, `s=(1-y+ix)/2`. The `bsums` branch takes $u=1-s$;
the `asums` branch takes $u=\overline s$ and is conjugated afterwards.
The multiplier `afac` equals $M_t(s)/M_t(1-s)=\gamma$; the constant
normalization difference between `H01` and the paper's $M_0$ cancels in
this ratio. Since

$$
\overline{s_*}+\kappa-y=s+\frac t2\alpha(s),
$$

the final `bsums + afac*conj(asums)` is exactly the $f_t$ in Polymath
equation (14), up to the separately enclosed two-series remainder.

The remainder proof has positive geometric denominators: here
$|\ell_n|\leq\log345494<13$, so its quantities
$A=0.66|\ell_n|$ and $B=0.05\ell_n^2$ satisfy
$A<8.58<63$ and $B<8.45<63$. For the first omitted term 62, both
$1-A/63$ and $1-B/63$ are positive. The rectangular product remainder
is bounded by $e^B I_A+e^A I_B$, where $I_A,I_B$ are the two geometric
factorial tails. The bound on the combined outer prefactors is deliberately
loose but conservative. The separate uniform interval calculation checks
both alpha arguments and the exact gamma multiplier on the whole box.

## Tail and barrier review

The tail's fixed-left endpoint cap follows from decreasing summands and
convexity after the change of variable $v=\log u$. Its convolution split
is a partition of pairs $(d,m)$ according to whether $dm$ exceeds the
head cutoff. The extra overshoot term is nonnegative padding. The
monotonicity gates for the error head must use their own cutoff, rather
than the convolution cutoff; the pinned source distinguishes them.

The barrier's interpolation factor of one half is valid. On each half
of a spatial mesh edge, the true image and the endpoint chord lie in
the same disk around the nearer endpoint, with radius at most half the
derivative bound times the edge length. Convexity of that disk gives a
zero-avoiding homotopy whenever the full spatial, time, and approximation
allowance is smaller than the endpoint modulus. The winding integer is
then preserved, and the argument principle applies because $B_t$ has
neither zeros nor poles there.

The pinned C source checks the time derivative on a whole closed prism,
uses the correct mesh denominator, includes the closing polygon edge,
and requires strict interval comparisons. Its quadrature callbacks keep
complex arguments when an analytic enclosure is requested. The finite
head plus decreasing integral tail addresses the discrete-sum issue.

The coefficient generator also has an older quadrature used to choose the
number of Taylor terms. Its projection of complex inputs is not a certified
holomorphic quadrature. It is not needed as an error estimate here: after
the size is selected, every coefficient is a finite Arb sum, and a separate
factorial remainder calculation proves that the selected 62-by-62 size
suffices. Both the matrix containment check and that independent remainder
are mandatory. The derivative-bound quadratures used by the barrier have
the repaired complex callbacks described above.

The error constant used in all current candidate lanes is the conservative
$179/50+173/25=21/2$. It follows from Proposition 6.6(vi) by replacing
$x-8.52$ with the smaller positive denominator $x-12$ and using
$1+u\le e^u$. The candidate does not need to recover the displayed 10.44
constant in equation (24).

## What this review establishes

The parameter transfer, zero-time limit, window directions, native
normalization, height reduction, tail reduction, and boundary homotopy
withstand this review. Two complete finite implementations have now checked
every required index; the second uses the interpolation theorem proved in
`INTERPOLATION.md`. The fresh analytic replay and its exact-rational
interface checker must also finish before `CLAIM.md` can be certified.

The review is by GPT-6 Astra, separately from the candidate's supplied
proof notes. It is not a report of external human review. The numerical
implementations share Arb where stated; repeating a precision does not
create a second implementation.
