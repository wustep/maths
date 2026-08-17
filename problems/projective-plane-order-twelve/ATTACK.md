# Attack log — projective plane of order 12

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House: write only here; no git; cite what we beat; no invented dent.
- Target: a 2-(157,13,1) design, equivalently 11 MOLS of order 12. Isolated SAT timeouts are not a dent.
- Tonight: a certified new forbidden automorphism type, an explicit construction, or a documented residue.

### Catalogue and literature (fetched tonight)

Eric Moorhouse, *Projective Planes of Small Order*, https://ericmoorhouse.org/pub/planes/ (revised November 2017; page re-fetched 2026-08-17). The table lists known planes of order \(n<34\). There is no order-12 incidence record. Completeness is claimed only through order 10 (Lam–Kolesova–Thiel; Lam–Thiel–Swiercz). The empty slot is a catalogue cross-check, not an exclusion.

TheoremDB packet `projective-plane-order-12` (snapshot 2026-07-25; records R592–R597) and the 2019/2023 Akiyama–Suetake–Tanaka papers:

| claim | source | status |
| --- | --- | --- |
| Bruck–Ryser silent: \(12\equiv0\pmod4\) | Bruck–Ryser, Canad. J. Math. 1 (1949) | theorem; det identity \(\lvert\det B\rvert=13\cdot12^{78}\) is a square |
| \(N(12)\ge5\) | Bose–Chakravarti–Knuth, Technometrics 2 (1960) | construction; 11 MOLS would be a plane |
| \(N(12)\ge5\) still the published lower bound | TheoremDB R596; Bruzda arXiv:2607.25954 (2026) still quotes five | no sixth square on the record |
| \(G\) is a \(\{2,3\}\)-group | Janko–van Trung 1980–82 | theorem |
| no elation of order 3 | Janko–van Trung, Stud. Sci. Math. 16 (1981) | theorem |
| \(\lvert G\rvert\) divides 16 or 9 | Horvatić-Baldasar–Kramer–Matulić-Bedenić 1986–87 | theorem |
| no group of order 16 | Suetake, JCTA 107 (2004) | theorem |
| no group of order 8 | Akiyama–Suetake, JCD 16 (2008) | theorem |
| no group of order 9 | Akiyama–Suetake–Tanaka, AJC 74 (2019) | theorem |
| no group of order 4 | Akiyama–Suetake–Tanaka, JCD 31 (2023) | theorem |
| hence \(\lvert G\rvert\in\{1,2,3\}\) | 2023 paper, combining the above | published record |
| no accepted plane / no complete exclusion | Moorhouse; TheoremDB R597, check through 2026-07-25; Wikipedia still open | open |
| equivalent to a balancedly multi-splittable quaternary Hadamard matrix of order 144 | Kharaghani–Suda, EJC 30 (2023) P2.49 | reformulation, not a resolution |

The 2019 corollary already said \(G\) is cyclic and \(\lvert G\rvert\) divides 3 or 4. The 2023 paper kills 4. Remaining automorphism *groups*: trivial, \(C_2\), \(C_3\).

### Remaining geometric types

Baer: an involution of a finite plane of order \(n\) is a homology (\(n\) odd), an elation (\(n\) even), or a Baer involution (\(n\) square). Here \(n=12\) is even and not square, so a non-identity element of \(C_2\) is an **involutory elation**.

Janko–van Trung exclude elations of *order 3*, not order 2. The 2023 classification leaving \(\lvert G\rvert=2\) possible is independent confirmation that involutory elations are still open. That is the first finite type to attack.

An involutory elation with centre \(C\) and axis \(L\ni C\) is equivalent to an affine plane of order 12 (delete \(L\)) admitting a translation of order 2. Coordinatize the 144 affine points as \(\mathbb Z_{12}\times\mathbb Z_{12}\) with \(\tau(x,y)=(x+6,y)\). After independent symbol relabelling of each parallel class, every Latin square in the corresponding MOLS family satisfies

\[
L(r+6,c)=L(r,c)+6\pmod{12}.
\]

