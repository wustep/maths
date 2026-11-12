//! RAM-light exact search for sets with no unique sum in Z/pZ (q7).
//!
//! Odd primes below 128 (128-bit masks). This does not use a SAT encoding.
//! Starting from the affine-normalized set {-1, 0, 1}, it repeatedly chooses
//! a sum having exactly one active unordered representation. Every admissible
//! completion must contain the endpoints of some other representation of that
//! sum, so branching over all such pairs is exhaustive. A branch is dropped
//! when its newly selected points strictly contain those of another repair
//! for the same sum: every completion of the larger repair already occurs
//! below the smaller one.
//!
//! Memo collisions evict a state; only full-key equality can prune. Eviction
//! costs time, never completeness. Default storage: 128 MiB.

use std::env;
use std::time::{Duration, Instant};

struct MaskSet {
    slots: Vec<u128>,
    len: usize,
}

impl MaskSet {
    fn new() -> Self {
        Self { slots: vec![0; 1 << 23], len: 0 }
    }

    fn insert(&mut self, value: u128) -> bool {
        let key = value;
        let mut mixed = (value as u64) ^ ((value >> 64) as u64);
        mixed ^= mixed >> 30;
        mixed = mixed.wrapping_mul(0xbf58_476d_1ce4_e5b9);
        mixed ^= mixed >> 27;
        mixed = mixed.wrapping_mul(0x94d0_49bb_1331_11eb);
        let index = ((mixed ^ (mixed >> 31)) as usize) & (self.slots.len() - 1);
        let old = self.slots[index];
        if old == key {
            return false;
        }
        self.len += usize::from(old == 0);
        self.slots[index] = key;
        true
    }

    fn len(&self) -> usize {
        self.len
    }
}

#[derive(Default)]
struct Stats {
    nodes: u64,
    memo_hits: u64,
    cover_prunes: u64,
    ap_prunes: u64,
    max_memo: usize,
}

struct Search {
    p: u32,
    limit: u32,
    pairs_by_sum: Vec<Vec<u128>>,
    images: Vec<Vec<u128>>,
    memo: MaskSet,
    stats: Stats,
    node_limit: Option<u64>,
    stopped_early: bool,
    forbidden_ap: u32,
    started: Instant,
    wall_limit: Option<Duration>,
}

impl Search {
    fn new(p: u32, limit: u32, node_limit: Option<u64>) -> Self {
        assert!(p >= 3 && p < 128 && p % 2 == 1);
        let mut d = 3;
        while d * d <= p {
            assert!(p % d != 0, "odd prime required");
            d += 2;
        }
        let mut pairs_by_sum = vec![Vec::new(); p as usize];
        for a in 0..p {
            for b in a..p {
                let pair = (1_u128 << a) | (1_u128 << b);
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
                if center == endpoint {
                    continue;
                }
                let multiplier = inverses[((endpoint + p - center) % p) as usize];
                for value in 0..p {
                    images[(center * p + endpoint) as usize][value as usize] =
                        1_u128 << (((value + p - center) % p) * multiplier % p);
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
            forbidden_ap: 0,
            started: Instant::now(),
            wall_limit: env::var("EXACT_SECONDS")
                .ok()
                .map(|raw| Duration::from_secs_f64(raw.parse().expect("EXACT_SECONDS"))),
        }
    }

    fn has_ap(&self, mask: u128, length: u32) -> bool {
        if length == 0 || mask.count_ones() < length {
            return false;
        }
        let selected = values(mask, self.p);
        let present = mask;
        for &start in &selected {
            for d in 1..self.p {
                if (0..length)
                    .all(|i| present & (1_u128 << ((start + i * d) % self.p)) != 0)
                {
                    return true;
                }
            }
        }
        false
    }

    fn canonical(&self, mask: u128) -> u128 {
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
                if mask & (1_u128 << opposite) == 0 {
                    continue;
                }
                let map = &self.images[(center * self.p + endpoint) as usize];
                let mut image = 0_u128;
                for &value in &selected {
                    image |= map[value as usize];
                }
                best = best.min(image);
            }
        }
        best
    }

    fn repair_options(&self, sum: usize, mask: u128, remaining: u32) -> Option<Vec<u128>> {
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

        let mut options: Vec<u128> = self.pairs_by_sum[sum]
            .iter()
            .map(|pair| pair & !mask)
            .filter(|addition| *addition != 0 && addition.count_ones() <= remaining)
            .collect();
        options.sort_unstable_by_key(|addition| (addition.count_ones(), *addition));
        options.dedup();
        let mut minimal = Vec::with_capacity(options.len());
        for option in options {
            if minimal.iter().any(|smaller| *smaller & option == *smaller) {
                continue;
            }
            minimal.push(option);
        }
        Some(minimal)
    }

