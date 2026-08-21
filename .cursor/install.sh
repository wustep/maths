#!/usr/bin/env bash
#
# Idempotent bootstrap for the maths notebook Cloud Agent environment.
#
# Base image already provides: python3.12, numpy, gcc/g++/make/cmake, and the
# Rust toolchain (rustc/cargo). This script adds the pieces the repo's compute
# and formal pipelines need on top of that:
#
#   * python3-venv (ensurepip) so the self-bootstrapping compute/run_all.sh
#     scripts can create their own throwaway virtualenvs
#   * the scientific Python stack the scripts import directly (scipy, sympy,
#     matplotlib, python-sat)
#   * elan + the Lean toolchain pinned by ./lean-toolchain (Lean 4.32.0)
#
# Safe to run repeatedly.
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

echo "==> system packages (python venv support)"
if ! python3 -c 'import ensurepip' >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv python3-venv
fi

echo "==> python packages"
# Installing python3-venv above pulls in Debian's PEP 668 EXTERNALLY-MANAGED
# marker, so a plain `pip --user` is refused. --break-system-packages only
# lifts that guard; packages still land in ~/.local, isolated from the system
# interpreter, and `python3` keeps resolving them via the user site.
python3 -m pip install --user --break-system-packages --no-input \
  -r "$ROOT/.cursor/requirements.txt"

echo "==> lean toolchain (elan)"
LEAN_TOOLCHAIN="$(tr -d '[:space:]' < "$ROOT/lean-toolchain")"
if ! command -v elan >/dev/null 2>&1 && [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl --proto '=https' --tlsv1.2 -sSf https://elan.lean-lang.org/elan-init.sh \
    -o /tmp/elan-init.sh
  bash /tmp/elan-init.sh -y --default-toolchain "$LEAN_TOOLCHAIN"
fi
export PATH="$HOME/.elan/bin:$PATH"
# Materialize the pinned toolchain so `lean`/`lake` are ready without a
# first-use download later. `elan toolchain install` errors if it already
# exists, so only install when missing.
if ! elan toolchain list | grep -qx "$LEAN_TOOLCHAIN"; then
  elan toolchain install "$LEAN_TOOLCHAIN"
fi

echo "==> versions"
python3 --version
rustc --version
lean --version

echo "install.sh: done"
