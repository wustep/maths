//! Independent verifier for the q2 Oppermann/Lucas certificate.

use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;

const PUBLISHED_END: u128 = 70_500_000_000_000;

#[derive(Clone, Debug)]
struct PrimeNode {
    witness: u128,
    factors: Vec<(u128, u32)>,
}

fn add_mod(left: u128, right: u128, modulus: u128) -> u128 {
    if left >= modulus - right {
        left - (modulus - right)
    } else {
        left + right
    }
}

fn mul_mod(mut left: u128, mut right: u128, modulus: u128) -> u128 {
    let mut result = 0;
    left %= modulus;
    while right != 0 {
        if right & 1 == 1 {
            result = add_mod(result, left, modulus);
        }
        right >>= 1;
        if right != 0 {
            left = add_mod(left, left, modulus);
        }
    }
    result
}

fn pow_mod(mut base: u128, mut exponent: u128, modulus: u128) -> u128 {
    let mut result = 1 % modulus;
    base %= modulus;
    while exponent != 0 {
        if exponent & 1 == 1 {
            result = mul_mod(result, base, modulus);
        }
        exponent >>= 1;
        if exponent != 0 {
            base = mul_mod(base, base, modulus);
        }
    }
    result
}

fn gcd(mut left: u128, mut right: u128) -> u128 {
    while right != 0 {
        let next = left % right;
        left = right;
        right = next;
    }
    left
}

fn verify_prime(
    prime: u128,
    nodes: &BTreeMap<u128, PrimeNode>,
    proved: &mut BTreeSet<u128>,
    active: &mut BTreeSet<u128>,
) -> Result<(), String> {
    if proved.contains(&prime) {
        return Ok(());
    }
    if !active.insert(prime) {
        return Err(format!("cycle in prime proof at {prime}"));
    }
    let node = nodes.get(&prime).ok_or_else(|| format!("missing prime node {prime}"))?;
    if prime == 2 {
        if node.witness != 0 || !node.factors.is_empty() {
            return Err("malformed base proof for 2".to_string());
        }
    } else {
        if prime < 3 || prime % 2 == 0 || !(2..prime).contains(&node.witness) {
            return Err(format!("malformed odd prime node {prime}"));
        }
        let mut previous = 0;
        let mut product = 1u128;
        for &(factor, exponent) in &node.factors {
            if factor <= previous || exponent == 0 || factor >= prime {
                return Err(format!("noncanonical factors for {prime}"));
            }
            verify_prime(factor, nodes, proved, active)?;
            for _ in 0..exponent {
                product = product.checked_mul(factor)
                    .ok_or_else(|| format!("factor product overflow for {prime}"))?;
            }
            previous = factor;
        }
        if product != prime - 1 {
            return Err(format!("factorization does not multiply to p-1 for {prime}"));
        }
        if pow_mod(node.witness, prime - 1, prime) != 1 {
            return Err(format!("Fermat congruence failed for {prime}"));
        }
        for &(factor, _) in &node.factors {
            let residue = pow_mod(node.witness, (prime - 1) / factor, prime);
            if residue == 0 || gcd(residue - 1, prime) != 1 {
                return Err(format!("Lucas gcd condition failed for {prime}, q={factor}"));
            }
        }
    }
    active.remove(&prime);
    proved.insert(prime);
    Ok(())
}

fn parse_u128(text: &str, context: &str) -> Result<u128, String> {
    text.parse().map_err(|_| format!("invalid integer for {context}: {text}"))
}

