// rustc -O -o verify_aspect_rs verify_aspect.rs
use std::fs::File;
use std::io::Write;

fn g(r: f64, u: f64) -> f64 {
    let m = if r >= u { r } else { u };
    (r * r * r + u * u * u) / (2.0 * m)
}

fn main() {
    let r = 10.0;
    let cut = 10.0 / 11.0;
    let mut empty_bad = 0u32;
    let mut nonempty_bad = 0u32;
    for qn in 890..1000 {
        let q = qn as f64 / 1000.0;
        let lo = ((1.0 - q) / q) * (r * r);
        let hi = q / (1.0 - q);
        if q <= cut + 1e-15 {
            if lo < hi - 1e-12 {
                empty_bad += 1;
            }
        } else if lo >= hi + 1e-12 {
            nonempty_bad += 1;
        }
    }
    assert_eq!(empty_bad, 0);
    assert_eq!(nonempty_bad, 0);

    let r1 = 1.0;
    let r2 = r;
    let mut m1 = 0.5 / (r1 * r1);
    let mut m2 = 0.5 / (r2 * r2);
    let s = m1 + m2;
    m1 /= s;
    m2 /= s;
    let d = m1 * r1 * r1 + m2 * r2 * r2;
    let mm1 = m1 / r1 + m2 / r2;
    let m3 = m1 * r1 * r1 * r1 + m2 * r2 * r2 * r2;
    let v1 = m1 * g(r1, r1) + m2 * g(r1, r2);
    let v2 = m1 * g(r2, r1) + m2 * g(r2, r2);
    let q = (m1 * v1 + m2 * v2) / d;
    assert!((v1 - (d / 2.0 + mm1 / 2.0)).abs() < 1e-12);
    assert!((v2 - (r2 * r2 / 2.0 + m3 / (2.0 * r2))).abs() < 1e-12);
    assert!(q > cut);

    let mut f = File::create("certs/aspect_rs.json").expect("write");
    writeln!(
        f,
        "{{\"empty_bad\":{empty_bad},\"nonempty_bad\":{nonempty_bad},\"two_atom_Q\":{q},\"cut\":{cut},\"ok\":true}}"
    )
    .unwrap();
    println!("verify_aspect.rs PASS  two-atom Q={q:.6}  cut={cut:.6}");
}
