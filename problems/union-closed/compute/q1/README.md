# q1 — pure Example 4 on the {b,1} ray

The 2026-08-17 campaign certified 0.38285 at mix weight β=1/5 and
stopped the β scan at 0.40.  On this ray the first-crossing keeps
rising through β=1.

For β=1 and b in (1−1/√2, 1/2], Liu Example 4 saturates
Π_{b,b}(0,0)=1/2, so the equality mean is 1−(1−b)h(b).  The minimum
solves

    h(b) = (1−b) log2((1−b)/b)

and equals 0.3830513565868….  The claimed 5-decimal constant is
0.38304, strictly below that crossing and strictly above 0.38285.

Replay:

```
./run_all.sh
```

That is: `solve_crossing.py` (mpmath dps=80), `verify.py` (published
constants, analytic residual, 4500×3500 mesh), and `verify.c` (same
mesh, nested loop).  Certificate: `certs/verify.json`.

This is the Gilmer constant for the optimizer family {b,1}, the same
hypothesis class as Liu Theorem 13.  It is not 1/2, and it is not a
bound for every measure on [0,1].  Isolated 2-atomic samples live in
`certs/hunt_two_atomic.json` and are not a lower bound.
