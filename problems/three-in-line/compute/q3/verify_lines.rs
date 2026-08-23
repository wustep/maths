//! Independent checker using normalized lines rather than point triples.

use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;

type Point = (i64, i64);
type Line = (i64, i64, i64);

fn gcd(mut a: i64, mut b: i64) -> i64 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let remainder = a % b;
        a = b;
        b = remainder;
    }
    a
}

fn normalized_line(left: Point, right: Point) -> Line {
    let dx = right.0 - left.0;
    let dy = right.1 - left.1;
    let mut a = dy;
    let mut b = -dx;
    let mut c = dx * left.1 - dy * left.0;
    let divisor = gcd(gcd(a, b), c);
    a /= divisor;
    b /= divisor;
    c /= divisor;
    if a < 0 || (a == 0 && b < 0) || (a == 0 && b == 0 && c < 0) {
        a = -a;
        b = -b;
        c = -c;
    }
    (a, b, c)
}

fn fail(message: &str) -> ! {
    eprintln!("INVALID\n- {message}");
    std::process::exit(1);
}

fn main() {
    let arguments: Vec<String> = env::args().collect();
    if arguments.len() < 2 || arguments.len() > 3 {
        fail("usage: verify_lines WITNESS [N]");
    }
    let n = if arguments.len() == 3 {
        arguments[2].parse::<usize>().unwrap_or_else(|_| fail("N is not a positive integer"))
    } else {
        71
    };
    if n == 0 {
        fail("N is not a positive integer");
    }
    let text = fs::read_to_string(&arguments[1]).unwrap_or_else(|error| {
        fail(&format!("cannot read {}: {error}", arguments[1]));
    });

    let mut points: Vec<Point> = Vec::new();
    for (line_number, raw_line) in text.lines().enumerate() {
        let line = raw_line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let fields: Vec<&str> = line.split_whitespace().collect();
        if fields.len() != 2 {
            fail(&format!("line {} does not contain two integers", line_number + 1));
        }
        let x = fields[0].parse::<i64>().unwrap_or_else(|_| {
            fail(&format!("line {} has an invalid x coordinate", line_number + 1));
        });
        let y = fields[1].parse::<i64>().unwrap_or_else(|_| {
            fail(&format!("line {} has an invalid y coordinate", line_number + 1));
        });
        points.push((x, y));
    }

    if points.len() != 2 * n {
        fail(&format!("point count is {}, expected {}", points.len(), 2 * n));
    }
    let mut distinct: HashSet<Point> = HashSet::new();
    let mut rows = vec![0_u8; n];
    let mut columns = vec![0_u8; n];
    for &point in &points {
        if point.0 < 0 || point.0 >= n as i64 || point.1 < 0 || point.1 >= n as i64 {
            fail(&format!("point {:?} is outside the grid", point));
        }
        if !distinct.insert(point) {
            fail(&format!("duplicate point {:?}", point));
        }
        columns[point.0 as usize] += 1;
        rows[point.1 as usize] += 1;
    }
    if rows.iter().any(|&count| count != 2) {
        fail("not every row contains exactly two points");
    }
    if columns.iter().any(|&count| count != 2) {
        fail("not every column contains exactly two points");
    }

    let mut seen: HashMap<Line, (usize, usize)> = HashMap::new();
    let mut pairs_checked = 0_usize;
    for left in 0..points.len() {
        for right in (left + 1)..points.len() {
            pairs_checked += 1;
            let line = normalized_line(points[left], points[right]);
            if let Some(&(old_left, old_right)) = seen.get(&line) {
                fail(&format!(
                    "points {:?}, {:?} and pair {:?}, {:?} share normalized line {:?}",
                    points[old_left], points[old_right], points[left], points[right], line
                ));
            }
            seen.insert(line, (left, right));
        }
    }

    println!("VALID");
    println!("n={n} points={}", points.len());
    println!("pair_lines_checked={pairs_checked}");
    println!("rows=2-each columns=2-each");
}
