# Cursor Grok 2026-08-28 — Simon ionization excess, leftover n=36

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q11/`.

## Result

Leftover at the q10 leading $1.1013$. Same
Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7).
q10 stays frozen: aspect $10$, $n=35$, $\varphi=0.9115$,
$1/\gamma=1.10129973$ prints as $1.1013$. Those faces were not
re-enumerated.

The leftover is $n=36$ mid-radius bins at the same split
($2^{36}-1$ faces). Face enumeration is the certificate. Until
that dump is copositive, the printed leading stays $1.1013$.

$R\le 9$ with the mass-opt cut cannot beat $1.1013$.
The withdrawn $1.1168$ stays withdrawn. q1 remainders unchanged.
Bounded excess is still open. Hydrogen $N_0(1)=2$ is not claimed.

Finite $Z$ remains leftover (Lieb integers). A higher-target
probe on the $n=34$ or $n=35$ matrix is not an $n=36$ lift.

## Replay

```bash
problems/simon-ionization-excess/compute/q11/run_all.sh
```

q11 exit 0 without `certs/raise_*.json` is the leftover record.
Certificate, if later certified: `compute/q11/certs/lift.json`.
