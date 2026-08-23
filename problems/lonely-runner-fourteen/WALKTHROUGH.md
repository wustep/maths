# Walkthrough — the gcd branch that composite 14 makes wide

## 0. What was actually missing

Not a search. A term.

The folder had been reading the 14-runner case as blocked by a missing
algebraic identity: Sungkawichai and Trakulthongchai prove that the tuple
$(1,2,\dots,k)$ is eventually $(k,p)$-proper when $k+1$ is an odd prime,
by a polynomial argument in the field with $k+1$ elements, and $14$ is
not prime. That reading is what set the previous campaign's target.

The degree of freedom that was actually sitting unused is on the other
side of the same proposition. Their Proposition 4.4 splits the fiber
above $(1,\dots,k)$ into three cases, and one of them is discharged not
by any witness time but by the *gcd condition* in their Definition 2.1: a
speed tuple is proper as soon as some prime dividing $l = k+1$ divides
all but one of its coordinates. When $k+1$ is prime that condition says
"at most one nonzero coordinate", which is nearly nothing, and it is easy
to read past it. When $k+1 = 14$ it says "some $q \in \{2,7\}$ divides
all but one coordinate", which is a large piece of $(\mathbb Z/14)^{13}$.

The previous campaign was searching a space with that piece left in. So
it was looking for witnesses for tuples that never needed one.

## 1. Named false starts

**Redo Proposition 4.1 over $\mathbb Z/14$.** Their proof compares
leading coefficients of two degree-$k$ polynomials that agree on $k+1$
points, and concludes $1 \equiv -|G|$. Both steps want a field.
$\mathbb Z/14$ has zero divisors and the argument dies on the first line.
Killed on paper, before writing code.

**Clear $B_{13}$ with more primes.** Proposition 2.7 gives
$\mathrm{LRC}(k)$ from $J(k,p) = \emptyset$ over a prime set with
$\prod p \ge B_k$. Here $\ln B_{13} = 670.35$, and the earlier note that
primes in $[191,800]$ only reach $591.6$ is right. But the conclusion
drawn from it — "one modular constraint cannot finish" — was answering
the wrong question: the requirement is a long enough *list*, and the list
just needs to run to about $p \approx 880$. What actually kills this is
their Section 7: each $J(13,p) = \emptyset$ needs $I(13,p,1)$, roughly
$1.1 \times 10^{17}$ tuples at $p = 191$ under their own Section 5.1
reduction. Dead on cost, not on arithmetic.

**Resume the leftover CSP.** The previous run enumerated *vectors* —
millions per zero-pattern — and had been left partway through the
"remaining columns 4 to 12" range. Continuing it would have been weeks
of arithmetic toward a false statement. See beat 2.

## 2. The useful failure

Rewriting the question as a covering problem made it cheap enough to just
*ask*, so the first thing to do was ask it in the form the previous
campaign had assumed, over all of $N_{13}$ — nonzero with a zero
coordinate, no gcd condition. The answer came back in 27 seconds, and it
was the wrong sign: there is such a vector,
$$v = 2\cdot(1,2,\dots,13) \bmod 14 = (2,4,6,8,10,12,0,2,4,6,8,10,12),$$
and none of the $14 \times 191 = 2674$ pairs $(s,j)$ saves it.

That was the useful failure. The target as stated was false, so the
search that was running could not have terminated the way it was aimed —
and the vector sits in exactly the unfinished range.

Then look at what the counterexample *is*. Every coordinate is even. It
is not a subtle object; it is the whole of $2\mathbb Z/14$. And a tuple
all of whose coordinates are even is precisely what the gcd condition
throws away. The false statement and the missing term are the same fact
seen twice.

## 3. The click

Put the gcd condition back and the hypothesis becomes clean. For a prime
$q \mid m$, "some $i$ has $q \mid v_j$ for all $j \ne i$" is the same as
$\#\{j : q \nmid v_j\} \le 1$. So with $m = 14$:

> $v$ needs a witness exactly when it has a zero coordinate, at least two
> odd coordinates, and at least two coordinates not divisible by 7.

Two counts and a flag. And it is the *same* shape at every composite
$m$ — which means the guess is testable at small $m$ where brute force
still runs.

It does. At $m = 6$ the p-independent statement has 64 obstructions and
at $p = 31$ it has none; at $m = 8$, 2596 and none at $p = 59$. Composite
$m$ breaks the $p$-free statement and $p$ repairs it. That is the pattern
the $k = 13$ case then reproduces.

## 4. The argument, in the order it was found

Write $B^{(j)}_i = \lfloor 14\{ij/p\}\rfloor$, the $i$-th entry of
$r_{13}(j/p)$. Call a pair $(s,j)$ a *constraint*, and say coordinate $i$
taking value $a$ *hits* it when $sa + B^{(j)}_i \equiv 0$ or
$13 \pmod{14}$. Unwinding the definition:

> $v$ has no witness $\iff$ the sets $\mathrm{hit}(i,v_i)$ cover *all*
> $14p$ constraints.

