//! Second-language check of HPS b(s). rustc only; no cargo.
//!
//! Different algorithm from `verify_b3.c`: evaluate
//!   b(s) = max_{0 <= t <= 1} (1 + t^{s-1}) / (1 + t^s)
//! by ternary search and by a dense grid, then compare to the closed forms
//!   b(2) = (sqrt(2)+1)/2
//!   b(3) = (2/3) * cbrt(1+sqrt(2)) / ((1+sqrt(2))^{2/3} - 1)
//! Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, (2.7) and Prop. 2.4–2.5.
//!
//! Not a new bound.

use std::fs;
use std::process;

fn fail(msg: &str) -> ! {
    eprintln!("FAIL: {msg}");
    process::exit(1);
}

fn ratio(s: f64, t: f64) -> f64 {
    if t == 0.0 {
        return 1.0;
    }
    (1.0 + t.powf(s - 1.0)) / (1.0 + t.powf(s))
}

fn max_ratio_ternary(s: f64) -> (f64, f64) {
    let mut lo = 0.0;
    let mut hi = 1.0;
    for _ in 0..400 {
        let m1 = lo + (hi - lo) / 3.0;
        let m2 = hi - (hi - lo) / 3.0;
        if ratio(s, m1) < ratio(s, m2) {
            lo = m1;
        } else {
            hi = m2;
        }
    }
    let t = 0.5 * (lo + hi);
    (t, ratio(s, t))
}

fn max_ratio_grid(s: f64, n: usize) -> (f64, f64) {
    let mut best_t = 0.0;
    let mut best = f64::NEG_INFINITY;
    for i in 0..=n {
        let t = i as f64 / n as f64;
        let v = ratio(s, t);
        if v > best {
            best = v;
            best_t = t;
        }
    }
    let span = 4.0 / n as f64;
    let lo = (best_t - span).max(0.0);
    let hi = (best_t + span).min(1.0);
    let refine = 200_000;
    for i in 0..=refine {
        let t = lo + (hi - lo) * (i as f64 / refine as f64);
        let v = ratio(s, t);
        if v > best {
            best = v;
            best_t = t;
        }
    }
    (best_t, best)
}

fn b2_closed() -> f64 {
    0.5 * (2.0_f64.sqrt() + 1.0)
}

fn b3_closed() -> f64 {
    let one_plus = 1.0 + 2.0_f64.sqrt();
    (2.0 / 3.0) * one_plus.cbrt() / (one_plus.powf(2.0 / 3.0) - 1.0)
}

fn in_open(x: f64, lo: f64, hi: f64) -> bool {
    x > lo && x < hi
}

fn main() {
    let _ = fs::create_dir_all("certs");

    let b2_cf = b2_closed();
    let b3_cf = b3_closed();
    let (t2_ter, b2_ter) = max_ratio_ternary(2.0);
    let (t3_ter, b3_ter) = max_ratio_ternary(3.0);
    let (t2_grid, b2_grid) = max_ratio_grid(2.0, 500_000);
    let (t3_grid, b3_grid) = max_ratio_grid(3.0, 500_000);

    println!("verify_b3.rs  ternary+grid max of (1+t^{{s-1}})/(1+t^s)");
    println!("not a new bound");
    println!("b2_closed  = {:.21}", b2_cf);
    println!("b2_ternary = {:.21}  t*={:.18}", b2_ter, t2_ter);
    println!("b2_grid    = {:.21}  t*={:.18}", b2_grid, t2_grid);
    println!("b3_closed  = {:.21}", b3_cf);
    println!("b3_ternary = {:.21}  t*={:.18}", b3_ter, t3_ter);
    println!("b3_grid    = {:.21}  t*={:.18}", b3_grid, t3_grid);

    for (label, val) in [
        ("b3_closed", b3_cf),
        ("b3_ternary", b3_ter),
        ("b3_grid", b3_grid),
    ] {
        if !in_open(val, 1.1184, 1.1185) {
            fail(&format!("{label} = {val:.21} not in (1.1184, 1.1185)"));
        }
    }
    for (label, val) in [
        ("b2_closed", b2_cf),
        ("b2_ternary", b2_ter),
        ("b2_grid", b2_grid),
    ] {
        if !in_open(val, 1.2071, 1.2072) {
            fail(&format!("{label} = {val:.21} not in (1.2071, 1.2072)"));
        }
    }
    println!("assert 1.1184 < b3 < 1.1185  PASS (closed, ternary, grid)");
    println!("assert 1.2071 < b2 < 1.2072  PASS (closed, ternary, grid)");

    let tol = 5e-14;
    if (b3_ter - b3_cf).abs() > tol {
        fail(&format!(
            "ternary b3 disagrees with closed form: {:.21} vs {:.21}",
            b3_ter, b3_cf
        ));
    }
    if (b3_grid - b3_cf).abs() > 5e-12 {
        fail(&format!(
            "grid b3 disagrees with closed form: {:.21} vs {:.21}",
            b3_grid, b3_cf
        ));
    }
    if (b2_ter - b2_cf).abs() > tol {
        fail(&format!(
            "ternary b2 disagrees with closed form: {:.21} vs {:.21}",
            b2_ter, b2_cf
        ));
    }
    if (b2_grid - b2_cf).abs() > 5e-12 {
        fail(&format!(
            "grid b2 disagrees with closed form: {:.21} vs {:.21}",
            b2_grid, b2_cf
        ));
    }
    println!("ternary/grid vs closed form  PASS");

    let json = format!(
        "{{\n  \"algorithm\": \"ternary+grid max of (1+t^{{s-1}})/(1+t^s)\",\n  \"b2_closed\": \"{:.21}\",\n  \"b3_closed\": \"{:.21}\",\n  \"b2_ternary\": \"{:.21}\",\n  \"b3_ternary\": \"{:.21}\",\n  \"b2_grid\": \"{:.21}\",\n  \"b3_grid\": \"{:.21}\",\n  \"t2_ternary\": \"{:.18}\",\n  \"t3_ternary\": \"{:.18}\"\n}}\n",
        b2_cf, b3_cf, b2_ter, b3_ter, b2_grid, b3_grid, t2_ter, t3_ter
    );
    fs::write("certs/b3_rs.json", json).unwrap_or_else(|e| fail(&format!("write b3_rs.json: {e}")));
    println!("wrote certs/b3_rs.json");
    println!("verify_b3.rs PASS");
}
