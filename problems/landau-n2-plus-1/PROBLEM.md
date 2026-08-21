# Landau 4: primes of the form n^2+1

- Slug: `landau-n2-plus-1`
- List: Landau 4 (1912); also Hilbert 8
- Solver: Maths + SuperGrok CLI grok-4.6 xhigh
- Status: open
- Area: Analytic / computational number theory
- Sources: Landau ICM 1912; Iwaniec 1978; OEIS A002496; Wolf arXiv:0803.1456
- Started: 2026-08-17

## Statement

Are there infinitely many primes of the form n^2+1?

## Tonight

Do not claim infinitude. A new bound is a replayable finite record:

- an independently certified list of n with n^2+1 prime, up to a stated N
- the Iwaniec P2s in the same range (at most two prime factors, multiplicity)
- or a prime n^2+1 that is not on the published list we cite

Incomplete search is not a lower bound on the number of such primes.

Done for N=10^6: 54110 primes (matches Wolf π_q(10^12)), 147612 Ω=2
composites, Bateman–Horn ratio 1.0026. No new prime off Wolf/Grantham.
