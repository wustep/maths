# Brocard–Ramanujan modular hunt

- Slug: `brocard`
- Solver: Codex `gpt-5.6-sol` Max (2026-08-16 overnight). Grok watched only.
- Status: open
- Area: Diophantine equations
- Sources: DeepMind formal-conjectures #1417; Berndt–Galway 2000; OEIS A085692; Erdős #398
- Started: 2026-08-16
- Tonight: short-lean, cost S — new modular / covering obstructions + one Lean lemma

## In general

Brocard (1876, 1885) and Ramanujan (1913) asked for the positive
integers \(n\) such that \(n!+1\) is a square. The only known
solutions are
\[
4!+1=5^2,\qquad 5!+1=11^2,\qquad 7!+1=71^2.
\]
Erdős conjectured there are no others. The equation is
formal-conjectures #1417 / Erdős #398; the Lean *statement* already
lives in `FormalConjectures/ErdosProblems/398.lean`. Overholt showed
that a weak form of \(abc\) implies only finitely many solutions.
That is not a proof, and it is not tonight's job.

The computational handle is modular. Berndt–Galway (2000) used a
quadratic-residue sieve: a candidate \(n\) dies if some prime \(p>n\)
has \(\bigl(\frac{n!+1}{p}\bigr)=-1\). They checked \(n\le 10^9\).
Later searches advertise much larger ranges (Wikipedia cites
\(10^{15}\)); those are not the overnight target. Textbook local
obstructions also include: for a prime \(p\) with \(n/2<p\le n\),
one has \(n!\equiv 0\pmod{p}\) so \(m^2\equiv 1\pmod{p}\), hence
\(m\equiv\pm 1\pmod{p}\). Covering systems that force a quadratic
nonresidue for every large residue class of \(n\) would eliminate
infinite families.

Tonight: mine modular / covering-system obstructions *beyond the
textbook ones*; re-run a published computational range (the
Berndt–Galway method on a slice you can actually finish, with the
method written down); Lean-formalize **one** sharp modular lemma.
Do **not** claim the conjecture. A new Brown number is not expected
and is not required.

## Precise statement

A *Brown pair* is a pair of integers \((n,m)\) with \(n\ge 1\) and
\(n!+1=m^2\). The known pairs are \((4,5)\), \((5,11)\), \((7,71)\).

**Tonight's finite subquestion.**

1. *Modular hunt.* Search for congruential obstructions to
   \(n!+1=m^2\) that are not the three textbook facts
   (\(n\ge 4\Rightarrow m\) odd; \(p\in(n/2,n]\Rightarrow m\equiv\pm 1\pmod{p}\);
   the Berndt–Galway QR sieve for a single prime \(p>n\)).
   Covering systems, simultaneous QR conditions, or a new modulus
   family that kills an infinite arithmetic progression of \(n\)
   all count. Write each obstruction as a lemma with a human-sized
   proof sketch.
2. *Re-run a published range.* Re-implement the Berndt–Galway
   quadratic-residue sieve and run it at least through \(n\le 10^4\)
   exactly, matching the three known solutions and no others.
   If time remains, push the same sieve as far as it goes in this
   quest and record the bound. Do not quote \(10^9\) or \(10^{15}\)
   as *your* bound unless you actually ran it.
3. *One Lean lemma.* Formalize **one** sharp modular statement
   already believed true, with the informal skeleton written first.
   Suggested target (change it only if you find a sharper one):
   ```
   If n! + 1 = m^2, p prime, and n/2 < p ≤ n, then
   m ≡ 1 [MOD p] ∨ m ≡ -1 [MOD p].
   ```
   Build it under `lean/` with Lean 4.32 + mathlib. No `sorry` in
   the main lemma.

## What a solution looks like

- A note in `ATTACK.md` listing every *new* obstruction, with a
  proof sketch and a computational check on a prefix of \(n\).
- `compute/` scripts for the QR sieve, a table of survivors on the
  re-run range, and a figure if the residue is a covering diagram
  or a survivor plot.
- One Lean file under `lean/` whose main theorem is the chosen
  modular lemma and which builds (`lake` from `/maths`, add a
  minimal lakefile stanza for this folder if needed).
- **Not a solution:** "we restated the conjecture." **Not a
  solution:** a new Brown number you did not independently re-run.
  Do not claim there are no other solutions.

## Related

- [google-deepmind/formal-conjectures #1417](https://github.com/google-deepmind/formal-conjectures/issues/1417)
- [FormalConjectures/ErdosProblems/398.lean](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/398.lean)
- [Erdős Problem #398](https://www.erdosproblems.com/398)
- [Berndt–Galway, *On the Brocard–Ramanujan Diophantine equation*, Ramanujan J. 4 (2000)](https://doi.org/10.1023/A:1009873805276) ([author PDF](https://faculty.math.illinois.edu/~berndt/articles/galway.pdf))
- [OEIS A085692](https://oeis.org/A085692) (the squares \(25,121,5041\)); [A146968](https://oeis.org/A146968) (the \(n\)'s \(4,5,7\))
- [Wikipedia, Brocard's problem](https://en.wikipedia.org/wiki/Brocard%27s_problem)

## Quests so far


## Figures

None yet. A covering diagram or a survivor plot belongs here if the
hunt produces one.
