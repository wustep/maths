# Walkthrough — $R(5,5)$, the three remaining integers

- Problem: `problems/ramsey-r55`
- Date: 2026-08-17
- Argument status: documented incomplete search; published record $43\le R(5,5)\le 46$ not beaten
- Problem status: open

## 0. What was actually missing

The missing object is not a better generic SAT encoding of $\omega<5$ and $\alpha<5$. Those clauses are ancient. What is missing is either

- one new 42-vertex graph that *does* extend, or a 43-vertex graph that is not an extension of the published 656, or
- a gluing / LP census at 45 on the scale of Angeltveit–McKay’s 80 CPU-year argument for 46.

The degree of freedom that is actually finite tonight is **symmetry**. Order 43 is prime, so every vertex-transitive graph is a circulant. Order 42 has exactly six groups, so the Cayley question is a finite list of inverse-closed connection sets. The published 656 graphs sit outside both lists; the open question is whether anything else sits with them.

## 1. False starts (named obstacles)

- **Unrestricted SAT on 43 vertices.** 903 edge variables, $\binom{43}{5}\cdot 2$ width-10 clauses. This is the instance the literature has been staring at for thirty years. An isolated timeout is not a new bound, and we did not treat it as one.
- **Hoping a circulant of order 43 exists.** Paley is unavailable: $43\equiv 3\pmod 4$. The full $2^{21}$ connection-set tree, pruned to degrees $[18,24]$, is one million leaves and finishes in under a second. It is empty. Harborth–Krause already said a cyclic improvement of the Table Ia lower bound needs 102 vertices; the census is a check, not a discovery.
- **Adding one vertex to a circulant 41-graph.** There *are* 20 circulant $(5,5,41)$-graphs (Paley-41 itself has $\omega=\alpha=5$ and is not among them). None extends. Because a non-extendable $n$-vertex $(5,5)$-graph cannot appear as an induced subgraph of any larger $(5,5)$-graph, this path cannot reach 42 or 43.
- **Replaying Angeltveit–McKay at 45.** Their own conclusion is that the 46-proof already used the dense end of $\mathcal R(4,5,n)$ and that 45 wants new theory. We did not start an 80-year gluing job.

## 2. The useful failure

The useful failure was the circulant 41-list existing and then refusing to grow. It split the problem in two.

On the *construction* side: every algebraic family we could exhaust — circulants through 45, then Cayley graphs on all six groups of order 42 — is empty in the legal degree window. The 656 published graphs are therefore not hiding in a group ring. They are irregular ($\delta=19$, $\Delta=22$ on every stored example), not regular of degree 20 or 21 as a Cayley graph would be.

On the *obstruction* side: the 656 graphs themselves are locally rigid. One-edge flips that stay $(5,5)$ stay inside the 194 canonical 1-WL types of the published set. Seidel switching on one or two vertices never stays $(5,5)$. None of the 656 extends. Whatever a 43-vertex example would be, it is not a one-vertex, one-flip, or small-Seidel neighbour of the known list, and it is not vertex-transitive.

## 3. The click

The click was small and administrative: **count the groups**.

Order 43 is prime, so VT = circulant, and that census is empty. Order 42 has six groups. Circulant is one of them and is empty. The other five have explicit multiplication tables of size $42\times 42$. Inverse-closed connection sets are $2^{O(30)}$ objects, but an incremental $K_4$ test in the neighbourhood of the identity (Cayley + vertex-transitivity) prunes to a few seconds except for $D_{21}$, which is 97 seconds and 155 million leaves. All six empty.

That is not $R(5,5)=43$. It is the statement: *if a $(5,5,42)$-graph is Cayley, it does not exist; therefore every example, including the 656, is non-Cayley.*

A second, smaller click: the involution-symmetric 43-vertex encoding is a 462-variable formula, and the same encoder produces a genuine $(5,5,17)$-graph on the Paley order, so a later UNSAT would not be a vacuous bug.

## 4. The argument, in the order it was found

