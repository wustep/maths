# q3 — alternative handles versus CCR 1.44655

Replay:

```bash
cd problems/simon-lieb-thirring/compute/q3
./run_all.sh
```

Carvalho Corso–Ried, arXiv:2403.04347v2, Corollary 1.7, is the published
later record

$$
\frac{L_{1,1,1}}{L_{1,1,1}^{\mathrm{cl}}}\le 1.44655
$$

from \(M_3=0.371185695\). That value is the method ceiling of the
Frank–Hundertmark–Jex–Nam / Hundertmark–Kunstmann–Ried–Vugalter
variational problem (solved in closed form as a Clausen series in
arXiv:2407.10117v2). A new FHJN trial pair cannot go below it. This
folder tries other published conversions and a 1D test-potential search.

What ran:

1. Weidl’s real interpolation between the sharp \(\gamma=\tfrac12\)
   (Hundertmark–Lieb–Thomas \(L_{1/2,1}=\tfrac12\)) and
   \(\gamma=\tfrac32\) (Laptev–Weidl \(3/16\)), independently in Python
   and `rustc`. The Ky-Fan factor forces \(C(\tfrac12)>2\), so the
   converted ratio is about \(3.84\).
2. Seiringer–Solovej remainder absorption (arXiv:2303.04504v2) at
   \(d=1\), with the Airy zero enclosed by a power series. \(R_1\approx 0.132\),
   ratio about \(2.75\).
3. Weidl’s Neumann covering, now scored at \(\gamma=1\). A constant well
   already gives local ratio \(1/\sqrt{3}\) over classical \(\approx 2.72\).
4. A Dirichlet-grid search over square wells, two-sech wells, Gaussian
   sums, and histograms, looking for a test potential whose ratio exceeds
   the one-bound-state value \(2/\sqrt{3}\).
5. Empirical \(T/\int\rho^3\) on Hermite and finite-well blocks (not a bound).

None of these beat \(1.44655\). The q2 Clausen envelope is replayed at the
end of `run_all.sh` so the published record is still independently enclosed.

Certificates live in `certs/`. Summary of the leftover:
`certs/leftover.json`.
