# Compute

Stdlib only (no venv):

```bash
python3 compute/verify_houzhao.py
python3 compute/verify_certificate.py compute/certs/hz_kernels_L6.json --beat 0.94349259
python3 compute/verify_beat_hz.py
python3 compute/cho_two_windows.py
python3 compute/construct_singer.py
python3 compute/construct_bose.py
```

Needs `compute/.venv` (numpy/scipy):

```bash
compute/.venv/bin/python compute/search_kernels.py --phase replay
compute/.venv/bin/python compute/plot_gamma.py
```

`refs/` is a snapshot of Hou–Zhao’s GitHub (8-kernel hash matches
arXiv:2607.01169v2 Claim 4.1). `certs/hz_kernels_L6.json` is our L=6
certificate: same a, smaller b.
