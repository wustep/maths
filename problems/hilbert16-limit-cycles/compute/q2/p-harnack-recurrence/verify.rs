//! Second verifier for the Harnack-recurrence replay of
//! arXiv:2510.11705v2 Corollary 2.
//!
//! Independent of verify.py: integer Har(m), pointwise max of the
//! emitted seed tables, exhaustive n+m <= 50 comparisons, Kolmogorov
//! H_K(5) arithmetic. rustc only.

use std::collections::BTreeMap;
use std::fs;
use std::io::Write;
use std::path::PathBuf;

fn fail(msg: &str) -> ! {
    eprintln!("verify.rs FAIL: {msg}");
    std::process::exit(1);
}

fn har(m: i64) -> i64 {
    if m < 1 {
        fail(&format!("Har index {m} < 1"));
    }
    let ovals = (m - 1) * (m - 2) / 2;
    let sign = if m % 2 == 0 { 1 } else { -1 };
    let parity = (1 + sign) / 2;
    let alt = if m % 2 == 0 { 1 } else { 0 };
    if parity != alt {
        fail(&format!("Har parity formulas disagree at m={m}"));
    }
    ovals + parity
}

fn combine_l_pub(sources: &[BTreeMap<i64, i64>]) -> BTreeMap<i64, i64> {
    let mut out = BTreeMap::new();
    for table in sources {
        for (&n, &val) in table {
            let e = out.entry(n).or_insert(val);
            if val > *e {
                *e = val;
            }
        }
    }
    out
}

fn increment_closed_recorded(n: i64, l_pub: &BTreeMap<i64, i64>) -> i64 {
    let mut best = l_pub.get(&n).copied().unwrap_or(0);
    for (&k, &val) in l_pub {
        if k < n {
            let cand = val + (n - k);
            if cand > best {
                best = cand;
            }
        }
    }
    best
}

fn chebyshev_one_step(seeds: &BTreeMap<i64, i64>, n_max: i64) -> BTreeMap<i64, i64> {
    let mut out = BTreeMap::new();
    for n_tot in 1..=n_max {
        let np = n_tot + 1;
        let mut best: Option<i64> = None;
        for m in 2..=np {
            if np % m != 0 {
                continue;
            }
            let n = np / m - 1;
            if n < 1 {
                continue;
            }
            if let Some(&seed) = seeds.get(&n) {
                let lift = m * m * seed;
                best = Some(best.map_or(lift, |b| b.max(lift)));
            }
        }
        if let Some(val) = best {
            out.insert(n_tot, val);
        }
    }
    out
}

// ---------------------------------------------------------------------------
// Tiny JSON reader for the integer tables Python emits.
// ---------------------------------------------------------------------------

fn skip_ws(s: &[u8], i: &mut usize) {
    while *i < s.len() && s[*i].is_ascii_whitespace() {
        *i += 1;
    }
}

fn expect(s: &[u8], i: &mut usize, c: u8) {
    skip_ws(s, i);
    if *i >= s.len() || s[*i] != c {
        fail(&format!(
            "expected '{}' at {i}, got {}",
            c as char,
            s.get(*i).map(|b| *b as char).unwrap_or('?')
        ));
    }
    *i += 1;
}

fn parse_string(s: &[u8], i: &mut usize) -> String {
    skip_ws(s, i);
    expect(s, i, b'"');
    let start = *i;
    while *i < s.len() && s[*i] != b'"' {
        *i += 1;
    }
    if *i >= s.len() {
        fail("unterminated string");
    }
    let out = String::from_utf8(s[start..*i].to_vec()).unwrap_or_else(|_| fail("utf8"));
    *i += 1;
    out
}

fn parse_i64(s: &[u8], i: &mut usize) -> i64 {
    skip_ws(s, i);
    let start = *i;
    if *i < s.len() && s[*i] == b'-' {
        *i += 1;
    }
    while *i < s.len() && s[*i].is_ascii_digit() {
        *i += 1;
    }
    if start == *i || (*i == start + 1 && s[start] == b'-') {
        fail("expected integer");
    }
    let txt = std::str::from_utf8(&s[start..*i]).unwrap_or_else(|_| fail("int utf8"));
    txt.parse::<i64>().unwrap_or_else(|_| fail("int parse"))
}

fn parse_pair_list(s: &[u8], i: &mut usize) -> BTreeMap<i64, i64> {
    let mut out = BTreeMap::new();
    expect(s, i, b'[');
    loop {
        skip_ws(s, i);
        if *i < s.len() && s[*i] == b']' {
            *i += 1;
            break;
        }
        expect(s, i, b'[');
        let n = parse_i64(s, i);
        expect(s, i, b',');
        let v = parse_i64(s, i);
        expect(s, i, b']');
        out.insert(n, v);
        skip_ws(s, i);
        if *i < s.len() && s[*i] == b',' {
            *i += 1;
            continue;
        }
        expect(s, i, b']');
        break;
    }
    out
}

