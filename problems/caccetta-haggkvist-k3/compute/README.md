# Compute

## Replay the F₄ certificate

```
python3 flags4.py          # rebuild AC, AR, BR; must match HKN Tables 1–2
python3 ind_fork.py        # rebuild IndT, IndV, Fork
/usr/bin/python3 verify_certificate.py certs/f4_certificate.json --margin 0.05 --c 0.34645
```

`verify_certificate.py` needs numpy. The venv at `/tmp/chvenv` has scipy/cvxpy if you want to rerun the SDP (`sdp_bound.py`, `optimize_bound.py`).

## Replay SAT + DRAT

`kissat` and `drat-trim` are compiled in this folder.

```
./kissat --time=10 $(python3 encode_ch.py --n 9 --d 3 | tee /tmp/x.cnf >/dev/null; echo /tmp/x.cnf)
# recorded proofs:
./drat-trim certs/ch-12-4-sb.cnf certs/ch-12-4-sb.drat   # s VERIFIED
./drat-trim certs/ch-15-5-sb.cnf certs/ch-15-5-sb.drat
./drat-trim certs/ch-16-6-sb.cnf certs/ch-16-6-sb.drat
./drat-trim certs/ch-17-6-sb.cnf certs/ch-17-6-sb.drat
```

`encode_ch.py` writes a DIMACS instance: oriented, no C₃, out-regular of degree `d`, $N^+(0)=\{1,\ldots,d\}$, lex order on out-neighbourhoods (disable with `--no-sb`).

## Small-n census

`certs/small_n_census.json` (n≤12, no lex SB). With lex SB, n=12,15,16 are UNSAT with DRAT.

The n=18 in-degree cubes live in `q1/`. Replay: `cd q1 && ./run_all.sh`.

The next exact holes after n=18 live in `q2/`. Stored DRATs cover
n=21, 24, 26, 27, 29, 30, 32, 33, 35, 36. Replay: `cd q2 && ./run_all.sh`.

Leftover holes from n=38 through n=72 live in `q3/`. Replay:
`cd q3 && ./run_all.sh`.

Leftover holes from n=73 through n=108 live in `q4/`, together with
the CKLS-fork F₄ certificate at c=0.34640. Replay:
`cd q4 && ./run_all.sh`.

Leftover holes from n=109 through n=114 live in `q5/`. Replay:
`cd q5 && ./run_all.sh`.

Leftover holes from n=115 live in `q6/`. Replay:
`cd q6 && ./run_all.sh`.

Leftover holes from n=116 live in `q7/`. Replay:
`cd q7 && ./run_all.sh`.

Leftover holes from n=117 live in `q8/`. Replay:
`cd q8 && ./run_all.sh`.

Leftover holes from n=118 live in `q9/`. Replay:
`cd q9 && ./run_all.sh`.

Leftover holes from n=119 live in `q10/`. Replay:
`cd q10 && ./run_all.sh`.

Leftover holes from n=120 live in `q11/`. Replay:
`cd q11 && ./run_all.sh`.

Leftover holes from n=121 live in `q12/`. Replay:
`cd q12 && ./run_all.sh`.

Leftover holes from n=122 live in `q13/`. Replay:
`cd q13 && ./run_all.sh`.

Leftover holes from n=123 live in `q14/`. Replay:
`cd q14 && ./run_all.sh`.

Leftover holes from n=124 live in `q15/`. Replay:
`cd q15 && ./run_all.sh`.

Leftover holes from n=125 live in `q16/`. Replay:
`cd q16 && ./run_all.sh`.

Leftover holes from n=126 live in `q17/`. Replay:
`cd q17 && ./run_all.sh`.

Leftover holes from n=127 live in `q18/`. Replay:
`cd q18 && ./run_all.sh`.

Leftover holes from n=128 live in `q19/`. Replay:
`cd q19 && ./run_all.sh`.

Leftover holes from n=129 live in `q20/`. Replay:
`cd q20 && ./run_all.sh`.

Leftover holes from n=130 live in `q21/`. Replay:
`cd q21 && ./run_all.sh`.

Leftover holes from n=131 live in `q22/`. Replay:
`cd q22 && ./run_all.sh`.

Leftover holes from n=132 live in `q23/`. Replay:
`cd q23 && ./run_all.sh`.

Leftover holes from n=133 live in `q24/`. Replay:
`cd q24 && ./run_all.sh`.

Leftover holes from n=134 live in `q25/`. Replay:
`cd q25 && ./run_all.sh`.

Leftover holes from n=135 live in `q26/`. Replay:
`cd q26 && ./run_all.sh`.

Leftover holes from n=136 live in `q27/`. Replay:
`cd q27 && ./run_all.sh`.

Leftover holes from n=137 live in `q28/`. Replay:
`cd q28 && ./run_all.sh`.

Leftover holes from n=138 live in `q29/`. Replay:
`cd q29 && ./run_all.sh`.

Leftover holes from n=139 live in `q30/`. Replay:
`cd q30 && ./run_all.sh`.

Leftover holes from n=140 live in `q31/`. Replay:
`cd q31 && ./run_all.sh`.

Leftover holes from n=141 live in `q32/`. Replay:
`cd q32 && ./run_all.sh`.

Leftover holes from n=142 live in `q33/`. Replay:
`cd q33 && ./run_all.sh`.

Leftover holes from n=143 live in `q34/`. Replay:
`cd q34 && ./run_all.sh`.