1. Fetch Radziszowski revision 18 and Angeltveit–McKay v2. Confirm the live window is still $43\le R(5,5)\le 46$.
2. Parse McKay’s `r55_42some.g6`. Independently certify all 656 graphs. Record $\delta=19$, $\Delta=22$, the edge-count histogram, and the file hash.
3. Replay non-extension of all 656 by a 42-variable DPLL with $K_4$ / independent-4 unit propagation.
4. Exhaust circulants at 25–45. Find the expected small-order examples, including 20 graphs on 41 vertices. Find zeros at 39 and at 42–45. Independently replay the zeros at 42 and 43 in Python.
5. Try to grow the 20+24 circulants on 41 and 40 by one vertex. Empty. Conclude they cannot sit inside a larger $(5,5)$-graph.
6. Walk the 1-flip neighbourhood of the 656 and the Seidel 1- and 2-switch neighbourhoods. Flips stay in the published 1-WL types; Seidel dies immediately.
7. Write down the six groups of order 42, check the tables, and exhaust inverse-closed Cayley graphs in the legal degree window. All six empty.
8. Encode involution-symmetric 43-vertex graphs. Validate the encoder at $n=17$. Run kissat for 15–20 minutes on both the fat and slim 43-instances. Both return `UNKNOWN`. A timeout is not a new bound.

No step moves an endpoint of the published interval.

## 5. Computer search

- `compute/refs/radziszowski-ds1-rev18.pdf`, `compute/refs/angeltveit-mckay-r55-le46.pdf`, `compute/refs/r55_42some.g6`
- `compute/certs/mckay42_verify.json` — 656 graphs, degrees, hash
- `compute/logs/extend_check.txt` — 656 non-extensions
- `compute/certs/py_circulant_{42,43}.json` — independent empty circulant censuses
- `compute/certs/cayley42_census.json` — six-group Cayley zeros
- `compute/certs/flip_types.json`, `compute/certs/seidel_switch.json`
- `compute/certs/involution17_model.json` — encoder is not vacuous
- `compute/cnf/involution43.cnf`, `compute/cnf/involution43_slim.cnf`

Replay: `compute/README.md` and `compute/replay.sh`.

## 6. What is proved vs still open

**Checked, not new as a bound.**

- The published 656 graphs are $(5,5,42)$ and none of them extends. (Replay of McKay–Radziszowski.)
- There is no circulant $(5,5)$-graph on 42, 43, 44 or 45 vertices, and no vertex-transitive $(5,5)$-graph on 43 vertices. (Circulant half already implicit in Harborth–Krause.)
- There is no legal-degree undirected Cayley $(5,5)$-graph of order 42 on any group.

**Still open.**

- $R(5,5)$ is still one of 43, 44, 45, 46.
- Whether the 656 graphs are all of $\mathcal R(5,5,42)$.
- Whether a 43-vertex example exists with trivial automorphism group, or with an involution (kissat `UNKNOWN` at 15–20 minutes on both encodings).
- Whether $\mathcal R(5,5,45)$ is empty.

Do not cite this folder as a bound.

---

# 2026-08-27

- Argument status: documented incomplete search; published record $43\le R(5,5)\le 46$ not beaten
- Problem status: open

## 0. What was actually missing

The 17 August census closed every group of order 42 and every circulant through 45. What it did not close was a 43-vertex graph that is *not* an extension of the published 656 in their given labellings — a 1-flip of one of those graphs, or a graph whose automorphism group is $C_7$ rather than an involution — and it did not close Cayley graphs of order 44 or 45, which would have moved the lower bound by two or three.

Order 44 has four groups, order 45 two. Both lists are finite. The 1-flip ball of the 656 is finite (564816 edges). Those were the degrees of freedom that were actually left.

## 1. False starts (named obstacles)

- **Replaying Angeltveit–McKay at 45.** Still the wrong object. Their own v2 says 45 wants new theory. We did not start an 80-year gluing job.
- **Treating Tamburini 2508.16699 as a bound.** The newest arXiv hit after 2409.15709 is a random-projector heuristic that “identifies $R(5,5)$ at $n=45$”. It is not a colouring and not a nonexistence log.
- **Reading the 1-WL histogram as an isomorphism test.** Stable colour-class sizes on the 656 are only two shapes — 42 singletons (the 424 asymmetric graphs) and 21 pairs (the 232 involutive ones). Radius-2 flips stayed in those two shapes. That does not mean the flipped graphs are isomorphic to the 656. The extension SAT is what actually speaks.

