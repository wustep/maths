use std::env;
use std::fmt;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Rational {
    numerator: i64,
    denominator: i64,
}

fn gcd(mut left: i64, mut right: i64) -> i64 {
    left = left.abs();
    right = right.abs();
    while right != 0 {
        let remainder = left % right;
        left = right;
        right = remainder;
    }
    if left == 0 { 1 } else { left }
}

impl Rational {
    fn new(mut numerator: i64, mut denominator: i64) -> Self {
        assert!(denominator != 0, "zero denominator");
        if denominator < 0 {
            numerator = -numerator;
            denominator = -denominator;
        }
        let divisor = gcd(numerator, denominator);
        Self {
            numerator: numerator / divisor,
            denominator: denominator / divisor,
        }
    }
}

impl fmt::Display for Rational {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.denominator == 1 {
            write!(formatter, "{}", self.numerator)
        } else {
            write!(formatter, "{}/{}", self.numerator, self.denominator)
        }
    }
}

fn csv_rows(path: &Path) -> Vec<Vec<String>> {
    let contents = fs::read_to_string(path)
        .unwrap_or_else(|error| panic!("cannot read {}: {error}", path.display()));
    contents
        .lines()
        .skip(1)
        .filter(|line| !line.trim().is_empty())
        .map(|line| line.split(',').map(str::to_owned).collect())
        .collect()
}

fn integer(field: &str) -> i64 {
    field
        .parse::<i64>()
        .unwrap_or_else(|error| panic!("bad integer {field}: {error}"))
}

fn verify_frontier(root: &Path, report: &mut Vec<String>) {
    let rows = csv_rows(&root.join("frontier_certificate.csv"));
    assert_eq!(rows.len(), 7, "frontier row count");
    report.push("Bourgain-Klein frontier".to_owned());
    report.push("d,gap,kappa,works".to_owned());

    for (index, row) in rows.iter().enumerate() {
        assert_eq!(row.len(), 6, "frontier column count");
        let dimension = integer(&row[0]);
        assert_eq!(dimension, index as i64 + 2, "dimension sequence");

        let stored_gap = Rational::new(integer(&row[1]), integer(&row[2]));
        let stored_kappa = Rational::new(integer(&row[3]), integer(&row[4]));
        let stored_works = match row[5].as_str() {
            "true" => true,
            "false" => false,
            other => panic!("bad Boolean {other}"),
        };

        let gap = Rational::new(4 - dimension, 3 * (dimension - 1));
        let kappa = Rational::new(4 - dimension, 8);
        let works = dimension < 4;
        assert_eq!(stored_gap, gap, "gap at d={dimension}");
        assert_eq!(stored_kappa, kappa, "kappa at d={dimension}");
        assert_eq!(stored_works, works, "outcome at d={dimension}");
        report.push(format!("{dimension},{gap},{kappa},{works}"));
    }
}

fn verify_free_directions(root: &Path, report: &mut Vec<String>) {
    let rows = csv_rows(&root.join("free_direction_certificate.csv"));
    assert_eq!(rows.len(), 8, "free-direction row count");
    report.push("free-direction modulus".to_owned());
    report.push("m,alpha,theta".to_owned());

    for (index, row) in rows.iter().enumerate() {
        assert_eq!(row.len(), 5, "free-direction column count");
        let dimension = integer(&row[0]);
        assert_eq!(dimension, index as i64 + 1, "free-dimension sequence");

        let stored_alpha = Rational::new(integer(&row[1]), integer(&row[2]));
        let stored_modulus = Rational::new(integer(&row[3]), integer(&row[4]));
        let alpha = Rational::new(dimension, 2);
        let modulus = if dimension < 2 {
            alpha
        } else {
            Rational::new(1, 1)
        };
        assert_eq!(stored_alpha, alpha, "alpha at m={dimension}");
        assert_eq!(stored_modulus, modulus, "modulus at m={dimension}");
        report.push(format!("{dimension},{alpha},{modulus}"));
    }
}

fn main() {
    let arguments: Vec<String> = env::args().collect();
    let root = if arguments.len() == 2 {
        PathBuf::from(&arguments[1])
    } else if arguments.len() == 1 {
        PathBuf::from(".")
    } else {
        panic!("usage: verify_frontier [certificate-directory]");
    };

    let mut report = Vec::new();
    verify_frontier(&root, &mut report);
    verify_free_directions(&root, &mut report);
    report.push("certificate verified".to_owned());
    println!("{}", report.join("\n"));
}
