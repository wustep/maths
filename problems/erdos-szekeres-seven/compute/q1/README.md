# q1 — replay the 32-point lower-bound witness

This directory gives exact integer coordinates for one instance of the
classical Erdős–Szekeres construction at `k=7`. The construction follows
Duque–Fabila-Monroy–Hidalgo-Toscano, arXiv:1602.03075v2, Section 2.

The certificate is `points.csv`. `generate_certificate.py` reconstructs it
from the recurrences in the paper. Two exact verifiers then check it by
different algorithms:

- `verify.py` uses the 4-subset criterion and exact triangle containment;
- `verify.c` enumerates every 7-subset and computes its convex hull by the
  monotone-chain algorithm.

Replay with:

```bash
./run_all.sh
```

The witness proves only the already-published inequality `ES(7) >= 33`.
It is not a new bound.
