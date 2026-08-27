# q7 — leading coefficient past 1.1026

q6 lifted the aspect-10 compact bound and replaced printed $1.1035$
by $1.1026$ at $n=32$ bins. The leftover slack was the $P_{\max}$
tax. $R\le 9$ with the mass-opt cut cannot beat $1.1026$.

This folder keeps the split at aspect $10$ and raises $n$ past $32$.
Mass-stationarity still forces any used support of aspect $\ge 10$
to have $Q>10/11$. A certified compact $\gamma$ with $10/11>\gamma$
and $1/\gamma<1.1026$ replaces $1.1026$ in the same Section 7
chain.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`
once a row is certified. Independent algebra: `verify_aspect.c`,
`verify_aspect.rs`. Leftover probes in `work/`.
