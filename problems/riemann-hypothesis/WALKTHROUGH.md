# Walkthrough — Riemann hypothesis

The first campaign did not change the published bound. It did leave a compact
replay of the live interval $0\leq\Lambda\leq0.2$, a fresh partial audit of a
much stronger recent lead, and a precise description of what remains before
that lead could count.

## 0. What was actually missing

Riemann's hypothesis has many finite equivalents, but most finite checks have
no record-changing endpoint. Verifying another initial block of zeros does not
prove that all zeros lie on the critical line. Checking finitely many Li
coefficients has the same limitation.

The de Bruijn–Newman constant is different. Rodgers and Tao proved
$\Lambda\geq0$, while RH is equivalent to $\Lambda\leq0$. Polymath 15 turned a
finite zero-height input, an asymptotic region, and a compact barrier into an
explicit upper bound. Platt and Trudgian supplied enough verified height to
make the published window $0\leq\Lambda\leq0.2$.

## 1. Named false starts

The first source identifier was wrong: arXiv:2007.02194 is about software
refactoring. The correct Platt–Trudgian paper is arXiv:2004.09765. Keeping the
failed lookup in the research log prevents the bad identifier from becoming a
citation by repetition.

The second trap was more mathematical. Polymath's displayed row uses
$t_0=0.186$ and $y_0=0.16733$. Treating those strings as exact gives
$0.19999966445$, apparently below $0.2$. They are rounded table entries. The
tiny difference is smaller than the information discarded by printing the
parameters, so it cannot support a theorem.

The historical Lehmer-pair direction also closes immediately as an attack on
the current record. Its negative lower bound is reproducible, but
Rodgers–Tao's zero lower bound is already stronger.

## 2. The useful failure

An August 2026 GitHub repository proposes $\Lambda\leq0.1787854$. It comes
with interval programs, millions of stored finite rows, two precision lanes,
and an assembly script. It is also outside arXiv and peer review. That made it
an excellent audit target without making it the published record.

The stored assembly passed. More importantly, the shorter numerical lanes
could be regenerated on this machine while the unrelated Hilbert 16(a) search
continued. The fresh tail and finite-error bounds agreed at 256 and 512 bits.
The barrier regeneration covered 883 consecutive time prisms with wide
positive margins. A one-row run through the finite producer also matched the
sealed first row exactly.

The failure is informative: the remaining trust is concentrated in the
3,149,013 archived finite rows and in the analytic bridge from the numerical
objects to every hypothesis of Polymath 15. Those are concrete review tasks.

## 3. The click

The candidate's headline decimal has unusually clean exact data:

$$
t_0=\frac{129}{800},\qquad y_0^2=\frac{87677}{2500000},
$$

so

$$
t_0+\frac{y_0^2}{2}=\frac{893927}{5000000}=0.1787854.
$$

Its horizontal location is
$X=6{,}000{,}000{,}185{,}827$. The Platt–Trudgian theorem reaches beyond
$X/2$ by $175{,}239{,}886.5$. The zero-height input is therefore already in
the published literature. The real work lies in the finite estimates,
infinite tail, barrier, and analytic transfer.

## 4. The argument being replayed

Polymath 15 evolves the Riemann $\Xi$ function by a backwards heat flow.
Their effective criterion packages three facts:

1. the original zeros are known to be on the line up to $X/2$;
2. at time $t_0$, zeros cannot enter from the asymptotic region; and
3. a vertical barrier near $X$ stays zero-free for every time from $0$ to
   $t_0$.

When these facts meet, zeros on the left cannot cross the barrier or arrive
from the right during the flow. A zero-free strip of half-width $y_0$ then
gives $\Lambda\leq t_0+y_0^2/2$.

The retained verifier checks exact parameter identities and the numerical
outputs. It deliberately does not claim that log hashes fill an unreviewed
analytic implication.

## 5. Computer work

The stored review read all finite rows from $N=690988$ through $N=3840000$.
The minimum stored lower bound was $7.91366\cdot10^{-7}$ and the interval error
upper bound was $2.33494905213\cdot10^{-7}$, leaving positive room.

Fresh FLINT/Arb runs checked that error majorant and the infinite tail twice,
at 256 and 512 bits. A separate fresh run rebuilt the barrier sums, verified
containment for 7,688 components, bounded the uniform numerical error by
$0.000356523012$, and closed all 883 prisms. The smallest printed prism margin
was above $0.5198$.

Only one compute job ran at a time. The full finite producer was left for a
future clean replay because the machine was already carrying the Hilbert
search and the upstream workflow expected parallel workers. Its first row was
regenerated separately on one low-priority core, taking 242 seconds and about
5 MB RSS.

