# Walkthrough — five-dimensional kissing number

## 0. What was actually missing

The published range is still $40\le\tau_5\le 44$. The missing object is
not a better floating 3-point SDP — Mittelmann–Vallentin already have
$s_{14}(5)=44.99899685\ldots$, which is how 45 died, and the house
rule is that a restricted numerical SDP without an exact positivity
certificate is an incomplete search.

What *would* move the needle is either

- a polynomial (or SOS matrix) whose Gegenbauer / Bachoc–Vallentin
  data are exactly nonnegative and whose value is strictly less than 44,
  43, 42 or 41 on the *unrestricted* interval $t\le 1/2$, or
- forty-one explicit points on $S^4$ with all inner products
  $\le 1/2$.

Neither exists in the 2026 record. The degree of freedom that *is*
available overnight is the inner-product support: if a putative 41–44
point code is forced to live in a finite set $T\subset[-1,1/2]$, the
Delsarte dual only has to be nonpositive on $T$, not on the whole
interval, and that LP is small enough to solve over $\mathbb Q$.

## 1. Named false starts

**Add a 41st point to $D_5$.** For unit $x$, the $D_5$ roots demand
$|x_i|+|x_j|\le 1/\sqrt{2}$ for every pair. The minimum of the largest
pair-sum on $S^4$ is $2/\sqrt{5}$, and $4/5>1/2$. Dead on arrival;
this is maximality of $D_5$, not a new code.

**Stack a 24-cell equator under the $Q_5$ caps.** $Q_5$ is
$10+20+10$ along the all-ones axis. Replacing the 20-point $A_4$
equator by a 24-cell would be a 44-point code. $A_4$ is not a 24-cell
minus two antipodal pairs (66 histograms, no match), and more simply
the equatorial polytope $\sum x_i=0$, $x_i-x_j\le 1$ has
$|x|^2\le 6/5<2$. There is no extra equatorial vector at all.

**Unrestricted high-degree Delsarte.** Levenshtein is exactly 48.
Odlyzko–Sloane already took the continuum dual to $\approx 46.345$.
Sidelnikov / Boyvalenkov–Danev–Bumova say you cannot beat Levenshtein
by a few extra degrees, and the 1979 table is the known continuum
optimum in this dimension. We did not rerun that search as a claim.

**Enlarging $T$ until it looks unrestricted.** Adding $Q_5$'s extra
angles $\{-4/5,-3/10,1/5\}$ to the $L_5$ dual lifts the exact bound
from $43.97$ to $45.66$ or $54.8$. The moment $T$ contains all
four known 40-point angle sets, Delsarte is back above 44.

**Numerical 41st point against $L_5,Q_5,R_5$.** Powell on the sphere,
91 starts each, best slack $\approx-0.2649$. The optimiser sits on a
deep hole (inner product $2/\sqrt{5}$). Evidence of maximality, not a
certificate, and not a construction.

## 2. The useful failure

The $Q_5$-equator attempt forced a clean description of extra points
over a *fixed* 4-dimensional kissing code. Once the equator is a
24-cell — which $D_5$ and $L_5$ both contain — the same calculation
gives a height constraint $h^2\ge 1/2$ and then Rankin's
$A(4,0)\le 8$ in each open hemisphere. That is an exact 40-point cap
for every 5-dimensional kissing code that contains a 24-cell.

The other useful failure was the *real* Delsarte relaxation on
$T_{D_5}=\{-1,-1/2,0,1/2\}$: it allows $N=42$ with
$A=(-1\mapsto 1,\,-1/2\mapsto 12.8,\,0\mapsto 14.4,\,1/2\mapsto 12.8)$.
Those averages are not integer pair-counts. The integrality slice is
empty at 42, 43 and 44, and at 41 it is nonempty only when there are
exactly twenty antipodal pairs.

## 3. The click

Delsarte on a *finite* $T$ is an interpolation problem, not an SDP.
The numerical $L_5$ dual used six Gegenbauer coefficients
$(c_0,c_1,c_2,c_3,c_4,c_9)$ and vanished on five angles. That is a
$5\times 5$ linear system over $\mathbb Q$. Solving it produces

$$
\frac{f(1)}{f_0}=\frac{239925}{5456}=44-\frac{139}{5456}<44
$$

with every $c_k\ge 0$ and $f\le 0$ on
$T_{L_5}=\{-1,-3/4,-1/2,-1/4,0,1/2\}$. The same pattern for $T_{D_5}$
gives the integer bound 42.

