# q1 — deciding the composite-14 analogue of ST26 Proposition 4.4

    gcc -O3 -march=native -std=c11 -o cover cover.c
    gcc -O3 -march=native -std=c11 -o cover_bdd cover_bdd.c
    gcc -O3 -march=native -std=gnu11 -o spotcheck spotcheck.c

The result, four minutes from a clean checkout:

    ./cover --k 13 --p 191
    -> RESULT UNSAT ... T2(13,191) HOLDS   (102905279 nodes, ~241 s)

Read `certs/T2_p191.txt` for what that means and what it does not.

## Gates, run these first

    python3 check_unsaved.py --selftest      # re-proves ST26 Prop 4.1 at k=4,6
    ./cover --k 5 --p 6    # SAT    - p-independent fails at composite m=6
    ./cover --k 5 --p 31   # UNSAT  - and p repairs it
    ./cover --k 7 --p 8    # SAT
    ./cover --k 7 --p 59   # UNSAT
    ./cover_bdd --k 7 --p 59                 # second procedure, same answers

Brute force says 64 / 0 / 2596 / 0 obstructions for those four; both
searches agree. `cover_bdd` state-explodes before k=13, so it does not
confirm p=191 — that is recorded as a limit, not glossed.

## Files

| file | what it is |
|---|---|
| `cover.c` | the decision procedure. Set-cover feasibility in 13 variables, MRV branching plus a counting bound. `--split N --part i` partitions the search; `--splitdepth` sets where. |
| `cover_bdd.c` | second procedure. Sweeps coordinates forward carrying the surviving pair set, keeps the full `(k+1)p` pairs with no reductions. |
| `check_unsaved.py` | one vector at a time, exhausting all `(k+1)p` pairs, written from the paper. `exhaustive(k,p)` brute-forces all of `Z_m^k`. |
| `spotcheck.c` | adversarial sampling: `--mode sparse|ap|perturb|random`. Shares no code with either search. |
| `certs/T2_p191.txt` | the certificate and the full verification chain. |
