//! Targeted fixed-cardinality search at the p=59 boundary.
//!
//! This is a witness finder, not a lower-bound verifier.  It keeps the
//! affine-normalizing progression {-1, 0, 1}, chooses a uniquely represented
//! sum, inserts the endpoints of another representation, and removes the same
//! number of non-normalizing points.  Every proposed repair is scored by a
//! fresh unordered-pair count.

use std::env;
use std::time::Instant;

const P: usize = 59;
const K: usize = 14;
const FIXED: [usize; 3] = [0, 1, P - 1];
const NEAR_MISS: [usize; K] = [0, 1, 3, 4, 5, 9, 13, 15, 16, 21, 29, 33, 45, 58];

#[derive(Clone, Copy)]
struct Rng(u64);

impl Rng {
    fn next(&mut self) -> u64 {
        let mut value = self.0;
        value ^= value << 13;
        value ^= value >> 7;
        value ^= value << 17;
        self.0 = value;
        value
    }

    fn below(&mut self, bound: usize) -> usize {
        (self.next() as usize) % bound
    }

    fn shuffle<T>(&mut self, values: &mut [T]) {
        for upper in (1..values.len()).rev() {
            let other = self.below(upper + 1);
            values.swap(upper, other);
        }
    }
}

fn mask(values: &[usize]) -> u64 {
    values.iter().fold(0_u64, |result, &value| result | (1_u64 << value))
}

fn values(selected: u64) -> Vec<usize> {
    (0..P)
        .filter(|&value| selected & (1_u64 << value) != 0)
        .collect()
}

fn counts(selected: u64) -> [u8; P] {
    let present = values(selected);
    let mut result = [0_u8; P];
    for (index, &left) in present.iter().enumerate() {
        for &right in &present[index..] {
            result[(left + right) % P] += 1;
        }
    }
    result
}

fn score(selected: u64) -> (usize, usize) {
    let multiplicities = counts(selected);
    let unique = multiplicities.iter().filter(|&&count| count == 1).count();
    let fragile = multiplicities.iter().filter(|&&count| count == 2).count();
    (unique, fragile)
}

fn random_start(rng: &mut Rng, restart: usize) -> u64 {
    let fixed = mask(&FIXED);
    if restart == 0 {
        return mask(&NEAR_MISS);
    }
    let mut candidates: Vec<usize> = (2..P - 1).collect();
    rng.shuffle(&mut candidates);
    candidates[..K - FIXED.len()]
        .iter()
        .fold(fixed, |result, &value| result | (1_u64 << value))
}

fn removable(selected: u64, additions: u64) -> Vec<usize> {
    let fixed = mask(&FIXED);
    values(selected & !additions & !fixed)
}

fn consider(
    candidate: u64,
    best_score: &mut (usize, usize),
    best_moves: &mut Vec<u64>,
) {
    debug_assert_eq!(candidate.count_ones(), K as u32);
    let candidate_score = score(candidate);
    if candidate_score < *best_score {
        *best_score = candidate_score;
        best_moves.clear();
        best_moves.push(candidate);
    } else if candidate_score == *best_score {
        best_moves.push(candidate);
    }
}

fn repair_moves(selected: u64, target: usize) -> Vec<u64> {
    let present = values(selected);
    let unique_pair = present.iter().enumerate().find_map(|(index, &left)| {
        present[index..]
            .iter()
            .copied()
            .find(|&right| (left + right) % P == target)
            .map(|right| mask(&[left, right]))
    });
    let unique_pair = unique_pair.expect("target must have an active pair");
    let mut best_score = (usize::MAX, usize::MAX);
    let mut best_moves = Vec::new();

    for left in 0..P {
        let right = (target + P - left) % P;
        if left > right {
            continue;
        }
        let pair = mask(&[left, right]);
        if pair == unique_pair || pair & selected == pair {
            continue;
        }
        let additions = pair & !selected;
        let added = additions.count_ones() as usize;
        let choices = removable(selected, additions);
        if added == 1 {
            for &removed in &choices {
                consider(
                    (selected | additions) & !(1_u64 << removed),
                    &mut best_score,
                    &mut best_moves,
                );
            }
        } else if added == 2 {
            for first in 0..choices.len() {
                for second in first + 1..choices.len() {
                    let removed = (1_u64 << choices[first]) | (1_u64 << choices[second]);
                    consider(
                        (selected | additions) & !removed,
                        &mut best_score,
                        &mut best_moves,
                    );
                }
            }
        }
    }
    best_moves.sort_unstable();
    best_moves.dedup();
    best_moves
}

