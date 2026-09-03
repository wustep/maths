# Grok 4.6 / 2026-09-03 — Simon ionization excess, q13

Grok 4.6. Folder `problems/simon-ionization-excess/compute/q13/`.

## Result

Dent. Printed leading moves from $1.1010$ to $1.1006$.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7).

$$
N_c < 1.1006 Z + 3.933 Z^{1/3}\qquad(Z\ge 4).
$$

q11 stays frozen: aspect $10$, $n=36$, $\varphi=0.9117$,
$1/\gamma=1.100940$ prints as $1.1010$. q12 $n=37$ leftover
shards were not resumed.

Gray-code faces at aspect $10$, $n=37$, target $\varphi=0.9119$:
$137{,}438{,}953{,}471$ faces, copositive, $0$ skips,
$\min\varphi=0.912085$, compact $\gamma=0.908606$,
$1/\gamma=1.100587$ prints as $1.1006$. Cut $10/11>\gamma$.
One thread, about 2 MB RSS.

$R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1006$. The withdrawn
$1.1168$ stays withdrawn. q1 remainders unchanged. Bounded
excess is still open.

## Replay

```bash
problems/simon-ionization-excess/compute/q13/run_all.sh
```

Certificate: `compute/q13/certs/lift.json`.
