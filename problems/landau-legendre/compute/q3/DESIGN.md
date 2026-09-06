# q3 design

## Claim boundary

The computation certifies one conditional exponent improvement. It reuses the
q1 exact certificate as the previous bound and does not rerun or change q1's
finite Oppermann certificates.

The only external inputs are the RH short-interval theorem quoted by
Chamberland--Straub and the Sorenson--Webster endpoint
$N=70{,}500{,}000{,}000{,}000$. The new arithmetic is exact and
network-free.

## Independent paths

- `make_certificate.py` constructs rational logarithm enclosures by a
  power-of-two reduction and a bounded atanh series.
- `verify_certificate.py` reconstructs every field, canonicalizes every
  rational, and checks all signs without trusting decimal fields.
- `verify_float.c` separately evaluates the splice with `long double` and
  checks wide diagnostic margins. The rational Python verification is
  authoritative.
- `run_all.sh` first invokes the q1 exact verifier on q1's committed
  `rh_delta.json`, then regenerates, byte-compares, and checks the q3
  certificate.

## Invariants

Let $d=0.22524401991935$, $\alpha=2+d$,
$X=N^{2/\alpha}$, and $A=X^{d/2}=N^{d/\alpha}$. The certificate proves

$$
2\cdot10^{12}<X<2.8\cdot10^{12},\qquad 25<A<26.
$$

It verifies that the logarithmic margin for Chamberland--Straub condition
(5) is negative. It then retains the quadratic Taylor term from their
inequality (6), bounds its relative contribution from below, and proves the
resulting logarithmic overlap margin positive.

Finally, an exact positive lower bound for the derivative shows that the
strengthened sufficient inequality continues to hold for every $x\geq X$.
The finite proposition covers $x<X$.