    fn dfs(&mut self, raw_mask: u128) -> Option<u128> {
        if self.stopped_early {
            return None;
        }
        if self.node_limit.is_some_and(|limit| self.stats.nodes >= limit) {
            self.stopped_early = true;
            return None;
        }
        self.stats.nodes += 1;
        if self.stats.nodes & 4095 == 0
            && self
                .wall_limit
                .is_some_and(|limit| self.started.elapsed() >= limit)
        {
            self.stopped_early = true;
            return None;
        }
        if raw_mask.count_ones() > self.limit {
            return None;
        }
        if self.has_ap(raw_mask, self.forbidden_ap) {
            self.stats.ap_prunes += 1;
            return None;
        }

        let mask = raw_mask;
        let remaining = self.limit - mask.count_ones();
        let mut constraints = Vec::new();

        let selected = values(mask, self.p);
        let mut counts = vec![0_u8; self.p as usize];
        for (index, &left) in selected.iter().enumerate() {
            for &right in &selected[index..] {
                counts[((left + right) % self.p) as usize] += 1;
            }
        }
        for sum in 0..self.p as usize {
            if counts[sum] != 1 {
                continue;
            }
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

    fn run(&mut self, initial_ap: u32, root: Option<u128>) -> Option<u128> {
        if self.limit < 3 {
            return None;
        }
        // The first r entries of 0,1,-1,2,-2,... form an r-term progression.
        // Any set containing such a progression has an affine image containing
        // this root. For r>3 the decision is restricted to that family.
        let mut initial = 1_u128;
        for index in 1..initial_ap {
            let point = if index % 2 == 1 {
                (index + 1) / 2
            } else {
                self.p - index / 2
            };
            initial |= 1_u128 << point;
        }
        if let Some(root) = root {
            initial = root;
        }
        self.dfs(initial)
    }
}

fn can_cover(constraints: &[Vec<u128>], chosen: u128, budget: u32) -> bool {
    let mut best = None;
    let mut best_count = usize::MAX;
    for (index, options) in constraints.iter().enumerate() {
        if options.iter().any(|option| *option & !chosen == 0) {
            continue;
        }
        let count = options
            .iter()
            .filter(|option| (chosen | **option).count_ones() <= budget)
            .count();
        if count == 0 {
            return false;
        }
        if count < best_count {
            best = Some(index);
            best_count = count;
        }
    }
    let Some(index) = best else {
        return true;
    };
    constraints[index].iter().any(|option| {
        let next = chosen | *option;
        next.count_ones() <= budget && can_cover(constraints, next, budget)
    })
}

fn values(mask: u128, p: u32) -> Vec<u32> {
    (0..p).filter(|value| mask & (1_u128 << value) != 0).collect()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if !(3..=7).contains(&args.len()) {
        eprintln!(
            "usage: {} PRIME LIMIT [NODE_LIMIT [INITIAL_AP [FORBID_AP [ROOT_MASK]]]]",
            args[0]
        );
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
    let initial_ap: u32 = args.get(4).map_or(3, |raw| raw.parse().expect("INITIAL_AP"));
    if initial_ap < 3 || initial_ap > p {
        eprintln!("INITIAL_AP must be between 3 and PRIME");
        std::process::exit(2);
    }
    let forbidden_ap: u32 = args.get(5).map_or(0, |raw| raw.parse().expect("FORBID_AP"));
    if forbidden_ap != 0 && (forbidden_ap < 3 || forbidden_ap > p) {
        eprintln!("FORBID_AP must be 0 or between 3 and PRIME");
        std::process::exit(2);
    }
    let root: Option<u128> = args.get(6).map(|raw| {
        u128::from_str_radix(
            raw.strip_prefix("0x")
                .or_else(|| raw.strip_prefix("0X"))
                .unwrap_or(raw),
            16,
        )
        .expect("ROOT_MASK hex")
    });
    let started = Instant::now();
    let mut search = Search::new(p, limit, node_limit);
    search.forbidden_ap = forbidden_ap;
    let result = search.run(initial_ap, root);
    let status = if result.is_some() {
        "SAT"
    } else if search.stopped_early {
        "UNKNOWN"
    } else {
        "UNSAT"
    };
    println!(
        "p={p} limit={limit} status={} initial_ap={initial_ap} forbid_ap={forbidden_ap} nodes={} memo_hits={} cover_prunes={} ap_prunes={} memo={} seconds={:.6}",
        status,
        search.stats.nodes,
        search.stats.memo_hits,
        search.stats.cover_prunes,
        search.stats.ap_prunes,
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
