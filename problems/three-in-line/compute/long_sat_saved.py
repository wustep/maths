#!/usr/bin/env python3
"""Run long, parent-bounded SAT searches on the saved n=71 rct4 CNF.

This is deliberately a *consumer* of ``n71-rct4.cnf``.  It neither imports
the line enumerator nor regenerates any clauses.  Two child processes stream
the saved DIMACS directly into the PySAT bindings for Kissat and CaDiCaL.  A
separate parent process enforces one total wall-clock deadline per child, so a
solver call that holds Python's GIL cannot overrun the advertised limit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import platform
import queue
import random
import signal
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pysat
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
EXPECTED_SHA256 = "9a87227d743e9a2e956ac427940f601e5722f9773a6035cacedbe43d3f824bd5"
EXPECTED_VARIABLES = 792_274
EXPECTED_CLAUSES = 1_931_230
ORIGINAL_VARIABLES = 1_260


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def emit(event: dict) -> None:
    print(json.dumps(event, sort_keys=True), flush=True)


def load_saved_dimacs(path: Path, solver: Solver) -> dict:
    """Stream the saved one-clause-per-line DIMACS into ``solver``."""

    declared_variables: int | None = None
    declared_clauses: int | None = None
    actual_clauses = 0
    actual_literals = 0
    maximum_variable = 0

    with path.open("r", encoding="ascii") as handle:
        for line_number, raw_line in enumerate(handle, 1):
            line = raw_line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                fields = line.split()
                if fields[:2] != ["p", "cnf"] or len(fields) != 4:
                    raise ValueError(f"line {line_number}: malformed DIMACS header")
                if declared_variables is not None:
                    raise ValueError("multiple DIMACS headers")
                declared_variables = int(fields[2])
                declared_clauses = int(fields[3])
                continue
            if declared_variables is None:
                raise ValueError(f"line {line_number}: clause precedes DIMACS header")

            fields = [int(field) for field in line.split()]
            if not fields or fields[-1] != 0 or 0 in fields[:-1]:
                raise ValueError(f"line {line_number}: malformed clause terminator")
            clause = fields[:-1]
            if not clause:
                raise ValueError(f"line {line_number}: unexpected empty clause")
            solver.add_clause(clause)
            actual_clauses += 1
            actual_literals += len(clause)
            maximum_variable = max(maximum_variable, *(abs(literal) for literal in clause))

    if declared_variables != EXPECTED_VARIABLES:
        raise ValueError(
            f"DIMACS declares {declared_variables} variables, expected {EXPECTED_VARIABLES}"
        )
    if declared_clauses != EXPECTED_CLAUSES or actual_clauses != EXPECTED_CLAUSES:
        raise ValueError(
            "DIMACS clause mismatch: "
            f"declared={declared_clauses}, actual={actual_clauses}, "
            f"expected={EXPECTED_CLAUSES}"
        )
    if maximum_variable != EXPECTED_VARIABLES:
        raise ValueError(
            f"maximum variable is {maximum_variable}, expected {EXPECTED_VARIABLES}"
        )

    return {
        "declared_variables": declared_variables,
        "declared_clauses": declared_clauses,
        "actual_clauses": actual_clauses,
        "actual_literals": actual_literals,
        "maximum_variable_seen": maximum_variable,
    }


def worker_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="internal saved-CNF solver worker")
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--solver-name", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--random-phases", action="store_true")
    args = parser.parse_args(argv)

    started = time.monotonic()
    try:
        with Solver(name=args.solver_name, use_timer=True) as solver:
            solver.configure({"seed": args.seed})
            loaded = load_saved_dimacs(args.cnf, solver)

            random_phases_effective = False
            if args.random_phases:
                rng = random.Random(args.seed)
                phases = [
                    variable if rng.getrandbits(1) else -variable
                    for variable in range(1, ORIGINAL_VARIABLES + 1)
                ]
                try:
                    solver.set_phases(phases)
                    random_phases_effective = True
                except NotImplementedError:
                    pass

            load_seconds = time.monotonic() - started
            emit(
                {
                    "event": "loaded",
                    "solver": type(solver.solver).__name__,
                    "solver_name": args.solver_name,
                    "seed": args.seed,
                    "load_seconds": load_seconds,
                    "random_phases": args.random_phases,
                    "random_phases_effective": random_phases_effective,
                    **loaded,
                }
            )

            solve_started = time.monotonic()
            answer = solver.solve()
            solve_seconds = time.monotonic() - solve_started
            try:
                stats = solver.accum_stats()
            except NotImplementedError:
                stats = {"cpu_time": solver.time_accum()}

            selected: list[int] | None = None
            if answer is True:
                model = set(solver.get_model())
                selected = [
                    variable - 1
                    for variable in range(1, ORIGINAL_VARIABLES + 1)
                    if variable in model
                ]
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            emit(
                {
                    "event": "complete",
                    "status": status,
                    "solve_seconds": solve_seconds,
                    "solver_stats": stats,
                    "selected_orbits": selected,
                }
            )
        return 0
    except BaseException:
        emit({"event": "error", "traceback": traceback.format_exc()})
        return 2


@dataclass(frozen=True)
class Engine:
    label: str
    solver_name: str
    version: str
    seed: int
    random_phases: bool


@dataclass
class RunningEngine:
    spec: Engine
    process: subprocess.Popen[str]
    started_monotonic: float
    started_utc: str
    lines: list[str]
    loaded: dict | None = None
    complete: dict | None = None
    error: dict | None = None
    max_rss_kb: int = 0


def read_output(label: str, stream, messages: queue.Queue[tuple[str, str]]) -> None:
    for line in stream:
        messages.put((label, line.rstrip("\n")))
    stream.close()


def process_rss_kb(pid: int) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text(encoding="ascii").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None
    return None


def stop_process(process: subprocess.Popen[str]) -> None:
    """Terminate only the solver process group created by this harness."""

    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def decode_witness(selected_orbits: list[int], output: Path) -> dict:
    """Decode only the saved CNF's 1,260 original orbit variables."""

    # This reuses q1's already-tested orbit order.  It builds no line set and
    # emits no clauses; the independent determinant checker remains separate.
    from rct4_model import build_rct4_geometry, selected_points

    geometry = build_rct4_geometry(71)
    points = selected_points(geometry, set(selected_orbits))
    if len(points) != 142:
        raise ValueError(
            f"SAT assignment selected {len(selected_orbits)} orbits and decoded to {len(points)} points"
        )
    payload = "".join(f"{x} {y}\n" for x, y in points)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")
    return {
        "path": str(output),
        "points": len(points),
        "selected_orbits": len(selected_orbits),
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
    }


