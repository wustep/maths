//! Independent exact search for sets with no unique sum in Z/pZ.
//!
//! This does not use the SAT encoding in `../search_green_m_p.py`.  Starting
//! from the affine-normalized set {-1, 0, 1}, it repeatedly chooses a sum
//! having exactly one active unordered representation.  Every admissible
//! completion must contain the endpoints of some other representation of
//! that sum, so branching over all such pairs is exhaustive.

use std::collections::HashSet;
use std::env;
use std::time::Instant;

#[derive(Default)]
struct Stats {
    nodes: u64,
    memo_hits: u64,
    max_memo: usize,
}

struct Search {
    p: u32,
    limit: u32,
    pairs_by_sum: Vec<Vec<u64>>,
    inverses: Vec<u32>,
    memo: HashSet<u64>,
    stats: Stats,
}

impl Search {
    fn new(p: u32, limit: u32) -> Self {
        assert!(p >= 3 && p < 64 && p % 2 == 1);
        let mut pairs_by_sum = vec![Vec::new(); p as usize];
        for a in 0..p {
            for b in a..p {
                let pair = (1_u64 << a) | (1_u64 << b);
                pairs_by_sum[((a + b) % p) as usize].push(pair);
            }
        }
        let expected = ((p + 1) / 2) as usize;
        assert!(pairs_by_sum.iter().all(|pairs| pairs.len() == expected));
        let mut inverses = vec![0; p as usize];
        for value in 1..p {
            inverses[value as usize] = (1..p)
                .find(|candidate| value * candidate % p == 1)
                .expect("nonzero residue must be invertible modulo a prime");
        }
        Self {
            p,
            limit,
            pairs_by_sum,
            inverses,
            memo: HashSet::new(),
            stats: Stats::default(),
        }
    }

    fn canonical(&self, mask: u64) -> u64 {
        // Normalize every nontrivial 3-term progression already in the set.
        // This identifies affine-equivalent search states while retaining the
        // root condition {-1,0,1} in every normalized image.
        let selected = values(mask, self.p);
        let mut best = mask;
        for &center in &selected {
            for &endpoint in &selected {
                if endpoint == center {
                    continue;
                }
                let difference = (endpoint + self.p - center) % self.p;
                let opposite = (center + self.p - difference) % self.p;
                if mask & (1_u64 << opposite) == 0 {
                    continue;
                }
                let multiplier = self.inverses[difference as usize];
                let mut image = 0_u64;
                for &value in &selected {
                    let shifted = (value + self.p - center) % self.p;
                    image |= 1_u64 << (shifted * multiplier % self.p);
                }
                best = best.min(image);
            }
        }
        best
    }

    fn active_pairs(&self, sum: usize, mask: u64) -> Vec<u64> {
        self.pairs_by_sum[sum]
            .iter()
            .copied()
            .filter(|pair| pair & mask == *pair)
            .collect()
    }

    fn dfs(&mut self, raw_mask: u64) -> Option<u64> {
        self.stats.nodes += 1;
        if raw_mask.count_ones() > self.limit {
            return None;
        }

        let mask = self.canonical(raw_mask);
        if !self.memo.insert(mask) {
            self.stats.memo_hits += 1;
            return None;
        }
        self.stats.max_memo = self.stats.max_memo.max(self.memo.len());

        let remaining = self.limit - mask.count_ones();
        let mut best_next: Option<Vec<u64>> = None;

        for sum in 0..self.p as usize {
            let active = self.active_pairs(sum, mask);
            if active.len() != 1 {
                continue;
            }

            let unique_pair = active[0];
            let mut next_masks: Vec<u64> = self.pairs_by_sum[sum]
                .iter()
                .copied()
                .filter(|pair| *pair != unique_pair)
                .map(|pair| mask | pair)
                .filter(|next| next.count_ones() - mask.count_ones() <= remaining)
                .collect();
            next_masks.sort_unstable_by_key(|next| (next.count_ones(), *next));
            next_masks.dedup();

            if next_masks.is_empty() {
                return None;
            }
            if best_next
                .as_ref()
                .is_none_or(|current| next_masks.len() < current.len())
            {
                best_next = Some(next_masks);
            }
        }

        let Some(next_masks) = best_next else {
            return Some(mask);
        };
        for next in next_masks {
            if let Some(witness) = self.dfs(next) {
                return Some(witness);
            }
        }
        None
    }

    fn run(&mut self) -> Option<u64> {
        if self.limit < 3 {
            return None;
        }
        let initial = 1_u64 | (1_u64 << 1) | (1_u64 << (self.p - 1));
        self.dfs(initial)
    }
}

fn values(mask: u64, p: u32) -> Vec<u32> {
    (0..p).filter(|value| mask & (1_u64 << value) != 0).collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: {} PRIME LIMIT", args[0]);
        std::process::exit(2);
    }
    let p: u32 = args[1].parse().expect("PRIME must be an integer");
    let limit: u32 = args[2].parse().expect("LIMIT must be an integer");
    let started = Instant::now();
    let mut search = Search::new(p, limit);
    let result = search.run();
    println!(
        "p={p} limit={limit} status={} nodes={} memo_hits={} memo={} seconds={:.6}",
        if result.is_some() { "SAT" } else { "UNSAT" },
        search.stats.nodes,
        search.stats.memo_hits,
        search.stats.max_memo,
        started.elapsed().as_secs_f64(),
    );
    if let Some(mask) = result {
        println!("witness={:?}", values(mask, p));
    }
}
