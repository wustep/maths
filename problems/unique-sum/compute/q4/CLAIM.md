# q4 claim ledger

Status: residue while the search runs. No new bound is asserted.

The inherited certificate `../q3/p59_upper.json` gives

$$
m(59)\le15.
$$

Its 225 ordered pairs were checked again with `../q3/verify_upper.py`.
All 15 saved witnesses through 53 also passed the existing direct verifier.
The published exact prefix is OEIS A398173; q4 has not extended it.

Target: decide existence at size at most 14, then independently replay every
lower exclusion needed for an exact value. `UNKNOWN` and bounded heuristic
searches do not imply any lower bound.
