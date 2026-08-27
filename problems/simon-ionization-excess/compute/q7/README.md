# q7 — leading coefficient 1.1026 to 1.1021

q6 lifted the aspect-10 compact bound and replaced printed $1.1035$
by $1.1026$ at $n=32$ bins. The leftover slack was the $P_{\max}$
tax. $R\le 9$ with the mass-opt cut cannot beat $1.1026$.

This folder keeps the split at aspect $10$ and raises $n$ to $33$.
Mid-radius faces certify $Q\ge 0.907407$ (target $\varphi=0.9111$).
Mass-stationarity still forces any used support of aspect $\ge 10$
to have $Q>10/11$. That replaces $1.1026$ in the same Section 7
chain.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Faces dump: `certs/beta3_mid_faces_R10_n33_t0p9111.txt`
(not re-enumerated on the fast path). Leftover probes in `work/`.
