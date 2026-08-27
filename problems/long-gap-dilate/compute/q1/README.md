# q1 — rising factorials, a SAT push past 71, and more families

The 2026-08-17 start left no `compute/qN/`. This folder is the first
named search. Shakan’s universal 2 is still the published record.

## What was tried

1. Rebuild the homogeneous Rédei slice and Wronskian on every stored
   SAT witness, and expand the unused rising-factorial polynomial
   `w(d,t) = d ∏_a (t+da+1)_m` far enough to read the actual Alon
   degrees of `u,v`. The extra Stirling terms do not cut those degrees
   below the wall `k = nm-p+1`. At the scales `C = 2.5` and `C = 3`
   one has `k ≥ p`, so the middle-coefficient list is empty.
2. Downward SAT for `G(p, round √p)` on the next primes after 71, with
   a hard process kill. `certs/sat_extend.jsonl` stores SAT upper
   bounds `G(73,9)≤24`, `G(79,9)≤26`, `G(83,9)≤27`, `G(89,9)≤30`.
   Cadical proves `T=23` unsat at `p=73`, so that value is 23 or 24.
   The `T` just below each upper bound timed out. A timeout is an
   incomplete search, not a lower bound. The exact table still ends
   at `p=71`.
3. More families (quadratic rulers, Paley prefixes, cyclotomic cosets,
   Singer orbits including the `(73,9,1)` set `{2^k}` in `F_73`, and a
   longer anneal) through `p = 200`. No infinite family with
   `max_d g ≤ (2+ε)√p`.

## Replay

```
cd problems/long-gap-dilate/compute/q1
./run_all.sh
```

Parent replay is unchanged:

```
cd problems/long-gap-dilate
sh compute/run_all.sh
```

Does not claim a universal `C>2`.
