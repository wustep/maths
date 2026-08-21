# How a 617-cycle refused to grow

## 0. What was actually missing

The published lower bound $W(2,7)>3703$ is an explicit 2-coloring, not a SAT folklore number. Herwig–Heule–van Lambalgen–van Maaren and then Rabung–Lotts build it from the index-$2$ subgroup of $\mathbb Z/617\mathbb Z$: color by the Legendre symbol, repeat the cycle six times, and add one extra bit. A new bound is one more integer, a coloring of $[3704]$ with no monochromatic 7-AP. The missing degree of freedom is not a new prime in a table. It is a way to break the residue-class 7-APs that appear the moment the sixth period is crossed, without creating ordinary 7-APs of other differences.

## 1. Named false starts

**Append a bit.** Both colors of $3704$ fail on the reconstructed seed. Color $0$ completes the class-$2$ progression of difference $617$. Color $1$ completes six other 7-APs whose differences $47,208,236,255,303,332$ have no obvious common modulus.

**Flip the class-$2$ point.** Each of the six earlier points on that progression, flipped alone, creates a new 7-AP. Five of those six new APs have difference $11$ and sit $617$ apart from each other. The quadratic-residue coloring is packed: the bits that block one family complete another.

**Few flips, SAT.** After the first cardinality encoder was found to over-forbid flips, PySAT’s sequential counter was used. Cadical refuted $1$ through $6$ flips of the $3703$ seed. Recoloring a suffix of length $24$ up to a full extra period ($619$) was also unsatisfiable. The five-period prefix is a cage.

**A bigger prime.** Longest QR/QNR run grows. No prime from $619$ to $50000$ has cyclic run $\le 6$. The run-$7$ primes $653,677,691,821,823,881,907,947,1069$ did not become cyclic 7-AP-free after one or two flips on their $7$-strings.

**Zipper.** The no-turn zip of $617$ is the cycle concatenated with itself, period $617$. The turned zip has complementary halves, which is exactly the condition that makes a difference-$617$ 7-AP alternate colors in any unfolding. It also has a monochromatic $9$-run. Forcing complements in SAT and adding violated 7-APs by CEGAR never dropped below about eleven thousand cyclic violations.

**A slightly longer cycle.** CEGAR on $\mathbb Z/n\mathbb Z$ for $n=618,\dots,622$ spent its time adding clauses against a moving set of roughly $2600$ 7-APs. No model.

## 2. The useful failure

The one-step obstruction is sharp enough to be useful. On the published coloring, position $3704$ is forced into a fork:

- keep the residue of $2$ and complete a $617$-AP;
- change that residue and complete a $11$-AP (or, at the first class-$2$ point, a $285$-AP);
- change the last $619$ bits of the five-period prefix and Cadical says no.

So any coloring of $[3704]$ that stays near the Rabung–Lotts seed must leave that seed by at least seven bit-flips, and cannot do so by rewriting only the last period. Local search from the seed repeatedly reaches a single leftover 7-AP and stops. That is the same fork, seen from the other side: min-conflicts can clear five of the six color-$1$ APs or the unique color-$0$ AP, but the last one is paid for by another.

The zipper failure is useful in a different way. Complementary halves are the arithmetic condition that would make six copies of a length-$1234$ coloring safe against difference $617$. The turned zip already has that condition and still contains thousands of other 7-APs. Complementarity is cheap; 7-AP-freeness on $\mathbb Z/1234\mathbb Z$ is not.

## 3. The click

There was no click that produced a longer coloring. The click that organized the search was that the published bound is a *periodic* certificate whose dangerous APs after length $3703$ are residue classes modulo $617$. Once that is seen, “try the next integer” and “try the next prime” are the same question: find another 2-coloring of a cycle whose unfolding past six periods does not monochromatize a class. Quadratic residues do this at $617$ and, in the range searched, nowhere else.

## 4. The argument, in the order it was found

1. Build the Paley coloring of $\mathbb Z/617\mathbb Z$. Check 7-strings and APs through $0$. Both colors of $0$ work; the longest run is $6$.
2. Repeat six times. The standard cyclic-unfolding argument gives a coloring of $[3702]$. The extra bit at $3703$ must oppose the $0$-class, or the seven multiples of $617$ in $[0,3702]$ become a 7-AP. The resulting string verifies.
3. Enumerate 7-APs through $3704$. Record the fork above.
4. Ask SAT how far the seed can move. Six flips, no. One rewritten period, no.
5. Ask whether another prime supplies a longer cycle. None through $50000$.
6. Ask whether the classical zip doubles the cycle. Without the turn it does not double; with the turn it doubles the alphabet action and breaks 7-AP-freeness. CEGAR does not repair it.
7. Stop. The verifier and the $3703$ coloring are the product. The exact value of $W(2,7)$ is not claimed.

## 5. Computer search

- `compute/coloring_3703.txt` — verified 2-coloring of length $3703$, letters `a`/`b`.
- `compute/cycle_617.txt` — the QR cycle.
- `compute/verify_coloring.py` — enumerates every 7-AP in the interval.
- `compute/extend_obstruction.json` — the seven blocking APs at $3704$.
- `compute/near_3704_color0_one_ap.txt` — length $3704$, one violation (class-$2$, difference $617$).
- `compute/search_summary.json` — compact list of refutations.
- Cadical logs: `compute/flip_sat.jsonl`, `compute/extend_sat.jsonl`.
- Zip / cycle attempts: `compute/zip_cegar.json`, `compute/cyclic_cegar.json`, `compute/prime_scan.json`.

## 6. What is proved vs still open

Proved here: the $617$ quadratic-residue coloring unfolds to a 7-AP-free 2-coloring of $[3703]$; that coloring does not extend by one bit; it does not become a coloring of $[3704]$ after at most six bit-flips; its first five periods do not extend to length $3704$; no larger QR prime through $50000$ gives a cyclic 7-AP-free 2-coloring.

Still open: $W(2,7)$ itself, and whether any 2-coloring of $[3704]$ exists. A coloring of length $\le 3703$ is not a new bound. This search did not find one of length $\ge 3704$.
