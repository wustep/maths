# Walkthrough — The modulus had to move with the factorial

- Problem: \`problems/brocard-ramanujan-factorial-square\`
- Quest: \`q2-second-pass\`
- Model: gpt-5.6-sol max
- Date: 2026-08-16 (America/Los_Angeles)
- Argument status: lean-certified structural lemma
- Problem status: open

## 0. What was actually missing

The missing object was not a better residue class. q1 had already exposed why
that setting is finite: a fixed modulus \(q\) sees \(n!+1\equiv1\pmod q\) as
soon as \(n\ge q\). What survives as \(n\) grows is the allocation of the
*entire prime-power blocks* of the factorial between the two neighbors of the
square root. That allocation produces moduli \(p^{\nu_p(n!)}\) which move with
\(n\), but it also reveals exactly what remains uncontrolled.

## 1. False starts (named obstacles)

- **Extending q1 with more primes.** It would enlarge a certified finite
  interval and nothing else. Every fixed row eventually becomes the square
  residue 1. The residue worth keeping was the need for a modulus depending on
  \(n\).
- **Using \((m-1)(m+1)=n!\) before removing the common two.** The factors have
  gcd 2, so saying “prime factors cannot split” is literally false for the
  2-part and awkward for every later statement. The useful normalization was
  to exploit parity first and divide both neighbors by two.
- **Treating the normalized split as an automatic algorithmic win.** Once the
  factors are coprime, each prime power becomes a binary choice. There are
  fewer choices than ordinary divisors, but still \(2^{\pi(n)-1}\) up to
  swapping. The factorization changes the language of the obstruction; by
  itself it does not make the conjecture finite.

## 2. The useful failure

We made the binary choices exact on a range small enough to inspect. For every
\(4\le n\le100\), we formed the complete prime-power blocks of \(n!/4\) and
looked for the subset product closest to its square root. The consecutive
splits were exactly

\[
6=2\cdot3,\qquad 30=5\cdot6,\qquad 1260=35\cdot36,
\]

which recover \(n=4,5,7\). But at \(n=100\), 25 blocks already leave
\(2^{24}=16{,}777{,}216\) complementary assignments. The computation did not
suggest an induction; it diagnosed the missing theorem as control of
prime-power subset products near \(\sqrt{n!/4}\).

## 3. The click

For \(n\ge2\), the factorial is even, so a hypothetical square root is odd.
Writing \(m=2a+1\) turns the two even neighbors into the consecutive integers
\(a\) and \(a+1\):

\[
n!=m^2-1=4a(a+1),\qquad \gcd(a,a+1)=1.
\]

Now an odd prime power in \(n!\) cannot partly enter each neighbor. It has to
choose a side in full. This is simultaneously the variable-modulus lemma and
the exact unitary-divisor reformulation.

## 4. The argument, in the order it became inevitable

### Parity exposes the right factors

Assume \(n\ge2\) and \(n!+1=m^2\). Since \(2\mid n!\), the left side is odd;
therefore \(m\) is odd and \(m=2a+1\) for some \(a\). Expanding the square and
cancelling 1 gives

\[
n!=4a(a+1).
\]

The identity \(\gcd(a,a+1)=1\) is what the unhalved factorization was hiding.

### A full prime power chooses one neighbor

Let \(p\ne2\) be prime and suppose \(p^k\mid n!\). Because \(p\nmid4\), the
factorization implies \(p^k\mid a(a+1)\). If \(p\mid a\), coprimality gives
\(p\nmid a+1\), so the whole \(p^k\) divides \(a\); the other case is symmetric.
Multiplying back by two yields

\[
p^k\mid m-1\quad\text{or}\quad p^k\mid m+1.
\]

We may choose \(k=\nu_p(n!)\). Thus every odd \(p\le n\) supplies the growing
modulus

\[
m\equiv\pm1\pmod {p^{\nu_p(n!)}}.
\]

This keeps more information than the familiar condition modulo \(p\) for a
prime in \((n/2,n]\). It is sharp as an exponent: at the known solution
\((7,71)\), the full 3-part is \(3^2\), and \(3^2\mid72\) while
\(3^3\nmid72\).

### Combining the moduli is a unitary-divisor problem

Put \(N=n!/4\). Since \(a\) and \(a+1\) are coprime, every block
\(p^{\nu_p(N)}\) lies wholly in one factor. Equivalently, \(a\) is a unitary
divisor of \(N\), and a Brown pair occurs exactly when a unitary divisor and its
complement differ by one.

For the finite experiment, we split the blocks into two halves, enumerated all
subset products in each half, and used binary search to find the largest product
not exceeding \(\sqrt N\). This product minimizes \(N/a-a\) exactly. The
algorithm uses the structure, but the number of underlying sign vectors remains
exponential.

### What Lean certifies

[FactorialPrimePower.lean](lean/FactorialPrimePower.lean) follows the same
argument. Its first exported theorem constructs \(a\), proves the exact
factorization, and records coprimality. Its main theorem,
\`odd_prime_power_dvd_neighbor\`, cancels the factor 4, applies prime-power
divisibility to the coprime neighbors, and returns the divisibility of \(m-1\)
or \(m+1\). It contains no bounded case split and no \`sorry\`.

## 5. Figures, numeric checks, computer residue

![Exact unitary-divisor gaps and sign-vector growth](figures/q2-unitary-factorization.png)

The upper panel plots the exact smallest gap between complementary unitary
divisors of \(n!/4\). The red stars are the three gap-one cases on
\(4\le n\le100\); the upward trend is data, not an extrapolated theorem. The
lower panel records the binary assignments remaining after complementary splits
are identified.

The primary computation is
[unitary_factorization.py](compute/unitary_factorization.py), with exact output
in [q2-results.json](compute/q2-results.json) and a compact run log in
[q2-run.txt](compute/q2-run.txt). The separately written
[verify_q2.py](compute/verify_q2.py) checked every emitted factorization,
brute-forced every subset through \(n=50\), reran direct integer-square tests
through \(n=100\), and checked each recorded prime-power sign. Its result is
[q2-verification.txt](compute/q2-verification.txt).

## 6. Proven vs still open

- **Lean-certified.** A Brown equation with \(n\ge2\) has the consecutive
  coprime factorization above, and every odd prime power dividing \(n!\) divides
  one neighboring factor in full. The required local \`lake build\` succeeds.
- **Exactly computed.** The unitary-divisor and direct-square tests agree on
  \(4\le n\le100\), with only the already known \(n=4,5,7\). The minimum-gap
  calculation was independently brute-checked only through \(n=50\); every
  reported factor certificate was checked through 100.
- **Not claimed.** The \(100\)-range is not a new search record, the
  factorization is not claimed as a literature novelty, and the plotted growth
  is not a lower bound for all \(n\). q1's separate modular sieve already went
  much farther finitely.
- **Still open.** Nothing here excludes all sign assignments for large \(n\),
  kills an infinite progression, or proves that \(4,5,7\) are the only Brown
  indices. The Brocard–Ramanujan conjecture remains open.

## 7. Digestion notes

Run the structural experiment and its independent verifier from the problem
directory:

\`\`\`text
python3 compute/unitary_factorization.py --max-n 100
python3 compute/verify_q2.py
python3 compute/plot_unitary_factorization.py
\`\`\`

Build both the untouched q1 certificate and the q2 theorem with:

\`\`\`text
cd lean
lake build
\`\`\`

The next genuinely different move would be an analytic or combinatorial theorem
forcing every prime-power partition of \(n!/4\) away from two consecutive
factors. Raising the finite enumeration bound or adding fixed primes would
repeat an obstruction whose limitation is now explicit.