## 2. The useful failure

The useful failure was the 4080 one-flip $(5,5,42)$-graphs refusing to take a 43rd vertex, in 183 seconds. Combined with the original non-extension of the 656, a 43-vertex example is not a 1-flip neighbour of a published graph plus a vertex. Whatever it is, it is at least two edits away from the known list, or it is not an extension of a 42-vertex $(5,5)$-graph at all.

The Cayley side failed the same way, one group at a time, except $D_{22}$ which needed the incremental $K_4$ test (470 million leaves, 407 seconds) after the naive rebuild enumerator sat for fifteen minutes without finishing.

## 3. The click

Count the groups again, but at 44 and 45. Four plus two, not six. Circulant is one of them at each order and was already empty. The other four have multiplication tables of size $44\times 44$ or $45\times 45$. Inverse-closed connection sets in the legal degree window are a few hundred thousand leaves except $D_{22}$.

A second, smaller click: none of the 656 has a 7-cycle. So a $C_7$-symmetric $(5,5,42)$-graph would be new. The encoder is not vacuous — it finds a $(5,5,14)$-graph in 44 milliseconds — but Cadical on the 42- and 43-vertex slim instances returns `UNKNOWN` at five minutes. A timeout is not a new bound.

## 4. The argument, in the order it was found

1. Fetch Radziszowski revision 18 and Angeltveit–McKay v2 again. Confirm the live window is still $43\le R(5,5)\le 46$. Note Tamburini 2508.16699 as a heuristic, not a citation.
2. Replay `compute/replay.sh` and `verify_mckay.py`. 328+328 still $(5,5,42)$, none extend, circulant 42/43 still empty.
3. Write down the four groups of order 44 and the two of order 45. Check the tables. Exhaust inverse-closed Cayley graphs. All six empty (circulant replayed; three small groups in C and Python; $D_{22}$ incremental).
4. Enumerate integral SRG parameters on 43 vertices in degrees $[18,24]$. Empty list; $43\not\equiv 1\pmod 4$. No SRG in the window.
5. Compute $|\mathrm{Aut}|$ of the 656 by colour refinement plus backtrack. 424 trivial, 232 order 2, no 7-cycle.
6. Flip every edge of every one of the 656, keep the 4080 that stay $(5,5)$, and run the 42-variable extension SAT on each. Zero models.
7. Encode $C_7$-symmetric graphs. Validate at $n=7$ and $n=14$. Run Cadical for five minutes at 42 and 43. Both `UNKNOWN`.

No step moves an endpoint of the published interval.

## 5. Computer search

- `compute/q1/certs/q1_summary.json` — collected DONE lines
- `compute/q1/certs/group_laws.json`, `py_c11c4.json`, `py_c3c15.json`
- `compute/q1/logs/cayley_{c2c22,c11c4,c3c15,d22}.txt`, `circ{44,45}.txt`
- `compute/q1/logs/extend_flips.txt` — 4080 flips, 0 extensions
- `compute/q1/certs/aut_mckay.json`, `srg43_params.json`, `two_flip.json`
- `compute/q1/certs/c7_selftest.json`, `c7_n14.json`, `c7_n{42,43}.json`

Replay: `cd problems/ramsey-r55/compute && ./replay.sh && cd q1 && ./run_all.sh`.

## 6. What is proved vs still open

**Checked, not new as a bound.**

- None of the 4080 one-flip $(5,5)$ neighbours of the 656 extend.
- There is no legal-degree undirected Cayley $(5,5)$-graph of order 44 or 45.
- There is no strongly regular graph on 43 vertices with degree in $[18,24]$.

**Still open.**

- $R(5,5)$ is still one of 43, 44, 45, 46.
- Whether the 656 graphs are all of $\mathcal R(5,5,42)$.
- Whether a 43-vertex example exists with trivial automorphism group, or with a $C_7$ (Cadical `UNKNOWN` at five minutes).
- Whether $\mathcal R(5,5,45)$ is empty.

