# Attack log

## 2026-08-17 — pick

See `notes/picks/2026-08-17-ideation-historical.md`. Landau 4 chosen over the rest of Hilbert/Smale/Landau because it is still open and has a checkable finite list plus Iwaniec's P2 theorem as a nearby object.

## 2026-08-17 — first compute

Enumerate even n (odd n>1 makes n^2+1 even and >2). Trial-split n^2+1; record primes and P2s. Write `compute/` tables and a verifier that ignores the tables and re-derives them.

## 2026-08-17 — certified prefix

`compute/sieve_n2p1.py` then `compute/verify.py`:
n_max=200000, exactly 12391 primes n^2+1 (including 2=1^2+1).
Verifier OK (extra=0 missing=0). First 8 values 2,5,17,37,101,197,257,401
match OEIS A002496. Not a proof of infinitude.

## 2026-08-17 — published record (do not claim a new prime)

Fetched the lists we will cite, before extending the sieve.

- Wolf, arXiv:0803.1456 (2008–2010): complete hunt for primes \(q=m^2+1<10^{20}\). Table I: \(\pi_q(10^{12})=54110\), \(\pi_q(10^{14})=456362\). Constant
  \[
  C_q=\prod_{p\ge 3}\Bigl(1-\frac{(-1)^{(p-1)/2}}{p-1}\Bigr)=1.372813462818246\ldots
  \]
  (OEIS A199401; Hardy–Littlewood conjecture E / Landau–Shanks). The better count is
  \[
  \pi_q(x)\sim\frac{C_q}{2}\int_2^x\frac{du}{\sqrt{u}\,\log u}=C_q\bigl(\mathrm{li}(\sqrt{x})-\mathrm{li}(\sqrt{2})\bigr).
  \]
  Equivalently Bateman–Horn for \(f(n)=n^2+1\): \(C_{\mathrm{BH}}=C_q\) and
  \(\#\{n\le N:n^2+1\text{ prime}\}\sim C_q\int_2^N dt/\log(t^2+1)\).
- OEIS A083844 = Wolf Table I through \(10^{16}\), then Gerbicz / Wolf–Gerbicz / Grantham:
  complete counts of such primes \(<10^n\) through \(n=28\) (Grantham–Graves arXiv:2502.03513 compute all such primes up to \(6.25\times10^{28}\)).
- OEIS A005574 / A002496 b-files: first 10000 values of \(n\) and of \(n^2+1\). The 10000th \(n\) is 158704, already inside the first prefix.
- Iwaniec, *Invent. Math.* 47 (1978): infinitely many \(n\) with \(\Omega(n^2+1)\le 2\) (multiplicity). Lemke Oliver: “at most two prime factors counted with multiplicity.”

A new prime not on those lists would require \(n\gtrsim 2.5\times10^{14}\). We will not beat that tonight. The dent is a replayable certified prefix, a complete Iwaniec-P2 table on the same range, and a Bateman–Horn / Wolf comparison. Search residue is not a lower bound.

## 2026-08-17 — bugs in the first sieve

1. `sqrt_minus_one` used \(a^{(q+1)/4}\) with \(a=-1\). That formula is for residues modulo a prime \(\equiv 3\pmod 4\); every \(q\equiv 1\pmod 4\) fell through to a linear search. Fine at the 200000 cap, fatal if we sieve with large \(q\).
2. `trial_omega` counted distinct prime factors \(\omega\), not \(\Omega\). Iwaniec's \(P_2\) is \(\Omega\le 2\). Counterexample: \(18^2+1=325=5^2\cdot 13\) has \(\omega=2\) and \(\Omega=3\), so it is not an Iwaniec \(P_2\). The stored count 34507 is an \(\omega\le 2\) count, and the \(P_2\) list was never written to disk.
3. The first sieve skipped \(n=1\) until the verifier caught it. Keep that discipline.

Next: residue factor-sieve with a correct \(\sqrt{-1}\bmod q\), classify by \(\Omega\), store factorizations, compare to Wolf / A083844 / A005574 and to \(C_q\int dt/\log(t^2+1)\).