fn main() -> Result<(), String> {
    let path = env::args().nth(1).ok_or("usage: verify_extension CERTIFICATE")?;
    let body = fs::read_to_string(path).map_err(|error| error.to_string())?;
    let mut headers = BTreeMap::<String, String>::new();
    let mut rows = Vec::<(u128, u128, u128)>::new();
    let mut nodes = BTreeMap::<u128, PrimeNode>::new();

    for (line_number, line) in body.lines().enumerate() {
        let fields: Vec<_> = line.split('\t').collect();
        match fields.first().copied() {
            Some("H") if fields.len() == 3 => {
                if headers.insert(fields[1].to_string(), fields[2].to_string()).is_some() {
                    return Err(format!("duplicate header at line {}", line_number + 1));
                }
            }
            Some("W") if fields.len() == 4 => rows.push((
                parse_u128(fields[1], "n")?,
                parse_u128(fields[2], "left witness")?,
                parse_u128(fields[3], "right witness")?,
            )),
            Some("P") if fields.len() == 4 => {
                let prime = parse_u128(fields[1], "prime node")?;
                let witness = parse_u128(fields[2], "Lucas witness")?;
                let mut factors = Vec::new();
                if !fields[3].is_empty() {
                    for item in fields[3].split(',') {
                        let (factor, exponent) = item.split_once('^')
                            .ok_or_else(|| format!("malformed factor {item}"))?;
                        factors.push((
                            parse_u128(factor, "factor")?,
                            exponent.parse().map_err(|_| format!("invalid exponent {exponent}"))?,
                        ));
                    }
                }
                if nodes.insert(prime, PrimeNode { witness, factors }).is_some() {
                    return Err(format!("duplicate prime node {prime}"));
                }
            }
            _ => return Err(format!("malformed line {}", line_number + 1)),
        }
    }

    let expected_headers = BTreeSet::from([
        "schema", "published_end", "start", "end", "rows",
    ]);
    if headers.keys().map(String::as_str).collect::<BTreeSet<_>>() != expected_headers {
        return Err("unexpected header set".to_string());
    }
    if headers["schema"] != "landau-legendre.oppermann-extension.v1" {
        return Err("unexpected schema".to_string());
    }
    let published = parse_u128(&headers["published_end"], "published_end")?;
    let start = parse_u128(&headers["start"], "start")?;
    let end = parse_u128(&headers["end"], "end")?;
    let row_count = parse_u128(&headers["rows"], "rows")?;
    if published != PUBLISHED_END || start != PUBLISHED_END + 1 || end < start {
        return Err("certificate does not extend the pinned published endpoint".to_string());
    }
    if row_count != end - start + 1 || row_count != rows.len() as u128 {
        return Err("row count does not equal the full contiguous range".to_string());
    }

    let mut proved = BTreeSet::new();
    let mut active = BTreeSet::new();
    let mut used = BTreeSet::new();
    for (index, &(n_value, left, right)) in rows.iter().enumerate() {
        if n_value != start + index as u128 {
            return Err(format!("missing or unordered row at n={n_value}"));
        }
        let square = n_value.checked_mul(n_value).ok_or("square overflow")?;
        let middle = n_value.checked_mul(n_value + 1).ok_or("middle overflow")?;
        let next_square = (n_value + 1).checked_mul(n_value + 1).ok_or("next square overflow")?;
        if !(square < left && left < middle && middle < right && right < next_square) {
            return Err(format!("Oppermann interval check failed at n={n_value}"));
        }
        verify_prime(left, &nodes, &mut proved, &mut active)?;
        verify_prime(right, &nodes, &mut proved, &mut active)?;
        used.insert(left);
        used.insert(right);
    }

    fn mark_dependencies(prime: u128, nodes: &BTreeMap<u128, PrimeNode>, used: &mut BTreeSet<u128>) {
        if !used.insert(prime) {
            return;
        }
        if let Some(node) = nodes.get(&prime) {
            for &(factor, _) in &node.factors {
                mark_dependencies(factor, nodes, used);
            }
        }
    }
    let roots: Vec<_> = used.iter().copied().collect();
    let mut reachable = BTreeSet::new();
    for prime in roots {
        mark_dependencies(prime, &nodes, &mut reachable);
    }
    if reachable != nodes.keys().copied().collect() {
        return Err("certificate contains unused prime nodes".to_string());
    }

    println!(
        "PASS oppermann_extension n={}..={} rows={} prime_nodes={}",
        start, end, rows.len(), nodes.len()
    );
    Ok(())
}
