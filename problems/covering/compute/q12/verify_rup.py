#!/usr/bin/env python3
"""Small independent checker for the RUP-only DRAT core saved in this folder."""
from collections import Counter
from pathlib import Path


def read_cnf(path: Path):
    clauses, header, pending = [], None, []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("c"):
            continue
        if line.startswith("p "):
            _, kind, nv, nc = line.split()
            assert kind == "cnf" and header is None
            header = (int(nv), int(nc))
            continue
        for token in line.split():
            lit = int(token)
            if lit:
                pending.append(lit)
            else:
                clauses.append(tuple(sorted(set(pending))))
                pending = []
    assert not pending and header is not None
    assert len(clauses) == header[1]
    assert all(0 < abs(lit) <= header[0] for c in clauses for lit in c)
    return header[0], clauses


def conflict_by_units(clauses, assumptions):
    """Return true only when unit propagation derives a contradiction."""
    assigned = {}
    for lit in assumptions:
        var, value = abs(lit), lit > 0
        if var in assigned and assigned[var] != value:
            return True
        assigned[var] = value
    while True:
        changed = False
        for clause, count in clauses.items():
            if not count:
                continue
            if any(assigned.get(abs(lit)) == (lit > 0) for lit in clause):
                continue
            unknown = [lit for lit in clause if abs(lit) not in assigned]
            if not unknown:
                return True
            if len(unknown) == 1:
                lit = unknown[0]
                assigned[abs(lit)] = lit > 0
                changed = True
        if not changed:
            return False


def verify(cnf_path: Path, proof_path: Path):
    nv, original = read_cnf(cnf_path)
    clauses = Counter(original)
    additions, empty = 0, False
    for line in proof_path.read_text().splitlines():
        tokens = line.split()
        if not tokens or tokens[0] == "c":
            continue
        deletion = tokens[0] == "d"
        values = list(map(int, tokens[1:] if deletion else tokens))
        assert values[-1] == 0 and 0 not in values[:-1]
        clause = tuple(sorted(set(values[:-1])))
        assert all(abs(lit) <= nv for lit in clause)
        if deletion:
            assert clauses[clause] > 0, "deleting an absent clause"
            clauses[clause] -= 1
        else:
            assert conflict_by_units(clauses, [-lit for lit in clause]), (
                "clause is not RUP", clause)
            clauses[clause] += 1
            additions += 1
            empty |= not clause
    assert empty, "proof never derives the empty clause"
    return len(original), additions


if __name__ == "__main__":
    import sys
    n, steps = verify(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"PASS RUP: {n} input clauses, {steps} additions, empty clause derived")
