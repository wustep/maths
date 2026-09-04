//! Independent Rust replay of the q14 finite-range tax.
//!
//! Reads the frozen q13 matrix and Gray summary, reconstructs the stored
//! F range, and checks the analytic geometric-bin envelope with explicit
//! f64 safety pads.  No Python modules or shared helpers.

use std::fs;

fn kernel(t: f64) -> f64 {
    (1.0 + t * t * t) / (1.0 + t * t)
}

fn face_value(text: &str, wanted: &str) -> String {
    for line in text.lines() {
        let mut fields = line.split_whitespace();
        if fields.next() == Some(wanted) {
            return fields.next().expect("missing face value").to_string();
        }
    }
    panic!("missing face key {}", wanted);
}

fn main() {
    let base = "../q13/certs";
    let matrix_path = format!("{base}/beta3_mid_R10_n37_t0p9119.txt");
    let faces_path = format!("{base}/beta3_mid_faces_R10_n37_t0p9119.txt");
    let matrix = fs::read_to_string(&matrix_path).expect("read q13 matrix");
    let faces = fs::read_to_string(&faces_path).expect("read q13 faces");
    let mut tok = matrix.split_whitespace();
    let n: usize = tok.next().unwrap().parse().unwrap();
    let target: f64 = tok.next().unwrap().parse().unwrap();
    assert_eq!(n, 37);
    assert!((target - 0.9119).abs() < 1e-15);
    let mut c = Vec::with_capacity(n);
    for _ in 0..n {
        c.push(tok.next().unwrap().parse::<f64>().unwrap());
    }
    let mut a = Vec::with_capacity(n * n);
    for _ in 0..(n * n) {
        a.push(tok.next().unwrap().parse::<f64>().unwrap());
    }
    assert!(tok.next().is_none());

    let mut stored_min = f64::INFINITY;
    let mut stored_max = f64::NEG_INFINITY;
    for i in 0..n {
        for j in 0..n {
            let fij = 2.0 * a[i * n + j] / (c[i] + c[j]);
            stored_min = stored_min.min(fij);
            stored_max = stored_max.max(fij);
        }
    }

    let total = (1u64 << n) - 1;
    let face_ok = face_value(&faces, "n").parse::<usize>().unwrap() == n
        && (face_value(&faces, "gamma_target").parse::<f64>().unwrap() - target).abs() < 1e-15
        && face_value(&faces, "n_faces").parse::<u64>().unwrap() == total
        && face_value(&faces, "gray_i").parse::<u64>().unwrap() == total
        && face_value(&faces, "copositive").parse::<u32>().unwrap() == 1
        && face_value(&faces, "singular_or_illconditioned").parse::<u64>().unwrap() == 0
        && face_value(&faces, "min_mMm_safe").parse::<f64>().unwrap() > 0.0;
    assert!(face_ok);

    let r = 10.0_f64;
    let q = r.powf(1.0 / n as f64);
    let p_hi = (q - 1.0) / (q + 1.0) + 1e-14;
    let u = (1.0 + 2.0_f64.sqrt()).powf(1.0 / 3.0);
    let t_star = u - 1.0 / u;
    let f_min_lo = 1.5 * t_star - 1e-14;
    let t_far = q * q / r;
    let t_near = 1.0 / q;
    let f_far_hi = kernel(t_far) + 1e-14;
    let f_near_hi = kernel(t_near) + 1e-14;
    assert!(t_far < t_star && t_star < t_near);
    assert!(f_near_hi < f_far_hi);
    assert!(stored_min + 1e-12 >= f_min_lo);
    assert!(stored_max <= f_far_hi + 1e-12);

    let span_hi = f_far_hi - f_min_lo;
    let matrix_pad = 1e-12;
    let error_hi = p_hi * span_hi + matrix_pad;
    let gamma_lo = target - error_hi;
    let leading_hi = 1.0 / gamma_lo + 1e-14;
    let cut = 10.0 / 11.0;
    assert!(gamma_lo < cut);
    assert!(leading_hi < 1.1002);
    assert!(leading_hi < 1.1006);

    let out = format!(
        concat!(
            "{{\n",
            "  \"implementation\": \"Rust f64 with 1e-14 outward pads\",\n",
            "  \"stored_F_min\": {:.17e},\n",
            "  \"stored_F_max\": {:.17e},\n",
            "  \"analytic_F_max_upper\": {:.17e},\n",
            "  \"span_upper\": {:.17e},\n",
            "  \"error_upper\": {:.17e},\n",
            "  \"matrix_rounding_pad\": {:.17e},\n",
            "  \"beta3_lower\": {:.17e},\n",
            "  \"leading_upper\": {:.17e},\n",
            "  \"cut\": {:.17e},\n",
            "  \"face_certificate_ok\": true,\n",
            "  \"ok\": true\n",
            "}}\n"
        ),
        stored_min, stored_max, f_far_hi, span_hi, error_hi, matrix_pad,
        gamma_lo, leading_hi, cut
    );
    fs::create_dir_all("certs").unwrap();
    fs::write("certs/span_rs.json", out).unwrap();
    println!("stored F range [{stored_min:.12}, {stored_max:.12}]");
    println!("beta3 >= {gamma_lo:.15}, leading <= {leading_hi:.15}");
    println!("verify_span.rs PASS");
}