An affine plane would give 11 such MOLS. Already \(t\) such MOLS, for any \(t\le11\), would be implied. So **UNSAT for any \(t\le11\)** is a certified exclusion of involutory elations, hence of \(\lvert\mathrm{Aut}\rvert=2\).

MacNeish (product of 2 MOLS of order 3 with 2 of order 4) supplies 2 MOLS of order 12, and the characteristic-2 translation on the order-4 factor is an involution of the required cycle type. So the \(t=2\) instance is expected SAT. The first interesting instance is \(t=3\).

Order-3 leftovers (for later): true homology impossible because \(3\nmid(n-1)=11\); true elation excluded 1981; remaining planar (Fix \(\cong\mathrm{PG}(2,2)\) or \(\mathrm{PG}(2,3)\)) and generalized elation/homology with \(1,4,7,10\) (and one generalized-homology \(f=13\)) fixed points.

### Plan

1. Write an exact \(t\)-MOLS encoder with the involution, plus an independent Latin/orthogonality/involution verifier.
2. Build the MacNeish pair in the standardized coordinates and check the encoding is faithful.
3. SAT-solve \(t=1,2,3,\ldots\) with kissat; on UNSAT emit and check a DRAT proof.
4. If \(t=3\) is SAT, climb; if the climb dies in timeouts, that is residue, not a dent.
5. In parallel, write the order-3 planar orbit model if the involution side stalls.

## 2026-08-17 — identities and remaining types

`compute/replay_identities.py` confirms \(v=157\), \(12246\) point-pairs, \(\lvert\det B\rvert=13\cdot12^{78}\), and that Bruck–Ryser is silent (\(12\equiv0\pmod4\)). \(12\) is not a sum of two squares; that fact has no force here.

`compute/classify_types.py` replays the cycle-index constraints for a collineation of order \(2\) or \(3\):

- \(v\equiv1\pmod3\), so an order-\(3\) element has \(f\equiv1\pmod3\) fixed points.
- A true homology would have \(f=n+2=14\equiv2\pmod3\), and also \(3\nmid(n-1)=11\). Impossible.
- A generalized homology has invariant axis \(L\not\ni C\) and \(f=1+k\) with \(k\) the number of fixed points on \(L\). Then \(k\equiv0\pmod3\) from \(f\equiv1\), but the axis action needs \(13-k\equiv0\pmod3\), i.e. \(k\equiv1\pmod3\). No solutions. Independently, the 2019 type list for order-\(3\) elements inside a group of order \(9\) already contains only planar and generalized-elation cases.
- A planar order-\(3\) element whose fixed subplane is a Fano plane forces an invariant ambient line with \(3\) fixed points and \(10\) extra points, and \(10\not\equiv0\pmod3\). Impossible. (The 2009/2019 papers already conclude that a planar element in their setting has a subplane of order \(3\).)
- A true elation of order \(3\) is the \(f=13\) generalized-elation case, excluded by Janko–van Trung 1981.

Remaining geometric types, after those divisibility checks and the published record:

| type | status |
| --- | --- |
| involutory elation | open; unique Baer type for \(\lvert G\rvert=2\) |
| planar, \(\mathrm{Fix}\cong\mathrm{PG}(2,3)\) | open |
| generalized elation, \(f\in\{1,4,7,10\}\) | open |

The first of those is a single type. Excluding it is exactly \(\lvert\mathrm{Aut}\rvert\neq2\).

## 2026-08-17 — involution as \(t\) MOLS

Coordinatize the affine plane obtained by deleting the axis so that \(\tau(x,y)=(x+6,y)\). After independent symbol relabelling of each parallel class, every Latin square satisfies \(L[r+6][c]=L[r][c]+6\). An affine plane would give \(t=11\). Already any \(t\le11\) is implied, so UNSAT for some \(t\le11\) excludes involutory elations.

Safe symmetry breaking (anything more, such as first-row identity on every square, does *not* commute with \(+6\) and produces false UNSAT):

- column permutation: \(L_0[0]=\) identity
- free-row sort: pair-index of \(L_0[r][0]\) is \(r\) for \(r=1,\dots,5\)
- for \(k\ge1\), a \(+6\)-commuting symbol map sends \(L_k[0][0]\) to \(0\)
- for \(t\ge3\), swap of squares \(1,2\) sorts \(L_1[0][1]\le L_2[0][1]\)

