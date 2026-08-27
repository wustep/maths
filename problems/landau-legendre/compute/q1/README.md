# Landau 3 / Legendre, first computation

## Outcome

There are three deliberately separate results.

1. **Conditional improvement.** Assume RH. For every real $x\geq1$ and every
   $\delta\geq901/4000=0.22525$, the interval
   $[x^{2+\delta},(x+1)^{2+\delta}]$ contains a prime. This tightens the
   printed $0.2253$ at the end of Chamberland--Straub, Section 3, by
   $1/20000$. It does not prove Legendre's conjecture.
2. **Incomplete public-data reconstruction.** The pinned public OLC worker logs contain five
   coverage components and four holes. Their maximum endpoint is
   $31{,}894{,}400{,}000{,}352$, below the published
   $70{,}500{,}000{,}000{,}000$. This is a statement about checked-in logs,
   not a challenge to the peer-reviewed computation.
3. **Independent finite replay.** Both Oppermann halves are certified for
   every $n$ from $2^{32}-100000$ through $2^{32}-1$. The CSV has 100,000
   rows and 200,000 least-prime witnesses, ending immediately below
   square-height $2^{64}$. The largest normalized least-prime offsets in this
   slice are $489/4294952072$ on the left and
   $479/4294923874$ on the right.

## Replay

From any directory:

```bash
problems/landau-legendre/compute/q1/run_all.sh
```

Dependencies are Python 3, Rust, and a standard C compiler. The command uses
no network and writes only to a temporary directory. It takes about 30 seconds
on the campaign machine.

To authenticate the OLC projection against a caller-supplied clone at the
pinned commit:

```bash
problems/landau-legendre/compute/q1/replay_olc.sh /path/to/olc
```

## Why the conditional exponent follows

Set

$$
N=70{,}500{,}000{,}000{,}000,qquad
d=\frac{901}{4000},\qquad
\alpha=2+d=\frac{8901}{4000},qquad
X=N^{2/\alpha}.
$$

Chamberland--Straub Proposition 3.4 applies the finite Oppermann computation
to every real $x\geq1$ with $x^{\alpha/2}<N$, hence to $x<X$. Under RH, their
Theorem 3.2 gives a prime in the still smaller interval
$[x^\alpha,(x+1)^\alpha-1)$ whenever

$$
x^{d/2}\geq\frac{22}{25}\log x.
$$

At $x=X$, this condition becomes

$$
N^{901/8901}\geq\frac{7040}{8901}\log N.
$$

Taking logarithms leaves the exact sign checked by `rh_delta.json`:

$$
\frac{901}{8901}\log N
-\log\!\left(\frac{7040}{8901}\log N\right)>0.
$$

The exact certified lower margin is greater than
$0.0000797000675$. The same certificate proves
$(901/8901)\log N>1$, so $x^{d/2}/\log x$ increases from the splice onward.
The analytic side therefore covers $x\geq X$, including equality, and the
finite side covers $x<X$.

For a larger exponent $\alpha'=r\alpha$ with $r\geq1$, put $y=x^r$.
Then $y^\alpha=x^{\alpha'}$ and
$y+1=x^r+1\leq(x+1)^r$, so the $\alpha$ interval at $y$ is contained in the
$\alpha'$ interval at $x$. This proves the stated range of $\delta$.

The exact verifier encloses logarithms with a rational atanh series after
power-of-two range reduction. The C program recomputes the signs with `logl`
through an unrelated code path.

## Certificates

- `certs/rh_delta.json`: exact logarithm intervals and positive margins.
- `certs/olc_rows.tsv.gz`: canonical projection of 322,073 cumulative rows
  from 2,560 tracked `*.out` worker files.
- `certs/olc_public_audit.json`: pinned commit, manifest and projection hashes,
  components, holes, duplicates, and invariant counts.
- `certs/edge_witnesses.csv`: least-prime offsets for both halves.
- `certs/edge_summary.json`: CSV hash and the top 20 exact ratios per half.

The Python edge verifier uses the first twelve prime Miller--Rabin bases.
Sorenson and Webster computed the first composite passing those bases as
$318665857834031151167461>2^{64}$ in
[*Strong Pseudoprimes to Twelve Prime Bases*](https://arxiv.org/abs/1509.00864),
so the test is deterministic on every certificate candidate.

`verify_gap_row.py` uses the same deterministic range to replay the reported
Oliveira e Silva--Herzog--Pardi row: both endpoints
$1425172824437699411$ and $1425172824437700887$ are prime, and all odd
interior values are composite, giving gap $1476$. This checks that row, not
the exhaustiveness of their full table.