So the question is set-cover feasibility in 13 variables of 14 values —
not an enumeration over the $14^{13} - 13^{13} - 1 \approx 7.9\times
10^{14}$ candidates. That is the entire reason this became a four-minute
computation instead of a multi-week one.

Two reductions come free. Every $s = 0$ constraint is hit by every $v$,
because some coordinate of $r_{13}(j/p)$ is always $0$ or $13$ — which is
just Goddyn–Wong tightness of $(1,\dots,13)$, and the code asserts it
rather than assuming it. And $(s,j)$ and $(-s,\,p-j)$ induce the same
hitting set. At $p = 191$ that takes 2674 constraints down to 1181.

## 5. Computer search

    ./cover --k 13 --p 191
    k=13 m=14 p=191 constraints=1181
    m factors: 2 7   search space = { some v_i = 0 } minus gcd-proper
    RESULT UNSAT (T2(13,191) HOLDS)
    nodes=102905279 bound_cuts=80243639 dead_cuts=8002240 seconds=240.73

Agreement table — brute force is an independent enumeration of all of
$\mathbb Z_m^k$ written from the paper, not from the search:

| $k$ | $m$ | $p$ | brute force | `cover` | `cover_bdd` |
|----|----|-----|-------------|---------|-------------|
| 4 | 5 | p-indep | 0 obstructions | UNSAT | — |
| 5 | 6 | p-indep | 64 | SAT | SAT |
| 5 | 6 | 31 | **0** | UNSAT | UNSAT |
| 7 | 8 | p-indep | 2596 | SAT | SAT |
| 7 | 8 | 59 | **0** | UNSAT | UNSAT |
| 8 | 9 | p-indep | — | SAT | SAT |
| 13 | 14 | p-indep | — | SAT | SAT |
| 13 | 14 | **191** | out of reach | **UNSAT** | state-explodes |

## 6. What is proved, what is not

Proved, and checkable in four minutes from a clean checkout:

> Every $(u_1,\dots,u_{13}) \in \mathbb Z^{13}_{>0}$ with
> $\gcd(u_1,\dots,u_{13}) = 1$ and $u_i \equiv i \pmod{191}$ has the
> lonely runner property.

Equivalently $(1,2,\dots,13) \notin J(13,191)$. Sungkawichai and
Trakulthongchai prove the corresponding statement only when $k+1$ and $p$
are both odd primes, so $k = 13$ falls outside it, and their Section 5.2
reports $(1,2,\dots,13)$ as the sole survivor of the $\times 2$ lifting
ladder — it is eliminated here with no $\times 7$ and no $\times 14$ lift.

Not proved, and worth being blunt about. This is not a bound on the
number of runners. The lonely runner conjecture for 14 runners is open,
and the reason it is open is untouched: their Section 7 names computing
$I(13,p,1)$ as the bottleneck, about $10^{17}$ tuples at $p=191$, and
nothing here reduces that. What has been removed is one named obstacle —
the tight tuple — at one prime.

Also not done. The forward-sweep second decision procedure agrees on
every small composite case but runs out of memory before $k=13$, so the
$p=191$ verdict rests on one exact search plus brute-force validation of
the reformulation and 23 million adversarial samples, rather than on two
exact searches. Subset dominance would fix it. And whether $T2(13,p)$
holds for *every* prime $p > 182$ — the statement that would actually
replace Proposition 4.1 for composite $k+1$ — is open; it fails at
$p = 17, 19$, so there is a threshold, and locating it is a sweep, not a
proof.

---

# Walkthrough II — where the modulus stops being enough

The first walkthrough ends with an admission: $T2(13,p)$ holds at $p = 191$ and
fails at $p = 17, 19$, so there is a threshold somewhere, and finding it "is a
sweep, not a proof". The sweep is the wrong instrument. Here is what replaced
it.

## 7. The witnesses were trying to tell us something

$p = 43$ would not resolve in forty minutes, in either direction. So stop
asking for a decision and ask only for a *witness* — restrict every coordinate
to a small alphabet and exhaust. The alphabet came from looking at what
$q1$ had already printed: at $p = 31$ the witness was
$(0,0,0,1,1,1,0,0,1,0,0,0,0)$, at $p = 37$ it used only $\{0,1,7\}$.

With $A = \{0,1,7\}$, $p = 43$ answers in milliseconds:
$$v = (0,0,0,0,0,0,0,0,0,0,0,1,1).$$
Two coordinates equal to $1$, everything else $0$. And the same shape comes
back at $47, 59, 61, 71, 73, 89$.

## 8. Why that shape works, exactly

Write $T$ for the two nonzero positions and $Z$ for the eleven zeros. Fix $j$.

A coordinate in $Z$ has value $0$, so it hits $(s,j)$ iff $B^{(j)}_i \in
\{0,13\}$ — a condition with **no $s$ in it**. Either it hits every $s$ at this
$j$, or none.

A coordinate in $T$ has value $1$, so it hits $(s,j)$ iff $s \equiv -B_i$ or
$-B_i - 1$: exactly two values of $s$.

