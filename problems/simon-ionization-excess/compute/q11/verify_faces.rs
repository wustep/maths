//! Re-enumerate the stored winning matrix with a different solver.
//! Cramer's rule on 3-faces; Gauss-Jordan otherwise. rustc only.
//!
//! rustc -O -o verify_faces_rs verify_faces.rs
//! ./verify_faces_rs certs/beta3_mid_R10_n24_t0p9080.txt certs/faces_rs.txt

use std::env;
use std::fs;
use std::process;

const NMAX: usize = 36;
const EPS: f64 = 1e-12;
const MARGIN: f64 = 1e-10;

fn fail(msg: &str) -> ! {
    eprintln!("FAIL: {msg}");
    process::exit(1);
}

fn solve(k: usize, g: &[[f64; NMAX]; NMAX], b: &[f64], x: &mut [f64]) -> bool {
    let mut aug = vec![0.0; k * (k + 1)];
    for i in 0..k {
        for j in 0..k {
            aug[i * (k + 1) + j] = g[i][j];
        }
        aug[i * (k + 1) + k] = b[i];
    }
    for p in 0..k {
        let mut piv = p;
        let mut best = aug[p * (k + 1) + p].abs();
        for i in (p + 1)..k {
            let v = aug[i * (k + 1) + p].abs();
            if v > best {
                best = v;
                piv = i;
            }
        }
        if best < 1e-14 {
            return false;
        }
        if piv != p {
            for j in p..=k {
                let tmp = aug[p * (k + 1) + j];
                aug[p * (k + 1) + j] = aug[piv * (k + 1) + j];
                aug[piv * (k + 1) + j] = tmp;
            }
        }
        let diag = aug[p * (k + 1) + p];
        for j in p..=k {
            aug[p * (k + 1) + j] /= diag;
        }
        for i in 0..k {
            if i == p {
                continue;
            }
            let f = aug[i * (k + 1) + p];
            for j in p..=k {
                aug[i * (k + 1) + j] -= f * aug[p * (k + 1) + j];
            }
        }
    }
    for i in 0..k {
        x[i] = aug[i * (k + 1) + k];
    }
    true
}

fn cramer3(g: &[[f64; 3]; 3], b: &[f64; 3]) -> Option<[f64; 3]> {
    let det = g[0][0] * (g[1][1] * g[2][2] - g[1][2] * g[2][1])
        - g[0][1] * (g[1][0] * g[2][2] - g[1][2] * g[2][0])
        + g[0][2] * (g[1][0] * g[2][1] - g[1][1] * g[2][0]);
    if det.abs() < 1e-14 {
        return None;
    }
    let mut x = [0.0; 3];
    for col in 0..3 {
        let mut h = *g;
        for i in 0..3 {
            h[i][col] = b[i];
        }
        let d = h[0][0] * (h[1][1] * h[2][2] - h[1][2] * h[2][1])
            - h[0][1] * (h[1][0] * h[2][2] - h[1][2] * h[2][0])
            + h[0][2] * (h[1][0] * h[2][1] - h[1][1] * h[2][0]);
        x[col] = d / det;
    }
    Some(x)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mat_path = if args.len() > 1 {
        args[1].clone()
    } else {
        "certs/beta3_mid_R10_n24_t0p9080.txt".to_string()
    };
    let out_path = if args.len() > 2 {
        args[2].clone()
    } else {
        "certs/faces_rs.txt".to_string()
    };
    let txt = fs::read_to_string(&mat_path).unwrap_or_else(|_| fail("cannot read matrix"));
    let mut toks = txt.split_whitespace();
    let n: usize = toks.next().unwrap().parse().unwrap();
    let gamma_t: f64 = toks.next().unwrap().parse().unwrap();
    if n > NMAX {
        fail("n too large");
    }
    let mut c = [0.0; NMAX];
    for i in 0..n {
        c[i] = toks.next().unwrap().parse().unwrap();
    }
    let mut a = [[0.0; NMAX]; NMAX];
    let mut mmat = [[0.0; NMAX]; NMAX];
    for i in 0..n {
        for j in 0..n {
            a[i][j] = toks.next().unwrap().parse().unwrap();
            mmat[i][j] = a[i][j] - 0.5 * gamma_t * (c[i] + c[j]);
        }
    }

    let nfaces = (1u64 << n) - 1;
    let mut min_val = f64::INFINITY;
    let mut interior = 0u64;
    let mut singular = 0u64;
    for i in 0..n {
        if mmat[i][i] < min_val {
            min_val = mmat[i][i];
        }
    }
    let mut rhs = [0.0; NMAX];
    let mut x = [0.0; NMAX];
    for mask in 1..=nfaces {
        if mask & ((1u64 << 22) - 1) == 0 {
            eprintln!("  ... mask {mask} / {nfaces}  minM={min_val:.4e}");
        }
        let mut idx = [0usize; NMAX];
        let mut k = 0usize;
        for b in 0..n {
            if mask & (1u64 << b) != 0 {
                idx[k] = b;
                k += 1;
            }
        }
        if k <= 1 {
            continue;
        }
        let mut g = [[0.0; NMAX]; NMAX];
        for p in 0..k {
            for q in 0..k {
                g[p][q] = mmat[idx[p]][idx[q]];
            }
            rhs[p] = 1.0;
        }
        if !solve(k, &g, &rhs, &mut x) {
            singular += 1;
            continue;
        }
        if k == 3 {
            let mut g3 = [[0.0; 3]; 3];
            for p in 0..3 {
                for q in 0..3 {
                    g3[p][q] = mmat[idx[p]][idx[q]];
                }
            }
            if let Some(xx) = cramer3(&g3, &[1.0, 1.0, 1.0]) {
                for p in 0..3 {
                    if (xx[p] - x[p]).abs() > 1e-8 {
                        fail("Cramer vs Gauss disagreement");
                    }
                }
            }
        }
        let mut rmax: f64 = 0.0;
        for p in 0..k {
            let mut acc = 0.0;
            for q in 0..k {
                acc += mmat[idx[p]][idx[q]] * x[q];
            }
            rmax = rmax.max((acc - 1.0).abs());
        }
        if rmax > 1e-8 {
            singular += 1;
            continue;
        }
        let mut sgn = 0i32;
        let mut s = 0.0;
        let mut good = true;
        for p in 0..k {
            if x[p].abs() <= EPS {
                good = false;
                break;
            }
            let sp = if x[p] > 0.0 { 1 } else { -1 };
            if sgn == 0 {
                sgn = sp;
            } else if sp != sgn {
                good = false;
                break;
            }
            s += x[p];
        }
        if !good || s.abs() <= EPS {
            continue;
        }
        interior += 1;
        let val = 1.0 / s;
        if val < min_val {
            min_val = val;
        }
    }
    let min_safe = min_val - MARGIN;
    let ok = min_safe >= 0.0;
    let out = format!(
        "n {n}\ngamma_target {gamma_t:.16e}\nn_faces {nfaces}\ninterior_critical {interior}\nsingular_or_illconditioned {singular}\nmin_mMm {min_val:.16e}\nmin_mMm_safe {min_safe:.16e}\ncopositive {}\n",
        if ok { 1 } else { 0 }
    );
    fs::write(&out_path, out).unwrap();
    println!(
        "n={n} target={gamma_t:.10} minM={min_val:.8e} safe={min_safe:.8e} interior={interior} singular={singular}"
    );
    if !ok {
        fail("M not copositive");
    }
    println!("verify_faces.rs PASS");
}
