// check.rs -- independent replay for q1 (Rust, rustc only).
//
// Two modes.
//   count D            enumerate all normalised straight-line programs of at
//                      most D steps in the canonical pending-queue order and
//                      print nodes per depth plus the number of distinct
//                      positive integers reached within d steps (exact, with
//                      a small bignum for values >= 2^128).
//   sample D T SEED F  draw T random canonical prefixes of D steps (random
//                      descent) and, for every target in file F, decide by
//                      brute force whether the target is reachable in at
//                      most three further steps.  Prints one JSON line per
//                      prefix; compare_endgame.py feeds the same prefixes to
//                      the C endgame.
//
// The enumeration rule is the same theorem as in slp_search.c (see
// README.md) but the code shares nothing with it: values are an enum over
// u128 and a limb vector, membership uses HashSet, and the endgame is a
// direct expansion of all three-step extensions without case analysis.
use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
enum Val { S(u128), B(Vec<u64>) }   // B: little-endian limbs, len >= 3, top limb nonzero

fn norm(mut v: Vec<u64>) -> Val {
    while v.last() == Some(&0) { v.pop(); }
    if v.len() <= 2 {
        let lo = *v.get(0).unwrap_or(&0) as u128;
        let hi = *v.get(1).unwrap_or(&0) as u128;
        Val::S(lo | (hi << 64))
    } else { Val::B(v) }
}
fn limbs(v: &Val) -> Vec<u64> {
    match v { Val::S(x) => vec![*x as u64, (*x >> 64) as u64], Val::B(b) => b.clone() }
}
fn add(a: &Val, b: &Val) -> Val {
    if let (Val::S(x), Val::S(y)) = (a, b) { if let Some(s) = x.checked_add(*y) { return Val::S(s); } }
    let (la, lb) = (limbs(a), limbs(b)); let n = la.len().max(lb.len());
    let mut r = Vec::with_capacity(n + 1); let mut carry: u128 = 0;
    for i in 0..n { let s = carry + *la.get(i).unwrap_or(&0) as u128 + *lb.get(i).unwrap_or(&0) as u128; r.push(s as u64); carry = s >> 64; }
    r.push(carry as u64); norm(r)
}
fn cmp(a: &Val, b: &Val) -> std::cmp::Ordering {
    match (a, b) {
        (Val::S(x), Val::S(y)) => x.cmp(y),
        (Val::S(_), Val::B(_)) => std::cmp::Ordering::Less,
        (Val::B(_), Val::S(_)) => std::cmp::Ordering::Greater,
        (Val::B(x), Val::B(y)) => { if x.len() != y.len() { return x.len().cmp(&y.len()); } for i in (0..x.len()).rev() { if x[i] != y[i] { return x[i].cmp(&y[i]); } } std::cmp::Ordering::Equal }
    }
}
fn sub(a: &Val, b: &Val) -> Val {   // requires a >= b
    if let (Val::S(x), Val::S(y)) = (a, b) { return Val::S(x - y); }
    let (la, lb) = (limbs(a), limbs(b)); let mut r = Vec::with_capacity(la.len()); let mut borrow: i128 = 0;
    for i in 0..la.len() { let mut d = la[i] as i128 - *lb.get(i).unwrap_or(&0) as i128 - borrow; if d < 0 { d += 1i128 << 64; borrow = 1; } else { borrow = 0; } r.push(d as u64); }
    assert!(borrow == 0); norm(r)
}
fn mul(a: &Val, b: &Val) -> Val {
    if let (Val::S(x), Val::S(y)) = (a, b) { if let Some(p) = x.checked_mul(*y) { return Val::S(p); } }
    let (la, lb) = (limbs(a), limbs(b)); let mut r = vec![0u64; la.len() + lb.len()];
    for i in 0..la.len() { let mut carry: u128 = 0; for j in 0..lb.len() { let t = la[i] as u128 * lb[j] as u128 + r[i + j] as u128 + carry; r[i + j] = t as u64; carry = t >> 64; } r[i + lb.len()] = carry as u64; }
    norm(r)
}
fn absdiff(a: &Val, b: &Val) -> Option<Val> {
    match cmp(a, b) { std::cmp::Ordering::Equal => None, std::cmp::Ordering::Greater => Some(sub(a, b)), std::cmp::Ordering::Less => Some(sub(b, a)) }
}
fn ops(a: &Val, b: &Val) -> Vec<Val> { let mut v = vec![add(a, b), mul(a, b)]; if let Some(d) = absdiff(a, b) { v.push(d); } v }