The same small verifier also redoes the 2011 Lehmer formula from four printed
zero ordinates. Python decimal arithmetic and a separate C floating-point
path both recover the paper's $-1.14541\cdot10^{-11}$ scale.

## 6. Proven and still open

The source papers establish

$$
0\leq\Lambda\leq0.2.
$$

The local code independently checks the exact small arithmetic, the historical
Lehmer calculation, the integrity of the fresh logs, every barrier prism, and
the decisive margins printed by the fresh interval runs.

The off-arXiv $0.1787854$ claim has not been promoted. A full independent
finite regeneration, an analytic review, and a published source are still
missing. RH itself remains open; it would force $\Lambda=0$.

## The second campaign: what remained

The earlier run had made the uncertainty unusually concrete. It had checked
the first finite row and all the short numerical lanes, but there were still
3,149,012 rows to regenerate and an analytic implication at time zero to
review. The second campaign chose that unfinished candidate, keeping its
exact rational parameters and giving the finite regeneration an exclusive
place on the machine.

The original producer could run sequentially. Its 23 segments all completed,
and every generated row matched the archived row. That finished the first
missing calculation. It did not yet provide a different algorithm against
which to check the producer.

## A direct check that could not scale

The first independent program simply performed the native convolution. It
merged the streams $d,2d,\ldots,dN$, gathered all contributions at the same
integer, and only then took absolute values. The weakest row required
22,111,616 pairs and took 73 seconds. Its result agreed with the original
floor with ample precision.

Doing this again from scratch at every next integer would repeat almost
all the work. An optimization that skipped inactive support indices in the
original program was also drafted, but it would still be a modification of
the same algorithm. The original full replay finished without using it.

## The useful failure and the new representation

The failed scaling attempt showed exactly what should be preserved between
indices: the positive sums after the signed convolution coefficients have
been combined. Their dependence on the exponent is smooth even though
their coefficients change when the cutoff changes.

The new program keeps those sums at eight fixed exponent nodes. When $N$
increases, only the products $dN$ receive a new pair. Their old coefficients
can be reconstructed from the divisor set, and the difference of the old
and new absolute values updates every node. There is no need to store the
whole support.

The remaining issue was whether interpolation could be rigorous near a
margin of order $10^{-7}$. Positivity supplies the derivative bound. For
$S(s)=\sum c_n n^{-s}$, $c_n\geq0$, and support at most $DN$,
$|S^{(8)}(s)|$ is bounded by $\log(DN)^8$ times a left-endpoint sum.
The interpolation remainder can then be included as an Arb error radius.
That was the step that made the second complete calculation practical.

## The calculation and the analytic handoffs

The four Rust ranges checked every integer from 690988 to 3840000 in a
total of 600 seconds. The original C replay took 4266 seconds. Both give
the same floor $791366/10^{12}$; the independent direct convolution confirms
the weakest row, and a Python dictionary convolution checks 100 small
cases. The two complete algorithms share Arb, which remains an explicit
common dependency.

The analytic review had its own traps. The absolute value of a coefficient
can have a kink at zero, so the height transfer needs the upper Dini
derivative there. Dividing by the Euler normalizer needs the numerator's
positivity first. A matrix that reproduces archived coefficients still
needs an algebraic identity connecting its polynomial to the required
finite sum. Each of those implications was checked and written down.

The coefficient generator also contains an old quadrature whose complex
callback is unsuitable as a rigorous error proof. Here it only selects a
matrix size. The actual finite coefficients are interval sums, and a
separate factorial calculation validates the selected 62-by-62 truncation.
Keeping that distinction prevents an unnecessary heuristic from becoming
a proof premise.

At time zero, the solution is a compact limit. The heat-flow integral has
an integrable bound independent of time on this fixed rectangle. Its
normalizer is continuous and nonzero, and the integer index stays constant.
Thus the uniform positive-time error estimate survives at zero. There is
no need to assert a limit over an unbounded horizontal region.

## What the second campaign has established so far

Both complete finite verifications and the fresh height, error, and tail
checks have passed. Their finite margin after approximation error is
exactly bounded below by $557871094787662151/10^{24}>0$. The analytic
transfer is documented in `compute/q2/ANALYTIC_REVIEW.md`, and a mathematical
note is in `compute/q2/NOTE.md`.

The fresh barrier replay and final complete-certificate assembly are still
running. Until they finish, `compute/q2/CLAIM.md` remains an attempted
inequality. The candidate number belongs to Gomila; this campaign's new
work is its complete independent finite verification and analytic audit.