fn parse_tables(src: &str) -> (i64, BTreeMap<String, BTreeMap<i64, i64>>) {
    let s = src.as_bytes();
    let mut i = 0;
    expect(s, &mut i, b'{');
    let mut maps = BTreeMap::new();
    let mut n_max = 0i64;
    loop {
        skip_ws(s, &mut i);
        if i < s.len() && s[i] == b'}' {
            break;
        }
        let key = parse_string(s, &mut i);
        expect(s, &mut i, b':');
        skip_ws(s, &mut i);
        if i < s.len() && s[i] == b'[' {
            maps.insert(key, parse_pair_list(s, &mut i));
        } else {
            let val = parse_i64(s, &mut i);
            if key == "N_max" {
                n_max = val;
            } else {
                fail(&format!("unexpected scalar key {key}"));
            }
        }
        skip_ws(s, &mut i);
        if i < s.len() && s[i] == b',' {
            i += 1;
            continue;
        }
        expect(s, &mut i, b'}');
        break;
    }
    if n_max < 2 {
        fail("N_max missing");
    }
    (n_max, maps)
}

fn require_map<'a>(
    maps: &'a BTreeMap<String, BTreeMap<i64, i64>>,
    name: &str,
) -> &'a BTreeMap<i64, i64> {
    maps.get(name)
        .unwrap_or_else(|| fail(&format!("missing table {name}")))
}

fn cwd_certs() -> PathBuf {
    let certs = std::env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .join("certs");
    fs::create_dir_all(&certs).unwrap_or_else(|e| fail(&format!("mkdir certs: {e}")));
    certs
}

fn write_json_i_map(body: &mut String, map: &BTreeMap<i64, i64>, indent: &str) {
    body.push_str("{\n");
    let keys: Vec<_> = map.keys().copied().collect();
    for (i, n) in keys.iter().enumerate() {
        let comma = if i + 1 == keys.len() { "" } else { "," };
        body.push_str(&format!("{indent}  \"{n}\": {}{comma}\n", map[n]));
    }
    body.push_str(indent);
    body.push('}');
}

fn write_core(
    n_max: i64,
    n_pairs: i64,
    har_named: &[i64],
    har_all: &BTreeMap<i64, i64>,
    l_pub: &BTreeMap<i64, i64>,
    m1: &(i64, i64, i64, i64, i64),
    four: &BTreeMap<i64, i64>,
    harnack_four: &BTreeMap<i64, i64>,
    best_recorded: &BTreeMap<i64, (i64, i64, i64)>,
    example_h6: i64,
    l_pub_6: i64,
) {
    let path = cwd_certs().join("rust_core.json");
    let mut body = String::new();
    body.push_str("{\n");
    body.push_str(&format!("  \"N_max\": {n_max},\n"));
    body.push_str(&format!("  \"n_pairs\": {n_pairs},\n"));
    body.push_str("  \"Har_1_to_6\": [");
    for (i, v) in har_named.iter().enumerate() {
        if i > 0 {
            body.push_str(", ");
        }
        body.push_str(&v.to_string());
    }
    body.push_str("],\n  \"Har\": ");
    write_json_i_map(&mut body, har_all, "  ");
    body.push_str(",\n  \"L_pub\": ");
    write_json_i_map(&mut body, l_pub, "  ");
    body.push_str(",\n  \"n_beats_quoted_m_ge_2\": 0,\n");
    body.push_str("  \"n_beats_closed_recorded\": 0,\n");
    body.push_str("  \"n_beats_claimed\": 0,\n");
    body.push_str("  \"m1_quoted_exceedances\": [\n    {\n");
    body.push_str(&format!("      \"n\": {},\n", m1.0));
    body.push_str(&format!("      \"m\": {},\n", m1.1));
    body.push_str(&format!("      \"N\": {},\n", m1.2));
    body.push_str(&format!("      \"lift\": {},\n", m1.3));
    body.push_str(&format!("      \"L_pub_N\": {},\n", m1.4));
    body.push_str("      \"L_pub_n\": 384,\n");
    body.push_str("      \"Har_m\": 0,\n");
    body.push_str("      \"increment_would_give\": 385,\n");
    body.push_str("      \"is_dent\": false\n");
    body.push_str("    }\n  ],\n");
    body.push_str("  \"H_K_5\": 28,\n");
    body.push_str("  \"L_pub_4\": 28,\n");
    body.push_str("  \"L_pub_5\": 37,\n");
    body.push_str("  \"H_K_5_equals_L_pub_4\": true,\n");
    body.push_str("  \"H_K_5_equals_9\": false,\n");
    body.push_str("  \"H_K_5_beats_H_5\": false,\n");
    body.push_str("  \"Har_1\": 0,\n");
    body.push_str("  \"weaker_than_increment\": true,\n");
    body.push_str("  \"four_chebyshev\": {\n");
    let four_keys: Vec<_> = four.keys().copied().collect();
    for (i, n) in four_keys.iter().enumerate() {
        let comma = if i + 1 == four_keys.len() { "" } else { "," };
        body.push_str(&format!("    \"{n}\": {}{comma}\n", four[n]));
    }
    body.push_str("  },\n  \"harnack_vs_four\": {\n");
    for (i, n) in four_keys.iter().enumerate() {
        let comma = if i + 1 == four_keys.len() { "" } else { "," };
        body.push_str(&format!("    \"{n}\": {}{comma}\n", harnack_four[n]));
    }
    body.push_str("  },\n");
    body.push_str("  \"do_not_claim_252_1080_1380_2012_as_ours\": true,\n");
    body.push_str("  \"do_not_claim_HK5_28_as_ours\": true,\n");
    body.push_str("  \"best_harnack\": {\n");
    let best_keys: Vec<_> = best_recorded.keys().copied().collect();
    for (i, n) in best_keys.iter().enumerate() {
        let (lift, nn, mm) = best_recorded[n];
        let comma = if i + 1 == best_keys.len() { "" } else { "," };
        body.push_str(&format!(
            "    \"{n}\": {{\n      \"lift\": {lift},\n      \"n\": {nn},\n      \"m\": {mm}\n    }}{comma}\n"
        ));
    }
    body.push_str("  },\n");
    body.push_str(&format!("  \"example_H6_from_H2\": {example_h6},\n"));
    body.push_str(&format!("  \"L_pub_6\": {l_pub_6},\n"));
    body.push_str("  \"L_closed_18\": 385\n}\n");

    let mut fh = fs::File::create(&path).unwrap_or_else(|e| fail(&format!("write {path:?}: {e}")));
    fh.write_all(body.as_bytes())
        .unwrap_or_else(|e| fail(&format!("write {path:?}: {e}")));
}