struct State { set: Vec<Val>, queue: Vec<Val>, members: HashSet<Val>, queued: HashSet<Val>, block_start: Vec<usize>, positions: Vec<usize> }
impl State {
    fn new() -> State {
        let one = Val::S(1); let two = Val::S(2);
        let mut members = HashSet::new(); members.insert(one.clone());
        let mut queued = HashSet::new(); queued.insert(two.clone());
        State { set: vec![one], queue: vec![two], members, queued, block_start: vec![], positions: vec![] }
    }
    fn push(&mut self, pos: usize) {
        let v = self.queue[pos].clone();
        self.block_start.push(self.queue.len()); self.positions.push(pos);
        self.queued.remove(&v); self.members.insert(v.clone()); self.set.push(v.clone());
        let snapshot: Vec<Val> = self.set.clone();
        for s in snapshot.iter() { for r in ops(&v, s) { if !self.members.contains(&r) && !self.queued.contains(&r) { self.queued.insert(r.clone()); self.queue.push(r); } } }
    }
    fn pop(&mut self) {
        let bs = self.block_start.pop().unwrap(); self.positions.pop();
        for i in bs..self.queue.len() { let r = self.queue[i].clone(); self.queued.remove(&r); }
        self.queue.truncate(bs);
        let v = self.set.pop().unwrap(); self.members.remove(&v); self.queued.insert(v);
    }
}

fn count_mode(dmax: usize) {
    let mut st = State::new();
    let mut nodes = vec![0u64; dmax + 1];
    let mut reached: HashMap<Val, usize> = HashMap::new();   // value -> least depth
    reached.insert(Val::S(1), 0);
    fn rec(st: &mut State, start: usize, depth: usize, dmax: usize, nodes: &mut Vec<u64>, reached: &mut HashMap<Val, usize>) {
        let end = st.queue.len();
        for pos in start..end {
            st.push(pos);
            nodes[depth] += 1;
            let v = st.set.last().unwrap().clone();
            let e = reached.entry(v).or_insert(depth); if *e > depth { *e = depth; }
            if depth < dmax { rec(st, pos + 1, depth + 1, dmax, nodes, reached); }
            st.pop();
        }
    }
    rec(&mut st, 0, 1, dmax, &mut nodes, &mut reached);
    let mut per = vec![0usize; dmax + 1]; for (_, d) in reached.iter() { per[*d] += 1; }
    let mut cum = 0usize; let mut cums = vec![];
    for d in 0..=dmax { cum += per[d]; cums.push(cum); }
    let bound: u128 = env::args().nth(3).map(|s| s.parse().unwrap()).unwrap_or(0);
    let mut table = vec![];
    for n in 1..=bound { table.push(match reached.get(&Val::S(n)) { Some(d) => *d as i64, None => -1 }); }
    println!("{{\"nodes_per_depth\": {:?}, \"reached_cumulative\": {:?}, \"tau_table_bound\": {}, \"tau\": {:?}}}", &nodes[1..], cums, bound, table);
}

// xorshift for reproducible sampling
struct Rng(u64);
impl Rng { fn next(&mut self) -> u64 { let mut x = self.0; x ^= x << 13; x ^= x >> 7; x ^= x << 17; self.0 = x; x } fn below(&mut self, n: usize) -> usize { (self.next() % n as u64) as usize } }

fn parse_val(s: &str) -> Val { Val::S(s.trim().parse::<u128>().expect("target must be below 2^128")) }
fn show(v: &Val) -> String {
    match v { Val::S(x) => x.to_string(), Val::B(_) => { // decimal via repeated division by 10^18
        let mut l = limbs(v); let mut chunks = vec![];
        while !l.is_empty() { let mut rem: u128 = 0; for i in (0..l.len()).rev() { let cur = (rem << 64) | l[i] as u128; l[i] = (cur / 1_000_000_000_000_000_000u128) as u64; rem = cur % 1_000_000_000_000_000_000u128; } while l.last() == Some(&0) { l.pop(); } chunks.push(rem as u64); }
        let mut s = chunks.last().unwrap().to_string(); for c in chunks.iter().rev().skip(1) { s.push_str(&format!("{:018}", c)); } s } }
}

