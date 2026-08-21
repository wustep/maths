#!/usr/bin/env python3
"""Independent log-energy verifier on S^2.

E(X) = sum_{i<j} log(1 / |x_i - x_j|)
     = - (1/2) sum_{i<j} log |x_i - x_j|^2

Points are projected onto the unit sphere before the sum. This file is the
from-scratch checker: it does not import the optimizer.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np


def project_to_sphere(points: np.ndarray) -> np.ndarray:
    pts = np.asarray(points, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] != 3:
        raise ValueError(f"expected (N,3) points, got {pts.shape}")
    norms = np.linalg.norm(pts, axis=1)
    if np.any(norms <= 0):
        raise ValueError("zero vector cannot be projected to S^2")
    return pts / norms[:, None]


def pairwise_sqdist(pts: np.ndarray) -> np.ndarray:
    """Strict upper-triangle squared Euclidean distances."""
    grams = pts @ pts.T
    # |xi-xj|^2 = 2(1 - <xi,xj>) on the unit sphere
    sq = np.clip(2.0 * (1.0 - grams), 0.0, 4.0)
    i, j = np.triu_indices(len(pts), k=1)
    return sq[i, j]


def log_energy(points, project: bool = True) -> float:
    pts = project_to_sphere(points) if project else np.asarray(points, dtype=np.float64)
    sq = pairwise_sqdist(pts)
    if np.any(sq <= 0):
        raise ValueError("coincident points: log-energy is +inf")
    return float(-0.5 * np.log(sq).sum())


def load_points(path: Path) -> np.ndarray:
    text = path.read_text()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("points") or data.get("p")
        return np.asarray(data, dtype=np.float64)
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.replace(",", " ")
        parts = [p for p in line.split() if p]
        if len(parts) < 3:
            continue
        rows.append([float(parts[0]), float(parts[1]), float(parts[2])])
    return np.asarray(rows, dtype=np.float64)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", help="JSON or whitespace xyz file")
    ap.add_argument("--no-project", action="store_true")
    args = ap.parse_args(argv)
    if not args.path:
        ap.print_help()
        return 2
    pts = load_points(Path(args.path))
    e = log_energy(pts, project=not args.no_project)
    print(f"N={len(pts)}  E={e:.16f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
