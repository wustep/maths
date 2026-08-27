# q3 — lift the aspect-12 compact bound

The q2 compact certificate gives $Q\ge 0.899526$ on $D$-aspect
$\le 12$, so $1/Q\le 1.11170$ *in that class*. Mass-stationarity
forces any used support of aspect $\ge 12$ to have $Q>12/13$.
Every finitely atomic radial measure reduces to one of those two
classes. Truncation plus shell approximation extends the bound to
HPS $D_3$. That replaces $b(3)<1.1185$ in the same Section 7 chain.

Do not quote the aspect-$\le 4$ number $1.1087$ as unrestricted.
The withdrawn $1.1168$ tail lift stays withdrawn.

```bash
./run_all.sh
```

Certificates: `certs/lift.json`, `leading.json`,
`aspect_identities.json`, `lift_stdlib.json`. Independent algebra:
`verify_aspect.c`, `verify_aspect.rs`. The $R=12$ faces dump is
`../q2/certs/beta3_mid_faces_R12_n22.txt` (not re-enumerated on
the fast path). Leftover probes in `work/` (finite $Z$, $s>3$).