fn write_table(best_all: &BTreeMap<i64, (i64, i64, i64)>, l_pub: &BTreeMap<i64, i64>) {
    let path = cwd_certs().join("rust_table.json");
    let mut body = String::from("{\n  \"best_harnack_N_le_50\": {\n");
    let keys: Vec<_> = best_all.keys().copied().collect();
    for (i, n) in keys.iter().enumerate() {
        let (lift, nn, mm) = best_all[n];
        let comma = if i + 1 == keys.len() { "" } else { "," };
        body.push_str(&format!(
            "    \"{n}\": {{\"lift\": {lift}, \"n\": {nn}, \"m\": {mm}}}{comma}\n"
        ));
    }
    body.push_str("  },\n  \"L_pub\": ");
    write_json_i_map(&mut body, l_pub, "  ");
    body.push_str(",\n  \"n_beats_claimed\": 0\n}\n");
    fs::write(&path, body).unwrap_or_else(|e| fail(&format!("write table: {e}")));
}

fn main() {
    let tables_path = cwd_certs().join("tables.json");
    let src = fs::read_to_string(&tables_path)
        .unwrap_or_else(|e| fail(&format!("read {tables_path:?}: {e}")));
    let (n_max, maps) = parse_tables(&src);

    let small = require_map(&maps, "SMALL_PUB");
    let pt = require_map(&maps, "PT_THM1");
    let han = require_map(&maps, "HAN_LI_APP_A");
    let cor2 = require_map(&maps, "PT_COR2");
    let han_only = require_map(&maps, "HAN_LI_TABLE1_ONLY");
    let lch_paper = require_map(&maps, "PAPER_L_CH");
    let four = require_map(&maps, "PAPER_FOUR_NEW");
    let seeds_app_a = require_map(&maps, "SEEDS_APP_A");

    let l_pub = combine_l_pub(&[
        small.clone(),
        pt.clone(),
        han.clone(),
        cor2.clone(),
        han_only.clone(),
        lch_paper.clone(),
    ]);

    let named_expected = [0i64, 1, 1, 4, 6, 11];
    let mut har_named = Vec::new();
    for m in 1..=6 {
        let v = har(m);
        har_named.push(v);
        if v != named_expected[(m - 1) as usize] {
            fail(&format!("Har({m}) = {v} != {}", named_expected[(m - 1) as usize]));
        }
    }
    if har(1) != 0 {
        fail("Har(1) != 0");
    }
    let mut har_all = BTreeMap::new();
    for m in 1..=n_max {
        har_all.insert(m, har(m));
    }

    if l_pub.get(&4).copied() != Some(28) {
        fail("L_pub[4] != 28");
    }
    if l_pub.get(&5).copied() != Some(37) {
        fail("L_pub[5] != 37");
    }
    if l_pub.get(&14).copied() != Some(252) {
        fail("L_pub[14] must include Chebyshev 252");
    }
    if l_pub.get(&18).copied() != Some(372) {
        fail("L_pub[18] must be the Han–Li quoted 372");
    }

    let mut n_pairs = 0i64;
    let mut quoted_m_ge_2 = 0i64;
    let mut closed_beats = 0i64;
    let mut m1_quoted: Vec<(i64, i64, i64, i64, i64)> = Vec::new();
    let mut best_all: BTreeMap<i64, (i64, i64, i64)> = BTreeMap::new();

    for n in 1..n_max {
        for m in 1..=(n_max - n) {
            n_pairs += 1;
            let n_tot = n + m;
            let seed = l_pub.get(&n).copied().unwrap_or(0);
            let lift = seed + har(m);
            let recorded = l_pub.contains_key(&n_tot);
            if recorded {
                let l_at = l_pub[&n_tot];
                let closed = increment_closed_recorded(n_tot, &l_pub);
                if lift > l_at && m >= 2 {
                    quoted_m_ge_2 += 1;
                }
                if lift > l_at && m == 1 {
                    m1_quoted.push((n, m, n_tot, lift, l_at));
                }
                if lift > closed {
                    closed_beats += 1;
                }
            }
            let cur = best_all.get(&n_tot).copied();
            let better = match cur {
                None => true,
                Some((bl, bn, bm)) => (lift, n, m) > (bl, bn, bm),
            };
            if better {
                best_all.insert(n_tot, (lift, n, m));
            }
        }
    }

    let expected_pairs = n_max * (n_max - 1) / 2;
    if n_pairs != expected_pairs {
        fail(&format!("pair count {n_pairs} != {expected_pairs}"));
    }
    if quoted_m_ge_2 != 0 {
        fail("m>=2 pair exceeds quoted L_pub");
    }
    if closed_beats != 0 {
        fail("pair exceeds increment-closed published bound");
    }
    if m1_quoted.len() != 1
        || m1_quoted[0] != (17, 1, 18, 384, 372)
    {
        fail(&format!("unexpected m=1 quoted exceedances {m1_quoted:?}"));
    }
    if increment_closed_recorded(18, &l_pub) != 385 {
        fail("increment-closed L(18) != 385");
    }

    let l_ch = chebyshev_one_step(seeds_app_a, n_max);
    for (&n, &paper_val) in lch_paper {
        match l_ch.get(&n) {
            Some(&got) if got == paper_val => {}
            other => fail(&format!("L_Ch({n}) = {other:?} != paper {paper_val}")),
        }
    }

    let mut harnack_four = BTreeMap::new();
    for (&n, &paper_val) in four {
        let (lift, _, _) = best_all.get(&n).copied().unwrap_or_else(|| fail("four N missing"));
        if lift > paper_val {
            fail(&format!("Harnack lift at {n} beats Chebyshev {paper_val}"));
        }
        harnack_four.insert(n, lift);
    }

    let hk5 = l_pub[&4];
    if hk5 != 28 {
        fail("H_K(5) replay is not 28");
    }
    if hk5 == 9 {
        fail("H_K(5) is not the Section-6 nine-oval field");
    }
    if hk5 >= l_pub[&5] {
        fail("H_K(5)>=28 must not beat planar H(5)>=37");
    }

    let example_h6 = l_pub[&2] + har(4);
    if example_h6 != 8 {
        fail(&format!("H(2)+Har(4) = {example_h6} != 8"));
    }
    let l_pub_6 = l_pub[&6];
    if l_pub_6 != 53 {
        fail("L_pub[6] != 53");
    }

    let mut best_recorded = BTreeMap::new();
    for (&n, &triple) in &best_all {
        if n >= 2 && l_pub.contains_key(&n) {
            best_recorded.insert(n, triple);
        }
    }

    write_core(
        n_max,
        n_pairs,
        &har_named,
        &har_all,
        &l_pub,
        &m1_quoted[0],
        four,
        &harnack_four,
        &best_recorded,
        example_h6,
        l_pub_6,
    );
    write_table(&best_all, &l_pub);

    println!("verify.rs: ok");
    println!("  pairs N=n+m<=50 = {n_pairs}");
    println!("  Har(1..6) = {har_named:?}");
    println!("  quoted m>=2 beats = 0");
    println!("  closed recorded beats = 0");
    println!("  claimed beats = 0");
    println!("  m=1 quoted exceedance N=18: 384 vs 372 (not a dent; increment 385)");
    println!("  H_K(5)>=28 == L_pub[4] = true; ==9? false");
    println!("  H(2)+Har(4) = {example_h6} vs L_pub[6]={l_pub_6}");
}
