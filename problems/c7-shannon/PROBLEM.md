# Shannon capacity of $C_7$, fifth strong power

- Slug: `c7-shannon`
- Solver: Grok 4.6
- Status: open
- Area: Zero-error information theory
- Sources: Polak–Schrijver 367-set; Itty–Rosin–Carstensen–Reichman 2026;
  Gao 2026 recursive; Lean-verified bounds arXiv:2607.29681
- Started: 2026-08-16

## Statement

Identify vertices of $C_7$ with $\mathbb Z/7\mathbb Z$. In the strong
product $C_7^{\boxtimes d}$, distinct $x,y\in(\mathbb Z/7\mathbb Z)^d$
are adjacent iff the circular distance is at most 1 in every coordinate.
The Shannon capacity satisfies
$\Theta(C_7)\ge\alpha(C_7^{\boxtimes d})^{1/d}$.

July 2026 papers improved the *capacity* lower bound via high powers
($\Theta(C_7)\ge 3.258805\ldots$ from a profile on the 200th power,
Lean-verified). The largest published independent set in the *fifth*
power is still the Polak–Schrijver set of size 367.

## Tonight

Find an independent set of size $\ge 368$ in $C_7^{\boxtimes 5}$, or
a certified obstruction that 367 is maximum. Emit the set and a verifier
that checks pairwise circular distance $>1$ in some coordinate.

Do not claim a new $\Theta(C_7)$ unless the 5th-root actually beats
$3.258805$. A 368-set in dimension 5 is already a finite new bound.

A set that misses a letter in any coordinate has size at most $345$.
Hamming distance $11$ from the published $367$-set contains no $368$-set.
No $8$-coset pack of a good $2$-dimensional $\mathbb F_7$-code exists.
That is not a certificate that $367$ is maximum.
