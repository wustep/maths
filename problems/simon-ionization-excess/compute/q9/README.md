# q9 — leading coefficient 1.1020 to 1.1017

q8 lifted the aspect-10 compact bound and replaced printed $1.1021$
by $1.1020$ at $n=33$ bins, target $0.9112$. The leftover slack
was the $P_{\max}$ tax: more bins shrink $q=R^{1/n}$. $R\le 9$
with the mass-opt cut cannot beat $1.1020$.

This folder keeps the split at aspect $10$ and raises the
mid-radius bin count to $34$. Faces certify $Q\ge 0.907716$
(target $0.9113$). Mass-stationarity still forces any used
support of aspect $\ge 10$ to have $Q>10/11$. That replaces
$1.1020$ in the same Section 7 chain.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue. $n=35$ at this
split is still a predicted $1.1013$ if faces certify.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Faces dump: `certs/beta3_mid_faces_R10_n34_t0p9113.txt`
(not re-enumerated on the fast path). Leftover probes in `work/`.
