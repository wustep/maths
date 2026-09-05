//! RAM-light exact search for sets with no unique sum in Z/pZ.
//!
//! This does not use the SAT encoding in `../search_green_m_p.py`.  Starting
//! from the affine-normalized set {-1, 0, 1}, it repeatedly chooses a sum
//! having exactly one active unordered representation.  Every admissible
//! completion must contain the endpoints of some other representation of
//! that sum, so branching over all such pairs is exhaustive.  Compared with
//! q3, this version drops a branch when its newly selected points strictly
//! contain those of another repair for the same sum: every completion of the
//! larger repair already occurs below the smaller one.

use std::env;
use std::time::Instant;

// Fixed direct-mapped cache: collisions evict a state; only full-key equality
// can prune. Eviction costs time, never completeness. Default storage: 64 MiB.
struct MaskSet {
    slots: Vec<u64>,
    len: usize,
}

impl MaskSet {
    fn new() -> Self {
        Self { slots: vec![0; 1 << 23], len: 0 }
    }

    fn insert(&mut self, mut value: u64) -> bool {
        let key = value;
        value ^= value >> 30;
        value = value.wrapping_mul(0xbf58_476d_1ce4_e5b9);
        value ^= value >> 27;
        value = value.wrapping_mul(0x94d0_49bb_1331_11eb);
        let index = ((value ^ (value >> 31)) as usize) & (self.slots.len() - 1);
        let old = self.slots[index];
        if old == key { return false; }
        self.len += usize::from(old == 0);
        self.slots[index] = key;
        true
    }

    fn len(&self) -> usize { self.len }
}

#[derive(Default)]
struct Stats {
    nodes: u64,
    memo_hits: u64,
    cover_prunes: u64,
    max_memo: usize,
}

struct Search {
    p: u32,
    limit: u32,
    pairs_by_sum: Vec<Vec<u64>>,
    images: Vec<Vec<u64>>,
    memo: MaskSet,
    stats: Stats,
    node_limit: Option<u64>,
    stopped_early: bool,
}

