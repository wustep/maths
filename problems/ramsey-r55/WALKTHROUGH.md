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
