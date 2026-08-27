# Cursor Grok 2026-08-27 — Simon ionization excess, leading 1.1057

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q4/`.

## Result

Dent of the q3 leading $1.1118$ and of the printed HPS $1.1185$.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7)
with

$$
\beta_3\ge 0.904414
$$

(the compact bound on $D$-aspect $\le 10$, lifted by
mass-stationarity: used aspect $\ge 10$ forces $Q>10/11$). Then

$$
N_c<1.1057Z+3.946\,Z^{1/3}\qquad(Z\ge 4).
$$

The unrestricted leading sits below the old aspect-$\le 4$
class-only number $1.1087$. The withdrawn $1.1168$ stays
withdrawn. q1 remainders unchanged. $N_0(Z)-Z$ bounded is still
open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ remains residue (Lieb integers).

## Replay

```bash
problems/simon-ionization-excess/compute/q1/run_all.sh
problems/simon-ionization-excess/compute/q2/run_all.sh
problems/simon-ionization-excess/compute/q3/run_all.sh
problems/simon-ionization-excess/compute/q4/run_all.sh
```

q4 exit 0 is the leading-coefficient dent. Certificate:
`compute/q4/certs/lift.json`.
