# Independent finite verification by interpolation

This algorithm verifies the same native Triangle functional as the original
producer. It uses neither that producer's Taylor moments nor its frozen
gamma weights. It evaluates the exact target time and height. Its interval
arithmetic library, Arb, is shared with the original C program; implementation
independence here concerns the language, summation, approximation, and update
algorithm, not the underlying transcendental library.

Fix an integer cutoff $N$, and let $B_n$ and $A_n$ be the two real
convolution coefficients in `ANALYTIC_REVIEW.md`. They are constructed from
the exact Euler products. Define three positive Laplace sums:

$$
S_B(s)=\sum_{n=2}^{DN}|B_n|n^{-s},\qquad
S_A(s)=\sum_{n=2}^{DN}|A_n|n^{-s},\qquad
U(s)=\sum_{n=2}^{N}b_t(n)n^{y_0}\log n\,n^{-s}.
$$

The code needs these functions at the frozen real-part minorant
$s=\sigma_N$. It maintains their interval values at eight fixed nodes
across each of four index ranges.

## Remainder bound

Consider any sum $S(s)=\sum c_n n^{-s}$ with $c_n\ge0$ and support bounded
by $DN$. Let $a\le s\le b$, let $s_0<\cdots<s_{m-1}$ be distinct nodes
inside this interval, and let $P$ interpolate $S$ there. Real polynomial
interpolation with remainder gives

$$
|S(s)-P(s)|\le
\frac{\sup_{u\in[a,b]}|S^{(m)}(u)|}{m!}
\left|\prod_{j=0}^{m-1}(s-s_j)\right|.
$$

Put $L=\log(DN)$. Positivity of every coefficient implies

$$
|S^{(m)}(u)|\le L^m S(a),\qquad
S(a)\le e^{(s_0-a)L}S(s_0).
$$

Thus the interval computation adds the error radius

$$
\frac{L^m e^{(s_0-a)L}S(s_0)}{m!}
\left|\prod_{j=0}^{m-1}(s-s_j)\right|.
$$

The code computes the product at the actual argument, including interval
uncertainty, and uses `arb_add_error` to add an outward error radius. It
does not estimate the remainder by comparing two floating-point answers.
The nodes are scaled cosine nodes. Their particular optimality is unnecessary
for validity: only their exact ordering, inclusion, and separation enter
the argument. The denominator products are checked to exclude zero.

Here $a$ and $b$ are the exact values of the minorant at the first and last
indices of a range. The horizontal monotonicity argument in
`ANALYTIC_REVIEW.md` shows that every intervening argument lies between them.
All occurrences of those exact transcendental numbers are enclosed by Arb
balls, including the node locations and Lagrange weights.

Prefix and suffix products evaluate the Lagrange weights in linear time in
the number of nodes. The same product gives the remainder factor for all
three sums.

## Initial sums and cutoff updates

For each divisor $d$, generate the increasing stream
$d,2d,\ldots,dN$. A merge visits the union of those streams in increasing
order. At a visited integer, collect every pair with that product before
taking either absolute value. The initializer checks that it consumed
exactly $N2^k$ pairs for $k$ Euler primes. Terms at index one are excluded
from the masses, as required by the native numerator.

When the cutoff increases from $N-1$ to $N$, the only new pair for divisor
$d$ is $(d,N)$. It changes the coefficient at index $dN$. Distinct
divisors give distinct changed indices. At that index the code independently
reconstructs the old coefficient from divisors $e$ satisfying

$$
e\mid dN,\qquad dN/e<N,
$$

then adds the new coefficient from $(d,N)$. Each node sum changes by
the difference of the two absolute coefficients times its fixed node weight.
This is an exact telescoping identity. The update difference may be negative;
the resulting exact sum still has nonnegative coefficients, so the
remainder bound continues to apply. Arb encloses all update roundoff.
The unmollified sum $U$ receives only its new term at $N$.

## Correction and decisive gate

For the positive kappa bound $\rho_N$ and $2\le n\le N$,

$$
e^{\rho_N\log n}-1
\le \rho_N\log n\,e^{\rho_N\log N}.
$$

Consequently the native correction is at most
$\gamma_N\rho_N e^{\rho_N\log N}U(\sigma_N)$. This is a different,
slightly weaker correction enclosure than direct use of `expm1` in the
singleton program.

At every required integer the interpolation program evaluates

$$
\frac{1-\gamma_N-S_B(\sigma_N)-\gamma_NS_A(\sigma_N)}{M_N}
-\gamma_N\rho_N e^{\rho_N\log N}U(\sigma_N).
$$

The entire calculation is an interval enclosure of a lower bound for the
native functional. The output is the floor of its lower endpoint times
$10^{12}$. The program rejects a production index unless that integer
exceeds 233495. This is stricter than comparison with the uniform error
upper bound $2.33494905212337849\cdot10^{-7}$.

Four complete contiguous ranges cover indices 690988 through 3840000.
An output parser must verify every index and the terminal counts; a
successful prefix of a terminated process is not accepted as a range.
The whole finite result still needs the separate height, tail, barrier,
and analytic inputs to imply the inequality in `CLAIM.md`.