Do not cite this folder as a bound.


## 7. Two-edit ball and large-prime automorphisms (2026-08-28)

The one-flip neighbourhood of the 656 was already empty for extensions. The
two-edit ball is the next finite neighbourhood that still sits on a laptop:
every unordered pair of edge toggles among 42 vertices, including pairs that
leave the Ramsey class in the middle. 242 million pairs, 11136 legal
endpoints, zero 43rd vertices.

Separately, a 43-vertex example with an automorphism of prime order $p\ge 11$
is now excluded for the cycle types that fit, by checked DRAT proofs, and a
few leftover types die on the degree window alone. Combined with the old
circulant census, that leaves only automorphism groups whose primes are
among $2,3,5,7$. Those SAT instances timed out.

A score-2 near graph from local search has no $(5,5,43)$-graph inside six
edge edits. That is a ball around one failed construction, not a bound.

Still $43\le R(5,5)\le 46$.

---

# 2026-08-29 — closing the order-7 symmetry

- Argument status: documented incomplete search; published record
  $43\le R(5,5)\le46$ not beaten
- Problem status: open

## 0. What was actually missing

q2 had proved that primes at least 11 cannot divide the automorphism-group
order of a hypothetical $(5,5,43)$-graph. It had not done the same for 7: the
maximum-cycle order-7 formula timed out, and the other five cycle counts had
not been exhausted. The finite degree of freedom was therefore the complete
list $7^c 1^{43-7c}$ for $1\le c\le6$.

## 1. False starts

- **Another monolithic solver portfolio.** Default, UNSAT-biased, CaDiCaL,
  Lingeling, and MapleChrono runs all left the $7^6 1^1$ formula `UNKNOWN`.
- **Treating one fixed-neighbour count as the cycle type.** A fixed vertex can
  meet different numbers $k$ of 7-cycles. Every degree-feasible $k$ must be
  checked or covered by complementation; one timeout or one representative is
  not an exclusion.
- **Using failed-assumption cores as a global proof.** Early cores covered one
  neighbourhood row each. They did not compress the 787 cases into a smaller
  unchecked assertion.

## 2. The useful failure

The hard maximum-cycle formula has one fixed vertex. Its degree is a multiple
of 7 and lies in $[18,24]$, so it is exactly 21. Its neighbourhood is therefore
three 7-cycles, with no $K_4$ and no independent 5-set. Enumerating only that
induced graph under q2's existing symmetry breaking produced 787 possibilities.
A full assignment of those 30 orbit variables turned the hard global formula
into a short UNSAT run.

## 3. The click

The split object did not need a new encoder. It needed two layers of evidence:
a small DRUP proving that the 787 neighbourhood rows are exhaustive, then one
DRUP against the original q2 CNF plus each row. Checking the pieces separately
keeps memory bounded and makes the finite cover explicit.

The other click was complementation. If a fixed vertex meets $k$ of the $c$
7-cycles, the complement meets $c-k$. Together with the degree window, one or
two representatives cover every $k$ for each of the five remaining cycle
counts.

## 4. The argument, in the order it was found

1. Regenerate q2's six maximum-cycle instances and match every recorded hash.
2. Run a solver portfolio. The maximum order-2, order-3, and order-5 cases stay
   `UNKNOWN`; the maximum order-7 case also stays hard monolithically.
3. Enumerate the 21-vertex order-7 neighbourhood: 787 rows, with a checked
   completion DRUP.
4. Refute all 787 full cubes and replay every proof with `drat-trim`.
5. Enumerate the degree-feasible fixed-neighbour counts for $c=1,\dots,5$,
   pair them by complementation, and run the eight representatives.
6. Check all eight direct DRAT proofs. The six cycle counts are now exhausted.

No step constructs a 43-vertex graph or proves nonexistence at 45.

## 5. Computer search

- `compute/q3/certs/q3_summary.json` — collected result and remaining timeouts
- `compute/q3/certs/p7_neighborhoods.json` — the 787-row finite cover
- `compute/q3/certs/p7_proofs.json` — hashes for every conquer proof and archive
- `compute/q3/certs/proofs/` — eight direct compressed DRATs, eight conquer
  archives, and the local-completion DRUP
