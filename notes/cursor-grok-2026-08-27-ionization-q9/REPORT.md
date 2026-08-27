# Cursor Grok 2026-08-27 — Simon ionization excess, leading 1.1017

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q9/`.

## Result

Dent of the q8 leading $1.1020$ and of the printed HPS $1.1185$.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7)
with

$$
\beta_3\ge 0.907716
$$

(the compact bound on $D$-aspect $\le 10$ at $n=34$ bins, target
$\varphi=0.9113$, lifted by mass-stationarity: used aspect $\ge 10$
forces $Q>10/11$). Then

$$
N_c<1.1017Z+3.936\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1020$ (residue).
The withdrawn $1.1168$ stays withdrawn. q1 remainders unchanged.
$N_0(Z)-Z$ bounded is still open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ remains residue (Lieb integers). $n=35$ at aspect 10
is still a predicted $1.1013$ if faces certify.

## Replay

```bash
problems/simon-ionization-excess/compute/q9/run_all.sh
```

q9 exit 0 is the leading-coefficient dent. Certificate:
`compute/q9/certs/lift.json`.
