# Lonely runner for 14 runners

- Slug: `lonely-runner-fourteen`
- List: P44
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open (LRC(13)); one dent — the tight tuple is excluded at p=191
- Area: Diophantine approximation / computational combinatorics
- Sources: Sungkawichai and Trakulthongchai, Eleven, twelve, and thirteen lonely runners (arXiv:2604.23906); Trakulthongchai, Nine and Ten Lonely Runners
- Started: 2026-08-17

## Statement

Computer-assisted work in 2025–26 established the lonely-runner conjecture through 13 runners. The next case, 14 runners (13 nonzero relative speeds), remains open.

## Tonight

A certified finite-reduction or modular-sieve certificate for 14 runners, a new excluded speed configuration with an independently checkable witness, or a documented incomplete search. Isolated floating-point scans are not a new bound. Fetch the 13-runner papers before searching.

## Outcome (2026-08-17)

Incomplete: SuperGrok hit quota before a walkthrough. Independently replayed `rk_inclusion.py --selftest` and two p=191 witnesses in `verify_witness.py`. Exhaustive leftover salvage not replayed. LRC(13) open. See `ATTACK.md`.


## Outcome (2026-08-22, Opus 5)

Read ST26 in full first. Two corrections to the record, then a result.

Correction: what the 2026-08-17 campaign was searching for is false. The
statement "every nonzero $v\in(\mathbb Z/14)^{13}$ with a zero coordinate
admits $s,j$ with $sv+r_{13}(j/191)\in\{1,\dots,12\}^{13}$" fails at
$v=2\cdot(1,\dots,13)$, which no pair among all 2674 saves. Correction:
that vector is entirely even, and ST26 Definition 2.1 already discharges it
through its gcd condition — a branch that is nearly empty when $k+1$ is
prime and wide when $k+1=14$, and which had been dropped in transcription.

With the branch restored, and checked exhaustively in 240 s:

> Every $(u_1,\dots,u_{13})\in\mathbb Z^{13}_{>0}$ with
> $\gcd(u_1,\dots,u_{13})=1$ and $u_i\equiv i \pmod{191}$ has the lonely
> runner property. Equivalently $(1,2,\dots,13)\notin J(13,191)$.

ST26 Proposition 1.4 proves the analogue only when $k+1$ and $p$ are both
odd primes, so $k=13$ is outside it; their Section 5.2 reports
$(1,2,\dots,13)$ as the sole survivor of the $\times2$ lifting ladder, and
it is eliminated here with no $\times7$ and no $\times14$ lift.

This is not a bound on the number of runners. LRC(13) is open and the
reason is untouched: ST26 Section 7 names computing $I(13,p,1)$, about
$10^{17}$ tuples at $p=191$, as the bottleneck.

Verifier `compute/q1/cover.c`, certificate `compute/q1/certs/T2_p191.txt`,
independent checks in `compute/q1/check_unsaved.py` and
`compute/q1/spotcheck.c`. See `WALKTHROUGH.md` and `ATTACK.md`.
