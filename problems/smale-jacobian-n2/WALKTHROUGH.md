# Walkthrough — from degree 100 to the exceptional pair

## 0. What was actually missing

The missing object was not a plausible inverse formula for every plane Keller
map. It was much smaller: a trustworthy certificate for the only explicit
degree pair left below 125 by the current Newton-polygon reduction.

At first the natural landmark looked like Moh's degree-100 computation. That
was too old and too broad to be a useful finite handle. The useful question was
whether the later \((72,108)\) exception was still genuinely alive.

## 1. Named false starts

**Start from the 2026 three-variable announcement.** The recent papers are
mathematically suggestive, especially their tangent-line geometry, but the
announcement is not community consensus and the mechanism uses an extra
dimension. It could not certify anything about the plane conjecture.

**Rebuild Moh's tree.** Moh's author page still hosts data, but the printed
argument is difficult to replay case by case. Reconstructing it would at best
recover 100, below two later records.

**Use an arbitrary high-degree automorphism.** The shear

$$
(x,y)\longmapsto
\bigl(x+cb(ax+by)^d,\ y-ca(ax+by)^d\bigr)
$$

works in every degree. That is a useful test fixture, but it also shows why
large degree alone says nothing about the conjecture.

**Commit the full certificate.** The hard identity is about 89 MB and the
complete replay archive is 86 MB compressed. Duplicating it would make the
notebook worse to review. An immutable source commit, a whole-archive hash,
internal hashes, and a one-command replay give the same byte-level pin without
copying the blob.

## 2. The useful failure

The homogeneous-family route collapsed completely: every homogeneous plane
Keller perturbation is a shear. This did not move the record, but it fixed the
sign conventions, produced an exact inverse at degree 125, and exposed a
general lesson. A degree search must classify possible counterexamples, not
merely construct Keller maps of that degree.

The tangent-sweep route failed in a different way. Its Jacobian determinant
always contains the sweep parameter. That explains, in one line, why the raw
higher-dimensional picture cannot simply be drawn in the plane. It does not
rule out more elaborate twists.

## 3. The click

The 2022 paper does more than improve Moh numerically. Its Theorem 2.1 names
the entire remaining finite frontier: maximum degree at least 125, except for
\((72,108)\) and its transpose. Proposition 4.3 then writes that exception as
two concrete Laurent-polynomial systems.

A 2026 archive claimed exact unit-ideal certificates for precisely those two
systems. The decisive observation was that this was not another open-ended
search. The archive could be hashed, replayed, and connected back to the
published proposition by a small independent program.

## 4. The argument in discovery order

First, the four source polygons were transcribed directly from Proposition
4.3. Independent enumeration found 61 and 125 lattice points in the first pair,
and 25 and 47 in the second.

Second, the Laurent coordinates were recomputed rather than copied. Put

$$
t=xy^2,\qquad z=y^{-1}.
$$

Then \([t,z]=-1\) and \(x=t z^2\). Writing the upper bands as

$$
P=Az^2+Bz+C,
\qquad
Q=Dz^3+Ez^2+Fz+G
$$

and expanding \(P_zQ_t-P_tQ_z\) gives exactly five coefficient identities,
with \(2AD'-3A'D=t^2\) at the top.

Third, the three normalized coefficients occur at \((1,0)\), \((8,14)\), and
\((8,16)\). Their exponent matrix has determinant 14. Over an algebraically
closed field, the required roots exist, and a fourth output scaling preserves
the right-hand side \(x^2\).

Only then was the large archive allowed to speak. Its hash and eight internal
hashes matched. It regenerated the residual systems, checked the small unit
ideals, evaluated the hard identity through a separate exact-arithmetic path,
checked the branch symmetry, and ended with both branch markers.

Finally, Theorem 2.1 was applied once: with the exceptional pair gone, the
other alternative is maximum degree at least 125.

## 5. Computer search and certificate

There was no new heuristic search. q1 is a certificate replay and bridge
audit.

| Check | Exact result |
| --- | ---: |
| Case 1 lattice points | \(61,125\) |
| Case 2 lattice points | \(25,47\) |
| Laurent coefficient identities | 5 |
| Normalization determinant | 14 |
| First-block number-field degree | 35 |
| Number-field products in independent path | 13,410 |
| Equivalent scalar products | 335,250 |
| Hard branches | 2/2 pass |

The bridge was independently implemented in Python and Rust, and their output
was required to agree byte for byte. The large archive was replayed under
Python 3.14 with exact `python-flint`, `sympy`, and `gmpy2` arithmetic. q2 used
sparse integer polynomials. q3 used distinct formal symbols for every curve
coefficient.

## 6. What is proved and what remains open

The checked finite implication is:

$$
\boxed{\text{Every plane counterexample has }
\max\{\deg P,\deg Q\}\ge125.}
$$

That is a dent over the previously surviving maximum degree 108. It depends on
the published Guccione–Guccione–Horruitiner–Valqui reduction in the ordinary
way a computer-assisted corollary depends on its mathematical input; the local
bridge removes the extra transcription and normalization assumptions identified
by the certificate author.

The plane Jacobian conjecture is still open. No inverse was constructed for an
arbitrary Keller map, and no plane counterexample was found. The 2026
three-variable announcement is neither assumed nor refuted here. The q3
obstruction covers only the raw tangent-sweep template.
