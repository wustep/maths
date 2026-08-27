# Line P — Gasull–Santana Harnack recurrence

Status: imagined, then work backwards.

Imagined certificate. Corollary 2 of arXiv:2510.11705v2,
H(n+m) ≥ H(n) + Har(m) with
Har(m) = (m−1)(m−2)/2 + [1+(−1)^m]/2,
beats a published table entry for some N = n+m ≤ 50.

Expected drop. Har(4) = 4, so H(6) ≥ H(2)+4 = 8, far below
Prohens–Torregrosa 53. Weaker than H(n+1) ≥ H(n)+1 when m = 1,
and much weaker than the Chebyshev factor m².

Fork to keep. Replay Har(m) and the one-step table
L_pub(n) + Har(m) against the published seeds used in q1
(Prohens–Torregrosa Theorem 1, Han–Li as quoted, small-n 4 and
13). Record that no N ≤ 50 is improved. Also replay
H_K(n) ≥ H(n−1): the printed H_K(5) ≥ 28 is already on
2510.11705 and depends on the unreplayed H(4) ≥ 28 seed. Do not
cite it as found here. Not a dent of planar H(n).

Replay: `./run.sh`
