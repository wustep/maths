#!/bin/sh
# Recompute certificates. Fourier and homometric n<=22 are cheap.
# The exact Z-census through n=18 is ~10 minutes; n=20 is ~40 minutes.
set -e
cd "$(dirname "$0")"
python3 fourier_theta.py
python3 verify_fourier.py
python3 closed_forms.py > closed_forms.txt
python3 count_01_factors.py
python3 verify_census.py
echo "optional: gcc -O3 -o homometric homometric.c && ./homometric 1 22"
echo "optional: python3 census_irred.py 1 18"
