use std::env;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::PathBuf;

fn mul_mod(a: u64, b: u64, modulus: u64) -> u64 {
    ((a as u128 * b as u128) % modulus as u128) as u64
}

fn pow_mod(mut base: u64, mut exponent: u64, modulus: u64) -> u64 {
    let mut result = 1_u64;
    base %= modulus;
    while exponent > 0 {
        if exponent & 1 == 1 {
            result = mul_mod(result, base, modulus);
        }
        base = mul_mod(base, base, modulus);
        exponent >>= 1;
    }
    result
}

fn is_prime_u64(n: u64) -> bool {
    const SMALL: [u64; 12] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37];
    const BASES: [u64; 7] = [2, 325, 9375, 28178, 450775, 9780504, 1795265022];
    if n < 2 {
        return false;
    }
    for prime in SMALL {
        if n % prime == 0 {
            return n == prime;
        }
    }

    let mut odd_part = n - 1;
    let mut twos = 0_u32;
    while odd_part & 1 == 0 {
        odd_part >>= 1;
        twos += 1;
    }
    'base: for base in BASES {
        let reduced = base % n;
        if reduced == 0 {
            continue;
        }
        let mut value = pow_mod(reduced, odd_part, n);
        if value == 1 || value == n - 1 {
            continue;
        }
        for _ in 1..twos {
            value = mul_mod(value, value, n);
            if value == n - 1 {
                continue 'base;
            }
        }
        return false;
    }
    true
}

fn least_prime_strictly_between(left: u128, right: u128) -> u64 {
    assert!(left < right);
    let mut candidate = left + 1;
    if candidate <= 2 && 2 < right {
        return 2;
    }
    if candidate & 1 == 0 {
        candidate += 1;
    }
    while candidate < right {
        assert!(candidate <= u64::MAX as u128);
        let value = candidate as u64;
        if is_prime_u64(value) {
            return value;
        }
        candidate += 2;
    }
    panic!("no prime in requested half-interval");
}

fn parse_args() -> (u64, u64, PathBuf) {
    let mut start = None;
    let mut end = None;
    let mut output = None;
    let mut args = env::args().skip(1);
    while let Some(flag) = args.next() {
        let value = args
            .next()
            .unwrap_or_else(|| panic!("missing value for {}", flag));
        match flag.as_str() {
            "--start" => start = Some(value.parse().expect("invalid --start")),
            "--end" => end = Some(value.parse().expect("invalid --end")),
            "--output" => output = Some(PathBuf::from(value)),
            _ => panic!("unknown argument {}", flag),
        }
    }
    let start = start.expect("--start is required");
    let end = end.expect("--end is required");
    let output = output.expect("--output is required");
    assert!(start <= end && end <= u32::MAX as u64);
    (start, end, output)
}

fn main() {
    let (start, end, output) = parse_args();
    let file = File::create(output).expect("cannot create output CSV");
    let mut writer = BufWriter::new(file);
    writeln!(writer, "n,left_offset,right_offset").unwrap();

    let mut n = start;
    loop {
        let wide_n = n as u128;
        let next = wide_n + 1;
        let square = wide_n * wide_n;
        let middle = wide_n * next;
        let next_square = next * next;
        let left_prime = least_prime_strictly_between(square, middle);
        let right_prime = least_prime_strictly_between(middle, next_square);
        let left_offset = left_prime as u128 - square;
        let right_offset = right_prime as u128 - middle;
        assert!(0 < left_offset && left_offset < wide_n);
        assert!(0 < right_offset && right_offset < next);
        writeln!(writer, "{n},{left_offset},{right_offset}").unwrap();
        if n == end {
            break;
        }
        n += 1;
    }
    writer.flush().unwrap();
}
