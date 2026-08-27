# q2 — twenty-five ideas, five lines backwards

Imagined end-states, then work backwards. No published H(n) moved.

The twenty-five claims and the ranking live in `ideas.md`.
Five lines were scored and assigned:

| Line | Imagined claim | Outcome |
| --- | --- | --- |
| `f-homogeneous/` | homogeneous field with n isolated cycles | dropped; fork: unperturbed homogeneous and quasi-homogeneous centers have 0 isolated cycles |
| `i-lienard/` | beat 2608.17773 B(n), or prove H(3,1)=1 | dropped; fork: B(n) arithmetic replayed; ẋ=y−(αx+βx³), ẏ=−x has 0 or 1 cycle |
| `o-iterated-squaring/` | iterated complex-squaring beats the quadratic ceiling | dropped; fork: z↦z² is 2-to-1, linear in N; Bézout ceiling still quadratic |
| `p-harnack-recurrence/` | Gasull–Santana H(n)+Har(m) beats a table entry | dropped; 1225 pairs, no beat; H_K(5)≥28 already on 2510.11705 |
| `q-pt-darboux/` | PT H_{4,5} field plus one Hopf, H(4)≥29 | dropped; fork: explicit degree-4 Darboux seed with 3 centers; Coppel contact identities |

Replay:

```
./run_all.sh
```

That also runs from the problem compute folder after q1. Exit 0.

Certificates: `f-homogeneous/certs/`, `i-lienard/certs/`, `o-iterated-squaring/certs/`, `p-harnack-recurrence/certs/`, `q-pt-darboux/certs/`. Second language: rustc on every line.