/// brute force: least number of further steps (0..=3) to reach target, or -1
fn brute(st: &State, target: &Val) -> i32 {
    if st.members.contains(target) { return 0; }
    if st.queued.contains(target) { return 1; }
    let s0: Vec<Val> = st.set.clone();
    let q: Vec<Val> = st.queue.iter().filter(|v| st.queued.contains(*v)).cloned().collect();
    let mut best = -1;
    for y1 in q.iter() {
        let mut s1 = s0.clone(); s1.push(y1.clone());
        // two steps: target = y1 o u, u in s1
        for u in s1.iter() { if ops(y1, u).iter().any(|r| r == target) { return 2; } }
        // three steps: y2 from s1 (must involve y1 or be any pair; take all pairs), then target = y2 o w
        let mut l2: HashSet<Val> = HashSet::new();
        for a in s1.iter() { for b in s1.iter() { for r in ops(a, b) { if !st.members.contains(&r) && r != *y1 { l2.insert(r); } } } }
        for y2 in l2.iter() {
            for w in s1.iter().chain(std::iter::once(y2)) { if ops(y2, w).iter().any(|r| r == target) { best = 3; } }
            if best == 3 { return 3; }
        }
    }
    best
}

/// full three-step reach set with minimal step counts (1..=3); values below 2^128 only
fn reach_all(st: &State) -> Vec<(Val, i32)> {
    let mut best: HashMap<Val, i32> = HashMap::new();
    let s0: Vec<Val> = st.set.clone();
    let q: Vec<Val> = st.queue.iter().filter(|v| st.queued.contains(*v)).cloned().collect();
    for y1 in q.iter() { best.entry(y1.clone()).or_insert(1); }
    for y1 in q.iter() {
        let mut s1 = s0.clone(); s1.push(y1.clone());
        let mut l2: Vec<Val> = vec![];
        for u in s1.iter() { for r in ops(y1, u) { if !st.members.contains(&r) && r != *y1 { let e = best.entry(r.clone()).or_insert(2); if *e > 2 { *e = 2; } l2.push(r); } } }
        // y2 not involving y1 is covered at level <= 2 unless the last step uses y1 too
        let mut l2b: Vec<Val> = vec![];
        for a in s0.iter() { for b in s0.iter() { for r in ops(a, b) { if !st.members.contains(&r) && r != *y1 { l2b.push(r); } } } }
        for y2 in l2.iter() { for w in s1.iter().chain(std::iter::once(y2)) { for r in ops(y2, w) { let e = best.entry(r.clone()).or_insert(3); if *e > 3 { *e = 3; } } } }
        for y2 in l2b.iter() { for r in ops(y2, y1) { let e = best.entry(r.clone()).or_insert(3); if *e > 3 { *e = 3; } } }
    }
    best.into_iter().filter(|(v, _)| matches!(v, Val::S(_)) && !st.members.contains(v)).collect()
}

fn sample_mode(dmax: usize, trials: usize, seed: u64, tfile: &str) {
    let txt = fs::read_to_string(tfile).expect("targets file");
    let targets: Vec<(String, Val)> = txt.lines().filter(|l| !l.trim().is_empty() && !l.starts_with('#')).map(|l| { let mut it = l.split_whitespace(); let name = it.next().unwrap().to_string(); let val = it.next().unwrap(); (name, parse_val(val)) }).collect();
    let mut rng = Rng(seed | 1);
    for _ in 0..trials {
        let mut st = State::new();
        let mut start = 0;
        for _ in 0..dmax { let end = st.queue.len(); let pos = start + rng.below(end - start); st.push(pos); start = pos + 1; }
        let prefix: Vec<String> = st.set.iter().map(show).collect();
        let mut res = vec![];
        for (name, t) in targets.iter() { res.push(format!("{{\"name\": \"{}\", \"steps\": {}}}", name, brute(&st, t))); }
        // a random selection of genuinely reachable values, for the positive side of the comparison
        let mut all = reach_all(&st);
        let mut members = vec![];
        for _ in 0..24 { if all.is_empty() { break; } let i = rng.below(all.len()); let (v, s) = all.swap_remove(i); members.push(format!("{{\"value\": \"{}\", \"steps\": {}}}", show(&v), s)); }
        println!("{{\"prefix\": [{}], \"results\": [{}], \"members\": [{}]}}", prefix.iter().map(|p| format!("\"{}\"", p)).collect::<Vec<_>>().join(","), res.join(","), members.join(","));
    }
}

fn main() {
    let a: Vec<String> = env::args().collect();
    match a.get(1).map(|s| s.as_str()) {
        Some("count") => count_mode(a[2].parse().unwrap()),
        Some("sample") => sample_mode(a[2].parse().unwrap(), a[3].parse().unwrap(), a[4].parse().unwrap(), &a[5]),
        _ => eprintln!("usage: check count D | check sample D T SEED TARGETS"),
    }
}
