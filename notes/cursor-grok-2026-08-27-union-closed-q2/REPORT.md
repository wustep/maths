# Union-closed q2, 2026-08-27

Continuation of the `{b,1}` frequency campaign. Search lives in
`problems/union-closed/compute/q2/`.

q1 left a ray-certified 0.38304 for pure Liu Example 4, with
analytic first-crossing 0.383051356…. The job was a certified
number strictly above 0.38304, toward 1/2, on a checkable class.

The constant did not move. Every 2-sample bit protocol on `{b,1}`
has first-crossing at most 0.383051356…, because `h(Π_{b,b})≤1`.
Mixes, a half-target protocol, and scaled `a(t)` sit at or below
that ceiling. Gilmer Conjecture 1 (the KL path to 1/2) fails on
Ellis's n=2 law, replayed at `−0.046797`. Pure Example 4 fails a
constructed 2-mixture at mean 0.38304 (CIID ratio 0.909137);
Python and C agree. That is residue off the ray.

Replay:

```
cd problems/union-closed/compute/q1 && ./run_all.sh
cd problems/union-closed/compute/q2 && ./run_all.sh
```

Certificate: `problems/union-closed/compute/q2/certs/verify.json`.
Not 1/2. Fetched Gilmer 2211.09055v2 and Liu 2306.08824v1.
