# q10 — prescribed automorphisms

A construction family for $\ell_2(r,2)$ that does not start from a known
covering. Instead of perturbing the certified 50-set, fix a $\sigma\in GL(r,2)$
of odd prime order $p$ and look only at $\sigma$-invariant sets. Such a set is
$k$ full orbits of size $p$ together with $m$ of the $2^c-1$ nonzero fixed
vectors, so $n=pk+m$ — usually a very short list of possibilities, and the
whole search collapses from $\binom{2^r-1}{n}$ to $\binom{\#\text{orbits}}{k}
\binom{2^c-1}{m}$.

## Files

| file | what it does |
| --- | --- |
| `setup.py` | the original $r=10$, order-7, 1-dimensional-fixed-space instance: orbits, partner pairs, centraliser classes |
| `sigma_setup.py` | general $\sigma$ builder — emits a column table plus its centraliser classes on orbits and on partner pairs |
| `fixed_classes.py` | centraliser classes of $m$-subsets of the fixed vectors |
| `orbit_search.c` | first search, $r=10$ order 7 hardcoded |
| `orbit_search_g.c` | general $r$, fixed space of dimension $0$ or $1$; also carries the randomised orbit-level search |
| `orbit_search_f.c` | general $r$ and general fixed space |
| `layer_lemma.py` | per-layer counting bound |
| `prime_orders.py` | which prime orders are possible at all, and what each would cost |
| `run_q10_checks.sh` | replay: rebuilds every artifact, runs the controls, reruns every search |

## The reduction

Coverage is tracked orbit-wise. With $\Delta$ for sums,

| source | covers |
| --- | --- |
| orbit $i\in S$ | orbit $i$ |
| sums inside orbit $i$ | $\mathrm{orb}(r_i+\sigma^d r_i)$, $d=1..p-1$ |
| sums across $i\ne j$ | $\mathrm{orb}(r_i+\sigma^d r_j)$, $d=0..p-1$ |
| orbit $i$ with fixed $g$ | $\mathrm{orb}(r_i+g)$ — a single orbit |
| fixed $g\in S$ | $g$ |
| fixed $g$ with fixed $h$ | $g+h$ |

Any of those sums can land on a fixed vector, which gets its own bit. Radius
$\le2$ is exactly "every bit set", which is what the C searches decide.

Two counting bounds cut the case list before any search. $\sigma$ has odd
order, so $V=M\oplus T$ canonically with $T$ the fixed space and the projection
onto $T$ is $\pi_T(v)=\sum_{i<p}\sigma^i(v)$. Call $\pi_T(v)$ the *layer*.
Every sum above has a forced layer, which gives

* **touched layers** (`prime_orders.py`): the layers a solution can reach lie in
  $\{0\}\cup\{t_i\}\cup\{t_i+t_j\}\cup\{t_i+g\}$, so $1+k+\binom k2+km\ge2^c$;
* **layer fill** (`layer_lemma.py`): a layer receiving no cross-orbit sum holds
  at most $k$ covered orbits (plus the internal sums when the layer is $0$), so
  if that is short of $L=\#\text{orbits}/2^c$ then every layer needs a cross
  pair and $\binom k2$ must cover them.

## Controls

* **Encoding.** The orbit masks reproduce the flat syndrome sweep hole for
  hole on hundreds of random selections, for every $\sigma$ used.
* **Positive.** The same code finds $\sigma$-invariant coverings at $n=63$
  ($r=10$) and $n=92,100,111$ ($r=11$), each re-verified $1024/1024$ or
  $2048/2048$ by the independent flat sweep. The family is not vacuous.
* **Pruning.** Rerunning $r=10$, $n=49$ with `--noprune` visits all
  $\binom{144}{5}=481{,}008{,}528$ subsets per class and returns the same
  verdict.
* **Two implementations.** `orbit_search_g.c` and `orbit_search_f.c` share no
  search code and agree on every case both can run.