def parse_parent_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cnf", type=Path, default=HERE / "n71-rct4.cnf")
    parser.add_argument("--seconds", type=float, default=1200.0)
    parser.add_argument("--kissat-seed", type=int, default=20_260_816)
    parser.add_argument("--cadical-seed", type=int, default=271_828)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument("--witness", type=Path, default=HERE / "n71-142.txt")
    parser.add_argument("--heartbeat-seconds", type=float, default=30.0)
    return parser.parse_args()


def main() -> int:
    args = parse_parent_args()
    if not 900.0 <= args.seconds <= 1200.0:
        raise ValueError("q2 requires a parent wall limit between 900 and 1200 seconds")
    if args.heartbeat_seconds <= 0:
        raise ValueError("heartbeat interval must be positive")

    digest = sha256_file(args.cnf)
    if digest != EXPECTED_SHA256:
        raise ValueError(f"saved CNF SHA-256 is {digest}, expected {EXPECTED_SHA256}")
    print(
        f"verified saved CNF sha256={digest}; launching two unrestricted solvers ",
        f"with {args.seconds:.0f}s parent wall limits",
        flush=True,
    )

    engines = (
        Engine("kissat", "kissat404", "Kissat 4.0.4 via PySAT", args.kissat_seed, True),
        Engine("cadical", "cadical195", "CaDiCaL 1.9.5 via PySAT", args.cadical_seed, True),
    )
    messages: queue.Queue[tuple[str, str]] = queue.Queue()
    running: dict[str, RunningEngine] = {}
    threads: list[threading.Thread] = []

    for spec in engines:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "_worker",
            "--cnf",
            str(args.cnf.resolve()),
            "--solver-name",
            spec.solver_name,
            "--seed",
            str(spec.seed),
        ]
        if spec.random_phases:
            command.append("--random-phases")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
        assert process.stdout is not None
        state = RunningEngine(spec, process, time.monotonic(), utc_now(), [])
        running[spec.label] = state
        thread = threading.Thread(
            target=read_output,
            args=(spec.label, process.stdout, messages),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    unfinished = set(running)
    next_heartbeat = time.monotonic() + args.heartbeat_seconds
    timed_out: set[str] = set()
    sat_label: str | None = None

    try:
        while unfinished:
            now = time.monotonic()
            try:
                label, line = messages.get(timeout=0.25)
                state = running[label]
                state.lines.append(line)
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[{label}] {line}", flush=True)
                else:
                    kind = event.get("event")
                    if kind == "loaded":
                        state.loaded = event
                        print(
                            f"[{label}] loaded saved CNF in {event['load_seconds']:.2f}s; "
                            f"{event['solver']} solving unrestricted rct4",
                            flush=True,
                        )
                    elif kind == "complete":
                        state.complete = event
                        state.process.wait()
                        unfinished.discard(label)
                        print(
                            f"[{label}] {event['status']} after {event['solve_seconds']:.2f}s solve time",
                            flush=True,
                        )
                        if event["status"] == "SAT" and sat_label is None:
                            sat_label = label
                    elif kind == "error":
                        state.error = event
                        state.process.wait()
                        unfinished.discard(label)
                        print(f"[{label}] worker error", flush=True)

            except queue.Empty:
                pass

            now = time.monotonic()
            for label in tuple(unfinished):
                state = running[label]
                rss = process_rss_kb(state.process.pid)
                if rss is not None:
                    state.max_rss_kb = max(state.max_rss_kb, rss)
                if state.process.poll() is not None and state.complete is None and state.error is None:
                    # Give the reader thread a brief chance to forward its last line.
                    time.sleep(0.1)
                    if messages.empty():
                        state.error = {
                            "event": "error",
                            "traceback": f"worker exited with code {state.process.returncode} without a result",
                        }
                        unfinished.discard(label)
                elif now - state.started_monotonic >= args.seconds:
                    stop_process(state.process)
                    timed_out.add(label)
                    unfinished.discard(label)
                    print(
                        f"[{label}] parent wall limit reached; child terminated at "
                        f"{now - state.started_monotonic:.2f}s",
                        flush=True,
                    )

            if sat_label is not None:
                for label in tuple(unfinished):
                    state = running[label]
                    stop_process(state.process)
                    unfinished.discard(label)
                    print(f"[{label}] stopped after independent solver found SAT", flush=True)

            if now >= next_heartbeat and unfinished:
                parts = []
                for label in sorted(unfinished):
                    state = running[label]
                    elapsed = now - state.started_monotonic
                    rss = process_rss_kb(state.process.pid)
                    rss_text = f", rss={rss / 1024:.0f}MiB" if rss is not None else ""
                    phase = "solving" if state.loaded is not None else "loading"
                    parts.append(
                        f"{label}:{phase} {elapsed:.0f}/{args.seconds:.0f}s{rss_text}"
                    )
                print("heartbeat " + " | ".join(parts), flush=True)
                next_heartbeat = now + args.heartbeat_seconds
    finally:
        for state in running.values():
            stop_process(state.process)
        for thread in threads:
            thread.join(timeout=1.0)

    finished_utc = utc_now()
    run_results: dict[str, dict] = {}
    for label, state in running.items():
        wall_seconds = min(time.monotonic() - state.started_monotonic, args.seconds)
        loaded = state.loaded or {}
        load_seconds = loaded.get("load_seconds")
        if state.complete is not None:
            status = state.complete["status"]
            solve_seconds = state.complete["solve_seconds"]
            hard_timeout = False
            stopped_after_other_sat = False
            solver_stats = state.complete.get("solver_stats", {})
        elif label in timed_out:
            status = "UNKNOWN"
            solve_seconds = (
                max(0.0, args.seconds - load_seconds) if load_seconds is not None else None
            )
            hard_timeout = True
            stopped_after_other_sat = False
            solver_stats = {
                "terminated_by_parent": True,
                "exit_code": state.process.returncode,
            }
        elif sat_label is not None and label != sat_label:
            status = "UNKNOWN"
            solve_seconds = (
                max(0.0, wall_seconds - load_seconds) if load_seconds is not None else None
            )
            hard_timeout = False
            stopped_after_other_sat = True
            solver_stats = {
                "terminated_by_parent": True,
                "exit_code": state.process.returncode,
            }
        else:
            status = "ERROR"
            solve_seconds = None
            hard_timeout = False
            stopped_after_other_sat = False
            solver_stats = {"exit_code": state.process.returncode}

        result = {
            "quest": "q2-second-pass",
            "n": 71,
            "target_points": 142,
            "symmetry": "canonical-rct4",
            "fixed_empty": "anti-diagonal",
            "fixed_main_diagonal_index": None,
            "cnf": str(args.cnf),
            "cnf_sha256": digest,
            "cnf_variables": EXPECTED_VARIABLES,
            "cnf_clauses": EXPECTED_CLAUSES,
            "original_variables": ORIGINAL_VARIABLES,
            "solver": state.spec.version,
            "solver_name": state.spec.solver_name,
            "solver_binding": loaded.get("solver"),
            "seed": state.spec.seed,
            "random_phases": state.spec.random_phases,
            "random_phases_effective": loaded.get("random_phases_effective"),
            "python": platform.python_version(),
            "pysat": pysat.__version__,
            "started_utc": state.started_utc,
            "finished_utc": finished_utc,
            "wall_limit_seconds": args.seconds,
            "wall_seconds": wall_seconds,
            "load_seconds": load_seconds,
            "solve_seconds": solve_seconds,
            "hard_timeout": hard_timeout,
            "stopped_after_other_sat": stopped_after_other_sat,
            "status": status,
            "max_parent_sampled_rss_kb": state.max_rss_kb,
            "solver_stats": solver_stats,
            "dimacs_stream_audit": {
                key: loaded.get(key)
                for key in (
                    "declared_variables",
                    "declared_clauses",
                    "actual_clauses",
                    "actual_literals",
                    "maximum_variable_seen",
                )
            },
            "worker_error": state.error,
            "worker_output": state.lines,
        }
        run_results[label] = result
        run_path = args.output_dir / f"q2-{label}-seed-{state.spec.seed}.json"
        write_json(run_path, result)

    witness: dict | None = None
    if sat_label is not None:
        selected = running[sat_label].complete.get("selected_orbits")
        if not isinstance(selected, list):
            raise ValueError("SAT worker returned no original-variable assignment")
        witness = decode_witness(selected, args.witness)
        run_results[sat_label]["witness"] = witness
        run_path = args.output_dir / f"q2-{sat_label}-seed-{running[sat_label].spec.seed}.json"
        write_json(run_path, run_results[sat_label])

    statuses = {label: result["status"] for label, result in run_results.items()}
    if "SAT" in statuses.values():
        overall_status = "SAT_UNCHECKED"
    elif "UNSAT" in statuses.values():
        overall_status = "RESTRICTED_UNSAT_REPORTED"
    elif all(status == "UNKNOWN" for status in statuses.values()):
        overall_status = "UNKNOWN"
    else:
        overall_status = "ERROR"

    summary = {
        "quest": "q2-second-pass",
        "status": overall_status,
        "cnf": str(args.cnf),
        "cnf_sha256": digest,
        "wall_limit_seconds_per_solver": args.seconds,
        "parallel": True,
        "engines": {
            label: f"q2-{label}-seed-{state.spec.seed}.json"
            for label, state in running.items()
        },
        "engine_statuses": statuses,
        "witness": witness,
        "note": (
            "SAT_UNCHECKED requires a fresh run of verify_n71.py before any solution claim. "
            "UNKNOWN records only the parent-enforced timeout."
        ),
    }
    write_json(args.output_dir / "q2-long-sat-summary.json", summary)
    print(json.dumps(summary, sort_keys=True), flush=True)
    return 2 if overall_status == "ERROR" else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "_worker":
        raise SystemExit(worker_main(sys.argv[2:]))
    multiprocessing.freeze_support()
    raise SystemExit(main())
