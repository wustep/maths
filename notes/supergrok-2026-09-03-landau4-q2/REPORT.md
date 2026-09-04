# Landau 4, N=10^7 census

Certified extension of the n^2+1 prime and Iwaniec P2 lists from
n≤10^6 to n≤10^7.

## Record

- 456362 integers n≤10^7 with n^2+1 prime. Equals Wolf Table I /
  OEIS A083844 π_q(10^14)=456362, and π_q(10^13)=156081.
- 1334083 further n in the range with Ω(n^2+1)=2, explicit factors
  on disk.
- Bateman–Horn ratio 0.99990 at N=10^7.
- Prefix of both lists equals the committed N=10^6 files (54110 primes,
  147612 Ω=2 rows).
- No new prime off Wolf / Grantham (that still needs n≳2.5×10^14).
- Infinitude not claimed.

## Replay

```bash
problems/landau-n2-plus-1/compute/q2/run_all.sh
```

C residue sieve 15 s, 56 MB RSS. Independent C trial+Pollard verifier
53 s. Python `verify.py` 885 s. Miller–Rabin bases 2,3,5,7,11,13,17,19,23
(OEIS A014233); the previous set without 17 does not cover n^2+1 at
N=10^7.
