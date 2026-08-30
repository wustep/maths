# Riemann, mashed: what a dent looks like this week

Status cutoff 2026-08-30. arXiv is the record. Clay list:
`notes/lists/millennium.md`. Folder: `problems/riemann-hypothesis/`.

Among the six open Clay problems, BSD is the one whose published *table*
can move in a session (Dujella rank, leftover Sha). Riemann is the one
this notebook already knows how to write: an explicit constant, a
verifier, a printed record. Hilbert 8(a), Smale 1. Landau 3 under RH
already lives in `problems/landau-legendre/`.

The live interval is

$$
0\le\Lambda\le 0.2.
$$

Rodgers–Tao (arXiv:1801.05914, *Forum Math. Pi* 2020) proved the lower
bound. Polymath 15 (arXiv:1904.12438) proved \(\Lambda\le 0.22\) by a
three-check barrier criterion. Platt–Trudgian (arXiv:2004.09765)
verified RH through height \(H_0=3\,000\,175\,332\,800\) (the lowest
\(12\,363\,153\,437\,138\) zeros, all simple and on the line) and fed
that height into Polymath Table 1 row 2 to get \(\Lambda\le 0.2\). They
left extra decimals on the table. The next printed row, \(0.19\), wants
\(H\gtrsim 10^{13}\).

A dent is a verified finite improvement of one of those printed
inequalities. An incomplete search is residue.

## Three attacks that share a library

**S1. Extra decimals on \(\Lambda\le 0.2\).** Polymath Theorem 1.2: if
\((t_0,y_0,X)\) pass (i) RH to height \(X/2\), (ii) an asymptotic
zero-free region for \(H_{t_0}\), (iii) a barrier with no zeros for
\(0\le t\le t_0\), then \(\Lambda\le t_0+y_0^2/2\). Row 2 only needs
\(H>2.51\cdot 10^{12}\); we already have \(H_0\). Replay the three
checks in Arb at the published parameters, then walk a rational grid
with \(t_0+y_0^2/2<1/5\). A certified \(\Lambda\le 0.199\) is the dent.
Gomila’s \(0.1787854\) is a map of where a barrier can sit, until it is
on arXiv.

**S2. Leong’s explicit \(|\zeta'/\zeta|\) and \(|1/\zeta|\).** Headline
row (arXiv:2405.04869): \(|\zeta'/\zeta|\le 24.303\log t\) for
\(\sigma\ge 1\), \(t\ge 13\), and \(|1/\zeta|\le 30.812\log t\) on the
same region. The paper maximises an explicit formula in a handful of
real parameters, plugging in the then-best \(W_0=5.558691\) and \(H_0\).
Bellotti–Trudgian–Yang (arXiv:2603.21490, March 2026) now have the
classical constant \(4.896\). Feeding that published \(W_0\) through
Leong’s formulae, then interval-reoptimising the remaining parameters,
is the first dent to try. A \(10^{-4}\) improvement on \(24.303\) counts.

**S3. A classical zero-free constant below \(4.896\).** Bellotti–
Trudgian–Yang, Theorem 1: no zeros for \(t\ge 3\) and
\(\sigma\ge 1-1/(4.896\log t)\). That is the live classical record
(Heath-Brown / Linnik method). Mossinghoff–Trudgian–Yang
(arXiv:2212.06867) had \(5.558691\) for \(|t|\ge 2\) by a nonnegative
trigonometric polynomial plus Kadiri integrals; beating \(5.558691\)
alone is no longer a dent. A new poly, or a tighter Heath-Brown
instantiation, with \(R<4.896\) in the same shape, is the dent.

**Remix R1 = published \(4.896\) into S2, then maybe S3.** Leong’s
\(Q\) and \(Y\) are monotone in \(W_0\). The 2026 constant already
updates every row if Leong’s hypotheses still close. A later poly
that beats \(4.896\) would update them again.

**Remix R2 = S1 and S2.** Both spend unused headroom in \(H_0\). Same
Arb estimates of zeta on the 1-line; two inequalities.

Day 0 is a replay of \(\Lambda\le 0.2\) from the published
\((t_0,y_0,X)\). Then S1, S2, S3, one job at a time on this machine
(Hilbert 16(a) leftover is already searching). Stay under 2 GB RSS.

## Backup, one lattice

**S4 / S5.** Kim–Nguyen (arXiv:2502.21021) put the first
Mertens-conjecture counterexample below \(\exp(1.96\cdot 10^{19})\) in
two core-days and say more trials should go lower. Hurst 2018 has
\(\limsup M(x)/\sqrt{x}\ge 1.826054\). One fplll/Arb enumerator, Pintz
damping on or off, \(N\le 120\). Dim 140 and Hurst’s \(N=800\) wait
until Hilbert is gone.

## Leave on the shelf

Platt–Trudgian height, isolated \(M(10^{25})\) (Hurst, 34.6 days), and
classical Li coefficients past \(n=10^5\) (Johansson, 48.7 GB) are
supercomputer records. A Sol session will not move them.

Weil positivity, Nyman–Beurling, and Robin/Lagarias are live as
*disproof* machines: one certified off-line zero, or \(Q_W(f)<0\) for
one test function, would finish RH in the negative. A finite positivity
check never proves RH.

2024–2026 Zenodo “proofs,” the Wikipedia Claude 2026 on-line proportion
\(\approx 67.25\%\), and arXiv:2608.13637 claiming \(2/3\) are leads.
The published Levinson-family record remains Pratt–Robles–Zaharescu–
Zeindler, \(\kappa>5/12\) (arXiv:1802.10521).

Tao (2019-04-30): the Polymath 15 method is not a path to \(\Lambda=0\).
Further improvement below \(0.1\) would need RH verification to about
\(10^{19}\). Extra decimals on \(0.2\) are the finite handle.

## Other Clay problems, one line each

BSD: independent points plus Sage Sha; Dujella’s rank table moved in
August 2026 (Alpöge–Howell \(\ge 30/31\); exact rank still 20). Better
one-session *construction* than RH. P vs NP: Li–Yang \(3.1n\) and
Iwama–Morizumi \(5n-o(n)\) are theorems; SAT exact size for \(n\le 5\)
does not lift. Navier–Stokes: Tao 2016 averaged blow-up is a theorem;
Chen–Hou is Euler with boundary. Hodge and Yang–Mills have no
replayable integer record. Poincaré is solved.

Raw notes: `01-records`, `02-ideas`, `03-clay-compare`,
`04-dent-sketches` under the local research dump from this session.
