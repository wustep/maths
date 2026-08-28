# Cursor Grok 2026-08-28 — Simon ionization excess, leading 1.1013

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q10/`.

## Result

Lift of the q9 leading $1.1017$ and of the printed HPS $1.1185$.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7)
with

$$
\beta_3\ge 0.908018
$$

(the compact bound on $D$-aspect $\le 10$ at $n=35$ bins, target
$\varphi=0.9115$, lifted by mass-stationarity: used aspect $\ge 10$
forces $Q>10/11$). Then

$$
N_c<1.1013Z+3.935\,Z^{1/3}\qquad(Z\ge 4).
$$

$R\le 9$ with the mass-opt cut cannot beat $1.1017$.
The withdrawn $1.1168$ stays withdrawn. q1 remainders unchanged.
Bounded excess is still open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ remains leftover (Lieb integers). The optional
$n=34$ target-$0.9114$ probe was not run and is not this lift.

## Replay

```bash
problems/simon-ionization-excess/compute/q10/run_all.sh
```

q10 exit 0 is the leading-coefficient lift. Certificate:
`compute/q10/certs/lift.json`.
