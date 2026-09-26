# Finite handles

Prefer an `open` leaf. One leaf per campaign folder.

| Leaf | Required evidence | State |
| --- | --- | --- |
| Certified prefix $n\le 10^6$ | Residue sieve plus independent trial+Pollard; Wolf $\pi_q(10^{12})=54110$ | certified (`compute/`) |
| Certified prefix $n\le 10^7$ | C residue sieve plus independent C/Python trial+Pollard; Wolf $\pi_q(10^{14})=456362$ | certified (`q2/`) |
| Certified prefix $n\le 10^8$ | C residue sieve plus independent C trial+Pollard; Wolf $\pi_q(10^{16})=3954181$; $\Omega=2$ count $12172983$ | certified (`q3/`) |
| A prime $n^2+1$ off Grantham–Graves | Construction with $n\gtrsim 2.5\times 10^{14}$ | blocked (range) |

The Iwaniec $P_2$ table on a stated range is not in Wolf, OEIS A083844, or Grantham–Graves. Infinitude of primes $n^2+1$ is not a finite handle.
