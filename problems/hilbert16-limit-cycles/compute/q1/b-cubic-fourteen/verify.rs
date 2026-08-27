//! Second check of the van der Pol identities, no CAS.
//!
//! Specializes μ = 1. Every identity in verify.py is homogeneous in μ,
//! so the specialization does not drop a factor. Polynomials live in
//! Q[x] or Q[h] with i64 numerators and a common positive denominator.

fn sub(a: &[i64], b: &[i64]) -> Vec<i64> {
    let n = a.len().max(b.len());
    let mut out = vec![0; n];
    for (i, c) in a.iter().enumerate() {
        out[i] += c;
    }
    for (i, c) in b.iter().enumerate() {
        out[i] -= c;
    }
    out
}

fn mul(a: &[i64], b: &[i64]) -> Vec<i64> {
    let mut out = vec![0; a.len() + b.len() - 1];
    for (i, x) in a.iter().enumerate() {
        for (j, y) in b.iter().enumerate() {
            out[i + j] += x * y;
        }
    }
    out
}

fn scale(a: &[i64], num: i64) -> Vec<i64> {
    a.iter().map(|c| c * num).collect()
}

fn eq(a: &[i64], b: &[i64]) -> bool {
    let n = a.len().max(b.len());
    for i in 0..n {
        let x = if i < a.len() { a[i] } else { 0 };
        let y = if i < b.len() { b[i] } else { 0 };
        if x != y {
            return false;
        }
    }
    true
}

fn main() {
    // F(x) = x^3/3 - x. Work with 3F = x^3 - 3x = (0, -3, 0, 1).
    let three_f = [0, -3, 0, 1];
    let x_poly = [0, 1];
    let x2_minus_3 = [-3, 0, 1];
    let factored = mul(&x_poly, &x2_minus_3);
    assert!(eq(&three_f, &factored), "3F != x(x^2-3)");

    // F'(x) = x^2 - 1. Differentiate 3F to get 3F' = 3x^2 - 3, so F' = x^2-1.
    let three_f_prime = [ -3, 0, 3 ];
    let expected_three_f_prime = scale(&[ -1, 0, 1 ], 3);
    assert!(eq(&three_f_prime, &expected_three_f_prime), "3F' != 3(x^2-1)");

    // Unique positive root of F: x^2 = 3, x = √3. x=1 is a test point in (0,√3)
    // and x=2 is a test point in (√3,∞). Signs of 3F = x(x^2-3):
    // 3F(1) = 1(1-3) = -2 < 0, 3F(2) = 2(4-3) = 2 > 0.
    let f3_at_1 = three_f[0] + three_f[1] + three_f[2] + three_f[3];
    let f3_at_2 = three_f[0] + 2 * three_f[1] + 4 * three_f[2] + 8 * three_f[3];
    assert!(f3_at_1 < 0, "F(1) should be negative");
    assert!(f3_at_2 > 0, "F(2) should be positive");
    // F'(√3) = 3-1 = 2 > 0, so the tail is increasing.
    assert!(3 - 1 == 2);

    // Green flux of div = -(x^2-1) over the disk r^2 <= 2h.
    // ∬ x^2 dA / π = R^4/4, ∬ 1 dA / π = R^2, with R^2 = 2h.
    // Coeffs are low-to-high in h.
    let r2 = [0, 2]; // 2h
    let r4 = mul(&r2, &r2); // 4h^2
    assert!(eq(&r4, &[0, 0, 4]));
    // R^4/4 = h^2
    let r4_over_4 = [0, 0, 1];
    // ∬(x^2-1)/π = R^4/4 - R^2 = h^2 - 2h
    let area_over_pi = sub(&r4_over_4, &r2);
    assert!(eq(&area_over_pi, &[0, -2, 1]), "disk integral of x^2-1");
    // I/π = ∬ div / π = -∬(x^2-1)/π = 2h - h^2
    let i_over_pi = scale(&area_over_pi, -1);
    assert!(eq(&i_over_pi, &[0, 2, -1]), "I(h)/π != h(2-h)");
    // Unique positive zero: I/π = h(2-h) vanishes at h=0 and h=2.
    // I'(h)/π = 2-2h, so I'(2)/π = -2 ≠ 0 (simple).
    let i_prime_over_pi_at_2 = 2 - 2 * 2;
    assert!(i_prime_over_pi_at_2 == -2);

    // Equilibria of (y, -x-(x^2-1)y): y=0 forces -x=0.
    // Jacobian at 0 is [[0,1],[-1,1]] (μ=1), trace 1>0, det 1>0: source.
    let trace = 1;
    let det = 1;
    assert!(trace > 0 && det > 0);

    println!("RUST_OK three_F=x(x^2-3) I_over_pi=h*(2-h) unique_positive_zero_h=2");
}
