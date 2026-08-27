# Cursor Grok 2026-08-27 — Simon ionization excess, leading 1.1020

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q8/`.

## Result

Dent of the q7 leading $1.1021$ and of the printed HPS $1.1185$.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7)
with

$$
\beta_3\ge 0.907507
$$

(the compact bound on $D$-aspect $\le 10$ at $n=33$ bins, target
$\varphi=0.9112$, lifted by mass-stationarity: used aspect $\ge 10$
forces $Q>10/11$). Then

$$
N_c<1.1020Z+3.937\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1021$ (residue).
The withdrawn $1.1168$ stays withdrawn. q1 remainders unchanged.
$N_0(Z)-Z$ bounded is still open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ remains residue (Lieb integers). $n=34$ at aspect 10
is still a predicted $1.1017$ if faces certify.

## Replay

```bash
problems/simon-ionization-excess/compute/q8/run_all.sh
```

q8 exit 0 is the leading-coefficient dent. Certificate:
`compute/q8/certs/lift.json`.
