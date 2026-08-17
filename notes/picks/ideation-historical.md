# Ideation: one historical problem (2026-08-17)

Lists: `lists/hilbert.md`, `lists/smale.md`, `lists/landau.md` (main `2fc53c5`).

## Rejected tonight

- Hilbert 1–7, 10, 11, 14, 17–19, 21: resolved or too vague, no finite leftover.
- Hilbert / Smale RH, P vs NP, Navier–Stokes: no isolated certificate.
- Hilbert 16 / Smale 13: no effective Hilbert number; a new limit-cycle example is possible but needs a heavy ODE pipeline we do not have up.
- Smale 7 (Fekete on S^2): computational, but the published energy tables are a moving target and a slightly better N-point energy is a weak dent.
- Smale 16 Jacobian n=2: still open; n≥3 has a 2026 claim without consensus. Not a one-night algebra search.
- Landau 1 Goldbach: verified to huge bounds; we will not beat that.
- Landau 2 twins: Zhang/Polymath is the theorem side; a new twin pair is not a dent.
- Landau 3 Legendre: already checked through 2^64 via maximal-gap tables.

## Picked: Landau 4

Infinitely many primes n^2+1. Still open. Finite handles that count:

1. Independently enumerate and primality-certify n^2+1 primes up to a stated N (replayable table, not OEIS trust).
2. Classify Iwaniec P2s (n^2+1 with at most two prime factors) in the same range.
3. Compare the count to the Landau–Shanks / Bateman–Horn prediction. A match is a check, not a proof.
4. A previously unpublished prime would be a construction; a proof of infinitude is out of scope.

Folder: `problems/landau-n2-plus-1`.
