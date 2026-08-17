# Walkthrough — Landau 4, first night

## 0. Missing degree of freedom

Infinitude of primes n^2+1 is the headline. Tonight is a certified finite prefix
and the Iwaniec P2s next to it, not a proof.

## 1. False starts

Hilbert 16 / Smale 13 (limit cycles) and Smale 7 (Fekete) were the other
computational reads. Both need a heavier pipeline than a primality sieve.
Landau 3 is already checked through 2^64. See `notes/picks/ideation-historical.md`.

## 2. Useful failure

The first sieve skipped n=1, so 2 was missing. The independent verifier
caught it. That is the point of the verifier.

## 3. The click

Only even n (and n=1) can work. A square-root sieve for primes q=1 mod 4
marks composites; deterministic 64-bit Miller-Rabin certifies the rest.

## 4. Argument

For 1 <= n <= 200000, there are exactly 12391 values of n with n^2+1 prime.
Replay: `python3 compute/sieve_n2p1.py --n-max 200000` then
`python3 compute/verify.py`. The verifier ignores the stored list and
re-tests every even n.

This does not prove infinitude. It is a checkable prefix.

## 5. Computer residue

`compute/n2p1.json`. First values match OEIS A002496: 2, 5, 17, 37, 101, ...
P2 classification in the same file is incomplete (trial bound).

## 6. Proven vs open

Proven here: the count 12391 through n=200000, by a second pass.
Open: Landau 4.
