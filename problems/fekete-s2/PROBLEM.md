# Elliptic Fekete / log-energy points on \(S^2\)

- Slug: `fekete-s2`
- List: Smale 7 (1998)
- Solver: Cursor Grok 4.6 cloud agent
- Status: open. Finite-\(N\) records are computational. The conjecture is not claimed.
- Area: Discrete energy / spherical points
- Sources: Smale, *Math. Intelligencer* 20 (1998); Beltrán; Brauchart–Hardin–Saff; Cohn–Kumar; Womersley; Ridgway–Cheviakov; Rathbun–Ridgway
- Started: 2026-08-19

## Statement

Place \(N\) distinct points \(X=\{x_1,\dots,x_N\}\) on the unit sphere \(S^2\subset\mathbb R^3\) so as to minimize the logarithmic energy

\[
E(X)=\sum_{1\le i<j\le N}\log\frac{1}{|x_i-x_j|}
= -\sum_{1\le i<j\le N}\log|x_i-x_j|.
\]

Equivalently, maximize the product of pairwise Euclidean distances. Minimizers are elliptic Fekete points. Smale's 7th problem asks for a polynomial-time algorithm that returns an \(N\)-tuple whose energy is within \(c\log N\) of the minimum, for a universal \(c\). That algorithmic question is **not** the target of this folder.

Exact global minimizers are known for \(N=1\)–\(6\) and \(N=12\) (regular icosahedron). For every other \(N\) the record is computational.

Two conventions appear in the literature and must not be mixed:

- this folder, Ridgway–Cheviakov (CPC 2018), Rathbun–Ridgway (arXiv:2008.04880): \(E=\sum_{i<j}\log(1/|x_i-x_j|)\);
- Beltrán–Lizarte (arXiv:2502.10152) and some potential-theory papers: \(\sum_{i\neq j}=2E\).

## Tonight

A finite dent, not the conjecture. Success is one of:

**(A)** An explicit \(N\)-point configuration on \(S^2\) whose independently recomputed log-energy strictly beats a documented published record for that \(N\), with points + energy + a from-scratch verifier, and a citation of the beaten number.

**(B)** If no beat: independently replay a published table for several \(N\) (recompute energies from published coordinates, or regenerate known optima for \(N=2\)–\(6,12\)), write the replay, and the best residue. That is not a dent.

A candidate is nothing until the independent verifier agrees and the published number being compared is from a paper. Forum numbers are leads, not citations.

## Outcome

See `ATTACK.md` and `WALKTHROUGH.md`. This folder does not claim Smale 7.