Together with the 24-cell lemma and the integer slice, every
$k\in\{41,42,43,44\}$ is now excluded in at least one exact restricted
class, and 44 is excluded in two of them ($T_{L_5}$, and anything
containing a 24-cell).

## 4. The argument, in the order it was found

### 4.1. The four 40-point codes are real

$D_5$ is the permutations of $(\pm 1,\pm 1,0,0,0)$. $L_5$ replaces
the layer $x_5=+1$ by the odd-sign half-spinor. $Q_5$ (resp. $R_5$)
replaces the coordinate-sum $+2$ layer of $D_5$ (resp. $L_5$) by
the reflection of the $-2$ layer across $\sum x_i=0$. All four have
squared norm 2 and max inner product 1, and the pair histograms match
Cohn–Rajagopal Table 2.1.

### 4.2. No 24-cell, no 41

Rotate a 24-cell to the hyperplane $x_5=0$. An extra unit point at
height $h$ has direction $u\in S^3$ satisfying
$\varphi(u)\le 1/\sqrt{2(1-h^2)}$. Because $\varphi\ge 1$, one has
$|h|\ge 1/\sqrt{2}$ (or a pole). In a single open hemisphere the
projected 4-vectors have pairwise inner products $\le 0$, so there
are at most $A(4,0)\le 8$ of them. The bound $A(4,0)\le 8$ is the
polynomial $t^2+t$, whose dimension-4 Gegenbauer expansion is
$\frac14 P_0+P_1+\frac34 P_2$. Poles are incompatible with any other
extra point in the same hemisphere. Hence at most $24+8+8=40$ points.

### 4.3. Exact dual for Leech's angles

Let $P_k^{(5)}$ be the dimension-5 Gegenbauer polynomials normalised
by $P_k(1)=1$, recurrence
$(k+3)P_{k+1}=(2k+3)t P_k-k P_{k-1}$. The polynomial

$$
\begin{align*}
f&=P_0+\frac{169541}{45136}P_1+\frac{28}{3}P_2+\frac{6095}{651}P_3\\
&\qquad+\frac{32}{3}P_4+\frac{131072}{13299}P_9
\end{align*}
$$

has nonnegative coefficients, vanishes at
$t\in\{-3/4,-1/2,-1/4,0,1/2\}$, and takes the value $-10773/5456<0$
at $t=-1$. Therefore any spherical code in $S^4$ whose distinct
inner products lie in that set has size at most $239925/5456<44$.

### 4.4. The $D_5$ angle set, with integrality

The companion polynomial
$P_0+(49/45)P_1+(28/3)P_2+(32/3)P_4+(896/45)P_5$ vanishes on
$\{-1,-1/2,0,1/2\}$ and gives the real bound 42. Enumerating integer
pair-counts at Gegenbauer degree 8 shows there is no such distribution
of size 42, 43 or 44, and the only size-41 distributions have exactly
twenty antipodal pairs. Those twenty pairs are a 40-point
$\{-1,-1/2,0,1/2\}$-code, hence (scaling by $\sqrt{2}$) forty roots
of an even lattice of rank $\le 5$, hence a copy of $D_5$, which
cannot be extended.

## 5. Computer search

- `compute/certs/restricted_delsarte.json` — the two exact duals.
- `compute/integer_d5.json` — the integer slice, including the empty
  $n_{-1}\le 19$ scan at $N=41$.
- `compute/q5_extend.json` — numerical slacks $\approx-0.2649$ against
  $L_5,Q_5,R_5$; equatorial obstruction $|x|^2\le 6/5$.
- `compute/construct_search.json` — cube+axes $=26$; $D_5$ plus holes
  never exceeds 40.
- `figures/restricted_duals.png` — the two duals on $[-1,1/2]$. They
  *are* allowed to be positive between the points of $T$; that is the
  whole point of restricting $T$.

Replay: `sh compute/run_all.sh`, or just
`compute/.venv/bin/python compute/verify_certificates.py`.

## 6. What is proved vs still open

**Proved here (restricted).**

- No 5-dimensional kissing code containing a 24-cell has more than 40
  points. In particular $k\in\{41,42,43,44\}$ is impossible in that
  class, and $D_5$ and $L_5$ are maximal.
- No spherical code in $S^4$ with inner products in
  $\{-1,-3/4,-1/2,-1/4,0,1/2\}$ has 44 points.
