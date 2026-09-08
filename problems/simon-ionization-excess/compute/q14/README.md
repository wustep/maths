# Ionization coefficient 1.1005

The certified inequality is

$$
N_c(Z)<1.1005Z+3.933Z^{1/3}\qquad(Z\ge4).
$$

This improves q13's leading coefficient 1.1006 and the published
HPS bound with leading 1.1185. The bounded-excess conjecture remains
open. [CLAIM.md](CLAIM.md) gives the precise scope and falsifier;
[PROOF.md](PROOF.md) supplies the argument from the matrices to the
electron bound.

Run from any directory:

```bash
/path/to/repo/problems/simon-ionization-excess/compute/q14/run_all.sh
```

Only Python's standard library and `rustc` are required. The replay
rebuilds all 37-bin kernel inequalities and checks two different
rational witnesses. Python proves positive definiteness by exact
Schur complements. Rust checks an explicit Gram matrix with outward
integer intervals. Each independently verifies the discretization
error and HPS constants. Exit 0 means CLAIM.md holds; missing or
invalid certificates return nonzero. Earlier enumeration logs and
solver status flags are not used.

`certificate.json` is the input. `python-result.json` records one
exact replay; it is output, not a premise. `check_rejections.py`
checks positive controls and deliberate corruptions, including the
missing-certificate exit behavior of the shell driver.

The search used `search.py`, NumPy 2.5.3, CVXPY 1.9.2 and Clarabel
0.11.1, with one BLAS thread. Its `optimal_inaccurate` result supplied
candidate entries only. The rational checks determine validity.
To repeat that optional search in an environment with those packages:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 search.py
./run_all.sh
```

The target remains $0.912$ on 37 bins. The edges are rational
approximations to a geometric grid, and the verifiers treat the
stored rational edges as the exact partition. The certified global
floor is $\beta_3\ge0.9087$.
