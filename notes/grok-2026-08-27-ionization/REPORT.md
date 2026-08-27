# Grok 2026-08-27 — Simon ionization excess

Cursor Grok 4.6 xhigh. Folder `problems/simon-ionization-excess/`.

## Result

Same Hundertmark–Pattakos–Schulz 2025 chain (arXiv:2504.18487v1 §7),
tighter arithmetic:

- $N_c < b(2)Z + 2.953 Z^{1/3}$ for $Z\ge 2$ (printed 2.96)
- $N < b(3)Z + 3.892 Z^{1/3} + 0.0134 + 0.184 Z^{-1/3} + 0.0196 Z^{-2/3}$
  for $Z\ge 4$ (printed 3.90)
- $N_c < 1.1185 Z + 3.9781 Z^{1/3}$ for $Z\ge 4$ (printed 4)

Leading coefficient 1.1185 unchanged. Bounded excess still open.

The handle is the interval for $a_1(N/Z)$. HPS maximised on
$[b(3),5/2]$ and quoted the left endpoint. Independently the max on
that interval is at $5/2$. On the Prop. 2.5 range $Z\ge 4$, Lieb gives
$N/Z < 9/4$, and there the max is at the left, $a_1<3.892$.

## Replay

```bash
problems/simon-ionization-excess/compute/q1/run_all.sh
```

Certs: `compute/q1/certs/hps_tight.json`, `hps_replay.json`,
`hminus.json`, `n0_z1.json`. Lean: `problems/simon-ionization-excess/lean/`.

Hydrogen $N_0(1)=2$ is a Hylleraas replay, already in Lieb 1984.
