# Compute — affine copies of {0,1,3}

Aaronson’s T(S) = #{(x,y,z)∈S³ : x+2y=3z}.

## Bound

`verify_half.py` checks T(S) ≤ ⌈n²/2⌉:

- the sum identity ∑(1+2 min(j−1,n−j)) = ⌈n²/2⌉ through n=399
- the fibre injection on exhaustive small subsets and 2360 random sets
- named witnesses (interval, {0,1,3}, n=7 sporadic, almost-interval)

Output: `certs/half_bound.json`.

`verify_interval.py` checks the interval closed form through n=79.

## Search residue (does not move 1/3)

| script | what |
|---|---|
| `search_exact.c` | exact max T on n-subsets of {0..4n} |
| `search_small.py` | same in Python, smaller n |
| `search_periodic.py` | lifts of P ⊂ ℤ/mℤ |
| `search_two_ap.py` | two/three APs of difference 3 |
| `search_intervals.py` | two intervals, {0,1,3}-blocks |
| `search_local.py` | hill-climb |
| `energy.py` | E(S,2S) versus the interval |

## Witnesses

- `certs/n7_triples.json` — the 18 solutions in {0,3,6,8,9,12,18}
- `plot_constants.py` → `../figures/constants.png`

## q1 (2026-08-27)

Endpoint recurrence and family search. Does not move 1/2.
Replay: `q1/run_all.sh`. Cert: `q1/certs/q1.json`.