- No spherical code in $S^4$ with inner products in
  $\{-1,-1/2,0,1/2\}$ has 41, 42, 43 or 44 points.
- $Q_5$ has no additional equatorial point.

**Still open (as of 17 August).**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- Existence of a 41–44 point code whose angle set is not contained in
  $T_{L_5}$ and which does not contain a 24-cell. $Q_5$ and $R_5$
  already show that such angle sets exist at size 40.
- An exact (SOS) certificate that the Bachoc–Vallentin number
  $s_d(5)$ is $<44$ for some $d$. The published $44.998\ldots$
  is high-accuracy numerical, not a rational Gram matrix.
- Maximality of $Q_5$ and $R_5$ as spherical codes (numerical slack
  is negative, not a proof).

## 7. 27 August: the polar is the same $5/4$ for every published code

The missing object on 17 August, for $Q_5$ and $R_5$, was a positivity
certificate that no 41st equal-norm point exists. Powell on the sphere
sat on a $2/\sqrt5$ hole with slack $\approx-0.2649$. That is the same
deep-hole inner product that kills $D_5$, but $Q_5$ does not contain
enough $D_5$ roots for the pair-sum argument.

The polar $P(C)=\{x:\langle x,p\rangle\le 1\ \forall p\in C\}$ is the
exact feasible set for a new point of any length. It is a 5-dimensional
polytope with rational vertices. $|x|^2$ is convex, so its maximum is
at a vertex. Enumerating the $C(40,5)$ tight 5-planes — once in C,
once in Python, same independent-set and vertex counts — gives

$$
\max_{x\in P(C)}|x|^2=\frac54<2
$$

for each of $D_5,L_5,Q_5,R_5$. The recorded maximizer of $Q_5$ is
$-\frac12(1,1,1,1,1)$, which saturates ten reflected-cap inequalities
at inner product 1 and has squared norm $5/4$. So the 17 August
numerical hole *was* the polar vertex, scaled up to the sphere; it
never reaches squared norm 2.

That closes maximality of $Q_5$ and $R_5$. It does not close $\tau_5$.

The other click the same night was integrality on $T_{Q_5}$. The real
dual sits at $44.67$ and cannot exclude 44. Clearing denominators in
the Gegenbauer rows and scanning the integer box
($14.7$ billion points, pad 15 around the real AABB, $n_{-1}$ unrestricted)
finds no feasible $(n_t)$ at $N=44$. The published $Q_5$ histogram at
$N=40$ passes the same tables. So 44 is impossible among codes whose
distinct inner products lie in the $Q_5$ angle set. Integer $T_{L_5}$
still has hits at 41, 42 and 43.

**Proved on 27 August (restricted).**

- $D_5,L_5,Q_5,R_5$ are all maximal as spherical codes.
- No spherical code in $S^4$ with inner products in
  $\{-1,-4/5,-1/2,-3/10,0,1/5,1/2\}$ has 44 points.

**Still open.**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- A 41–43 point code whose angles are not contained in $T_{D_5}$ and
  which is not one of the four published 40-point codes plus a point
  (those four are now maximal).
- An exact SOS certificate that $s_d(5)<44$.

## 8. 27 August, later: the $T^5$ pool is 360, not 355

q1 left a 355-vertex compatibility graph unsearched. Rebuilding it
showed the missing five points were the basis itself: a basis vector
fails $\langle v,v\rangle\le 1$. After that check is “other points of
the basis”, the pool has 360 equal-norm rational vectors and contains
all four published 40-point codes as cliques.

Those five basis vectors are adjacent to every other pool point. So

$$
\omega(G_{360})=\omega(G_{355})+5.
$$

A 41-clique in the pool is exactly a 36-clique in the remainder. The
41-search on the 355-graph finishes (607171 nodes, empty). The 36-search,
which is the one that would actually produce a 41-point code, did not
finish. That is residue, not a construction and not an exclusion.

The same night, the half-integer sphere
$(1/2)\mathbb Z^5\cap\{\lvert x\rvert^2=2\}$ is a 200-point graph
containing $D_5$ and $L_5$, and it has no 41-clique. Layer-swaps of
$D_5$ and $L_5$ across every short integer normal recover size 40
(including $Q_5$ / $R_5$) and nothing larger. The $Q_5$-cap orbit of
320 signed permutations has no 41-clique.

