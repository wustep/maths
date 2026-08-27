# q3 — ten ideas, five lines backwards

Imagined end-states, then work backwards. No published H(n) moved.

The ten claims and the ranking live in `ideas.md`. Official three
plus two extras so the menu was not left idle:

| Line | Imagined claim | Outcome |
| --- | --- | --- |
| `ff-two-well/` | two-well cubic, 14 Abelian zeros | dropped; fork: energy, I(0), L1 at both wells |
| `gg-pt-lyapunov/` | L1 rank 29 at the three PT centers | dropped; fork: unperturbed L1 = 0; two L1(μ) |
| `hh-qh-melnikov/` | four zeros of M1 on ẋ=2y, ẏ=−x³ | dropped; fork: first-order cyclicity ≤ 1 |
| `ii-complex-cube/` | holomorphic cube attains 9 sheets | dropped; fork: 3-to-1, N=3n+2, weaker than T3 |
| `jj-weak-hilbert/` | beat Z(2,n) by one Abelian zero | dropped; fork: radial family attains the formula |

Pruned without a worker: KK constructive +1 (2 does not beat 28),
OO five Abelian zeros (not H(3)≥14), LL cubic+line, MM Abel two
zeros (recycled I), NN PT algebraic extra (recycled Q).

Replay:

```
./run_all.sh
```

That also runs from the problem compute folder after q1 and q2.
Exit 0.

Certificates: `ff-two-well/certs/`, `gg-pt-lyapunov/certs/`,
`hh-qh-melnikov/certs/`, `ii-complex-cube/certs/`,
`jj-weak-hilbert/certs/`. Second language: rustc on every line.
