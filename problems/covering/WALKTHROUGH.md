# How One Missing Column Became a Covering Code

## 0. What was missing

The asymptotic question in Green's Problem 40 is deliberately out of reach here. The useful finite question was narrower: could one write down a parity-check matrix that improves a documented small parameter, then make the covering claim independently checkable?

For a binary parity-check matrix, the entire problem lives in syndrome space. If its columns form a set $S\subset\mathbb F_2^r$, radius at most 2 means that every syndrome is either zero, a column, or the sum of two columns. The desired matrix was therefore a small additive basis of order two, with no zero or repeated columns.

That reformulation made the proof tiny. It did not make the search easy.

## 1. The attractive gaps that did not close

The first target was $(r,n)=(8,25)$. The documented length was 26, and deleting a single column would settle a conspicuous one-column gap. Random annealing repeatedly came close, but its best 25-set missed three of the 256 syndromes. CP-SAT and Z3 encodings also ran to their limits without a model or a refutation.

The second target was $(9,38)$, one column below the documented length 39. Here the monolithic SAT instance had roughly 130,000 pair auxiliaries. A five-minute CP-SAT run returned `UNKNOWN`. Reconstructing the classical Gabidulin 39-column set helped, but every direct deletion missed eight syndromes, and an exhaustive two-out/one-in neighborhood contained no solution.

These failures had names and numbers: three missed at $(8,25)$, eight missed at $(9,38)$, and `UNKNOWN` from every bounded exact run. None was a lower bound.

## 2. What the failures taught us

The near-solutions exposed a mismatch between the prettiest parameter gaps and the easiest search landscapes. At $r=8,n=25$, there are only
$$
1+25+\binom{25}{2}=326
$$
zero-, one-, and two-column representations for 256 syndromes. Almost every collision matters. The 26-column algebraic seed was also highly regular: deleting any column destroyed many uniquely covered syndromes.

The search needed more slack and a less rigid seed. The current table supplied both at redundancy 10. Its 51-column Kaikkonen--Rosendahl matrix has 1,327 representations for 1,024 syndromes and an explicit hexadecimal description. Deleting its least costly column left only 11 syndromes uncovered—worse as an absolute number than the $r=8$ residue, but with much more room to rearrange pair sums.

## 3. The click

The click was to stop asking which published bound was numerically closest and ask which seed had enough redundant representations to move.

The local-search state was a set of exactly 50 nonzero ten-bit columns. An array stored, for every syndrome, how many times it appeared as zero, a singleton, or a pair sum. Swapping one column changes only its singleton and the 49 pair sums involving it, so the uncovered count can be updated without recomputing all $\binom{50}{2}$ pairs.

Most proposals were targeted. Pick an uncovered syndrome $g$, then propose either $g$ itself or $g+s$ for a current column $s$; either choice has an immediate way to cover $g$, unless the compensating deletion breaks it again. Simulated annealing admitted the occasional uphill move needed to leave local minima.

With a fixed xorshift seed, run 0 reached zero uncovered syndromes at proposal 3,600,281. The result had 50 distinct nonzero columns.

## 4. Why the short certificate proves the coding statement

Let $H$ be the resulting $10\times50$ matrix and let $C=\ker H$. The independent checker first finds $\operatorname{rank}H=10$, so $C$ has dimension $50-10=40$.

Now take any word $x\in\mathbb F_2^{50}$ and compute its syndrome $s=Hx^T$. The certificate gives indices of at most two columns of $H$ whose sum is $s$. Put ones in those coordinate positions to obtain an error vector $e$ of weight at most two. Then
$$
H(x-e)^T=Hx^T-He^T=s-s=0,
$$
so $x-e\in C$ and $d(x,C)\le2$.

The radius is exactly 2, not merely at most 2: zero and the 50 singleton columns account for only 51 of the 1,024 syndromes. Some syndrome necessarily needs two columns.

## 5. What the computer checked

The committed certificate has one entry for every integer syndrome from 0 through 1,023. It uses the empty representation once, a singleton 50 times, and a pair 973 times. The verifier checks every supplied XOR, reconstructs the matrix from its text rows, computes its binary rank, and then ignores the certificate and performs a second exhaustive enumeration of all 1,276 representations.

That independent enumeration covers all 1,024 syndromes. Its multiplicity histogram is
$$
\{1:859,\ 2:129,\ 4:24,\ 5:9,\ 6:3\},
$$
where the key is the number of representations and the value is the number of syndromes with that multiplicity. In particular, there are no zeroes in the histogram.

The finite covering density is therefore
$$
\mu=\frac{1+50+\binom{50}{2}}{2^{10}}
=\frac{319}{256}=1.24609375.
$$
The November 2025 best-known table lists length 51 and density $1327/1024\approx1.29590$ at redundancy 10. The exhaustive witness moves that documented entry down by one column.

![The certified point and the unresolved targets from the same search](figures/q1_density_vs_length.png)

## 6. Proven, and still open

What is proved is concrete:
$$
\boxed{\ell_2(10,2)\le50.}
$$
The matrix, all 1,024 certificate entries, the certificate generator, the independent verifier, and the deterministic search trace live under [`compute/`](compute/). The witness reruns without Lean and without trusting the heuristic.

What is not proved matters just as much. The search did not show that 50 is optimal; its $n=49$ run stopped with seven uncovered syndromes. It did not resolve the 25-versus-26 gap at redundancy 8 or the 38-versus-39 gap at redundancy 9. Most importantly, one finite upper-bound improvement does not determine, or even claim to determine, Green's asymptotic constant $f(2)$.

The durable idea is the separation between discovery and proof. The heuristic only had to find the columns once. After that, a short syndrome argument and an exhaustive, independent certificate carried the mathematical claim.

## 7. The 49 push (quest q4): certified residue, no dent

A later session attacked $\ell_2(10,2)\le 49$ directly and did not land it. What it left behind is negative knowledge with certificates, under [`compute/q4/`](compute/q4/):

- **Symmetry is dead at 49 = 7×7.** If a 49-covering were invariant under a subgroup of $GL(10,2)$, it would be a union of orbits, and coverage collapses to orbit-class space where exhaustive search is feasible. Seventy-nine subgroup classes were exhausted with zero witnesses, including *every* $C_7\times C_7$ class (orbit sizes 1/7/49) and the order-7 classes with one-dimensional fixed space (up to 8.9 billion nodes each). The engine's negatives were validated three ways: planted direct-sum coverings recovered at n=62/78, a no-prune rerun, and an independent naive enumerator agreeing on 7.26 million leaves. A few fixed-space-heavy classes timed out and remain open.
- **The 7-hole floor is real and deep.** Fresh deterministic anneals reproduce exactly 7 uncovered syndromes. One such configuration is provably not within *any* swap of 5 columns of a covering (exhaustive over all 1.9M removal sets with an exact re-add search, validated on 4/4 planted controls); a second is proven to depth 4.
- **There are at least two basins.** The two 7-hole optima have identical GL-invariants — same multiplicity histogram, same hole-set structure (rank 5, one zero-sum quadruple) — yet an exhaustive color-guided search proves no linear map carries one onto the other.

None of this is a lower bound. $\ell_2(10,2)=49$ remains possible; what is excluded is every highly symmetric 49-covering in the classes listed, and every small perturbation of the best-known near-misses.
