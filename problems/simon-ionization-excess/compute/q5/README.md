# q5 — leading coefficient past 1.1057

q4 lifted the aspect-10 compact bound and replaced printed $1.1118$
by $1.1057$. The leftover slack is still the compact $\gamma$ at
the split where $R/(R+1)$ exceeds $\gamma$. $R\le 9$ with the
mass-opt cut cannot beat $1.1057$ ($9/10$ gives $1.1111$).

This folder raises $n$ on the same mid-radius Rayleigh at
aspect $10$, or records a residue if no certified row beats
$1.1057$.

```bash
./run_all.sh
```

Certificates, when present: `certs/lift.json`, `leading.json`,
`aspect_identities.json`. Leftover probes in `work/`.