On the dual side the continuum Delsarte number is still
$46.3368\ldots$. Exact polynomials of the form $(t-1/2)q(t)^2$ with
nonnegative Gegenbauer coefficients exist — the best in a small
search is $53235/1109\approx 48.003$ — but nothing goes below 44 on
the whole interval $[-1,1/2]$. Odlyzko–Sloane already said that LP
cannot.

**Proved on 27 August, later (restricted / finite graphs).**

- No 41-point code in the 355-point $T^5$ remainder, in the
  200-point half-integer sphere, or in the 320-point $Q_5$-cap orbit.
- No certified unrestricted Delsarte dual below 44 at the degrees
  searched.

**Still open.**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- A 36-clique in the 355-point $T^5$ remainder (that plus the five
  basis vectors would be a 41-point code).
- An exact SOS certificate that $s_d(5)<44$.

## 9. 27 August, later: extras miss at least four $D_5$ roots

The 1480-point leftover is not an unstructured 41-clique. In the
integer model $a\in\mathbb Z^5$, $a\cdot a=32$, the 40 vectors with
two $\pm 4$ entries *are* $D_5$. Every one of the 1440 extras kisses
at most 36 of those 40. Polar maximality already forbids $n_1=40$,
so a 41-set in this graph is $n_1\le 36$ $D_5$-type points plus at
least five extras.

Two extras with missed-root sets $M,M'$ have common $D_5$
neighbourhood $40-|M\cup M'|$. An extras-clique $E$ therefore
contributes

$$
|E|+(40-|U|),\qquad U=\bigcup_{e\in E}M_e,
$$

and that total is at least 41 if and only if $|E|\ge|U|+1$ with every
missed set contained in $U$. The $U$ that can arise all contain at
least one actual missed set, so enumerating $k$-supersets of those
seeds is a complete generation for each $k$.

That scan finishes for $k=4,5,6,7$. No extras-clique of size
$k+1$. So there is no 41-point code in $(1/4)\mathbb Z^5$ that uses
33 or more $D_5$ roots. The same night the 36-clique in the $T^5$
remainder was repaired out to edit distance 2 around each published
35-clique and searched to 40 million B&B nodes; neither produced a
hit, and neither is an emptiness proof.

Unrestricted Delsarte is still $46.3368\ldots$. Opening a gap at
$t=-2/3$ drops the numerical value to $\approx 37.46$, which would
exclude 41–44 if the gap were a theorem. It is not: $D_5,L_5,Q_5,R_5$
all have an angle in $[-1,-2/3)$. The rationalized polynomials fail
Sturm besides.

**Proved on 27 August, later (restricted).**

- No 41-point code in $(1/4)\mathbb Z^5\cap\{\lvert x\rvert^2=2\}$
  uses 33 or more $D_5$-type points.
- No certified unrestricted Delsarte dual below 44.

**Still open.**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- The $n_1\le 32$ slice of the 1480-point graph, and a 36-clique in
  the 355-point $T^5$ remainder.
- An exact SOS certificate that $s_d(5)<44$.

## 10. 27 August, later: exact $S_k^5$ over $\mathbb Q$, no dual below 44

The missing object is still an exact 3-point certificate with value
strictly less than 44. Mittelmann–Vallentin already have a
high-accuracy number $s_{14}(5)=44.99899685\ldots$; that is how 45
died, and it is not a rational Gram matrix.

`compute/q4/bv.py` builds the matrices. $Q_k^{4}$ is the polynomial
identity that clears the square roots in
$P_k^{4}((t-uv)/\sqrt{(1-u^2)(1-v^2)})$. $S_k^5$ is the average of
$u^i v^j Q_k$ over the six permutations of $(u,v,t)$ (Bachoc–Vallentin
Remark 3.4). The self-tests check $Q_0=1$, $Q_1=t-uv$,
$Q_k(u,u,1)=(1-u^2)^k$, $S_0(1,1,1)=J$, and $S_k(1,1,1)=0$ for
$k\ge 1$.

1-point Delsarte on the whole interval is still $46.3368\ldots$. A
polynomial with nonnegative Gegenbauer coefficients cannot go below
that, so the rest of the night was 3-point. Constant-multiplier
Putinar, the exact $p_4$-span of $g$, a dictionary of squares, and a
floating Putinar SDP at $d\le 6$ all failed to produce a rational
identity with value $<44$. The $d=6$ dictionary number $40.38$ did
not snap; the SDP values near 40 failed a grid sign check. Residue.

