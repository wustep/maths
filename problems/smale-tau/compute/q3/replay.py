#!/usr/bin/env python3
"""One heavy child at a time; complete enumerations supply the lower bounds.

Default: replay the full claim and compare with committed artifacts.
--write: regenerate the artifacts after completing all checks.
--counts C_JSON RUST_JSON: use already completed census runs (development).
The normal replay never trusts cached counts.
"""
import argparse
from collections import Counter
import hashlib
import json
from math import isqrt
from pathlib import Path
import resource
import subprocess
import time

HERE = Path(__file__).resolve().parent
Q1 = HERE.parent / "q1"
BOUND = 50000
NODES = [1, 2, 8, 59, 663, 10609, 225219, 6057298, 199290037]
COUNTS = [1, 2, 4, 9, 26, 102, 562, 4363, 46154, 652227]


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(args, output=None):
    start = time.monotonic()
    print("Running:", " ".join(map(str, args)), flush=True)
    if output:
        with output.open("w") as stream:
            subprocess.run(list(map(str, args)), stdout=stream, check=True)
    else:
        subprocess.run(list(map(str, args)), check=True)
    print(f"Finished in {time.monotonic() - start:.1f}s", flush=True)


def check_values(n, values, steps):
    require(values[0] == 1 and values[-1] == n, f"bad endpoints: {n}")
    require(len(values) - 1 == steps, f"bad length: {n}")
    require(len(set(values)) == len(values) and min(values) > 0,
            f"not normalized: {n}")
    for k, value in enumerate(values[1:], 1):
        require(any(value in (a + b, a * b, abs(a - b))
                    for a in values[:k] for b in values[:k]),
                f"invalid step {k} for {n}")


