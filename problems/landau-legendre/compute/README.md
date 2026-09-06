# Computation: Landau 3 / Legendre

The current conditional exponent certificate lives in `q3/`. Assuming RH,
it verifies primes between consecutive $(2+\delta)$-powers for every real
$x\geq1$ when

$$
\delta\geq0.22524401991935.
$$

It retains the quadratic Taylor term in Chamberland--Straub inequality (6),
which certifies a value where their simpler condition (5) fails. Replay it
with:

```bash
problems/landau-legendre/compute/q3/run_all.sh
```

The first campaign lives in `q1/`. It has three independent targets:

1. certify an RH-conditional exponent refinement by exact rational arithmetic;
2. audit the scope of the public Sorenson--Webster OLC logs; and
3. independently replay both Oppermann halves for a finite slice immediately
   below square-height $2^{64}$, including a near-miss table.

Run all committed, network-free checks from any working directory with:

```bash
problems/landau-legendre/compute/q1/run_all.sh
```

The OLC source-data reparse is optional because it needs a local clone pinned
to the commit named in the certificate.
