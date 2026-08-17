# Attack log

## 2026-08-17 — pick

See `notes/ideation-historical.md`. Landau 4 chosen over the rest of Hilbert/Smale/Landau because it is still open and has a checkable finite list plus Iwaniec's P2 theorem as a nearby object.

## 2026-08-17 — first compute

Enumerate even n (odd n>1 makes n^2+1 even and >2). Trial-split n^2+1; record primes and P2s. Write `compute/` tables and a verifier that ignores the tables and re-derives them.

## 2026-08-17 — certified prefix

`compute/sieve_n2p1.py` then `compute/verify.py`:
n_max=200000, exactly 12391 primes n^2+1 (including 2=1^2+1).
Verifier OK (extra=0 missing=0). First 8 values 2,5,17,37,101,197,257,401
match OEIS A002496. Not a proof of infinitude.
