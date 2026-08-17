# Compute — Tuza packing/covering

Replay path (no search, no network):

```
./.venv/bin/python replay_known.py
./.venv/bin/python verify_c7.py
# optional, ~50s: ./.venv/bin/python census_wke.py 7 --labelled
```

`verify_c7.py` rebuilds every 8-regular codegree-7 certificate from
`certs/reduce_c7_8reg.json` and checks the three Puleo conditions by
edge incidence. It does not import the searcher.

`bin/geng` is nauty 2.8.9, compiled from the upstream tarball.

| file | what |
| --- | --- |
| `tuza.py` | exact \(\nu,\tau\) (search + CBC) |
| `wke.py` | bitset WKE / graph6 |
| `census_wke.py` | unlabelled n=5..8 WKE census; optional labelled n=7 |
| `inspect_n8_exceptions.py` | second WKE implementation on the n=8 \(\Delta=4\) list |
| `reduce_codegree.py` | searcher for 8-regular codegree-7 certificates |
| `verify_c7.py` | independent checker of those certificates |
| `reduce_c6.py` | incomplete codegree-6 attempt (12 transferable-template failures) |
| `split_census.py` | `geng -S` split graphs, \((\nu,\tau)\) |
| `regular7_census.py` | 7-regular graphs, \((\nu,\tau)\) |
| `certs/c7_8reg_verified.json` | 1044 explicit \((S,X)\) |
| `certs/n8_exceptions.json` | the eight connected non-WKE 8-vertex graphs with \(\Delta=4\) |
