#!/usr/bin/env python3
"""Rebuild the at-most-17 CNF, check its saved proof core, and replay CaDiCaL."""
import argparse
import hashlib
from collections import Counter
from pathlib import Path

from pysat.solvers import Cadical195
from search_ok37_p_le17_sat import build_solver, ok37_columns, precompute_reps
from verify_rup import read_cnf, verify

HERE = Path(__file__).resolve().parent


class ClauseSink:
    def __init__(self):
        self.clauses = []

    def add_clause(self, clause):
        self.clauses.append(tuple(clause))


def formula():
    columns = ok37_columns()
    return build_solver(columns, *precompute_reps(columns), ell=0, p=17,
                        force_nonempty=False, solver_factory=ClauseSink)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-proof-dir", type=Path,
                        help="also write the full DIMACS and fresh CaDiCaL DRAT")
    args = parser.parse_args()
    sink, meta = formula()
    assert (meta["nvars"], len(sink.clauses)) == (8821, 412564)
    nv, core = read_cnf(HERE / "atmost17_core.cnf")
    assert nv == meta["nvars"]
    available = Counter(tuple(sorted(set(c))) for c in sink.clauses)
    assert not (Counter(core) - available), "proof core is not part of the encoding"
    n, steps = verify(HERE / "atmost17_core.cnf", HERE / "atmost17_core.drat")
    print(f"PASS core: {n} clauses belong to the at-most-17 encoding; "
          f"{steps} RUP additions prove UNSAT")
    with Cadical195(bootstrap_with=sink.clauses,
                    with_proof=args.raw_proof_dir is not None) as solver:
        assert solver.solve() is False, "expected at-most-17 UNSAT"
        print("PASS CaDiCaL195: ell=0, at most 17 blocks, UNSAT")
        if args.raw_proof_dir is not None:
            args.raw_proof_dir.mkdir(parents=True, exist_ok=True)
            cnf = f'p cnf {meta["nvars"]} {len(sink.clauses)}\n'
            cnf += "".join(" ".join(map(str, c)) + " 0\n" for c in sink.clauses)
            (args.raw_proof_dir / "atmost17.cnf").write_text(cnf)
            (args.raw_proof_dir / "atmost17.drat").write_text(
                "\n".join(solver.get_proof()) + "\n")
            print("Full DIMACS SHA256", hashlib.sha256(cnf.encode()).hexdigest())


if __name__ == "__main__":
    main()
