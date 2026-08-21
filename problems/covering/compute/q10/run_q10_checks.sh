#!/bin/sh
# Replay for q10: prescribed-automorphism (Kramer-Mesner) search.
# Everything below finishes in a few minutes on one core.
set -e
cd "$(dirname "$0")/../.."
TMP=$(mktemp -d)
gcc -O2 -o "$TMP/os"  compute/q10/orbit_search.c
gcc -O2 -o "$TMP/osg" compute/q10/orbit_search_g.c
gcc -O2 -o "$TMP/osf" compute/q10/orbit_search_f.c

echo "--- sigma tables and centraliser classes rebuild byte-identically ---"
python3 compute/q10/setup.py 30 "$TMP/i30.json"
python3 compute/q10/setup.py 21 "$TMP/i21.json"
cmp "$TMP/i30.json" compute/q10/instance_30.json
cmp "$TMP/i21.json" compute/q10/instance_21.json
for K in r10-30 r10-21 r10-7-c4a r10-7-c4b r10-7-c7 r11-11 r11-17-c3 r11-23 r11-31-c6; do
  (cd compute/q10 && python3 sigma_setup.py "$K" "$TMP/s.txt" "$TMP/c.json")
  cmp "$TMP/s.txt" "compute/q10/sigma_$K.txt"
  cmp "$TMP/c.json" "compute/q10/classes_$K.json"
done

echo "--- encoding control: orbit masks vs the flat syndrome sweep ---"
"$TMP/os"  --kind 30 --selftest 400
"$TMP/os"  --kind 21 --selftest 400
for K in r10-30 r11-11 r11-23; do "$TMP/osg" --sigma "compute/q10/sigma_$K.txt" --selftest 300 | tail -1; done
for K in r10-7-c4a r10-7-c7 r11-17-c3; do "$TMP/osf" --sigma "compute/q10/sigma_$K.txt" --selftest 400 | tail -1; done

echo "--- positive controls: the search does find sigma-invariant coverings ---"
P=$(python3 -c "import json;print(*json.load(open('compute/q10/instance_21.json'))['forced_pairs'][0])")
"$TMP/os" --kind 21 --orbits 9 --pair $P | grep flat-sweep
R=$(python3 -c "import json;print(json.load(open('compute/q10/classes_r11-23.json'))['orbit_class_reps'][0])")
"$TMP/osg" --sigma compute/q10/sigma_r11-23.txt --orbits 4 --force $R | grep flat-sweep

echo "--- r = 10, n = 49: order 7, every fixed-space dimension ---"
python3 - "$TMP" <<'PY'
import json, subprocess, sys
tmp = sys.argv[1]
def run(binary, args, want=3):
    r = subprocess.run([f"{tmp}/{binary}"] + args, capture_output=True, text=True)
    assert r.returncode == want, (args, r.stdout, r.stderr)
    print("   ", " ".join(args[-4:]), "->", r.stdout.strip().splitlines()[-2])
for kind in ("r10-30", "r10-21"):                     # c = 1
    sig = f"compute/q10/sigma_{kind}.txt"
    for pr in json.load(open(f"compute/q10/classes_{kind}.json"))["pair_class_reps"]:
        run("osg", ["--sigma", sig, "--orbits", "7", "--force", str(pr[0]), "--force", str(pr[1])])
for kind in ("r10-7-c4a", "r10-7-c4b"):               # c = 4
    sig = f"compute/q10/sigma_{kind}.txt"
    reps = json.load(open(f"compute/q10/classes_{kind}.json"))["orbit_class_reps"]
    for k, m in ((7, 0), (5, 14)):
        for rep in reps:
            run("osf", ["--sigma", sig, "--orbits", str(k), "--fixed", str(m), "--force", str(rep)])
    fc = subprocess.run(["python3", "fixed_classes.py", kind, "7"], cwd="compute/q10",
                        capture_output=True, text=True).stdout
    for line in fc.strip().splitlines():
        run("osf", ["--sigma", sig, "--orbits", "6", "--fixed", "7",
                    "--fixedset", line.split("#")[0].strip()])
PY
echo "--- c = 7 and the other primes need no search ---"
python3 compute/q10/layer_lemma.py compute/q10/sigma_r10-7-c7.txt 49
python3 compute/q10/prime_orders.py 10 49

echo "--- r = 11: 78, 77, 67, 66 (order 11), 69 (order 23), 68..75 (order 17) ---"
python3 - "$TMP" <<'PY'
import json, subprocess, sys
tmp = sys.argv[1]
def run(binary, args):
    r = subprocess.run([f"{tmp}/{binary}"] + args, capture_output=True, text=True)
    assert r.returncode == 3, (args, r.stdout, r.stderr)
    print("   ", r.stdout.strip().splitlines()[-2])
c11 = json.load(open("compute/q10/classes_r11-11.json"))
s11 = "compute/q10/sigma_r11-11.txt"
for rep in c11["orbit_class_reps"]:
    run("osg", ["--sigma", s11, "--orbits", "7", "--withf", "--force", str(rep)])   # 78
    run("osg", ["--sigma", s11, "--orbits", "6", "--withf", "--force", str(rep)])   # 67
pr = c11["pair_class_reps"][0]
for k in ("7", "6"):                                                                # 77, 66
    run("osg", ["--sigma", s11, "--orbits", k, "--force", str(pr[0]), "--force", str(pr[1])])
r23 = json.load(open("compute/q10/classes_r11-23.json"))["orbit_class_reps"][0]
run("osg", ["--sigma", "compute/q10/sigma_r11-23.txt", "--orbits", "3", "--force", str(r23)])
s17 = "compute/q10/sigma_r11-17-c3.txt"
for rep in json.load(open("compute/q10/classes_r11-17-c3.json"))["orbit_class_reps"]:
    for m in range(8):
        run("osf", ["--sigma", s17, "--orbits", "4", "--fixed", str(m), "--force", str(rep)])
PY
python3 compute/q10/prime_orders.py 11 78 69
echo "q10 checks OK -- every search above returned EXHAUSTED, no 49 and no dent"
