# q1 — endpoint induction and family search

The 2026-08-17 note has T(S) ≤ ⌈n²/2⌉, so γ_{1,2,−3} ≤ 1/2.
This folder asks whether an endpoint recurrence can move that
constant toward 1/3, and whether a periodic or self-similar seed
beats 1/3 on an infinite family.

Neither happens. Isolated small-n counts stay an incomplete search.

## What was checked

Removing a leftmost or rightmost point loses 1 + N1 + N2 triples, where
N2 (resp. N1) counts {0,1,3} (resp. {0,2,3}) starting at that end.
If min(N1+N2 at left, N1+N2 at right) were always ≤ 2(n−1)/3, induction
would give γ ≤ 1/3. That 2/3 budget already fails at n=5
({0,2,3,4,6} scores 3 and 3). Those sets do not beat the interval.

Both ends can score as high as 9/10 of n−1 (the 11-set
{0,18,27,36,48,54,60,72,81,90,108}). A uniform factor α < 1 for the
endpoint recurrence is not certified. Periodizing the n=9 seed keeps
the end-score ratio near 5/6 and drops T/n² toward 0.30.

The almost-interval {0,…,n−2,n} for n=3m still has T = n²/3+1, by the
residue profile (m+1,m,m−1) and the unique pair whose z is the hole.
No other infinite family in the search exceeds 1/3.

`ends.py` recounts T as n + ∑(N1+N2) over every point, a different
loop from `../count.py`. That identity and the 1/2 bound are rechecked
on the named witnesses.

## Replay

```
./run_all.sh
```

Certificate: `certs/q1.json`. Parent 1/2 check: `../certs/half_bound.json`.