- `compute/q3/run_all.sh` — regenerate all CNFs and replay every proof

## 6. What is proved vs still open

**Checked, not new as a Ramsey bound.** No $(5,5,43)$-graph has an
automorphism of order 7. Combining q2 and q3, a hypothetical graph's
automorphism-group order can have prime divisors only among 2, 3, and 5.

**Still open.** The interval is still $43\le R(5,5)\le46$. Orders 2, 3, and 5
remain `UNKNOWN`, and their non-maximum cycle types have not been exhausted.
Graphs with trivial automorphism group are untouched.

Do not cite this folder as a bound.

---

# 2026-08-29 — leftover orders 2, 3, and 5

- Argument status: documented incomplete search; published record
  $43\le R(5,5)\le46$ not beaten
- Problem status: open

## 0. What was actually missing

q3 had closed every order-7 cycle type. The finite leftover was the list
$p^c 1^{43-pc}$ for $p\in\{2,3,5\}$. q2 and q3 had only run the five
maximum-cycle representatives, and those had timed out.

## 1. False starts

- **Plain CDCL at three minutes.** Every order-5 representative returned
  `UNKNOWN`. The configuration that had worked for most of the order-7 list
  did not move these leftover primes.
- **Neighbourhood cubes copied from order 7.** After the existing
  cycle/phase breaking there are 706 legal neighbourhoods for $5^7 1^8$ and
  3036 for $5^8 1^3$. The first $5^7$ cube still timed out at a minute:
  assigning the selected cycles leaves twenty or more free vertices, unlike
  the order-7 maximum-cycle split.
- **Treating one timeout as an exclusion.** The maximum-cycle order-5
  formula stayed `UNKNOWN` at fifteen minutes even under the UNSAT-biased
  kissat configuration.

## 2. The useful failure

The neighbourhood split taught the wrong size. What actually solved two
cycle types was the same UNSAT-biased kissat run that q3 had used for
$7^1 1^{36}$, applied to the high-cycle order-5 formulas $5^6 1^{13}$ and
$5^7 1^8$. Those instances are small enough for inprocessing to finish and
large enough that the cyclic constraints bite.

## 3. The click

Complementation still pairs $k$ with $c-k$. For $5^6 1^{13}$ the legal
values are $k=2,3,4$; checking 2 and 3 covers all three. For $5^7 1^8$ the
only legal values are 3 and 4, so one representative is enough. The
encoder did not change.

## 4. The argument, in the order it was found

1. Fetch Radziszowski revision 18 and Angeltveit–McKay v2 again. The live
   window is still $43\le R(5,5)\le46$. Tamburini 2508.16699 remains a
   heuristic.
2. Enumerate the 142 degree-feasible leftover representatives. Match the
   five maximum-cycle CNF hashes from q2/q3.
3. Run plain CDCL for three minutes on all fourteen order-5 cases. All
   `UNKNOWN`.
4. Switch to `kissat --unsat --seed=17`. Store checked DRATs for
   $5^6 1^{13}$ ($k=2,3$) and $5^7 1^8$ ($k=3$).
5. Independently regenerate those three CNFs and replay every stored proof
   with the pinned `drat-trim`.
6. Leave the maximum-cycle formulas and the rest of orders 2 and 3 as
   timeouts.

No step constructs a 43-vertex graph or proves nonexistence at 45.

## 5. Computer search

- `compute/q4/certs/q4_summary.json` — collected result
- `compute/q4/certs/proofs/p5_c6_k2.drat.gz`, `p5_c6_k3.drat.gz`,
  `p5_c7_k3.drat.gz` — the three stored proofs
- `compute/q4/logs/replay_direct.txt` — independent `VERIFIED` lines
- `compute/q4/run_all.sh` — regenerate the CNFs and replay the proofs

## 6. What is proved vs still open

**Checked, not new as a Ramsey bound.** No $(5,5,43)$-graph has an
automorphism of cycle type $5^6 1^{13}$ or $5^7 1^8$. Combined with q2 and
q3, a hypothetical graph's automorphism-group order can have prime
divisors only among 2, 3, and 5, and if 5 divides that order then the
permutation is not of type $5^6$ or $5^7$.

