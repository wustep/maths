# Completing a named midpoint cover

The target is a set of size at most 14 modulo 59 in which every represented
sum has at least two unordered representations. Both ordered counts 1 and 2
are forbidden. Supporting the diagonal sums alone is a necessary condition,
not the full predicate.

Every admissible set has an affine image containing {-1,0,1}: a second
representation of a diagonal gives a nontrivial three-term progression.
The first entries of 0,1,-1,2,-2,... form an arithmetic progression. Starting
with five entries therefore covers all sets containing an AP5, up to affine
equivalence. Starting with four covers all sets containing an AP4.

For a selected center c, list all distinct endpoint pairs u,v with
u+v=2c modulo p. At least one such pair must be selected. Fixing that pair
gives a named root for a completion search. `midpoint_cases.py` records every
pair, removes roots already containing the forbidden progression, and
identifies affine-equivalent roots. The representative still has its
original coordinates and pair name. There is no lexicographic restriction
on its completions.

At p=59 the AP3 root and center 1 give 29 pairs. If AP4 is forbidden,
three roots are impossible and the remaining 26 fall into 25 affine
classes. For the AP4 root, center -1 and forbidden AP5, two of the 29
roots are impossible and the other 27 are distinct classes. These are
conditional partitions: forbidding an AP requires a separate exclusion
of the family that contains it before one can infer an unrestricted result.

The C search checks ordered multiplicities using the size of the
intersection of S with its reflection s-S. When that count is 1 or 2,
every admissible extension must include another unordered pair with sum s.
The search branches on every possible missing endpoint set. Those endpoint
sets are disjoint for a fixed sum, since its unordered pairs partition the
residues. Each branch strictly enlarges S and respects the cardinality cap.

With at most six places left, a second recursion asks whether a union of
repair choices can cover all currently unique sums within the budget.
Failure excludes the state. Success does not establish admissibility:
the main search still checks sums involving newly added vertices.
The search also uses the necessary support bound

$$
|S+S|\le \left\lfloor\frac{k(k+1)}4\right\rfloor,
$$

where k is the final cardinality cap. An admissible extension has at most
k(k+1)/2 unordered pairs, with at least two per represented sum, and its
sumset contains S+S.

A fixed 128 MiB cache stores full masks after affine normalization using
internal three-term progressions. Equality of a cache key identifies
affine-equivalent completion problems; a hash collision only evicts a key.
All descendants are larger than their ancestors, so an earlier equal-size
state in depth-first search has finished before it can be encountered again.
Node-limit termination aborts the entire run, and the cache is discarded.
No cache is shared after an interrupted case. The per-process address-space
limit is 1536 MiB, and only one heavy job is run at a time.

`audit_cover.py` compares decisions with complete subset enumeration through
13, including named roots and forbidden progressions. `audit_partition.py`
checks the endpoint list, every affine identification, and coverage on small
sets without using the C search. These controls test implementation errors;
they do not establish a bound at 59. `run_cover.py` saves UNKNOWN on a wall
timeout, and `midpoint_cases.py` saves a manifest after every completed case.
A case without a result remains unsearched. No absent or interrupted case
counts as an exclusion.

For the current certified predicates, run:

```bash
bash problems/unique-sum/compute/q4/run_all.sh
```

This replays witnesses, controls, and the AP5 exclusion. It does not turn
the incomplete unrestricted search into a lower bound. There is no retained
DRAT proof object; the lower-search evidence consists of source and reruns.
The exact assertion and its falsifiers are in [`CLAIM.md`](CLAIM.md).
