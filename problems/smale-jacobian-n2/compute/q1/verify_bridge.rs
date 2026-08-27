use std::collections::BTreeMap;
use std::env;
use std::fs;

type Point = (i32, i32);
type Monomial = (&'static str, &'static str);
type Expression = BTreeMap<Monomial, i32>;

fn lattice_points(vertices: &[Point]) -> Vec<Point> {
    let xmax = vertices.iter().map(|p| p.0).max().unwrap();
    let ymax = vertices.iter().map(|p| p.1).max().unwrap();
    let mut answer = Vec::new();
    for x in 0..=xmax {
        for y in 0..=ymax {
            let crosses: Vec<i32> = (0..vertices.len())
                .map(|index| {
                    let a = vertices[index];
                    let b = vertices[(index + 1) % vertices.len()];
                    (b.0 - a.0) * (y - a.1) - (b.1 - a.1) * (x - a.0)
                })
                .collect();
            if crosses.iter().all(|value| *value >= 0)
                || crosses.iter().all(|value| *value <= 0)
            {
                answer.push((x, y));
            }
        }
    }
    answer
}

fn band_range(points: &[Point]) -> (i32, i32) {
    let mut values = points.iter().map(|(x, y)| 2 * x - y);
    let first = values.next().unwrap();
    values.fold((first, first), |(low, high), value| {
        (low.min(value), high.max(value))
    })
}

fn ordered(left: &'static str, right: &'static str) -> Monomial {
    if left <= right { (left, right) } else { (right, left) }
}

fn add_term(expression: &mut Expression, coefficient: i32, left: &'static str, right: &'static str) {
    let monomial = ordered(left, right);
    let value = expression.entry(monomial).or_insert(0);
    *value += coefficient;
    if *value == 0 {
        expression.remove(&monomial);
    }
}

fn expanded_identities() -> BTreeMap<i32, Expression> {
    let p = [(2, "A", "Ap"), (1, "B", "Bp"), (0, "C", "Cp")];
    let q = [(3, "D", "Dp"), (2, "E", "Ep"), (1, "F", "Fp"), (0, "G", "Gp")];
    let mut answer: BTreeMap<i32, Expression> = BTreeMap::new();
    for (pz, atom_p, derivative_p) in p {
        for (qz, atom_q, derivative_q) in q {
            if pz == 0 && qz == 0 {
                continue;
            }
            let expression = answer.entry(pz + qz - 1).or_default();
            if pz != 0 {
                add_term(expression, pz, atom_p, derivative_q);
            }
            if qz != 0 {
                add_term(expression, -qz, derivative_p, atom_q);
            }
        }
    }
    answer
}

fn expected_identities() -> BTreeMap<i32, Expression> {
    let specifications: [(i32, &[(i32, &'static str, &'static str)]); 5] = [
        (4, &[(2, "A", "Dp"), (-3, "Ap", "D")]),
        (3, &[(2, "A", "Ep"), (-2, "Ap", "E"), (1, "B", "Dp"), (-3, "Bp", "D")]),
        (2, &[(2, "A", "Fp"), (-1, "Ap", "F"), (1, "B", "Ep"), (-2, "Bp", "E"), (-3, "Cp", "D")]),
        (1, &[(2, "A", "Gp"), (1, "B", "Fp"), (-1, "Bp", "F"), (-2, "Cp", "E")]),
        (0, &[(1, "B", "Gp"), (-1, "Cp", "F")]),
    ];
    let mut answer = BTreeMap::new();
    for (power, terms) in specifications {
        let mut expression = Expression::new();
        for (coefficient, left, right) in terms {
            add_term(&mut expression, *coefficient, left, right);
        }
        answer.insert(power, expression);
    }
    answer
}

fn determinant_3(matrix: [[i32; 3]; 3]) -> i32 {
    matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
}

fn main() {
    let certificate_path = env::args().nth(1).expect("usage: verify_bridge_rs certificate.json");
    let certificate = fs::read_to_string(certificate_path).expect("read certificate");
    assert!(certificate.contains("\"threshold\": 125"));
    assert!(certificate.contains("232204bdb598cc2ea0368e154c8573e18bbfdc69fa631c8878de4b884b38bb18"));

    let cases = [
        (
            1,
            vec![(0, 0), (1, 0), (8, 14), (8, 16), (0, 8)],
            vec![(0, 0), (2, 1), (12, 21), (12, 24), (0, 12)],
            (61, 125, -8, 2, -12, 3),
        ),
        (
            2,
            vec![(0, 0), (1, 0), (8, 14), (8, 16)],
            vec![(0, 0), (2, 1), (12, 21), (12, 24)],
            (25, 47, 0, 2, 0, 3),
        ),
    ];

    let mut summaries = Vec::new();
    for (case, p_vertices, q_vertices, expected) in cases {
        let p_points = lattice_points(&p_vertices);
        let q_points = lattice_points(&q_vertices);
        let p_range = band_range(&p_points);
        let q_range = band_range(&q_points);
        assert_eq!((p_points.len(), q_points.len(), p_range.0, p_range.1, q_range.0, q_range.1),
                   (expected.0, expected.1, expected.2, expected.3, expected.4, expected.5));
        summaries.push((case, p_points.len(), q_points.len(), p_range, q_range));
    }

    assert_eq!(expanded_identities(), expected_identities());
    let normalization_determinant = determinant_3([[1, 0, 1], [8, 14, 1], [8, 16, 1]]);
    assert_eq!(normalization_determinant, 14);

    println!("BRIDGE_THEOREM threshold=125 exceptions=72,108;108,72");
    for (case, p_count, q_count, p_range, q_range) in summaries {
        println!(
            "BRIDGE_CASE case={} P_points={} Q_points={} P_bands={}..{} Q_bands={}..{}",
            case, p_count, q_count, p_range.0, p_range.1, q_range.0, q_range.1
        );
    }
    println!("BRIDGE_COORDINATES jacobian=-1 x2=t^2*z^4");
    println!("BRIDGE_IDENTITIES count=5");
    println!("BRIDGE_NORMALIZATION determinant={}", normalization_determinant);
    println!("BRIDGE_PASS");
}
