# Cursor Grok 2026-08-27 — Simon ionization excess, leading 1.1035

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q5/`.

## Result

Dent of the q4 leading $1.1057$ and of the printed HPS $1.1185$.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7)
with

$$
\beta_3\ge 0.906238
$$

(the compact bound on $D$-aspect $\le 10$ at $n=30$ bins, lifted by
mass-stationarity: used aspect $\ge 10$ forces $Q>10/11$). Then

$$
N_c<1.1035Z+3.941\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1057$ (residue).
The withdrawn $1.1168$ stays withdrawn. q1 remainders unchanged.
$N_0(Z)-Z$ bounded is still open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ remains residue (Lieb integers).

## Replay

```bash
problems/simon-ionization-excess/compute/q5/run_all.sh
```

q5 exit 0 is the leading-coefficient dent. Certificate:
`compute/q5/certs/lift.json`. Intermediate certified row
$R=10$, $n=28$ prints $1.1046$.
