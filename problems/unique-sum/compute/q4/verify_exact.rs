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

struct MaskSet {
    slots: Vec<u64>,
    len: usize,
}

impl MaskSet {
    fn new() -> Self {
        Self {
            slots: vec![0; 1024],
            len: 0,
        }
    }

    fn hash(mut value: u64) -> usize {
        value ^= value >> 30;
        value = value.wrapping_mul(0xbf58_476d_1ce4_e5b9);
        value ^= value >> 27;
        value = value.wrapping_mul(0x94d0_49bb_1331_11eb);
        (value ^ (value >> 31)) as usize
    }

    fn insert_without_growing(&mut self, value: u64) -> bool {
        debug_assert_ne!(value, 0);
        let mut index = Self::hash(value) & (self.slots.len() - 1);
        loop {
            match self.slots[index] {
                0 => {
                    self.slots[index] = value;
                    self.len += 1;
                    return true;
                }
                present if present == value => return false,
                _ => index = (index + 1) & (self.slots.len() - 1),
            }
        }
    }

    fn insert(&mut self, value: u64) -> bool {
        if (self.len + 1) * 10 >= self.slots.len() * 7 {
            let new_capacity = self.slots.len() * 2;
            let old_slots = std::mem::replace(&mut self.slots, vec![0; new_capacity]);
            self.len = 0;
            for old in old_slots {
                if old != 0 {
                    self.insert_without_growing(old);
                }
            }
        }
        self.insert_without_growing(value)
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
    max_memo: usize,
}

struct Search {
    p: u32,
    limit: u32,
    pairs_by_sum: Vec<Vec<u64>>,
    inverses: Vec<u32>,
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
        Self {
            p,
            limit,
            pairs_by_sum,
            inverses,
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

        let mask = self.canonical(raw_mask);
        if !self.memo.insert(mask) {
            self.stats.memo_hits += 1;
            return None;
        }
        self.stats.max_memo = self.stats.max_memo.max(self.memo.len());

        let remaining = self.limit - mask.count_ones();
        let mut constraints = Vec::new();

        for sum in 0..self.p as usize {
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
    let mut best: Option<Vec<u64>> = None;
    for options in constraints {
        if options.iter().any(|option| *option & !chosen == 0) {
            continue;
        }
        let mut next: Vec<u64> = options
            .iter()
            .map(|option| chosen | option)
            .filter(|candidate| candidate.count_ones() <= budget)
            .collect();
        next.sort_unstable_by_key(|candidate| (candidate.count_ones(), *candidate));
        next.dedup();
        if next.is_empty() {
            return false;
        }
        if best.as_ref().is_none_or(|current| next.len() < current.len()) {
            best = Some(next);
        }
    }
    let Some(next) = best else {
        return true;
    };
    next.into_iter()
        .any(|candidate| can_cover(constraints, candidate, budget))
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
