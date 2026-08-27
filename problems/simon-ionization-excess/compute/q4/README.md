# q4 — push the leading coefficient past 1.1118

q3 lifted the aspect-12 compact bound to every radial probability
and replaced printed $1.1185$ by $1.1118$. The leftover slack is
the face target (certified $\varphi=0.9055$, SLSQP $\approx 0.9069$)
and the binning error $P_{\max}(1-f_{\min})$.

This folder raises $\varphi$ and/or $n$ on the same mid-radius
Rayleigh, still using the mass-opt dichotomy. The aspect-$\le 4$
number $1.1087$ stays class-only unless a large-aspect cut at
$R=4$ is proved. The withdrawn $1.1168$ stays withdrawn.

```bash
./run_all.sh
```

Cheap probes always run. Face enumerations are stored; the fast
path reads the dumps.