impl Search {
    fn new(p: u32, limit: u32, node_limit: Option<u64>) -> Self {
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
        let mut images = vec![vec![0; p as usize]; (p * p) as usize];
        for center in 0..p {
            for endpoint in 0..p {
                if center == endpoint { continue; }
                let multiplier = inverses[((endpoint + p - center) % p) as usize];
                for value in 0..p {
                    images[(center * p + endpoint) as usize][value as usize] =
                        1 << (((value + p - center) % p) * multiplier % p);
                }
            }
        }
        Self {
            p,
            limit,
            pairs_by_sum,
            images,
            memo: MaskSet::new(),
            stats: Stats::default(),
            node_limit,
            stopped_early: false,
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
                let map = &self.images[(center * self.p + endpoint) as usize];
                let mut image = 0_u64;
                for &value in &selected {
                    image |= map[value as usize];
                }
                best = best.min(image);
            }
        }
        best
    }

    fn repair_options(&self, sum: usize, mask: u64, remaining: u32) -> Option<Vec<u64>> {
        let mut active_pair = None;
        for &pair in &self.pairs_by_sum[sum] {
            if pair & mask == pair {
                if active_pair.is_some() {
                    return None;
                }
                active_pair = Some(pair);
            }
        }
        active_pair?;

        let mut options: Vec<u64> = self.pairs_by_sum[sum]
            .iter()
            .map(|pair| pair & !mask)
            .filter(|addition| {
                *addition != 0 && addition.count_ones() <= remaining
            })
            .collect();
        options.sort_unstable_by_key(|addition| (addition.count_ones(), *addition));
        options.dedup();
        let mut minimal = Vec::with_capacity(options.len());
        for option in options {
            if minimal
                .iter()
                .any(|smaller| *smaller & option == *smaller)
            {
                continue;
            }
            minimal.push(option);
        }
        Some(minimal)
    }

    fn dfs(&mut self, raw_mask: u64) -> Option<u64> {
        if self.stopped_early {
            return None;
        }
        if self
            .node_limit
            .is_some_and(|limit| self.stats.nodes >= limit)
        {
            self.stopped_early = true;
            return None;
        }
        self.stats.nodes += 1;
        if raw_mask.count_ones() > self.limit {
            return None;
        }

        let mask = raw_mask;
        let remaining = self.limit - mask.count_ones();
        let mut constraints = Vec::new();

        let selected = values(mask, self.p);
        let mut counts = [0_u8; 64];
        for (index, &left) in selected.iter().enumerate() {
            for &right in &selected[index..] {
                counts[((left + right) % self.p) as usize] += 1;
            }
        }
        for sum in 0..self.p as usize {
            if counts[sum] != 1 { continue; }
            let Some(options) = self.repair_options(sum, mask, remaining) else {
                continue;
            };
            if options.is_empty() {
                return None;
            }
            constraints.push(options);
        }

        if constraints.is_empty() {
            return Some(mask);
        }
        if remaining <= 6 && !can_cover(&constraints, 0, remaining) {
            self.stats.cover_prunes += 1;
            return None;
        }
        // Expensive normalization only after cheap arithmetic and cover pruning.
        let key = self.canonical(mask);
        if !self.memo.insert(key) {
            self.stats.memo_hits += 1;
            return None;
        }
        self.stats.max_memo = self.stats.max_memo.max(self.memo.len());
        constraints.sort_unstable_by_key(Vec::len);
        for addition in &constraints[0] {
            let next = mask | addition;
            if let Some(witness) = self.dfs(next) {
                return Some(witness);
            }
            if self.stopped_early {
                return None;
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

fn can_cover(constraints: &[Vec<u64>], chosen: u64, budget: u32) -> bool {
    let mut best = None;
    let mut best_count = usize::MAX;
    for (index, options) in constraints.iter().enumerate() {
        if options.iter().any(|option| *option & !chosen == 0) { continue; }
        let count = options.iter().filter(|option| (chosen | **option).count_ones() <= budget).count();
        if count == 0 { return false; }
        if count < best_count {
            best = Some(index);
            best_count = count;
        }
    }
    let Some(index) = best else { return true; };
    constraints[index].iter().any(|option| {
        let next = chosen | *option;
        next.count_ones() <= budget && can_cover(constraints, next, budget)
    })
}

fn values(mask: u64, p: u32) -> Vec<u32> {
    (0..p).filter(|value| mask & (1_u64 << value) != 0).collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if !(3..=4).contains(&args.len()) {
        eprintln!("usage: {} PRIME LIMIT [NODE_LIMIT]", args[0]);
        std::process::exit(2);
    }
    let p: u32 = args[1].parse().expect("PRIME must be an integer");
    let limit: u32 = args[2].parse().expect("LIMIT must be an integer");
    let node_limit: Option<u64> = args.get(3).map(|raw| {
        raw.parse()
            .expect("NODE_LIMIT must be a positive integer")
    });
    if node_limit == Some(0) {
        eprintln!("NODE_LIMIT must be positive");
        std::process::exit(2);
    }
    let started = Instant::now();
    let mut search = Search::new(p, limit, node_limit);
    let result = search.run();
    let status = if result.is_some() {
        "SAT"
    } else if search.stopped_early {
        "UNKNOWN"
    } else {
        "UNSAT"
    };
    println!(
        "p={p} limit={limit} status={} nodes={} memo_hits={} cover_prunes={} memo={} seconds={:.6}",
        status,
        search.stats.nodes,
        search.stats.memo_hits,
        search.stats.cover_prunes,
        search.stats.max_memo,
        started.elapsed().as_secs_f64(),
    );
    if let Some(mask) = result {
        println!("witness={:?}", values(mask, p));
    }
    if search.stopped_early {
        std::process::exit(3);
    }
}
