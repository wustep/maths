# Smale 4 — the Shub–Smale τ-conjecture

- Slug: `smale-tau`
- Status: open — campaign in progress (see ATTACK.md); status line to be
  updated when the 13-step factorial search finishes.
- Area: algebraic complexity; straight-line programs; Diophantine
  geometry; BSS model
- Started: 2026-09-02

## In general

A *program* for a polynomial \(f\in\mathbb Z[t]\) is a sequence
\((1,t,u_1,\dots,u_k)\) with \(u_k=f\), where every \(u_l\) is
\(u_i\circ u_j\) for earlier entries and \(\circ\in\{+,-,\times\}\).
No constants other than \(1\) are free and there is no division. The
cost \(\tau(f)\) is the least \(k\). Smale's fourth problem, in his
1998 list, asks whether the number \(Z(f)\) of distinct integer zeros
of \(f\) is polynomially bounded in \(\tau(f)\):

$$
Z(f)\le a\,\tau(f)^c\qquad\text{for all } f\in\mathbb Z[t],
$$

with universal constants \(a,c\). Shub and Smale proved that a positive
answer makes the Hilbert Nullstellensatz intractable over
\(\mathbb C\), so \(\mathrm P_{\mathbb C}\ne\mathrm{NP}_{\mathbb C}\).
Bürgisser proved that it also forces the permanent out of
polynomial-size constant-free circuits. Smale's text records that the
exponent must satisfy \(c\ge 2\) (Strassen's fast evaluation), that
the trivial bound is \(Z(f)\le\deg f\le 2^{\tau(f)}\), and that the
real analogue is false because Chebyshev polynomials have exponentially
many real zeros. The conjecture is open.

The same essay states the integer form of the question inside Problem
4. For an integer \(m\), \(\tau(m)\) is the least length of a program
\((1,m_1,\dots,m_l)\) with \(m_l=m\) built by \(+,-,\times\) from
\(1\). Shub and Smale ask whether

$$
\tau(k!)\le(\log k)^c\qquad\text{for all } k,
$$

and expect the answer to be no. Their Main Theorem says that if every
sequence of nonzero multiples of \(k!\) is hard in this sense then
\(\mathrm P_{\mathbb C}\ne\mathrm{NP}_{\mathbb C}\). No nontrivial
lower bound on \(\tau(k!)\) is known; the general bounds are
\(\log_2\log_2 m+1\le\tau(m)\le 2\log_2 m\).

## Published finite record

The integer cost function is tabulated. OEIS A173419 lists
\(\tau(n)\) for \(n\le 1800\), and an August 2026 comment there
extends the computation below 5000. The factorial sequence
\(\tau(n!)\) is OEIS A217032, known for \(n\le 19\): the 2013 Al
Zimmermann contest produced short programs and an exhaustive 12-step
search (Mertensotto, Rokicki) showed that 18! and 19! need 13 steps.
Markström (arXiv:1306.3091, INTEGERS 14, 2014) reports the same exact
values for \(n\le 19\) and gives \(\tau(20!)\in\{13,14\}\). The
contest's best programs have

| \(n\) | 13–14 | 15–17 | 18–19 | 20–22 | 23, 24, 26 | 25, 27, 28 | 29, 30, 34 | 31–33, 36 | 35 | 37 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| steps | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |

so for \(20\le n\le 22\) the published state is \(13\le\tau(n!)\le 14\).
Markström also tabulates primorials: \(\tau(29\#)\le 13\) and
\(\tau(31\#)\le 15\), both with lower bound 12.

On the polynomial side no published table of the largest number of
integer zeros attainable with \(\tau(f)\le k\) was found.

## Precise finite question attacked here

Decide \(\tau(20!)\), \(\tau(21!)\) and \(\tau(22!)\) by a complete,
exact-arithmetic search of all straight-line programs of length 13,
replaying the 12-step record on the way. Decide \(\tau(29\#)\) and
\(\tau(31\#)\) in the same runs. Replay OEIS A173419 and Markström's
reached-set counts as controls.

## What would count as a new bound

A complete exhaustive search with exact integer arithmetic that settles
a new term of A217032. Since 14-step programs for 20!, 21! and 22! are
published, "no 13-step program" gives the equalities

$$
\tau(20!)=\tau(21!)=\tau(22!)=14 .
$$

A shorter program than the contest or Markström record for any
factorial or primorial, verified by the Python replay, is also a new
bound. A search that skips large intermediate values, works modulo a
word size, or stops early is residue and changes no bound.

## Sources

- [Smale, *Mathematical problems for the next century* (1998), Problem 4](http://smaleinstitute.com/Mathematical_problems_for_the_next_century.pdf)
- [Shub–Smale, *On the intractability of Hilbert's Nullstellensatz and an algebraic version of "NP≠P?"*, Duke Math. J. 81 (1995)](http://web.archive.org/web/20220307211001/http://www.cityu.edu.hk/ma/doc/people/smales/pap97.pdf)
- [Bürgisser, *On defining integers in the counting hierarchy and proving lower bounds in algebraic complexity*, ECCC TR06-113 (2006); journal version Comput. Complexity 18 (2009)](https://eccc.weizmann.ac.il/report/2006/113/)
- [Koiran, *Valiant's model and the cost of computing integers*, Comput. Complexity 13 (2004)](https://perso.ens-lyon.fr/pascal.koiran/Publis/tau.springer.pdf)
- [de Melo–Svaiter, *The cost of computing integers*, Proc. AMS 124 (1996)](https://www.ams.org/journals/proc/1996-124-05/S0002-9939-96-03173-5/S0002-9939-96-03173-5.pdf)
- [Moreira, *On asymptotic estimates for arithmetic cost functions*, Proc. AMS 125 (1997)](https://www.ams.org/journals/proc/1997-125-02/S0002-9939-97-03583-1/S0002-9939-97-03583-1.pdf)
- [Rojas, *A direct ultrametric approach to additive complexity and the Shub–Smale tau conjecture*, arXiv:math/0304100](https://arxiv.org/abs/math/0304100)
- [Markström, *The straight line complexity of small factorials and primorials*, arXiv:1306.3091v4, INTEGERS 14 (2014)](https://arxiv.org/abs/1306.3091)
- [OEIS A173419](https://oeis.org/A173419), [OEIS A217032](https://oeis.org/A217032), [OEIS A217031](https://oeis.org/A217031), [OEIS A216999](https://oeis.org/A216999)
- [Al Zimmermann's Programming Contests, *Factorials* (2013)](http://www.azspcs.com/Contest/Factorials)
