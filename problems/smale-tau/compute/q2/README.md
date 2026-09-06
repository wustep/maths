# q2 — largest number of distinct integer zeros at small cost

The polynomial side of Smale's Problem 4. For \(k\ge 0\) let

$$
T(k)=\max\{Z(f): f\in\mathbb Z[x],\ \tau(f)\le k\},
$$

where \(\tau(f)\) counts operations \(+,-,\times\) from \(\{1,x\}\) and
\(Z(f)\) counts distinct integer zeros. No published table of \(T(k)\)
was found (RESEARCH.md), so the values here are new data rather than an
improvement of a record. The conjecture asks for \(T(k)\le a k^c\); the
Strassen construction gives \(T(k)\ge k^{2-o(1)}\) for large \(k\).

## Files

| file | role |
| --- | --- |
| `poly_enum.c` | prototype: counts programs and distinct polynomials per depth |
| `poly_search.c` | the search: canonical enumeration, exact 128-bit coefficients, rigorous root-count filters, candidate output |
| `count_roots.py` | exact distinct-integer-root count of every candidate (rational root theorem, sympy for the divisor list) |
| `cand5.txt`, `cand6.txt`, `cand7.txt` | candidate polynomials with their programs |
| `table.json` | the table \(T(k)\) with witnesses, written by `run_all.sh` |

## Method

Programs are enumerated in the canonical pending-queue order of q1
(every set of values that a program can produce is visited once, at the
least possible depth). Coefficients are exact signed 128-bit integers; a
bound on the sum of absolute coefficients is carried with every
polynomial and an operation whose bound exceeds \(2^{125}\) is refused,
which by the bound \(\sum|c_i|\le 2^{2^k}\) never happens below depth 8
except for products at the last step, reported separately.

For a polynomial \(f\) of degree at least the threshold of its depth,
three rigorous upper bounds on \(Z(f)\) are computed: Descartes' rule on
\(f(x)\) and \(f(-x)\); for small primes \(q\) the number of roots of
the primitive part modulo \(q\) counted with multiplicity, each residue
class capped by the number of integers in \([-B,B]\) in that class,
where \(B\) is the Cauchy root bound; and, when \(2B<2\cdot10^7\), the
number of distinct roots modulo a prime \(q>2B\) (the degree of
\(\gcd(f,x^q-x)\) over \(\mathbb F_q\)). Only polynomials whose bound
reaches the threshold are written out; `count_roots.py` then finds their
integer roots exactly. In leaf mode (`--leaf`) the last depth is not
pushed: every one-step child of a depth \(D-1\) node is formed and
examined directly, skipping children whose degree is below the threshold
and products \(fg\) with \(\bar Z(f)+\bar Z(g)\) below it, where
\(\bar Z\) is the rigorous bound computed for every set member (since
\(Z(fg)\le Z(f)+Z(g)\)). This visits about one child in fifteen. The threshold at depth \(d\) is one more than the
best construction known at that depth, so an empty candidate list proves
the construction optimal, and a nonempty list yields the exact maximum.

## Results

| \(k\) | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| \(T(k)\) | 1 | 1 | 2 | 3 | 3 | 4 | 5 |
| witness | \(x\) | \(x+1\) | \(x(x-1)\) | \(x^3-x\) | \(x^3-x\) | \((x^2-2x)(x^2-1)\) | \(x\bigl((x^2-2)^2-x^2\bigr)\) |

Node counts per depth 7, 67, 880, 16141, 396475, 12465248; distinct
polynomials reached within \(k\) steps 2, 9, 36, 186, 1270, 11404,
133743. With thresholds \(T(k-1)+1\) and \(T(k)+1\) the candidate lists
are empty for \(k\le 5\); at \(k=6\) exactly four polynomials
(\(\pm x(x^4-5x^2+4)\), \(\pm x^2(x^4-5x^2+4)\), root set
\(\{-2,\dots,2\}\)) reach five zeros and none reaches six. \(k=7\) is
pending (`table.json`).