fn kick(selected: u64, rng: &mut Rng) -> u64 {
    let fixed = mask(&FIXED);
    let mut old = values(selected & !fixed);
    let mut new: Vec<usize> = (0..P)
        .filter(|&value| selected & (1_u64 << value) == 0)
        .collect();
    rng.shuffle(&mut old);
    rng.shuffle(&mut new);
    let width = 2 + rng.below(3);
    let mut result = selected;
    for index in 0..width {
        result &= !(1_u64 << old[index]);
        result |= 1_u64 << new[index];
    }
    result
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() > 4 {
        eprintln!("usage: {} [RESTARTS] [STEPS] [SEED]", args[0]);
        std::process::exit(2);
    }
    let restarts: usize = args.get(1).map_or(2_000, |raw| raw.parse().expect("RESTARTS"));
    let steps: usize = args.get(2).map_or(2_000, |raw| raw.parse().expect("STEPS"));
    let seed: u64 = args
        .get(3)
        .map_or(0x4d59_14c0_de56_501_u64, |raw| raw.parse().expect("SEED"));
    if restarts == 0 || steps == 0 || seed == 0 {
        eprintln!("RESTARTS, STEPS, and SEED must be positive");
        std::process::exit(2);
    }

    let started = Instant::now();
    let mut rng = Rng(seed);
    let mut global_score = (usize::MAX, usize::MAX);
    let mut global = 0_u64;
    let mut evaluated_steps = 0_u64;

    for restart in 0..restarts {
        let mut selected = random_start(&mut rng, restart);
        let mut stagnation = 0_usize;
        for _ in 0..steps {
            evaluated_steps += 1;
            let current_score = score(selected);
            if current_score < global_score {
                global_score = current_score;
                global = selected;
                eprintln!(
                    "best unique={} fragile={} restart={} steps={} set={:?}",
                    global_score.0,
                    global_score.1,
                    restart,
                    evaluated_steps,
                    values(global),
                );
            }
            if current_score.0 == 0 {
                println!(
                    "SAT p={P} cardinality={K} restarts={} steps={} seconds={:.6}",
                    restart + 1,
                    evaluated_steps,
                    started.elapsed().as_secs_f64(),
                );
                println!("witness={:?}", values(selected));
                return;
            }

            let multiplicities = counts(selected);
            let targets: Vec<usize> = (0..P)
                .filter(|&sum| multiplicities[sum] == 1)
                .collect();
            let target = targets[rng.below(targets.len())];
            let next = repair_moves(selected, target);
            if next.is_empty() {
                selected = kick(selected, &mut rng);
                stagnation = 0;
                continue;
            }
            let candidate = next[rng.below(next.len())];
            if score(candidate) < current_score || rng.below(100) < 8 {
                selected = candidate;
                stagnation = 0;
            } else {
                stagnation += 1;
            }
            if stagnation >= 25 {
                selected = kick(selected, &mut rng);
                stagnation = 0;
            }
        }
    }

    println!(
        "UNKNOWN p={P} cardinality={K} restarts={restarts} steps={evaluated_steps} \
         best_unique={} best_fragile={} seconds={:.6}",
        global_score.0,
        global_score.1,
        started.elapsed().as_secs_f64(),
    );
    println!("best={:?}", values(global));
    std::process::exit(3);
}
