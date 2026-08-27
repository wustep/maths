# Line I — Liénard H(2n+1, 5) and the (3,1) family

Status: imagined, then work backwards.

Imagined certificate. An explicit Liénard field with deg f = 2n+1,
deg g = 5 has more than
B(n) = 2n + ⌊n/3⌋ + ⌊(n+1)/3⌋ − 2
isolated cycles (arXiv:2608.17773v1 Theorem 3), or every field
ẋ = y − F(x), ẏ = −x with deg F ≤ 3 has at most one cycle.

Expected drop. The origin-plus-lips compatibility is the paper’s
obstruction. Full H(3,1)=1 is open.

Fork to keep. (1) Replay B(n) against Han–Romanovski
2\lfloor(N-1)/3\rfloor + \lfloor(N-1)/2\rfloor for N = 2n+1; record where B is larger
(n ≥ 7) and where it is not. This is their arithmetic, not a
planar H(n). (2) The named family
ẋ = y − (αx + βx³), ẏ = −x
satisfies Zhang Zhifen / Liénard uniqueness when β > 0
(f/g = α + βx² strictly monotone on x ≠ 0): at most one cycle.
For β = 0, α ≠ 0 the field is linear damping and has none.
Not a bound on H(3).

Replay: `./run.sh`
