# Landau 3 / Legendre, second computation

## Outcome

Both strict Oppermann halves contain a certified prime for every integer

$$
70{,}500{,}000{,}000{,}001\leq n\leq70{,}500{,}000{,}010{,}000.
$$

Together with the published Sorenson--Webster computation through
$70{,}500{,}000{,}000{,}000$, this moves the verified endpoint to
$70{,}500{,}000{,}010{,}000$. The extension is unconditional. It does not
prove Oppermann's or Legendre's conjecture beyond this finite range.

## Fast verification

From any directory, run:

```bash
problems/landau-legendre/compute/q2/verify.sh
```

The command compiles a dependency-free Rust verifier and checks the committed
certificate. It takes about 15 seconds on the campaign machine.

For full regeneration, including the unchanged first-computation replay, run:

```bash
problems/landau-legendre/compute/q2/run_all.sh
```

Full regeneration also requires GNU `factor`. It took about six minutes on the
campaign machine and used one factorization process at a time.

## What is certified

`certs/oppermann_extension.tsv` has 10,000 witness rows and 107,937 unique
prime-proof nodes. For each row, the verifier checks

$$
n^2<p_0<n(n+1)<p_1<(n+1)^2.
$$

Every prime is proved by a recursive Lucas certificate. A node records the
complete factorization of $p-1$, recursively proved prime factors, and a
single Lucas witness. The Rust verifier checks the factorization product,
Fermat congruence, and every Lucas gcd condition using overflow-safe modular
arithmetic. It also rejects missing or unordered values of $n$, unused proof
nodes, and any interval endpoint failure.

The Python generator uses probable-prime filtering only to choose candidates.
Those filters are not part of the proof. The Rust verifier accepts a witness
only through the recursive Lucas argument.
