# compute — hilbert16-limit-cycles

Verifier plus certificate. Every claimed number needs an independent
check that runs from the files in this folder. SAT UNKNOWN is not a
bound; search residue is not a lower bound.

Replay:

```
./run_all.sh
```

That runs `q1/run_all.sh` (five lines). Exit 0.

No published H(n) is claimed here. The reusable lemmas are the
Chebyshev pullback identity, the radial-cubic uniqueness identities,
the Bézout sheet ceiling, and the first Lyapunov quantity of a
quadratic focus. Shi’s order-3 jet and van der Pol’s Liénard
hypotheses are replayed, not new bounds.
