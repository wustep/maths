# q4 — leading coefficient 1.1118 to 1.1057

q3 lifted the aspect-12 compact bound and replaced printed $1.1185$
by $1.1118$. The leftover slack was the face target and the
mid-radius binning error. This folder raises $\varphi$ and $n$
on the same Rayleigh. The winning row is aspect $10$, $n=26$,
$\varphi=0.9091$, so $Q\ge 0.904414$ on that class. Mass-stationarity
forces any used support of aspect $\ge 10$ to have $Q>10/11$.
Every finitely atomic radial measure reduces to one of those two
classes. That replaces $1.1118$ in the same Section 7 chain.

The aspect-$\le 4$ number $1.1087$ is not used as a class-only
quote: the unrestricted leading $1.1057$ sits below it. The
withdrawn $1.1168$ stays withdrawn. Finite $Z$ and $N_0(Z)-Z$
stay residue.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`, `rebuild.json`.
Independent algebra: `verify_aspect.c`, `verify_aspect.rs`.
Faces dump: `certs/beta3_mid_faces_R10_n26_t0p9091.txt`
(not re-enumerated on the fast path). Second enum:
`certs/faces_rs.txt` (Rust Cramer, copositive). Leftover
probes in `work/`.
