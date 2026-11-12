//! Independent witness/near-miss checker. Input: PRIME then selected residues.
//! For each target s, intersect A with its reflection s-A. This counts ordered
//! representations without enumerating pairs. Both counts 1 and 2 are forbidden.
use std::io::{self, Read};
fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).expect("input");
    let numbers: Vec<usize> = input.split_whitespace().map(|s| s.parse().expect("integer")).collect();
    assert!(!numbers.is_empty(), "missing prime");
    let p = numbers[0];
    assert!(p >= 3 && p <= 199 && p % 2 == 1 && (2..p).all(|d| p % d != 0), "odd prime <=199 required");
    let values = &numbers[1..];
    assert!(values.len() >= 2, "nontrivial set required");
    let mut present = vec![false; p];
    for &x in values { assert!(x < p && !present[x], "duplicate/out of range"); present[x] = true; }
    let counts: Vec<usize> = (0..p).map(|s| (0..p).filter(|&x| present[x] && present[(s+p-x)%p]).count()).collect();
    let forbidden: Vec<usize> = (0..p).filter(|&s| counts[s] == 1 || counts[s] == 2).collect();
    println!("{{\"p\":{p},\"cardinality\":{},\"ordered_counts\":{:?},\"unique_sums\":{:?}}}", values.len(), counts, forbidden);
    if !forbidden.is_empty() { std::process::exit(1); }
}