Encoder: `compute/encode_involution_mols.py`. Independent checker: `compute/verify_involution_mols.py`.

## 2026-08-17 — \(t=1,2\) are SAT; two explicit 2-MOLS

kissat 4.0.4:

- \(t=1\): SAT, reconstructed square is Latin and involution-compatible (`certs/t1_squares.json`).
- \(t=2\): first attempt with over-normalization was a false UNSAT; after the fix, SAT, independently verified Latin / orthogonal / involution (`certs/t2_squares.json`).

MacNeish product of the two MOLS of order \(3\) with two MOLS of \(\mathrm{AG}(2,4)\), using the characteristic-\(2\) translation on the \(\mathbb F_4\) factor, relabels to the same involution (`compute/macneish_pair.py`). Independently verified (`certs/macneish_involution_2mols.json`). Intercalate counts \(108+108\) versus \(90+78\) for the SAT pair, so these are two distinct isotopy classes.

The SAT pair does *not* quotient to Latin squares of order \(6\) on columns \(0..5\). The MacNeish pair does; those order-\(6\) squares are not orthogonal (Tarry), as they must not be.

## 2026-08-17 — both known 2-families have no third involution-mate

`compute/encode_mate.py` encodes one more involution-Latin square orthogonal to a given family. After fixing a first-version orbit-mixup (the UNSAT of the buggy encoder was discarded), the corrected encoder:

- accepts a mate of \(t=2\) square \(0\) (SAT, independently verified orthogonal)
- proves the SAT \(t=2\) pair has no third mate: kissat UNSAT, `drat-trim` **VERIFIED** (`certs/mate_t2.drat`)
- proves the MacNeish pair has no third mate: kissat UNSAT, `drat-trim` **VERIFIED** (`certs/mate_macneish.drat`)

These are certificates that two isotopy classes of involution 2-MOLS are maximal. They are not a classification of all classes, so they are not yet \(\lvert G\rvert\neq2\).

Allsat of mates of each \(L_0\) found \(\ge200\) mates; a 50-pair sample had no two mates orthogonal to each other. The orthogonality graph on those mates looks like a star with centre \(L_0\). Suggestive, not a proof.

## 2026-08-17 — \(t=3\) SAT (the actual \(\lvert G\rvert=2\) instance)

`certs/t3b.cnf`: \(66960\) variables, \(221917\) clauses, tight breaking. kissat default and `--stable`, 2400s budget, no proof log (a proof-logging run wrote multiple gigabytes without finishing and was killed). Isolated timeout is not a dent.

`compute/encode_sigma_delta.py` rewrites the same instance in \((\sigma,\delta)\) coordinates (\(A=\sigma+6\delta\) on the free half): \(8640\) variables for \(t=3\). \(t=1,2\) SAT and independently reconstruct to verified squares. The \(t=3\) CNF is `certs/sd3.cnf`.

`compute/search_t3.c` is a column-major backtrack of the same normalized \(t=3\) instance (construction hunter, not a proof log).

`compute/encode_two_mates.py` (fix \(L_0\), search two orthogonal mates) timed out at 120s on the SAT \(L_0\). Same hardness.

While this runs: do not claim \(\lvert G\rvert\neq2\). The published record remains Akiyama–Suetake–Tanaka 2023, \(\lvert G\rvert\in\{1,2,3\}\).

## 2026-08-17 — \(t=3\) SAT timed out

kissat 4.0.4 `--time=2400`:

- `certs/t3b.cnf` (cell-symbol, 66960 vars): `s UNKNOWN` after 2396.43s and 45,210,387 conflicts (`certs/t3c.out`).
- `certs/sd3.cnf` (\(\sigma,\delta\), 8640 vars): `s UNKNOWN` after 2396.14s and 21,232,051 conflicts (`certs/sd3.out`).

Isolated SAT timeouts are not a dent. No \(\lvert G\rvert\neq2\) claim.

Certified tonight, and only this: two non-isotopic involution 2-MOLS, each with a drat-trim-verified proof that it has no third involution-mate. That is residue, not a new forbidden Aut type and not a bound.
