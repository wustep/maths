# Leftover type-(0,5) and |U|=19 SAT, continued

Replay:

```bash
sh compute/q9/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. This folder
resumes the leftover SAT that q8 did not finish, using the same
encoding:

- leftover-tight SAT on the type-$(0,5)$ orbit representative
  ($k=30$, 625 extras, 32 hosts)
- global leftover SAT $|U|=19$ forbidding type-$(2,1)$ and
  type-$(1,3)$ five-stars

The encoder is imported from `../q8/` and is not rewritten. CNF
rebuilds must match q8 sha256 `cdec5e76…` (leftover-tight) and
`5e3c482a…` (global). Independently replayed type-$(2,1)$ and
type-$(1,3)$ names stay skipped.

A stored Heule-verified DRAT, or a leftover 41-set, would be a
finite-graph fact. Incomplete leftover SAT is not a move of
$40$–$44$. Tiny leftover_k30 smoke is not a certificate.

Native solvers: `sh compute/q9/setup_solvers.sh`.
