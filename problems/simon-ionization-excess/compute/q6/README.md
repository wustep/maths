# q6 — leading coefficient past 1.1035

q5 lifted the aspect-10 compact bound and replaced printed $1.1057$
by $1.1035$ at $n=30$ bins. The leftover slack was the $P_{\max}$
tax. $R\le 9$ with the mass-opt cut cannot beat $1.1035$.

This folder keeps the split at aspect $10$ and raises $n$ past $30$.
SLSQP plus the $P$ tax predicts $n=32$ at target $\varphi=0.9108$
gives $\gamma=0.906992$ and $1/\gamma=1.102546$ (printed $1.1026$
if faces certify). Mass-stationarity still forces any used support
of aspect $\ge 10$ to have $Q>10/11$.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue.

```bash
./run_all.sh
```

Certificates, when present: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Leftover probes in `work/`.
