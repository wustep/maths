# q2 — past 0.38304 on a richer class

q1 certified 0.38304 for pure Example 4 on `{b,1}` and identified
the analytic first-crossing 0.383051356….  This campaign asks
whether a new mix weight, an Example-5 mix, a 3-point law, or a
new 2-sample protocol can certify a frequency strictly above
0.38304, toward 1/2.

It cannot, inside the 2-sample bit-protocol class.  On `{b,1}`
with a product coupling of `(S,T)`, every protocol has
`h(Π_{b,b}) ≤ 1`, so the first-crossing is at most

    f(b) = 1 − (1-b) h(b).

The minimum on the saturation interval is the q1 critical point
0.383051356….  Example 4 already attains it.  Replay:

```
./run_all.sh
```

That is: `ceiling.py` (mpmath dps=80), `verify_ceiling.c` (grid +
golden-section), `replay_ellis.py` (Gilmer Conjecture 1 fails),
the three hunts, and `verify.py` (published constants, small mesh,
hunt summaries).  Certificate: `certs/verify.json`.

The constant is still 0.38304.  This is not 1/2.  Isolated
3-atomic samples live in `certs/hunt_three.json` and are not a
lower bound.