def primes(bound):
    # Trial division is independent of the Rust sieve in verify_witnesses.rs.
    return [n for n in range(2, bound + 1)
            if all(n % d for d in range(2, isqrt(n) + 1))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--counts", nargs=2, type=Path)
    args = parser.parse_args()
    work = HERE / ".work"
    work.mkdir(exist_ok=True)
    run(["gcc", "-O3", "-fopenmp", Q1 / "slp_search.c", "-o", work / "census-c"])
    run(["rustc", "-O", Q1 / "check.rs", "-o", work / "census-rust"])
    run(["gcc", "-O3", "-fopenmp", HERE / "find_witness.c", "-o", work / "find-witness"])
    run(["rustc", "-O", HERE / "verify_witnesses.rs", "-o", work / "verify-witnesses"])
    if args.counts:
        paths = args.counts
    else:
        paths = [work / "count-c.json", work / "count-rust.json"]
        run([work / "census-c", "--count", 9, "--table", BOUND, "--threads", 1], paths[0])
        run([work / "census-rust", "count", 9, BOUND], paths[1])
    c, r = [json.loads(path.read_text()) for path in paths]
    for result in (c, r):
        require(result["nodes_per_depth"] == NODES, "node count mismatch")
        require(result["reached_cumulative"] == COUNTS, "Markström count mismatch")
        require(result["tau_table_bound"] >= BOUND, "census too short")
        require(len(result["tau"]) == result["tau_table_bound"], "truncated census")
    require(c["tau"][:BOUND] == r["tau"][:BOUND], "C/Rust disagreement")
    lower = c["tau"][:BOUND]
    for source in (Q1 / "b173419.txt", Q1 / "tau_table_10266.txt"):
        for line in source.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            n, cost = map(int, line.split())
            require(lower[n - 1] == cost, f"baseline mismatch at {n}")
    require(lower.index(-1) + 1 == 10267, "initial interval mismatch")
    require(all(-1 <= cost <= 9 for cost in lower), "invalid census depth")
    # Every absent value has cost at least 10. We still need an explicit
    # ten-step program for each one before replacing any -1 with 10.
    tau = [10 if cost == -1 else cost for cost in lower]
    prime_list = primes(BOUND)
    exceptions = [p for p in prime_list if tau[p - 1] < tau[p - 2]]
    require([p for p in exceptions if p < 5000] == [3359, 3623, 4909, 4943],
            "Patanè classification mismatch")
    require([(tau[p-1], tau[p-2]) for p in [3359, 3623, 4909, 4943]] ==
            [(7, 8), (8, 9), (7, 8), (8, 9)], "Patanè costs mismatch")
    for p in [3323, 3803, 3929, 3947, 4139, 4583, 4783, 4871, 4987]:
        require(lower[p-1] == lower[p-2] == 9, "Patanè nine-step pair mismatch")
    needs = {n: 10 for n, cost in enumerate(lower, 1) if cost == -1}
    for p in exceptions:
        for n in (p - 1, p):
            needs[n] = tau[n - 1]
    witnesses = {}
    # Existing witnesses are hints only: both verifiers check them again.
    saved = HERE / "witnesses.txt"
    if saved.exists():
        for line in saved.read_text().splitlines():
            n, *values = map(int, line.split())
            if n in needs:
                check_values(n, values, needs[n])
                witnesses[n] = values
    for steps in sorted(set(needs.values())):
        todo = sorted(n for n in needs if needs[n] == steps and n not in witnesses)
        for start in range(0, len(todo), 1000):
            batch = todo[start:start + 1000]
            target_file = work / "targets.txt"
            target_file.write_text("".join(f"{n} {n}\n" for n in batch))
            output = work / "found.jsonl"
            run([work / "find-witness", steps, target_file], output)
            found = {}
            for line in output.read_text().splitlines():
                row = json.loads(line)
                n = int(row["value"])
                values = list(map(int, row["program"]["values"]))
                require(n in batch and n not in found, "unexpected/duplicate target")
                require(row["steps"] == steps, "reported cost mismatch")
                check_values(n, values, steps)
                found[n] = values
            require(set(found) == set(batch), "incomplete upper bounds")
            witnesses.update(found)
    require(set(witnesses) == set(needs), "missing witnesses")
    table_text = "".join(f"{n} {cost}\n" for n, cost in enumerate(tau, 1))
    witness_text = "".join(" ".join(map(str, [n, *witnesses[n]])) + "\n"
                           for n in sorted(witnesses))
    exception_text = "p,tau_p,tau_previous\n" + "".join(
        f"{p},{tau[p-1]},{tau[p-2]}\n" for p in exceptions)
    (work / "table.txt").write_text(table_text)
    (work / "witnesses.txt").write_text(witness_text)
    run([work / "verify-witnesses", work / "table.txt", work / "witnesses.txt"])
    require(len(exceptions) == 69, "claimed counterexample count does not hold")
    require(Counter(tau)[10] == 3779, "claimed ten-step count does not hold")
    summary = {
        "bound": BOUND,
        "exact_table": True,
        "tau_histogram": {str(k): v for k, v in sorted(Counter(tau).items())},
        "nodes_per_depth": NODES,
        "reached_cumulative": COUNTS,
        "prime_count": len(prime_list),
        "prime_counterexamples": len(exceptions),
        "prime_counterexample_cost_pairs": {
            f"{a},{b}": v for (a, b), v in sorted(Counter(
                (tau[p-1], tau[p-2]) for p in exceptions).items())},
        "published_counterexamples_below_5000": [3359, 3623, 4909, 4943],
        "explicit_witnesses": len(witnesses),
        "table_sha256": hashlib.sha256(table_text.encode()).hexdigest(),
        "witnesses_sha256": hashlib.sha256(witness_text.encode()).hexdigest(),
    }
    outputs = {"tau_table_50000.txt": table_text, "witnesses.txt": witness_text,
               "prime_counterexamples.csv": exception_text,
               "certificate.json": json.dumps(summary, indent=2) + "\n"}
    for name, content in outputs.items():
        path = HERE / name
        if args.write:
            tmp = work / (name + ".new")
            tmp.write_text(content)
            tmp.replace(path)
        else:
            require(path.read_text() == content, f"artifact mismatch: {name}")
    peak = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    print(f"CLAIM holds: exact tau table through {BOUND}; 69 prime counterexamples.")
    print(f"Peak child RSS in this invocation: {peak} KiB")


if __name__ == "__main__":
    main()
