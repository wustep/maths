# Claim — integer τ table through 50,000

**Certified 2026-11-11: the full `replay.py` enumeration and both witness verifiers passed (`CLAIM holds: exact tau table through 50000; 69 prime counterexamples.`).**

Starting from the single free constant 1, let $\tau(n)$ be the least
number of additions, subtractions, and multiplications needed to compute
the positive integer $n$. Reusing either operand is allowed.

The exact predicate is that `tau_table_50000.txt` equals $\tau(n)$ for
every $1\le n\le 50000$. In particular,

$$
\max_{1\le n\le 50000}\tau(n)=10,
\qquad
\#\{p\le50000:p\text{ prime},\ \tau(p)<\tau(p-1)\}=69.
$$

Exactly 3,779 entries have cost 10. The counterexamples consist of two
cost pairs $(7,8)$, 37 pairs $(8,9)$, and 30 pairs $(9,10)$, where the
pair is $(\tau(p),\tau(p-1))$. `prime_counterexamples.csv` is the full list.

## Prior record and scope

Patanè, [arXiv:2609.28512v1](https://arxiv.org/abs/2609.28512v1),
Theorem 1 and Table 1, classifies exactly four such primes below 5,000:
3359, 3623, 4909, 4943. This extends that finite classification to
50,000, adding 65 examples and giving the global lower bound of at least
69 such primes, compared with the four exhibited in that paper.

Markström, [arXiv:1306.3091v4](https://arxiv.org/html/1306.3091v4),
Figure 1, gives the complete reached-set counts through nine steps and
the initial interval 10,266. q1 already reproduced those counts and
tabulated that interval. OEIS A141414 lists 74,587 as the first integer
of cost 11 in our convention. Consequently the maximum-cost inequality
above is a replay, not an improvement of that record. The new finite
comparison is the prime classification. Smale's conjecture and the
factorial decisions remain open.

## Certificate and falsification

Two exhaustive nine-step enumerators (q1 C and independent Rust) must
agree on every entry through 50,000, their node counts, and Markström's
reached-set counts. Neither bounds intermediate values. They also replay
the OEIS b-file through 1,800 and the existing q1 table through 10,266.
Each entry absent at depth nine must have an explicit ten-step witness,
checked by Python and Rust using different verification algorithms.
Every prime counterexample and its predecessor also has an explicit
optimal witness. Python trial division and a Rust sieve independently
classify the primes.

A shorter program for any tabulated value, an invalid upper-bound
witness, an omitted nine-step program, a mismatch between enumerators,
or a missing or extra prime counterexample falsifies this claim. A
timeout or incomplete census cannot certify it. Default `run_all.sh`
reruns both censuses and exits zero only after checking the entire claim
and matching the committed artifacts.
