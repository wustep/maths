#!/usr/bin/env python3
"""Watch live leftover SAT hunts; adopt a finished proof; start the next job.

Does not kill solvers. Starts at most one new heavy job when a core is free.
q7 k=30 leftover-tight CNF has the same sha256 as q8; a verified q7 DRAT
is the type-(0,5) certificate. q7 global is the weaker |U|=19 CNF (no
type-(2,1)/(1,3) forbids). q8 global needs its own proof.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q7 = HERE.parent / "q7"
CERTS = HERE / "certs"
Q7C = Q7 / "certs"
BIN = HERE / "bin"
PY = HERE.parent / ".venv" / "bin" / "python"
LOG = CERTS / "watch_hunts.log"

K30_SHA = "cdec5e76ef58cddadf999f77ec31f7e319764ab867454cdac0ae74f2e53f078c"


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    CERTS.mkdir(exist_ok=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def _sz(p: Path) -> dict:
    if not p.is_file():
        return {"exists": False, "path": str(p)}
    st = p.stat()
    return {"exists": True, "path": str(p), "bytes": st.st_size, "mtime": st.st_mtime}


def cadical_running(cnf: Path, proof: Path | None = None) -> list[int]:
    pids = []
    needle = str(cnf)
    try:
        out = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
    except subprocess.CalledProcessError:
        return pids
    for line in out.splitlines():
        if "cadical" in line and needle in line:
            if proof is not None and str(proof) not in line:
                continue
            pids.append(int(line.split()[0]))
    return pids


def kissat_running(cnf: Path) -> list[int]:
    pids = []
    needle = str(cnf)
    try:
        out = subprocess.check_output(["ps", "-eo", "pid,cmd"], text=True)
    except subprocess.CalledProcessError:
        return pids
    for line in out.splitlines():
        if "kissat" in line and needle in line:
            pids.append(int(line.split()[0]))
    return pids


def n_busy_solvers() -> int:
    try:
        out = subprocess.check_output(["ps", "-eo", "cmd"], text=True)
    except subprocess.CalledProcessError:
        return 0
    n = 0
    for line in out.splitlines():
        if any(x in line for x in ("/cadical ", "/kissat ", "/drat-trim ", "/leftover_k30 ")):
            if "watch_hunts" in line or "ps -eo" in line:
                continue
            n += 1
    return n


def snapshot() -> dict:
    rec = {
        "t": time.time(),
        "loadavg": os.getloadavg(),
        "n_busy": n_busy_solvers(),
        "q8": {
            "k30_cnf": _sz(CERTS / "five_k30_n0_5.cnf"),
            "k30_kissat_json": _sz(CERTS / "five_k30_n0_5.kissat.sat.json"),
            "k30_native": _sz(CERTS / "five_k30_n0_5.sat.json"),
            "k30_drat": _sz(CERTS / "five_k30_n0_5.native.drat"),
            "k30_trim": _sz(CERTS / "five_k30_n0_5.native.drat-trim.log"),
            "global_cnf": _sz(CERTS / "n1_k19_star5_no21_no13.cnf"),
            "global_kissat_json": _sz(CERTS / "n1_k19_star5_no21_no13.kissat.sat.json"),
            "global_native": _sz(CERTS / "n1_k19_star5_no21_no13.sat.json"),
            "global_drat": _sz(CERTS / "n1_k19_star5_no21_no13.native.drat"),
            "code41": _sz(CERTS / "code41.json"),
        },
        "q7": {
            "k30_drat": _sz(Q7C / "five_k30_n0_5.native.drat"),
            "k30_sat": _sz(Q7C / "five_k30_n0_5.sat.json"),
            "k30_trim": _sz(Q7C / "five_k30_n0_5.native.drat-trim.log"),
            "global_drat": _sz(Q7C / "n1_k19_star5.native.drat"),
            "global_sat": _sz(Q7C / "n1_k19_star5.sat.json"),
        },
        "running": {
            "q7_k30_cadical": cadical_running(Q7C / "five_k30_n0_5.cnf"),
            "q7_global_cadical": cadical_running(Q7C / "n1_k19_star5.cnf"),
            "q8_k30_kissat": kissat_running(CERTS / "five_k30_n0_5.cnf"),
            "q8_global_kissat": kissat_running(CERTS / "n1_k19_star5_no21_no13.cnf"),
            "q8_global_cadical": cadical_running(CERTS / "n1_k19_star5_no21_no13.cnf"),
        },
    }
    (CERTS / "hunt_status.json").write_text(json.dumps(rec, indent=2) + "\n")
    return rec


def read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def adopt_k30_from_q7() -> None:
    """Copy a finished q7 k=30 proof and run Heule drat-trim only.

    Do not re-invoke CaDiCaL: native_sat.py --proof would overwrite the DRAT.
    """
    from native_sat import run_drat

    src_cnf = Q7C / "five_k30_n0_5.cnf"
    src_proof = Q7C / "five_k30_n0_5.native.drat"
    src_sat = Q7C / "five_k30_n0_5.sat.json"
    dst_proof = CERTS / "five_k30_n0_5.native.drat"
    dst_cnf = CERTS / "five_k30_n0_5.cnf"
    if not src_proof.is_file():
        log("adopt k30: q7 DRAT missing")
        return
    if cadical_running(src_cnf):
        return
    sat = read_json(src_sat)
    if sat is None:
        log("adopt k30: waiting for q7 sat.json")
        return
    if sat.get("sat") is True:
        if not (CERTS / "code41.json").is_file():
            log("adopt k30: q7 cadical SAT — decode in q8")
            subprocess.check_call(
                [str(PY), "-c",
                 "from five_star_sat import decode_if_sat, write_code41; "
                 "from cnfutil import load_graph; "
                 "G=load_graph(); d=decode_if_sat(G); "
                 "assert d; write_code41(G['extras'], G['D'], d[0], d[1], "
                 "'q8 type-(0,5) leftover SAT', "
                 "__import__('pathlib').Path('certs/code41.json'))"],
                cwd=str(HERE),
            )
        return
    if sat.get("sat") is not False:
        log(f"adopt k30: q7 sat.json sat={sat.get('sat')}")
        return
    tlog = CERTS / "five_k30_n0_5.native.drat-trim.log"
    if tlog.is_file() and "s VERIFIED" in tlog.read_text():
        return
    if n_busy_solvers() >= 4:
        log("adopt k30: cores busy, defer drat-trim")
        return
    log(f"adopt k30: copy DRAT {src_proof.stat().st_size} bytes")
    shutil.copy2(src_proof, dst_proof)
    shutil.copy2(src_cnf, dst_cnf)
    if src_sat.is_file():
        shutil.copy2(src_sat, CERTS / "five_k30_n0_5.q7sat.json")
    log("adopt k30: start drat-trim (no re-solve)")
    rec = run_drat(dst_cnf, dst_proof, tlog)
    out = {
        "cnf": str(dst_cnf),
        "solver": "cadical-3.0.1",
        "sat": False,
        "adopted_from": "q7",
        "drat": dst_proof.name,
        "drat_bytes": dst_proof.stat().st_size,
        "drat_trim": rec,
        "cadical": sat.get("cadical"),
    }
    (CERTS / "five_k30_n0_5.sat.json").write_text(json.dumps(out, indent=2) + "\n")
    log(f"adopt k30: trim {rec}")


def start_q8_global_cadical() -> None:
    cnf = CERTS / "n1_k19_star5_no21_no13.cnf"
    if cadical_running(cnf) or kissat_running(cnf):
        return
    if (CERTS / "n1_k19_star5_no21_no13.sat.json").is_file():
        return
    if n_busy_solvers() >= 4:
        log("q8 global cadical: cores busy")
        return
    log("start q8 global cadical + DRAT")
    env = os.environ.copy()
    subprocess.Popen(
        [str(PY), str(HERE / "native_sat.py"),
         str(cnf), "--proof", "--trim",
         "--json-out", str(CERTS / "n1_k19_star5_no21_no13.sat.json")],
        cwd=str(HERE),
        env=env,
        stdout=open(CERTS / "n1_k19_star5_no21_no13.watch.out", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def start_leftover_k30_bb() -> None:
    flag = CERTS / "leftover_k30_bb.started"
    if flag.is_file():
        return
    if n_busy_solvers() >= 4:
        return
    bin_path = HERE / "leftover_k30"
    if not bin_path.is_file():
        subprocess.check_call(["gcc", "-O3", "-std=c11", "leftover_k30.c",
                               "-o", "leftover_k30", "-lm"], cwd=str(HERE))
    log("start leftover_k30 B&B 20G five_mode 3")
    flag.write_text("started\n")
    subprocess.Popen(
        [str(bin_path), "20", "20000000000", "3"],
        cwd=str(HERE),
        stdout=open(HERE / "leftover_k30.json", "w"),
        stderr=open(CERTS / "leftover_k30.err", "w"),
        start_new_session=True,
    )


def start_cube_kissat(u: int) -> None:
    cnf = CERTS / f"five_k30_u{u}.cnf"
    out = CERTS / f"five_k30_u{u}.kissat.sat.json"
    if out.is_file() or kissat_running(cnf) or cadical_running(cnf):
        return
    if n_busy_solvers() >= 4:
        return
    if not cnf.is_file():
        subprocess.check_call([str(PY), str(HERE / "cube_k30.py"), "write"])
    log(f"start kissat cube u={u}")
    subprocess.Popen(
        [str(PY), str(HERE / "cube_k30.py"), "solve", "--u", str(u),
         "--solver", "kissat"],
        cwd=str(HERE),
        stdout=open(CERTS / f"five_k30_u{u}.watch.out", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def maybe_decode_kissat() -> None:
    k30 = read_json(CERTS / "five_k30_n0_5.kissat.sat.json")
    if k30 and k30.get("sat") is True and not (CERTS / "code41.json").is_file():
        if not (CERTS / "five_k30_n0_5.decoded").is_file():
            log("k30 kissat SAT — decode")
            subprocess.check_call(
                [str(PY), str(HERE / "five_star_sat.py"), "--solver", "kissat",
                 "--no-proof"],
                cwd=str(HERE),
            )
            (CERTS / "five_k30_n0_5.decoded").write_text("ok\n")
    glob = read_json(CERTS / "n1_k19_star5_no21_no13.kissat.sat.json")
    if glob and glob.get("sat") is True and not (CERTS / "code41.json").is_file():
        if not (CERTS / "global.decoded").is_file():
            log("global kissat SAT — decode")
            subprocess.check_call(
                [str(PY), str(HERE / "leftover_sat.py"), "--solver", "kissat",
                 "--no-proof"],
                cwd=str(HERE),
            )
            (CERTS / "global.decoded").write_text("ok\n")


def step() -> dict:
    rec = snapshot()
    maybe_decode_kissat()

    q7_k30 = rec["running"]["q7_k30_cadical"]
    if not q7_k30 and (Q7C / "five_k30_n0_5.sat.json").is_file():
        adopt_k30_from_q7()

    k30k = read_json(CERTS / "five_k30_n0_5.kissat.sat.json")
    globk = read_json(CERTS / "n1_k19_star5_no21_no13.kissat.sat.json")

    # Stronger global CNF still needs its own cadical DRAT if kissat says unsat.
    if globk and globk.get("sat") is False:
        if not rec["running"]["q8_global_cadical"]:
            start_q8_global_cadical()

    # When a core frees: leftover_k30 B&B, then high-|U| cubes.
    if rec["n_busy"] < 4:
        start_leftover_k30_bb()
    if rec["n_busy"] < 4:
        for u in (30, 29, 28, 19):
            if not (CERTS / f"five_k30_u{u}.kissat.sat.json").is_file():
                start_cube_kissat(u)
                break
    return snapshot()


def main() -> None:
    CERTS.mkdir(exist_ok=True)
    log(f"watch start k30_sha={K30_SHA} pid={os.getpid()}")
    while True:
        rec = step()
        k30b = (rec["q7"]["k30_drat"] or {}).get("bytes", 0)
        gb = (rec["q7"]["global_drat"] or {}).get("bytes", 0)
        log(
            f"busy={rec['n_busy']} q7k30={k30b} q7g={gb} "
            f"run={rec['running']}"
        )
        # stop if both target certificates or a 41-set exist
        if (CERTS / "code41.json").is_file():
            log("code41 present — watcher idle")
        k30done = (CERTS / "five_k30_n0_5.sat.json").is_file()
        gdone = (CERTS / "n1_k19_star5_no21_no13.sat.json").is_file()
        if k30done and gdone:
            log("both q8 SAT json present — watcher done")
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
