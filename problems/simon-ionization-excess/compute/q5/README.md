# q5 — leading coefficient 1.1057 to 1.1035

q4 lifted the aspect-10 compact bound and replaced printed $1.1118$
by $1.1057$. The leftover slack was the $P_{\max}$ tax on $n=26$
bins. $R\le 9$ with the mass-opt cut cannot beat $1.1057$.

This folder keeps the split at aspect $10$ and raises $n$ to $30$.
Mid-radius faces certify $Q\ge 0.906238$ (target $\varphi=0.9103$).
Mass-stationarity still forces any used support of aspect $\ge 10$
to have $Q>10/11$. That replaces $1.1057$ in the same Section 7
chain.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Faces dump: `certs/beta3_mid_faces_R10_n30_t0p9103.txt`
(not re-enumerated on the fast path). Intermediate certified
row: $R=10$, $n=28$, leading $1.1046$. Leftover probes in `work/`.