So at a given $j$ there are only two outcomes. Either some zero coordinate
fires and all fourteen $s$ are covered at once; or no zero coordinate fires,
and the two coordinates of $T$ between them reach at most $4$ of the $13$
nonzero $s$ — and $4 < 13$, so $v$ is saved. The whole question collapses:

> $v = e_a + e_b$ is unsaved at $p$ $\iff$ every $j \in \mathbb{Z}_p$ has some
> $i \notin \{a,b\}$ with $\|i j/p\| < 1/14$.

Read the right-hand side out loud and it is a lonely-runner statement about
*eleven* speeds: delete two runners from the tight configuration, and ask
whether the survivors have a witness time **on the grid** $(1/p)\mathbb{Z}$.
They always have one on the circle — deleting two speeds makes $1/14$ slack, so
the good set $G(Z) = \{t : \|it\| \ge 1/14 \ \forall i \in Z\}$ contains
intervals, not just the six points $j/14$. The only question is whether the
grid is fine enough to land in one.

That is computable once and for all. $G(Z)$ is a union of closed intervals with
endpoints over $D = 14 \cdot \mathrm{lcm}(1,\dots,13) = 5045040$; for each of
the $78$ pairs, list them, and for each $p$ ask whether any interval contains a
multiple of $1/p$. No search over $v$, no search over $p$.

The answer: $T2(13,p)$ fails at $p = 43, 47, 59, 61, 71, 73, 89$ and at no
larger prime *from this family*, the largest failing integer being $116$. The
tightest pair is $\{6,10\}$, whose longest good interval is
$31680/5045040 = 1/159.25$; past $p = 159$ every pair has room.

The last known failure moves from $41$ to $89$. Two programs that share no code
agree on the list, including the composite cases $90, 95, 99, 105, 116$, and
$q1$'s own checker — written from the paper — calls the $p = 43$, $61$ and $89$
vectors genuine obstructions.

## 9. The correction this forces

It is tempting to now say "so the threshold is 89". It is not, and $k=5$ is the
proof. There, brute force over all $7776$ vectors decides every $p$ outright:
$T2(5,p)$ fails at $6..14, 19, 21, 22, 24, 26, 27, 39, 42, 57$. The pair family
accounts for $p \le 13$ and nothing else. Everything from $19$ to $57$ comes
from one richer vector, $v = (1,5,0,1,5) = (1,-1,0,1,-1)$ — the balanced lift
of $i \bmod 3$, and $3 = m/2$.

So the pair family is a lower bound on where failure stops, not the threshold.
(The obvious $m=14$ analogue, the balanced lift of $i \bmod 7$, is saved at
every prime from $17$ to $293$. The construction does not transfer; the caution
does.)

That same $k=5$ table kills a second habit. $19$ fails and $17$ holds. The
pass/fail set is **not an interval**, so "the first $p$ that holds" is not a
well-posed quantity, and a sweep column must not be read as a threshold.

## 10. Deciding every large $p$ with one search

Which leaves the other direction: not "which $p$ fails" but "is there a $q$
past which nothing can". For that, get rid of $p$.

Everything in the problem depends on $j$ only through the real number
$t = j/p$, via $B_i(t) = \lfloor 14\,\{i t\}\rfloor$. That function is
right-continuous and jumps only where $14 i t$ crosses an integer — on
$(1/(14i))\mathbb{Z}$. Take all of those together, $i = 1,\dots,13$: $812$
breakpoints, cutting the circle into $812$ half-open cells on which the entire
hitting structure is *constant*. Every real $t$ is in exactly one. No boundary
cases.

Now the only fact needed about the grid: **every half-open interval of length
$1/p$ contains a point of $(1/p)\mathbb{Z}$.** So fix $q$, and for each cell
start $c_r$ look at the window $[c_r, c_r + 1/q)$. If $p \ge q$, that window
contains a grid point, and that grid point lies in one of the cells the window
meets. An unsaved $v$ must hit at least one of them. Union those cells' hitting
sets and it is a set-cover constraint again — the same DFS, the same counting
bound, the same gcd branch as $q1$, with only the constraints rebuilt:

> no eligible $v$ covers all of it $\implies$ $T2(13,p)$ holds for **every**
> integer $p \ge q$.

One run, an infinite tail. And monotone in $q$, so the smallest $q$ that
returns UNSAT is the statement to report.

The first version of this used only cells *longer* than $1/q$, throwing away
every short cell. It works, but loosely: at $k=7$ it certifies $p \ge 121$
where the window version certifies $p \ge 84$. The union over a window is what
recovers the short cells, and it is kept side by side (`--strictcell`) so the
difference is visible.

Calibration, where brute force can check everything: $k=5$ certifies $p \ge 90$
against a true last failure of $57$; brute force over $\mathbb{Z}_6^5$ for all
$p \in [90, 399]$ finds no contradiction. So the certificate is sound and about
$1.6\times$ loose. At $k = 13$ the lemma of §8 forces any such $q$ to be at
least $117$.
