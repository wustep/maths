# Cursor Grok 2026-08-27 — Simon ionization excess, leading lift

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q3/`.
Branched from `cursor/simon-ionization-q2-37ce` (PR #94 not on main).

## Result

Dent of the printed fermionic leading coefficient. Same
Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7) with

$$
\beta_3\ge 0.899526
$$

(the q2 compact bound on $D$-aspect $\le 12$, lifted by
mass-stationarity: used aspect $\ge 12$ forces $Q>12/13$). Then

$$
N_c<1.1118Z+3.966\,Z^{1/3}\qquad(Z\ge 4).
$$

This beats printed $1.1185$. It does **not** quote the aspect-$\le 4$
number $1.1087$ as unrestricted. The withdrawn $1.1168$ stays
withdrawn. q1 remainders unchanged. $N_0(Z)-Z$ bounded is still
open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ and $s>3$ remain residue (Lieb integers; two-shell
dipoles).

## Replay

```bash
problems/simon-ionization-excess/compute/q1/run_all.sh
problems/simon-ionization-excess/compute/q2/run_all.sh
problems/simon-ionization-excess/compute/q3/run_all.sh
```

q3 exit 0 is the leading-coefficient dent. Certificate:
`compute/q3/certs/lift.json`.