**Still open.** The interval is still $43\le R(5,5)\le46$. The
maximum-cycle order-2, order-3, and order-5 instances remain `UNKNOWN`.
Other leftover 2/3/5 cycle types are unfinished. Graphs with trivial
automorphism group are untouched.

Do not cite this folder as a bound.

---

# 2026-08-29 — leftover SAT after 5^6 and 5^7

- Argument status: documented incomplete search; published record
  $43\le R(5,5)\le46$ not beaten
- Problem status: open

## 0. What was actually missing

q4 closed $5^6 1^{13}$ and $5^7 1^8$. The finite leftover was still the
list $p^c 1^{43-pc}$ for $p\in\{2,3,5\}$, now minus those two types.
The five maximum-cycle formulas had never returned a decision.

## 1. False starts

- **Storing the 5^4 proof as gzip.** The same `kissat --unsat --seed=17`
  run that closed $5^6$ and $5^7$ also closed $5^4 1^{23}$ at $k=4$ in
  about ten minutes, but the trimmed DRAT is 829MB and gzip -9 is 119MB.
  GitHub rejects that blob. The exclusion is real; the archive format
  was wrong.
- **Waiting on maximum-cycle SAT.** All five max-cycle representatives
  stayed `UNKNOWN` at thirty minutes. A timeout is not a restriction.
- **Expecting the other 5^4 neighbour counts to fall the same way.**
  $k=1$ and $k=2$ timed out at thirty minutes. Completing the $5^4$
  type needs those two, and they did not finish.

## 2. The useful failure

The oversized gzip taught the size of the lemma core: about seven
million lemmas survive the trim. `xz -9` of the same bytes is 93MB,
under the blob limit, and decompresses to a DRAT the pinned checker
accepts.

## 3. The click

$5^4 1^{23}$ at $k=4$ is the same high-but-not-max band that closed
$5^6$ and $5^7$. Complementation pairs $k=4$ with $k=0$, so one
representative covers both. The encoder did not change. The
maximum-cycle hashes from q2/q3 still match.

## 4. The argument, in the order it was found

1. Fetch Angeltveit–McKay v2 and the revision-18 survey again. The live
   window is still $43\le R(5,5)\le46$.
2. Copy the q4 stack to a new folder. Skip the three certified
   $5^6$/$5^7$ names.
3. Re-solve $5^4 1^{23}$ at $k=4$ with `kissat --unsat --seed=17`.
   UNSAT in 562s. The raw DRAT is byte-identical to the leftover q4
   solve (1197192721 bytes). Trim, then `drat-trim` prints `s VERIFIED`.
4. Store `xz -9` of the trimmed proof. Independently regenerate the CNF
   and replay.
5. Run the five maximum-cycle formulas and the other nearby leftover
   names for thirty minutes. All `UNKNOWN`.

No step constructs a 43-vertex graph or proves nonexistence at 45.

## 5. Computer search

- `compute/q5/certs/q5_summary.json` — collected result
- `compute/q5/certs/proofs/p5_c4_k4.drat.xz` — the stored proof
- `compute/q5/logs/replay_direct.txt` — independent `VERIFIED` line
- `compute/q5/run_all.sh` — regenerate the CNF and replay the proof

## 6. What is proved vs still open

**Checked, not new as a Ramsey bound.** No $(5,5,43)$-graph has an
automorphism of cycle type $5^4 1^{23}$ in which a fixed vertex meets
0 or 4 of the four 5-cycles. Combined with q2, q3, and q4, a
hypothetical graph's automorphism-group order can have prime divisors
only among 2, 3, and 5, and if 5 divides that order then the
permutation is not of type $5^6$ or $5^7$ and is not this $5^4$
neighbour-count pair.

**Still open.** The interval is still $43\le R(5,5)\le46$. All five
maximum-cycle order-2, order-3, and order-5 instances remain
`UNKNOWN`. Other leftover 2/3/5 cycle types, including the rest of
$5^4$, are unfinished. Graphs with trivial automorphism group are
untouched.

Do not cite this folder as a bound.
