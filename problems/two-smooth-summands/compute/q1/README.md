# q1 — closed-form templates and polynomial obstruction

Continuation of the 2026-08-17 search. The parent folder already has
the square covering, $F(131486759)=83$, $G(y)$ through $y=79$, and a
failed finite-shift cover. This folder looks at templates that could
have lifted: a closed-form $a(n)$, a floor-divisor rewrite of the
short-interval idea, a two-factor Balog–Sárközy shape, and the whole
polynomial-value family.

Nothing here is an exponent below Balog $4/(9\sqrt{e})$, and nothing
is an infinite covering at any $\varepsilon<1/2$.

## Certificates

| file | what it checks |
| --- | --- |
| `certs/poly_obstruction.json` | degree $d\ge 2$ remainder windows have exponent $1-1/d\ge 1/2$ |
| `certs/infinite_family.json` | explicit $n=Pu+1$ failures of floor-divisor; $n=2^k+q$ failures of largest-power-of-two |
| `certs/q1_search.json` | first holes for square / triangular / cube / power-of-two / floor-divisor at $9/20,2/5,1/3,27/100$, plus two-factor $u\le n^{1/5}$ |

Replay:

```
./run_all.sh
```

A last hole on a prefix is not $N_0$. The square template at exponent
$1/2$ is the covering already recorded in the parent folder.
