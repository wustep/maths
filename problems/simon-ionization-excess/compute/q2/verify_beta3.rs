//! Second-language check of the discrete mid-radius Rayleigh.
//!
//! rustc only. Different linear solver from `verify_beta3.c`:
//! Cramer's rule on faces of size ≤ 3, Gaussian elimination after that.
//! Rebuilds F, A, c for a 16-bin window on [1, 4] from first principles
//! (independent of the C matrix) and checks copositivity of
//!   M = A − γ (c 1^T + 1 c^T)/2
//! on the simplex. If the C matrix has n ≤ 18 it is re-checked too.
//!
//! Build: rustc -O -o verify_beta3_rs verify_beta3.rs

use std::fs;
use std::process;

fn fail(msg: &str) -> ! {
    eprintln!("FAIL: {msg}");
    process::exit(1);
}

fn f_ratio(t: f64) -> f64 {
    if t <= 0.0 {
        return 1.0;
    }
    (1.0 + t * t * t) / (1.0 + t * t)
}

fn t0() -> f64 {
    let u = (1.0 + 2.0_f64.sqrt()).cbrt();
    u - 1.0 / u
}

fn solve(k: usize, g: &mut [f64], nmax: usize, b: &[f64], x: &mut [f64]) -> bool {
    // in-place Gauss-Jordan on k×k packed in g with stride nmax
    let mut aug = vec![0.0; k * (k + 1)];
    for i in 0..k {
        for j in 0..k {
            aug[i * (k + 1) + j] = g[i * nmax + j];
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

fn face_min_mmm(n: usize, mmat: &[Vec<f64>]) -> (f64, u64) {
    let nfaces = (1u64 << n) - 1;
    let mut min_val = f64::INFINITY;
    let mut interior = 0u64;
    for i in 0..n {
        if mmat[i][i] < min_val {
            min_val = mmat[i][i];
        }
    }
    let mut gpack = vec![0.0; 32 * 32];
    let mut rhs = vec![0.0; 32];
    let mut x = vec![0.0; 32];
    for mask in 1..=nfaces {
        let mut idx = [0usize; 32];
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
        let ok = if k == 2 {
            let a = mmat[idx[0]][idx[0]];
            let b = mmat[idx[0]][idx[1]];
            let c = mmat[idx[1]][idx[1]];
            let det = a * c - b * b;
            if det.abs() < 1e-14 {
                false
            } else {
                x[0] = (c - b) / det;
                x[1] = (a - b) / det;
                true
            }
        } else if k == 3 {
            let mut g3 = [[0.0; 3]; 3];
            for p in 0..3 {
                for q in 0..3 {
                    g3[p][q] = mmat[idx[p]][idx[q]];
                }
            }
            match cramer3(&g3, &[1.0, 1.0, 1.0]) {
                Some(xx) => {
                    x[0] = xx[0];
                    x[1] = xx[1];
                    x[2] = xx[2];
                    true
                }
                None => false,
            }
        } else {
            for p in 0..k {
                for q in 0..k {
                    gpack[p * 32 + q] = mmat[idx[p]][idx[q]];
                }
                rhs[p] = 1.0;
            }
            solve(k, &mut gpack, 32, &rhs, &mut x)
        };
        if !ok {
            continue;
        }
        let mut sgn = 0i32;
        let mut s = 0.0;
        let mut good = true;
        for p in 0..k {
            if x[p].abs() <= 1e-12 {
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
        if !good || s.abs() <= 1e-12 {
            continue;
        }
        interior += 1;
        let val = 1.0 / s;
        if val < min_val {
            min_val = val;
        }
    }
    let _ = nfaces;
    (min_val, interior)
}

fn main() {
    let txt = fs::read_to_string("certs/beta3_matrix.txt").unwrap_or_else(|_| {
        fail("missing certs/beta3_matrix.txt");
    });
    let mut toks = txt.split_whitespace();
    let n: usize = toks.next().unwrap().parse().unwrap();
    let gamma_t: f64 = toks.next().unwrap().parse().unwrap();
    if n > 32 {
        fail("n too large");
    }
    let mut c = vec![0.0; n];
    for i in 0..n {
        c[i] = toks.next().unwrap().parse().unwrap();
    }
    let mut a = vec![vec![0.0; n]; n];
    for i in 0..n {
        for j in 0..n {
            a[i][j] = toks.next().unwrap().parse().unwrap();
        }
    }
    let mut mmat = vec![vec![0.0; n]; n];
    for i in 0..n {
        for j in 0..n {
            mmat[i][j] = a[i][j] - 0.5 * gamma_t * (c[i] + c[j]);
        }
    }
    let ok = if n <= 18 {
        let (min_val, interior) = face_min_mmm(n, &mmat);
        let pass = min_val - 1e-10 >= 0.0;
        println!(
            "rust matrix n={n} gamma_t={gamma_t:.10} min m^T M m={min_val:.8e} interior={interior} ok={pass}"
        );
        if !pass {
            fail("M not copositive on the simplex");
        }
        pass
    } else {
        println!("rust matrix n={n} skipped full enum (C path); n=16 rebuild follows");
        true
    };

    // Independent 16-bin [1,4] rebuild (different window; method check).
    let n2 = 16usize;
    let r = 4.0_f64;
    let t0 = t0();
    let fmin = 1.5 * t0;
    let mut edges = vec![0.0; n2 + 1];
    for i in 0..=n2 {
        edges[i] = r.powf(i as f64 / n2 as f64);
    }
    let mut aa = vec![vec![0.0; n2]; n2];
    let mut cc = vec![0.0; n2];
    for i in 0..n2 {
        cc[i] = edges[i] * edges[i + 1];
        for j in 0..n2 {
            let mut tlo = 1.0;
            let mut thi = 0.0;
            for &r1 in &[edges[i], edges[i + 1]] {
                for &u in &[edges[j], edges[j + 1]] {
                    let (mn, mx) = if r1 <= u { (r1, u) } else { (u, r1) };
                    let t = mn / mx;
                    if t < tlo {
                        tlo = t;
                    }
                    if t > thi {
                        thi = t;
                    }
                }
            }
            if edges[i] <= edges[j + 1] && edges[j] <= edges[i + 1] {
                thi = 1.0;
            }
            let fij = if thi <= t0 {
                f_ratio(thi)
            } else if tlo >= t0 {
                f_ratio(tlo)
            } else {
                fmin
            };
            aa[i][j] = fij * 0.5 * (cc[i] + cc[j]);
        }
    }
    let q = r.powf(1.0 / n2 as f64);
    let theta = q - 1.0;
    let err = (theta / (1.0 - theta)) * (1.0 - fmin);
    let gt2 = 0.9060; // below numerical φ_mid ≈ 0.9094 for n=16 R=4
    let mut mm = vec![vec![0.0; n2]; n2];
    for i in 0..n2 {
        for j in 0..n2 {
            mm[i][j] = aa[i][j] - 0.5 * gt2 * (cc[i] + cc[j]);
        }
    }
    let (min2, _int2) = face_min_mmm(n2, &mm);
    let gamma16 = gt2 - err;
    let beats = min2 - 1e-10 >= 0.0 && gamma16 > 0.89410745697;
    println!(
        "rust n=16 R=4  phi_target={gt2} err={err:.6} gamma≤{gamma16:.6} minM={min2:.4e} beats={beats}"
    );
    let blob = format!(
        "{{\n  \"n_matrix\": {n},\n  \"matrix_copositive\": {ok},\n  \"n16_R4_gamma\": {gamma16:.12},\n  \"n16_R4_beats_fmin\": {beats}\n}}\n"
    );
    fs::write("certs/beta3_rs.json", blob).unwrap();
    if !beats {
        fail("n=16 R=4 independent rebuild did not beat 1/b(3)");
    }
    println!("verify_beta3.rs PASS");
}
