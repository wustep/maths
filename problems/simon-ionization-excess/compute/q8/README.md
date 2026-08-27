# q8 — leading coefficient 1.1021 to 1.1020

q7 lifted the aspect-10 compact bound and replaced printed $1.1026$
by $1.1021$ at $n=33$ bins, target $0.9111$. The leftover slack
was unused $\varphi$: SLSQP sits at $0.91122$. $R\le 9$ with the
mass-opt cut cannot beat $1.1021$.

This folder keeps the split at aspect $10$ and raises the face
target to $0.9112$ on the same $n=33$ matrix. Faces certify
$Q\ge 0.907507$. Mass-stationarity still forces any used support
of aspect $\ge 10$ to have $Q>10/11$. That replaces $1.1021$ in
the same Section 7 chain.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue. $n=34$ at this
split is still a predicted $1.1017$ if faces certify.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Faces dump: `certs/beta3_mid_faces_R10_n33_t0p9112.txt`
(not re-enumerated on the fast path). Leftover probes in `work/`.
