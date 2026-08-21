# Walkthrough — involutory elations as three MOLS

- Problem: `problems/projective-plane-order-twelve`
- Quest: P31, SuperGrok 2026-08-17
- Model: grok-4.6 `--reasoning-effort xhigh`
- Date: 2026-08-17
- Argument status: residue. Two verified maximal involution 2-MOLS classes; the $t=3$ instance that would forbid $\lvert G\rvert=2$ was not decided.
- Problem status: open. Published Aut restriction remains $\lvert G\rvert\in\{1,2,3\}$.

## 0. What was actually missing

The missing degree of freedom was not a generic 157-point SAT. After Akiyama–Suetake–Tanaka 2023, a hypothetical plane has Aut of order 1, 2, or 3. Baer's theorem plus $12$ even and not square collapses order 2 to a single geometric type: an involutory elation. Deleting the axis converts that elation into a translation of order 2 of an affine plane of order 12. The translation can be written $\tau(x,y)=(x+6,y)$. Symbol relabelling of each parallel class puts every Latin square of the associated MOLS family into the form

$$
L[r+6][c] \;=\; L[r][c]+6\pmod{12}.
$$

A plane would give eleven such squares. Already three pairwise orthogonal ones would be implied. So the finite leftover is not “search a 2-(157,13,1)” but “does an involution 3-MOLS of order 12 exist?”

## 1. Named false starts, with the specific obstruction

- **Bruck–Ryser as an exclusion.** $12\equiv0\pmod4$, so the sum-of-two-squares test is silent. The determinant identity $\lvert\det B\rvert=13\cdot12^{78}$ is an integer. Replaying it (`compute/replay_identities.py`) is a parameter check, not a dent.
- **Generic 11-MOLS SAT.** TheoremDB R592 already writes the 1,584-cell model. Isolated timeouts on that model are forbidden as a dent, and they do not touch a new automorphism type.
- **First-row identity on every square.** The usual OLS normalization $L_k[0][c]=c$ for all $k$ does not commute with $+6$. The first SAT run of the $t=2$ instance returned UNSAT in seconds. That UNSAT was false: the MacNeish product is an explicit involution 2-MOLS. The leftover symbol relabelling of square $k\ge1$ has to lie in the wreath product that commutes with $+6$, and that is not enough to force its first row to the identity after the columns have already been used to normalize square 0.
- **Quotient to OLS of order 6.** MacNeish does split into Latin squares of order 6 on columns $0..5$. Those squares are not orthogonal, so Tarry's theorem does not fire. The SAT $t=2$ pair does not even split. The reduction “3 involution-MOLS $\Rightarrow$ OLS of order 6” is false.
- **Mate-encoder orbit mix-up.** The first `encode_mate.py` attached both $A[r][c]$ and $A[r+6][c]$ to the same free cell. UNSAT from that encoder was discarded. The corrected encoder accepts a mate of a single square and is independently checked.

## 2. The useful failure

The false $t=2$ UNSAT forced a written list of *safe* symmetries: column permutation, free-row sort on pair-indices of $L_0[\cdot][0]$, and a $+6$-commuting symbol map sending $L_k[0][0]$ to $0$. With that list, both MacNeish and a SAT search produce verified involution 2-MOLS, and they are not isotopic (intercalate counts $108+108$ versus $90+78$). The same list is what makes a later $t=3$ UNSAT, if one ever arrives, mean something.

The two mate-UNSAT proofs then showed that both of those 2-families are maximal. That is the strongest finite statement actually certified tonight. It taught the shape of the orthogonality graph — many mates of a single $L_0$, none of the sampled pairs orthogonal to each other — without classifying the graph.

## 3. The click

The click was the reduction, not a finished exclusion: $\lvert G\rvert=2$ is exactly one MOLS problem of order 12 with a linear involution, and the first interesting unsatisfiable number of squares, if it is at most 11, is already a forbidden automorphism type. $t=2$ exists, so the first candidate is $t=3$.

## 4. The argument, in the order it was found

1. Fetch Moorhouse and TheoremDB. No plane. $\lvert G\rvert\in\{1,2,3\}$.
2. Replay the parameter identities. No arithmetic obstruction.
3. Classify order-2/3 elements by fixed-point congruence. Recover: unique involutory elation; no order-3 homology of either kind; no Fano-planar order-3; leftover planar-$\mathrm{PG}(2,3)$ and generalized elations with $f\in\{1,4,7,10\}$.
4. Write the involution-MOLS encoding and break only the symmetries that preserve $+6$.
5. Build MacNeish; SAT-find a second 2-MOLS; verify both with an encoder-independent checker.
6. Prove, with DRAT, that neither family has a third involution-mate.
7. Launch the $t=3$ instance (cell-symbol form and $\sigma,\delta$ form). Both kissat runs returned `UNKNOWN` at the 2400s budget (45M and 21M conflicts). That is a timeout, not an exclusion.

There is no finished proof that involutory elations are absent.

## 5. Computer residue

- `certs/identities.json` — $v=157$, 12246 pairs, $\lvert\det B\rvert=13\cdot12^{78}$.
- `certs/type_classification.json` — remaining types.
- `certs/macneish_involution_2mols.json` — explicit 2-MOLS with the involution.
- `certs/t2_squares.json` — a second, non-isotopic 2-MOLS from SAT.
- `certs/mate_t2.drat`, `certs/mate_macneish.drat` — drat-trim verified UNSAT for a third mate of each family.
- `certs/t3b.cnf`, `certs/sd3.cnf` — the undecided $t=3$ instances.

Replay commands are in `compute/README.md`.

## 6. What is proved vs still open

Proved tonight, independently checked:

- The two explicit involution 2-MOLS are Latin, pairwise orthogonal, and satisfy $L[r+6][c]=L[r][c]+6$.
- Neither family admits a third involution-Latin orthogonal mate. The two DRAT files verify.

Not proved:

- Nonexistence of *every* involution 3-MOLS, i.e. of an involutory elation, i.e. of $\lvert G\rvert=2$.
- Anything new about order-3 planar or generalized-elation cases.
- Existence or nonexistence of the plane.

The published Aut restriction is still Akiyama–Suetake–Tanaka 2023. A failed search with a verifier is the product; search residue is not a bound.
