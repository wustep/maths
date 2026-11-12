// Independent upper-bound replay: solve backwards for the second operand.
// Python instead evaluates all forward operand pairs. Checked arithmetic
// rejects overflow; this verifier never supplies a search lower bound.
use std::{collections::{HashMap, HashSet}, env, fs};

fn check(n: usize, values: &[u128], cost: usize) {
    assert_eq!(values.len(), cost + 1);
    assert_eq!(values[0], 1);
    assert_eq!(values[cost], n as u128);
    let mut earlier = HashSet::from([1u128]);
    for &v in &values[1..] {
        assert!(v > 0 && !earlier.contains(&v));
        let valid = earlier.iter().any(|&a| {
            // v = a+b, a-b, b-a, or a*b. Reusing an operand is allowed.
            (v > a && earlier.contains(&(v-a))) ||
            (a > v && earlier.contains(&(a-v))) ||
            a.checked_add(v).map_or(false, |b| earlier.contains(&b)) ||
            (v % a == 0 && earlier.contains(&(v/a)))
        });
        assert!(valid, "invalid step for {}: {}", n, v);
        earlier.insert(v);
    }
}

fn main() {
    let args: Vec<_> = env::args().collect();
    assert_eq!(args.len(), 3);
    let mut tau = vec![usize::MAX];
    for line in fs::read_to_string(&args[1]).unwrap().lines() {
        let row: Vec<usize> = line.split_whitespace().map(|s| s.parse().unwrap()).collect();
        assert_eq!(row.len(), 2);
        assert_eq!(row[0], tau.len());
        assert!(row[1] <= 10);
        tau.push(row[1]);
    }
    assert_eq!(tau.len(), 50001);
    assert_eq!(tau[1], 0);
    let mut witnesses = HashMap::new();
    for line in fs::read_to_string(&args[2]).unwrap().lines() {
        let mut row = line.split_whitespace();
        let n: usize = row.next().unwrap().parse().unwrap();
        assert!(n > 0 && n < tau.len());
        let values: Vec<u128> = row.map(|s| s.parse().unwrap()).collect();
        check(n, &values, tau[n]);
        assert!(witnesses.insert(n, values).is_none());
    }
    for n in 1..tau.len() {
        if tau[n] == 10 { assert!(witnesses.contains_key(&n)); }
    }
    let mut prime = vec![true; tau.len()];
    prime[0] = false;
    prime[1] = false;
    for p in 2..tau.len() {
        if prime[p] {
            for n in (p*2..tau.len()).step_by(p) { prime[n] = false; }
        }
    }
    let bad: Vec<usize> = (2..tau.len()).filter(|&p| prime[p] && tau[p] < tau[p-1]).collect();
    assert_eq!(bad.len(), 69);
    assert_eq!(bad.iter().copied().filter(|&p| p < 5000).collect::<Vec<_>>(),
               vec![3359, 3623, 4909, 4943]);
    for p in bad {
        assert_eq!(tau[p] + 1, tau[p-1]);
        assert!(witnesses.contains_key(&p) && witnesses.contains_key(&(p-1)));
    }
    println!("Rust verified {} witnesses and all 69 prime counterexamples", witnesses.len());
}
