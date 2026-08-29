# Cursor Grok 2026-08-29 — Simon ionization excess, n=37 leftover

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q12/`.

## Result so far

Residue. The q11 printed leading $1.1010$ is unchanged.
Same Hundertmark–Pattakos–Schulz chain (arXiv:2504.18487v1, §7).
q11 stays frozen: aspect $10$, $n=36$, $\varphi=0.9117$,
$1/\gamma=1.100940$ prints as $1.1010$. Those faces were not
re-enumerated. q10 $n=35$ stays frozen too.

Copied the q11 stack into `compute/q12/` and raised `NMAX` from
$36$ to $40$ so $n=37$ loads. $R\le 9$ with $Q>R/(R+1)$ cannot
beat $1.1010$. Chebyshev does not reopen that line. Finite-$Z$
integers and $s>3$ stay leftover. Whether $n=37$ prints below
$1.1010$ is a hypothesis until faces certify.

The withdrawn $1.1168$ stays withdrawn. q1 remainders unchanged.
Bounded excess is still open.

## Replay

```bash
problems/simon-ionization-excess/compute/q12/run_all.sh
```

Exit 0 without `certs/lift.json` is residue.