The hierarchy itself explains the miss. Bachoc–Vallentin needed
$d=10$ to reach 45. Mittelmann–Vallentin needed $d=14$ to reach
$44.998$. Any feasible dual at $d=14$ has value at least that
optimum, so it cannot exclude 44. A dent would need $d>14$ or a
different hierarchy, and then an exact SOS certificate of a number
strictly less than 44.

## 11. 27 August, later: the octads are the $D_5$ coordinate-stars

The $n_1\le 32$ leftover is not an unstructured $k$-superset scan.
The 40 $D_5$ roots are the signed pairs $\pm 4e_i\pm 4e_j$. For each
axis $i$ and sign $s$ the eight roots with $x_i=s\cdot 4$ form a
star. There are ten of them. The 160 four-seeds partition among those
stars: inside a star the four other axes each contribute a sign pair,
and the 16 four-seeds are the $2^4$ ways to pick one sign on each.

A 7- or 8-subset of a star is exactly the promising $U$ at $k=7,8$.
The extras pool of a star has 80 vertices and clique number 8, so the
best 41-candidate on that $U$ is $8+(40-8)=40$. C and Python empty
every 8-superset of an actual seed ($7\,407\,770$ of them; only the
ten stars are promising). Seed-union BFS then empties $k=9,10$ by
part-count and $k=11,12$ by a coloured search: 960 and 4640 promising
unions, $\omega=k$ again, total 40.

That is the $n_1\ge 28$ half of the leftover graph, on top of q3's
$n_1\ge 33$. The remaining 41-candidates use at least 13 extras. A
hash-free walk of the same seed-unions — each $U$ has a unique
parent, the union of all but its last irredundant seed — finishes
$k=13$ through $18$ without a table. Promising pools grow into the
tens of millions by $k=18$, but every extras-clique is size $k$,
total 40. So there is no 41-set with $n_1\ge 22$. The $n_1\le 21$
slice is unfinished. Residue, not a 41-code.

The $T^5$ remainder still has $\omega\ge 35$ and $\chi\ge 36$. Two
SAT solvers return no 36-clique; without a DRAT that is not a
certificate. Share 30 through 24 with each published 35 are empty
in C, so a 36-clique, if one exists, shares at most 23 with
$D_5,L_5,Q_5$ and $R_5$.

**Proved on 27 August, later (restricted).**

- No 41-point code in $(1/4)\mathbb Z^5\cap\{\lvert x\rvert^2=2\}$
  uses 22 or more $D_5$-type points.
- Each $D_5$ coordinate-star has extras-clique number 8.
- No 36-clique in the $T^5$ remainder shares 24 or more vertices with
  a published 35-clique.
- No certified unrestricted Delsarte dual below 44.

**Still open.**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- A 41-set in the 1480-graph with $n_1\le 21$, and a 36-clique in
  the $T^5$ remainder that shares at most 23 with every published 35.
- An exact SOS certificate that $s_d(5)<44$.

## 12. 27 August, later: the $T^5$ remainder has no 36-clique

The leftover that actually had a handle was the 355-graph, not the
continuum dual. q4 already knew $\omega\ge 35$ and $\chi\ge 36$, and
two SAT solvers returned no 36-clique. That is not a certificate.
Share 24 through 30 being empty only says that a 36-clique, if one
exists, is far from every published 35.

PySAT Cadical195 produced a 16.5-million-line ASCII DRAT. Heule
`drat-trim` read it and died with `s NOT VERIFIED` / no conflict.
The solver said unsat; the proof object was junk. Residue.

The useful failure on the other leftover was the seed graph. Two
seeds are compatible if *some* extras kiss. The 80 six-seeds form
an 80-clique of union 40. Every three coordinate-stars give a
leftover-tight seed pool — $(22,21)$ or $(23,22)$. Those pools are
not 41-codes. Extras B&B on all 120 of them is complete: extras
clique number at most 19 on the size-22 unions and at most 18 on
the size-21 unions. With q4's $|U|\le 18$ empty, no 41-set has its
missed-root union inside three stars. The $n_1\le 21$ leftover, if
it is nonempty, has star-cover at least 4.

The click on $T^5$ was to stop asking PySAT for a proof and run
native CaDiCaL 3.0.1 on the same DIMACS. It writes a binary DRAT.
`drat-trim` then says `s VERIFIED`: 671{,}198{,}215 bytes, 4.79
million of 10.8 million lemmas in the core, 303 million resolution
steps, no RAT. So there is no 36-clique in the 355-graph. The five
universal basis vectors of the Szöllősi pool do not extend to 41.

