//! Independent check of the ten D5 coordinate-stars.
//!
//! Replay:
//!   rustc -O -o verify_n1 verify_n1.rs && ./verify_n1
//!
//! Rebuilds the integer model a·a = 32, edge iff a·b ≤ 16.  Each of
//! the ten stars {x_i = ±4} ∩ D5 contains 16 four-seeds and an extras
//! pool of 80 with ω = 8, so the best 41-candidate on that U is 40.

use std::process;

const N: usize = 1480;
const N1: usize = 40;
const TARGET: i32 = 32;
const THRESH: i32 = 16;

fn enumerate_sphere() -> Vec<[i32; 5]> {
    let lim = 6;
    let mut pts = Vec::with_capacity(N);
    for a in -lim..=lim {
        let r2 = TARGET - a * a;
        for b in -lim..=lim {
            let r3 = r2 - b * b;
            if r3 < 0 {
                continue;
            }
            for c in -lim..=lim {
                let r4 = r3 - c * c;
                if r4 < 0 {
                    continue;
                }
                for e in -lim..=lim {
                    let rem = r4 - e * e;
                    if rem < 0 {
                        continue;
                    }
                    let mut f = 0;
                    while (f + 1) * (f + 1) <= rem {
                        f += 1;
                    }
                    if f * f != rem {
                        continue;
                    }
                    if f == 0 {
                        pts.push([a, b, c, e, 0]);
                    } else {
                        pts.push([a, b, c, e, f]);
                        pts.push([a, b, c, e, -f]);
                    }
                }
            }
        }
    }
    pts
}

fn ip(a: &[i32; 5], b: &[i32; 5]) -> i32 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3] + a[4] * b[4]
}

fn is_d5(p: &[i32; 5]) -> bool {
    let mut nz = 0;
    for &x in p {
        let a = x.abs();
        if a == 0 {
            continue;
        }
        nz += 1;
        if a != 4 {
            return false;
        }
    }
    nz == 2
}

fn omega(pool: &[usize], adj: &[Vec<bool>], target: usize) -> (usize, u64) {
    let m = pool.len();
    let mut local = vec![vec![false; m]; m];
    for i in 0..m {
        for j in 0..m {
            local[i][j] = adj[pool[i]][pool[j]];
        }
    }
    let mut nodes = 0u64;
    let mut best = 0usize;
    fn rec(
        local: &[Vec<bool>],
        cand: &[usize],
        clique: usize,
        best: &mut usize,
        nodes: &mut u64,
        target: usize,
    ) {
        *nodes += 1;
        if clique > *best {
            *best = clique;
        }
        if *best >= target {
            return;
        }
        for i in 0..cand.len() {
            if clique + (cand.len() - i) <= *best {
                return;
            }
            let v = cand[i];
            let nxt: Vec<usize> = cand[i + 1..]
                .iter()
                .copied()
                .filter(|&u| local[v][u])
                .collect();
            rec(local, &nxt, clique + 1, best, nodes, target);
            if *best >= target {
                return;
            }
        }
    }
    let cand: Vec<usize> = (0..m).collect();
    rec(&local, &cand, 0, &mut best, &mut nodes, target);
    (best, nodes)
}

fn main() {
    let pts = enumerate_sphere();
    if pts.len() != N {
        eprintln!("point count {} != {}", pts.len(), N);
        process::exit(1);
    }
    let d5: Vec<usize> = (0..pts.len()).filter(|&i| is_d5(&pts[i])).collect();
    if d5.len() != N1 {
        eprintln!("D5 count {} != {}", d5.len(), N1);
        process::exit(1);
    }
    let extras: Vec<usize> = (0..pts.len()).filter(|&i| !is_d5(&pts[i])).collect();
    let n = pts.len();
    let mut adj = vec![vec![false; n]; n];
    for i in 0..n {
        for j in i + 1..n {
            if ip(&pts[i], &pts[j]) <= THRESH {
                adj[i][j] = true;
                adj[j][i] = true;
            }
        }
    }
    let mut missed = vec![Vec::<usize>::new(); extras.len()];
    for (ei, &i) in extras.iter().enumerate() {
        for (j, &dj) in d5.iter().enumerate() {
            if !adj[i][dj] {
                missed[ei].push(j);
            }
        }
    }

    let mut stars = Vec::new();
    for axis in 0..5 {
        for &s in &[-4i32, 4] {
            let bits: Vec<usize> = (0..N1)
                .filter(|&j| pts[d5[j]][axis] == s)
                .collect();
            if bits.len() != 8 {
                eprintln!("star size {}", bits.len());
                process::exit(1);
            }
            stars.push(bits);
        }
    }
    if stars.len() != 10 {
        eprintln!("expected 10 stars");
        process::exit(1);
    }

    let mut ok = true;
    for (t, u) in stars.iter().enumerate() {
        let mut pool = Vec::new();
        for (ei, m) in missed.iter().enumerate() {
            if m.iter().all(|x| u.contains(x)) {
                pool.push(extras[ei]);
            }
        }
        let mut fours = std::collections::BTreeSet::<Vec<usize>>::new();
        for m in &missed {
            if m.len() == 4 && m.iter().all(|x| u.contains(x)) {
                let mut s = m.clone();
                s.sort_unstable();
                fours.insert(s);
            }
        }
        let n_four = fours.len();
        let (om, nodes) = omega(&pool, &adj, 9);
        println!(
            "star {} U={:?} four={} pool={} omega={} nodes={}",
            t,
            u,
            n_four,
            pool.len(),
            om,
            nodes
        );
        if n_four != 16 || pool.len() != 80 || om != 8 {
            ok = false;
        }
    }
    if !ok {
        eprintln!("FAIL");
        process::exit(1);
    }
    println!("ok stars=10 each_four=16 each_pool=80 each_omega=8");
}
