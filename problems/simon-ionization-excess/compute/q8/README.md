# q8 — past the leading coefficient 1.1021

q7 lifted the aspect-10 compact bound and replaced printed $1.1026$
by $1.1021$ at $n=33$ bins. The leftover slack is the $P_{\max}$
tax, and unused $\varphi$ at that same $n=33$ matrix. $R\le 9$
with the mass-opt cut cannot beat $1.1021$.

This folder keeps the split at aspect $10$. The cheap live line
is a higher face target on the $n=33$ mid-radius matrix; the
predicted $n=34$ row prints $1.1017$ if faces certify. Mass-
stationarity still forces any used support of aspect $\ge 10$
to have $Q>10/11$.

The withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue. $s>3$ along Lemma 4.3 stays residue.

```bash
./run_all.sh
```

Certificates, once a row certifies: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Leftover probes in `work/`.
