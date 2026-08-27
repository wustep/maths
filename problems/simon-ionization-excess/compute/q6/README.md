# q6 — leading coefficient 1.1035 to 1.1026

q5 lifted the aspect-10 compact bound and replaced printed $1.1057$
by $1.1035$ at $n=30$ bins. The leftover slack was the $P_{\max}$
tax. $R\le 9$ with the mass-opt cut cannot beat $1.1035$.

This folder keeps the split at aspect $10$ and raises $n$ to $32$.
Mid-radius faces certify $Q\ge 0.906992$ (target $\varphi=0.9108$).
Mass-stationarity still forces any used support of aspect $\ge 10$
to have $Q>10/11$. That replaces $1.1035$ in the same Section 7
chain.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Faces dump: `certs/beta3_mid_faces_R10_n32_t0p9108.txt`
(not re-enumerated on the fast path). Leftover probes in `work/`.
