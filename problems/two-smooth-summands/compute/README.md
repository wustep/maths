# Compute — two smooth summands

Independent checks for Green #59 / Erdős #334. Nothing here is a
published-exponent improvement.

| script | what it certifies |
| --- | --- |
| `trivial_cover.py` | \(F(n)<2\sqrt{n}+1\) on a stated range, via the square-plus-remainder split |
| `obstruction.py` | Jacobi form of the negative-pseudosquare lemma; exact \(F(131486759)=83\) |
| `g_of_y.py` / `g_of_y.c` | first missing sum \(G(y)\) by exact bitset coverage of \(S_y+S_y\) |
| `covering_search.py` | residue-class and factorization templates; prints holes |
| `f_exceptions.c` | exact exceptions to \(F(n)\le n^{p/q}\) via \(F^q>n^p\) |
| `plot_exceptions.py` | the two figures under `../figures/` |

Heavy \(G(y)\) (y ≥ 37) should use the C bitset:

```
cc -O3 -std=c11 -o g_of_y_c g_of_y.c
./g_of_y_c 73 131486759 200000
```

Exact exception sweeps:

```
cc -O3 -std=c11 -o f_exceptions f_exceptions.c -lm
./f_exceptions 0.4 1000000 2 5
```

A hole-free prefix is not an asymptotic bound. See `CONSTANTS.md`.
