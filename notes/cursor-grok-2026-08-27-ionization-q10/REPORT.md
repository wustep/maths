# Cursor Grok 2026-08-27 — Simon ionization excess, leftover past 1.1017

Cursor Grok 4.6. Folder `problems/simon-ionization-excess/compute/q10/`.

## Result so far

No new printed leading. q9 (`#119` / `b258707`) stays the notebook
record: compact $\gamma=0.9077156846635223$, $1/\gamma$ prints as
$1.1017$. Independent replay of `compute/q9/verify_lift.py` passed.
The stored $17{,}179{,}869{,}183$ faces were not re-enumerated.

HPS is still v1 only (25 Apr 2025). OpenAlex W4416381655
`cited_by_count` 0. Nam $1.22$ and BGB $1.4811$ (bosonic /
statistics-independent, $Z\ge 12$) do not beat $1.1017$ for
fermions.

Leftover at the proven aspect-10 split:

- Primary: $n=35$, target $0.9115$. SLSQP $\varphi=0.911672$.
  Predicted $1/\gamma=1.101300$, printed $1.1013$ if faces
  certify ($34{,}359{,}738{,}367$ faces). Cut $10/11>\gamma$.
- Optional probe: target $0.9114$ on the $n=34$ matrix.
  Predicted printed $1.1016$. Not an $n=35$ dent.

$R\le 9$ with $Q>R/(R+1)$ cannot beat $1.1017$. Chebyshev
on the endpoint slab does not reopen that line. Finite-Z
integers (Lieb), bounded excess, and $s>3$ along Lemma 4.3
stay leftover.

## Replay

```bash
problems/simon-ionization-excess/compute/q10/run_all.sh
```

Exit 0 with no `certs/raise_*.json` is a recorded leftover, not a
new leading. Do not invent a printed coefficient.
