# Walkthrough — Move the prime just beyond the factorial

- Problem: `problems/brocard`
- Run: `q3-prime-offsets`
- Model: GPT-5.6 Sol
- Date: 2026-08-23 (America/Los_Angeles)
- Argument status: exact certificate and one Lean theorem
- Problem status: open

## 0. What was actually missing

A fixed prime cannot exclude an infinite set of large factorial indices.  Once
$n\ge p$, one has $n!+1\equiv1\pmod p$, which is already a square residue.
The missing degree of freedom was a prime modulus that moves with $n$ while
leaving only a constant-size tail between $n$ and the Wilson factorial
$(p-1)!$.

## 1. Named false starts

- **More fixed primes.**  They can extend the finite q1 interval but every row
  eventually becomes the residue 1.
- **The central prime $p=2n+1$.**  Wilson gives
  $(n!)^2\equiv(-1)^{n+1}\pmod p$, but the resulting quartic in the putative
  square root has both passing and failing primes in the small congruence
  classes checked.  No progression certificate emerged.
- **Prime-power sign vectors.**  The q2 factorization supplies growing moduli,
  but it also leaves an exponential choice of which neighbor receives each
  prime-power block.

## 2. The useful failure

Writing the modulus as a fixed number was the common defect.  Writing it as
$p=n+c$ makes it grow, and Wilson's theorem evaluates the missing tail:

$$
n!\equiv\frac{(-1)^c}{(c-1)!}\pmod p.
$$

This is useful only when the resulting constant is provably a nonresidue on a
whole prime congruence class.

## 3. The click

The smallest offset is already enough.  If $p=n+2$, then Wilson gives
$n!\equiv1\pmod p$, so a Brown equation would force

$$
m^2\equiv2\pmod p.
$$

The supplementary law says that 2 is a quadratic nonresidue when
$p\equiv3$ or $5\pmod8$.  Those two prime classes are infinite, and shifting
them by 2 produces two infinite families of excluded indices.  Offset 3 gives
two more families with the same character.

## 4. The argument

For $p=n+2$, Wilson's congruence is

$$
-1\equiv(p-1)!=(p-2)!(p-1)\equiv-n!\pmod p.
$$

Thus $n!+1\equiv2\pmod p$.  This cannot equal a square when
$p\equiv3,5\pmod8$.

For $p=n+3>3$, the two omitted factors give

$$
-1\equiv(p-1)!=n!(p-2)(p-1)\equiv2n!\pmod p.
$$

Hence $n!+1\equiv1/2\pmod p$.  If $m^2\equiv1/2$, then
$(2m)^2\equiv2$, again impossible in the same two prime classes.

Dirichlet's theorem supplies infinitely many primes in each of the reduced
classes 3 and 5 modulo 8.  The result therefore excludes the four infinite
prime-offset families

$$
n=p-2\quad\text{and}\quad n=p-3,qquad p\equiv3,5\pmod8.
$$

The condition that the shifted number is prime remains essential.

## 5. Computer search and formal check

The certificate file `compute/q3/offset-certificate.json` records the offset,
prime class, index class, rational target, and sample count for every row.
The Python generator recomputes factorials modulo each prime through 10,000.
The independent C verifier uses separate primality, modular exponentiation,
and factorial loops.  Their complete reports agree: 1,249 row instances pass.

`lean/WilsonOffset.lean` formalizes the offset-2 proof.  It derives the
factorial congruence from mathlib's Wilson theorem and closes the nonresidue
step with mathlib's characterization of when 2 is a square modulo a prime.
The theorem has no bounded enumeration and no `sorry`.

Replay all three checks with:

```text
problems/brocard/compute/q3/run_all.sh
```

## 6. Proved versus still open

- **Proved.**  No Brown index belongs to any of the four stated prime-offset
  families.  Each family is infinite.
- **Exactly replayed.**  Independent Python and C implementations agree for
  every applicable prime through 10,000; the offset-2 theorem builds in Lean
  4.32.0.
- **Not claimed.**  The result does not exclude an entire residue class of
  integers modulo 8, does not improve the published finite search range, and
  is not claimed as a literature novelty.
- **Still open.**  Indices for which the useful offsets are composite remain,
  and nothing here proves that $4,5,7$ are the only solutions.
