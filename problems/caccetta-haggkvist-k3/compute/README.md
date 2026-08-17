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

`encode_ch.py` writes a DIMACS instance: oriented, no C₃, out-regular of degree `d`, \(N^+(0)=\{1,\ldots,d\}\), lex order on out-neighbourhoods (disable with `--no-sb`).

## Small-n census

`certs/small_n_census.json` (n≤12, no lex SB). With lex SB, n=12,15,16 are UNSAT with DRAT.