Share 23 finished the same afternoon, independently: each published
remainder 35 has $C(35,12)$ candidate 23-cores, and every common
neighbourhood has extras clique number at most 12 (need 13). That
is now redundant for emptiness of 36, but it is the reason we
believed the SAT.

The $n_1\le 21$ SAT on the 1480-graph is still running. Part-count
does not empty those slices. No 41-code and no unrestricted dual
below 44. The published interval did not move.

**Proved on 27 August, later still (restricted).**

- No 36-clique in the 355-point $T^5$ remainder (native CaDiCaL
  DRAT, `drat-trim` verified).
- No 41-point kissing code in the Szöllősi $T^5$ pool.
- No leftover 41-set in the 1480-graph whose missed-root union sits
  in three $D_5$ coordinate-stars.
- No leftover-tight type-A extras clique ($|C|\ge 20$ and
  $|U|\le|C|-1$).
- Share 23 with each published 35 is empty.

**Still open.**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- A 41-set in the 1480-graph with $n_1\le 21$ and star-cover at
  least 4.
- An exact SOS certificate that $s_d(5)<44$.

## 13. 27 August, later: four stars are not enough

The leftover after three stars was a union that needs at least four
coordinate-stars. Colouring does not kill it. Every 4-star extras
graph uses 20 to 32 colours, so the 3-star bound $\omega\le 19$
does not lift.

The useful failure was the colouring, and also the part-count: all
210 four-star unions are leftover-tight by seed count (64, 72, or
79 seeds). A seed pool is not a 41-code.

The click was to stop asking for extras $\omega$ and run the
leftover-tight cut. A 20-clique of extras with large missed-union
is not a 41-set. C branch-and-bound on each of the 210 pools, with
that cut, finishes: 26.8 million nodes, no leftover 41-set.
Python leftover-tight search on a covering sample of 38 pools
(every two-axis $k=28$ pool and a stride of the rest) matches, 38
of 38. Two algorithms, same emptiness. Restricted to the 1480-graph.

So a remaining 41-set in that graph has star-cover at least 5. That
is not empty by combinatorics: the smallest $D_5$-root set that
hits every 4-star complement has size 5. Five-star extras graphs
are larger (528 to 625 vertices, 28 to 39 colours). Four of them
ate 20 million nodes and did not finish. Leftover-tight SAT on
those four $k=32$ pools came back unsat, without a stored DRAT.
Global leftover SAT on $|U|=19$ with the 4-star forbid, and a
200-million-node extras B&B with that prune, did not finish.

No unrestricted dual below 44. 1-point Delsarte is still the
Odlyzko–Sloane number. The $(t-1/2)q^2$ grid that certified sat
near 59, worse than the previous ansatz 52. Did not claim
$\tau_5=40$.

**Proved on 27 August, later still (restricted).**

- No leftover 41-set in the 1480-graph whose missed-root union sits
  in four $D_5$ coordinate-stars.

**Still open.**

- The unrestricted kissing number: $40\le\tau_5\le 44$, unchanged.
- A 41-set in the 1480-graph with $n_1\le 21$ and star-cover at
  least 5.
- An exact SOS certificate that $s_d(5)<44$.

## 14. 27 August, later: five stars and the $|U|=19$ SAT

The leftover after four stars was a union that needs at least five
coordinate-stars. Colouring does not kill it: every 5-star extras
graph uses 28 to 39 colours.

The useful failure was the 20-million-node C cutoff on four $k=32$
pools, and leftover-tight SAT on those four coming back unsat
without a stored DRAT. Same lesson as the $T^5$ 36-clique: PySAT
unsat is a lead; native CaDiCaL plus `drat-trim` is the
certificate.

The click on the 252 five-star hosts is the signed-permutation
group of the coordinates. It has order $3840$ and acts
transitively on each axis type: 60 pools of type $(2,1)$ ($k=32$),
160 of type $(1,3)$ ($k=31$), 32 of type $(0,5)$ ($k=30$). One
leftover-tight CNF per type, if unsat with a stored DRAT, empties
the orbit.

The other leftover is the global $|U|=19$ SAT with the 4-star
forbid. Minimum $|U|$ with star-cover at least 5 is still 5, so
combinatorics does not empty that slice. The q6 grow prune that
only fired at $|P|\le 160$ is the B&B hole: the remaining
missed-union is cheap to compute at every node.

The dual line is the same 1-point Delsarte floor. Drop it if
another $(t-1/2)^p q^2$ grid stays above 44.
