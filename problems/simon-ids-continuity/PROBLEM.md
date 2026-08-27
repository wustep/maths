# Continuity of the integrated density of states

- Slug: `simon-ids-continuity`
- Status: residue — the general bounded continuum case in dimensions at
  least four remains open
- Area: spectral theory, ergodic Schrödinger operators, quantitative
  unique continuation
- Sources: [Simon 2000](http://www.math.caltech.edu/papers/bsimon/r40.pdf),
  [Bourgain–Klein](https://arxiv.org/abs/1112.1716), and
  [Frank–Ivanisvili](https://arxiv.org/abs/2608.00802)
- Started: 2026-08-27

## Result

No new continuity class is claimed. Bourgain and Klein already prove a
deterministic log-Hölder estimate for every bounded continuum potential
in dimensions one, two, and three. Their proof has a sharp dimensional
frontier: its quantitative unique-continuation exponent is $4/3$, and
the argument requires

$$
\frac{d}{d-1}>\frac{4}{3}.
$$

The verifier in `compute/q1/` replays the exact balance. For the
published bounds in $d=2,3$, the logarithmic exponent is

$$
\kappa_d=\frac{4-d}{8}.
$$

Its formal continuation is positive only for $d=2,3$ and is zero at
$d=4$.
Frank and Ivanisvili's 2026 real-valued Landis examples rule out
replacing $4/3$ by any smaller power in a uniform estimate of the
same form. That closes this particular route through dimension four;
it does not supply a discontinuous IDS.

One reusable special case was checked. If a lower-bounded ergodic
operator $A$ is extended by $m\geq1$ free continuum directions,

$$
H=A\otimes I+I\otimes(-\Delta_{\mathbb R^m}),
$$

then its density-of-states measure is the convolution of the measure
for $A$ with the free density of states. Consequently its IDS is
locally absolutely continuous in every total dimension. This is a
standard separable-operator consequence. It is recorded as a finite
handle, and no dent follows from it.

## The object Simon called \(k(E)\)

Let an ergodic group action translate a covariant family

$$
H_\omega=-\Delta+V_\omega
$$

on $L^2(\mathbb R^d)$. Assume the family is lower bounded and has a
locally finite density-of-states measure. For a unit cube $Q$, the
Pastur–Shubin trace formula is

$$
\nu(B)=\mathbb E\!\left[
  \operatorname{Tr}\bigl(\chi_Q\mathbf 1_B(H_\omega)\chi_Q\bigr)
\right].
$$

Simon writes the cumulative distribution as

$$
k(E)=\nu(({-\infty},E]).
$$

Equivalently, at continuity points it is the almost-sure
thermodynamic limit of the number of finite-volume eigenvalues at most
$E$, divided by volume. On $\mathbb Z^d$, the local trace is the
expected spectral measure at one lattice site.

Continuity of $k$ is equivalent to the absence of atoms in the DOS
measure. An atom at a fixed energy corresponds, in the ergodic
setting, to an eigenspace with positive dimension per unit volume.

## Published cases

| Setting | Published conclusion |
| --- | --- |
| One-dimensional continuum | Craig–Simon log-Hölder continuity for bounded ergodic potentials. |
| Discrete, every dimension | Craig–Simon log-Hölder continuity; Delyon–Souillard give a short continuity proof. |
| Continuum, dimensions 2 and 3 | Bourgain–Klein log-Hölder continuity for every bounded potential whenever the IDS exists. |
| Singular continuum potentials, dimensions at most 3 | Klein–Tsang extend the density-of-states outer-measure estimate under their stated integrability hypotheses. |
| Anderson-type continuum models, every dimension | Wegner estimates give global continuity for atomless single-site laws and local continuity for arbitrary laws in localization regimes. |
| Periodic continuum models, every dimension | Floquet theory and the absence of flat bands give continuity. |

The leftover addressed here is the continuum family with no
independence, periodicity, localization, or separability assumption,
already for bounded real potentials in dimension four.

## A checked free-direction lemma

Let $A_\omega$ act on $L^2(\mathbb R^n)$, be bounded below by $a$,
and have DOS measure $\nu$.

Let $v_m$ denote the volume of the unit ball in $\mathbb R^m$, and put

$$
C_m=\frac{v_m}{(2\pi)^m},\qquad \alpha=\frac m2.
$$

For the tensor-sum operator above, Fourier transformation in the free
variables gives, first for compactly supported bounded Borel test
functions and then for bounded energy intervals,

$$
\nu_H(B)=\frac1{(2\pi)^m}
\int_{\mathbb R^m}\int_{\mathbb R}
\mathbf 1_B(\lambda+|p|^2)\,d\nu(\lambda)\,dp.
$$

Tonelli's theorem and radial integration therefore give

$$
k_H(E)=C_m\int_{(-\infty,E]}(E-\lambda)^\alpha\,d\nu(\lambda).
$$

Thus the DOS is locally absolutely continuous, with an almost-everywhere
density

$$
n_H(E)=C_m\alpha\int_{(-\infty,E]}(E-\lambda)^{\alpha-1}
\,d\nu(\lambda).
$$

The apparent square-root singularity for $m=1$ is locally
integrable. More explicitly, fix $E\leq E_0$ and $0<h\leq1$. Put

$$
M_0=\nu(({-\infty},E_0+1]).
$$

For $m=1,2$, concavity gives

$$
0\leq k_H(E+h)-k_H(E)\leq C_mM_0h^{m/2}
\quad(m=1,2).
$$

For $m\geq3$, the mean-value theorem gives

$$
0\leq k_H(E+h)-k_H(E)
\leq C_m\alpha M_0 R^{\alpha-1}h,
\qquad R=\max\{1,E_0+1-a\}.
$$

The certificate records the exponent $\min\{1,m/2\}$. The convolution
identity is standard for separable operators; the notebook therefore
makes no priority claim for this lemma.

## What would count as a new bound

A dent would be a checked continuity theorem that strictly enlarges a
published class. Examples include continuity for arbitrary bounded
ergodic continuum potentials in one new dimension $d\geq4$, a new
potential class not covered by the cited Wegner or separable results,
or a strictly stronger certified modulus on a published class.

A complete proof must also identify the thermodynamic IDS with the
local trace measure and handle every energy. An incomplete
finite-volume search or an improvement of an auxiliary inequality
that does not yield continuity is residue.

## Acknowledgements

Stephen Wu selected the problem and set the verification standard.
GPT-5.6 Sol performed the literature triage, obstruction analysis,
free-direction derivation, and verifier implementation.
