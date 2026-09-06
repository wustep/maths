# compute — smale-tau

Verifier plus certificate. Every claimed number needs an independent
check that runs from the files in this folder. SAT UNKNOWN is not a
bound; search residue is not a lower bound.

- `q1/` — exhaustive search over integer straight-line programs:
  replay of OEIS A173419 and A217032, Markström's reached-set counts,
  and the 13-step decision for 20!, 21!, 22!, 29# and 31#.
  Entry point: `q1/run_all.sh`.
