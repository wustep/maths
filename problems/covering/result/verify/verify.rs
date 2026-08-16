// Verifier #2 for the covering-code artifact.  Rust, no crates, `rustc` only.
//
//   rustc -O -o verify_rs verify.rs
//
// Same contract as verify.py: read a binary r x n parity-check matrix from a
// plain text file, confirm that its column set S satisfies
// {0} u S u (S+S) = F_2^r, and report the invariants.  Emits the same
// key<TAB>value lines, sorted, so the two dumps can be diffed byte for byte.
//
// COLUMN ENCODING.  LSB-first: bit k of the integer encoding of a column is
// row k+1 of the matrix.  The hexadecimal listing of M_KR in arXiv:2511.02542
// Theorem 4.3 is the opposite convention (row 1 is the most significant of the
// r bits) and is reversed on import by build_propagation.py.  If the KR matrix
// alone fails a check, suspect bit order rather than mathematics.
//
// WHY THIS IS NOT A PORT OF verify.py.  Sharing the encoding is unavoidable --
// that is the file format, not an algorithm.  Everything else is deliberately
// different:
//
//   * coverage runs in the opposite direction.  verify.py is pair-driven: walk
//     the C(n,2) pairs and mark what they hit.  This file is syndrome-driven:
//     for every s in 0..2^r, scan the columns and ask whether s ^ h is in a
//     membership table.  A transcription slip in one does not reproduce in the
//     other.  This file then ALSO runs its own pair loop for the multiplicity
//     histogram and asserts the two verdicts agree before reporting anything.
//   * rank pivots on the highest set bit; verify.py pivots on the lowest.
//   * the parser accumulates column integers while streaming tokens instead of
//     building rows and transposing.
//   * the density is reduced with an explicit u128 gcd and printed by long
//     division, not by a rational library.
//   * the partition check marks cross-block pair sums into a table and then
//     sweeps the syndromes, instead of scanning for a partner per syndrome.
//   * minimality is derived per syndrome from the multiplicity of that
//     syndrome and the contribution of the deleted column, rather than by
//     walking the deleted column's star.
//
// Nothing here reads a stored certificate.  No sampling, no early exit from
// the syndrome sweep.

use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::process;

// ---------------------------------------------------------------------------
// parsing
// ---------------------------------------------------------------------------

/// Read an r x n 0/1 matrix, accumulating column integers as tokens stream by.
fn parse_matrix(path: &str) -> (usize, usize, Vec<u64>) {
    let text = fs::read_to_string(path)
        .unwrap_or_else(|e| fatal(&format!("cannot read {}: {}", path, e)));

    let mut columns: Vec<u64> = Vec::new();
    let mut row_index: usize = 0;
    let mut width: Option<usize> = None;

    for (lineno, raw) in text.lines().enumerate() {
        let line = match raw.find('#') {
            Some(pos) => &raw[..pos],
            None => raw,
        };
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let mut col_index: usize = 0;
        for tok in line.split_whitespace() {
            let bit = match tok {
                "0" => 0u64,
                "1" => 1u64,
                _ => fatal(&format!(
                    "{}:{}: token {:?} is not 0 or 1",
                    path,
                    lineno + 1,
                    tok
                )),
            };
            if row_index == 0 {
                columns.push(0);
            } else if col_index >= columns.len() {
                fatal(&format!(
                    "{}: row {} is longer than row 1",
                    path,
                    row_index + 1
                ));
            }
            if bit == 1 {
                columns[col_index] |= 1u64 << row_index;
            }
            col_index += 1;
        }
        match width {
            None => width = Some(col_index),
            Some(w) => {
                if w != col_index {
                    fatal(&format!(
                        "{}: row {} has {} entries, row 1 has {}",
                        path,
                        row_index + 1,
                        col_index,
                        w
                    ));
                }
            }
        }
        row_index += 1;
    }

    let r = row_index;
    let n = width.unwrap_or_else(|| fatal(&format!("{}: no data rows", path)));
    if r == 0 || r > 63 {
        fatal(&format!("{}: r = {} out of supported range", path, r));
    }
    (r, n, columns)
}

fn fatal(message: &str) -> ! {
    eprintln!("verify.rs: {}", message);
    process::exit(1);
}

fn require(condition: bool, message: &str) {
    if !condition {
        fatal(message);
    }
}

// ---------------------------------------------------------------------------
// linear algebra over F_2 -- pivot on the HIGHEST set bit
// ---------------------------------------------------------------------------

fn f2_rank(columns: &[u64], r: usize) -> usize {
    let mut pivot: Vec<u64> = vec![0; r];
    let mut rank = 0usize;
    for &col in columns {
        let mut cur = col;
        while cur != 0 {
            let hi = 63 - cur.leading_zeros() as usize;
            if pivot[hi] == 0 {
                pivot[hi] = cur;
                rank += 1;
                break;
            }
            cur ^= pivot[hi];
        }
    }
    rank
}

// ---------------------------------------------------------------------------
// exact rational output
// ---------------------------------------------------------------------------

fn gcd_u128(mut a: u128, mut b: u128) -> u128 {
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

/// Exact finite decimal expansion of num/2^k, by long division on u128.
fn dyadic_decimal(num: u128, den: u128) -> String {
    require(
        den != 0 && (den & (den - 1)) == 0,
        "density denominator is not a power of two",
    );
    let k = den.trailing_zeros() as usize;
    if k == 0 {
        return num.to_string();
    }
    let mut scaled = num;
    for _ in 0..k {
        scaled = scaled
            .checked_mul(5)
            .unwrap_or_else(|| fatal("decimal expansion overflowed u128"));
    }
    let mut text = scaled.to_string();
    while text.len() < k + 1 {
        text.insert(0, '0');
    }
    let split = text.len() - k;
    let integer_part = text[..split].to_string();
    let frac = text[split..].trim_end_matches('0').to_string();
    if frac.is_empty() {
        integer_part
    } else {
        format!("{}.{}", integer_part, frac)
    }
}

fn histogram_string(hist: &BTreeMap<u64, u64>) -> String {
    hist.iter()
        .map(|(k, v)| format!("{}:{}", k, v))
        .collect::<Vec<_>>()
        .join(",")
}

// ---------------------------------------------------------------------------
// hand-rolled JSON array extraction (no crates)
// ---------------------------------------------------------------------------

/// Pull the integer array that follows `"key"` in `text`.
fn json_int_array(text: &str, key: &str) -> Vec<i64> {
    let needle = format!("\"{}\"", key);
    let start = text
        .find(&needle)
        .unwrap_or_else(|| fatal(&format!("partition JSON: key {:?} not found", key)));
    let rest = &text[start + needle.len()..];
    let open = rest
        .find('[')
        .unwrap_or_else(|| fatal(&format!("partition JSON: key {:?} is not an array", key)));
    let close = rest[open..]
        .find(']')
        .unwrap_or_else(|| fatal(&format!("partition JSON: key {:?} is unterminated", key)))
        + open;
    let body = &rest[open + 1..close];
    let mut out = Vec::new();
    for piece in body.split(',') {
        let piece = piece.trim();
        if piece.is_empty() {
            continue;
        }
        match piece.parse::<i64>() {
            Ok(v) => out.push(v),
            Err(_) => fatal(&format!(
                "partition JSON: {:?} in key {:?} is not an integer",
                piece, key
            )),
        }
    }
    out
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

struct Options {
    matrix: String,
    name: String,
    expect_r: Option<usize>,
    expect_n: Option<usize>,
    partition: Option<String>,
    minimality: bool,
    triples: bool,
    emit_flat: Option<String>,
}

fn parse_args() -> Options {
    let argv: Vec<String> = env::args().collect();
    let mut opts = Options {
        matrix: String::new(),
        name: String::new(),
        expect_r: None,
        expect_n: None,
        partition: None,
        minimality: false,
        triples: false,
        emit_flat: None,
    };
    let mut i = 1;
    while i < argv.len() {
        let a = argv[i].as_str();
        let mut take = || -> String {
            i += 1;
            if i >= argv.len() {
                fatal("missing value for a flag");
            }
            argv[i].clone()
        };
        match a {
            "--name" => opts.name = take(),
            "--expect-r" => opts.expect_r = Some(take().parse().unwrap()),
            "--expect-n" => opts.expect_n = Some(take().parse().unwrap()),
            "--partition" => opts.partition = Some(take()),
            "--emit-flat" => opts.emit_flat = Some(take()),
            "--minimality" => opts.minimality = true,
            "--triples" => opts.triples = true,
            other => {
                if other.starts_with("--") {
                    fatal(&format!("unknown flag {}", other));
                }
                opts.matrix = other.to_string();
            }
        }
        i += 1;
    }
    if opts.matrix.is_empty() {
        fatal("usage: verify_rs MATRIX.txt [--name N] [--expect-r R] [--expect-n N] [--partition P.json] [--minimality] [--triples] [--emit-flat OUT]");
    }
    if opts.name.is_empty() {
        let base = opts.matrix.rsplit('/').next().unwrap();
        opts.name = base.trim_end_matches(".txt").to_string();
    }
    opts
}

fn main() {
    let opts = parse_args();
    let (r, n, columns) = parse_matrix(&opts.matrix);
    let total: usize = 1usize << r;
    let mut facts: Vec<(String, String)> = Vec::new();
    let put = |facts: &mut Vec<(String, String)>, k: &str, v: String| {
        facts.push((k.to_string(), v));
    };

    if let Some(er) = opts.expect_r {
        require(r == er, &format!("{}: got r = {}, expected {}", opts.name, r, er));
    }
    if let Some(en) = opts.expect_n {
        require(n == en, &format!("{}: got n = {}, expected {}", opts.name, n, en));
    }

    put(&mut facts, "name", opts.name.clone());
    put(&mut facts, "r", r.to_string());
    put(&mut facts, "n", n.to_string());

    // -- well-formedness -----------------------------------------------------
    let mut member = vec![false; total];
    for &c in &columns {
        require(c != 0, &format!("{}: a column is zero", opts.name));
        require(
            (c as usize) < total,
            &format!("{}: a column exceeds {} bits", opts.name, r),
        );
        require(
            !member[c as usize],
            &format!("{}: columns are not pairwise distinct", opts.name),
        );
        member[c as usize] = true;
    }
    put(&mut facts, "columns_nonzero", "1".to_string());
    put(&mut facts, "columns_distinct", "1".to_string());

    // -- rank ----------------------------------------------------------------
    let rank = f2_rank(&columns, r);
    require(
        rank == r,
        &format!("{}: F_2 rank is {}, expected {}", opts.name, rank, r),
    );
    put(&mut facts, "rank", rank.to_string());

    // -- coverage, SYNDROME-DRIVEN ------------------------------------------
    // For each s, decide membership of {0} u S u (S+S) by scanning columns.
    // Full sweep of 0..2^r; no early exit from the sweep itself.
    let mut covered_syndrome_driven = 0usize;
    let mut first_uncovered: Option<usize> = None;
    for s in 0..total {
        let hit = if s == 0 || member[s] {
            true
        } else {
            let mut found = false;
            for &h in &columns {
                if member[s ^ (h as usize)] {
                    found = true;
                    break;
                }
            }
            found
        };
        if hit {
            covered_syndrome_driven += 1;
        } else if first_uncovered.is_none() {
            first_uncovered = Some(s);
        }
    }
    if let Some(s) = first_uncovered {
        fatal(&format!(
            "{}: {} of {} syndromes uncovered, first is {}",
            opts.name,
            total - covered_syndrome_driven,
            total,
            s
        ));
    }

    // -- multiplicities, PAIR-DRIVEN (independent second opinion) -----------
    // mult[s] = number of representations of s as a sum of AT MOST two
    // columns: the empty sum (s = 0), each single column, each unordered pair.
    let mut mult = vec![0u64; total];
    mult[0] += 1;
    for &c in &columns {
        mult[c as usize] += 1;
    }
    for i in 0..n {
        for j in (i + 1)..n {
            mult[(columns[i] ^ columns[j]) as usize] += 1;
        }
    }
    let covered_pair_driven = mult.iter().filter(|&&m| m > 0).count();
    require(
        covered_pair_driven == covered_syndrome_driven,
        &format!(
            "{}: internal disagreement -- syndrome-driven sweep says {} covered, \
             pair-driven count says {}",
            opts.name, covered_syndrome_driven, covered_pair_driven
        ),
    );
    let expected_reps: u64 = 1 + n as u64 + (n as u64) * (n as u64 - 1) / 2;
    require(
        mult.iter().sum::<u64>() == expected_reps,
        &format!("{}: representation bookkeeping is inconsistent", opts.name),
    );
    put(&mut facts, "syndromes_total", total.to_string());
    put(&mut facts, "syndromes_covered", covered_pair_driven.to_string());

    // -- radius exactly two --------------------------------------------------
    let pair_needed = (0..total).filter(|&s| s != 0 && !member[s]).count();
    require(
        pair_needed > 0,
        &format!("{}: covering radius is at most 1, not 2", opts.name),
    );
    put(&mut facts, "radius_exactly_2", "1".to_string());
    put(&mut facts, "pair_needed", pair_needed.to_string());

    // -- histograms ----------------------------------------------------------
    let mut hist: BTreeMap<u64, u64> = BTreeMap::new();
    let mut pair_hist: BTreeMap<u64, u64> = BTreeMap::new();
    let mut forced_split = 0u64;
    for s in 0..total {
        *hist.entry(mult[s]).or_insert(0) += 1;
        if s != 0 && !member[s] {
            *pair_hist.entry(mult[s]).or_insert(0) += 1;
            if mult[s] == 1 {
                forced_split += 1;
            }
        }
    }
    put(&mut facts, "mult_hist", histogram_string(&hist));
    put(&mut facts, "pair_hist", histogram_string(&pair_hist));
    put(&mut facts, "forced_split", forced_split.to_string());

    // -- density -------------------------------------------------------------
    let num_raw: u128 = expected_reps as u128;
    let den_raw: u128 = 1u128 << r;
    let g = gcd_u128(num_raw, den_raw);
    let (dnum, dden) = (num_raw / g, den_raw / g);
    put(&mut facts, "density_num", dnum.to_string());
    put(&mut facts, "density_den", dden.to_string());
    put(&mut facts, "density_decimal", dyadic_decimal(dnum, dden));

    // -- minimum distance and dependent triples ------------------------------
    let mut triples: Vec<(u64, u64, u64)> = Vec::new();
    if opts.triples {
        for i in 0..n {
            for j in (i + 1)..n {
                let s = columns[i] ^ columns[j];
                if member[s as usize] {
                    // count each unordered triple once: require the third
                    // column to be strictly larger than both, by value
                    if s > columns[i] && s > columns[j] {
                        let mut t = [columns[i], columns[j], s];
                        t.sort();
                        triples.push((t[0], t[1], t[2]));
                    }
                }
            }
        }
        triples.sort();
        put(
            &mut facts,
            "min_distance",
            if triples.is_empty() { "4" } else { "3" }.to_string(),
        );
        put(&mut facts, "dependent_triples", triples.len().to_string());
        put(
            &mut facts,
            "triples_list",
            triples
                .iter()
                .map(|t| format!("({},{},{})", t.0, t.1, t.2))
                .collect::<Vec<_>>()
                .join(";"),
        );
    }

    // -- minimality (locally optimal covering code) --------------------------
    if opts.minimality {
        // Derived per syndrome: deleting column k removes from s exactly the
        // representations that use k, namely s == h_k (one) plus the pair
        // {k, j} with h_j == s ^ h_k when that is a column other than h_k.
        // s becomes uncovered iff mult[s] equals that contribution.
        let mut best: Option<u64> = None;
        let mut best_cols: Vec<u64> = Vec::new();
        for k in 0..n {
            let hk = columns[k];
            let mut left = 0u64;
            for s in 0..total {
                let mut contrib = 0u64;
                if s as u64 == hk {
                    contrib += 1;
                }
                let partner = (s as u64) ^ hk;
                if partner != 0 && partner != hk && member[partner as usize] {
                    contrib += 1;
                }
                if contrib > 0 && mult[s] == contrib {
                    left += 1;
                }
            }
            match best {
                None => {
                    best = Some(left);
                    best_cols = vec![hk];
                }
                Some(b) if left < b => {
                    best = Some(left);
                    best_cols = vec![hk];
                }
                Some(b) if left == b => best_cols.push(hk),
                _ => {}
            }
        }
        best_cols.sort();
        put(
            &mut facts,
            "min_uncovered_on_deletion",
            best.unwrap().to_string(),
        );
        put(
            &mut facts,
            "argmin_deletion_columns",
            best_cols
                .iter()
                .map(|c| c.to_string())
                .collect::<Vec<_>>()
                .join(","),
        );
    }

    // -- (2,0)-partition -----------------------------------------------------
    if let Some(path) = opts.partition.as_ref() {
        // (triples, if computed, are cross-referenced against the blocks below)
        let text = fs::read_to_string(path)
            .unwrap_or_else(|e| fatal(&format!("cannot read {}: {}", path, e)));
        let json_columns = json_int_array(&text, "columns");
        let block_of = json_int_array(&text, "block_of_column");
        require(
            json_columns.len() == n && block_of.len() == n,
            &format!("{}: partition JSON length does not match matrix", opts.name),
        );
        for j in 0..n {
            require(
                json_columns[j] as u64 == columns[j],
                &format!(
                    "{}: partition JSON column {} is {}, matrix text says {}",
                    opts.name, j, json_columns[j], columns[j]
                ),
            );
        }
        let mut labels: Vec<i64> = block_of.clone();
        labels.sort();
        labels.dedup();
        let p = labels.len();
        for (idx, lab) in labels.iter().enumerate() {
            require(
                *lab == idx as i64,
                &format!("{}: block labels are not 0..p-1", opts.name),
            );
        }

        // mark every syndrome realised by a CROSS-BLOCK pair, then sweep
        let mut cross = vec![false; total];
        for i in 0..n {
            for j in (i + 1)..n {
                if block_of[i] != block_of[j] {
                    cross[(columns[i] ^ columns[j]) as usize] = true;
                }
            }
        }
        let mut failures = 0usize;
        let mut first_failure: Option<usize> = None;
        for s in 0..total {
            // s = 0 is the empty sum and s in S is a sum of one column;
            // Definition 3.2 admits both for an (R,0)-partition.
            if s == 0 || member[s] {
                continue;
            }
            if !cross[s] {
                failures += 1;
                if first_failure.is_none() {
                    first_failure = Some(s);
                }
            }
        }
        let mut sizes = vec![0usize; p];
        for &b in &block_of {
            sizes[b as usize] += 1;
        }
        // Analogue of arXiv:2511.02542 Theorem 5.2(ii): a linearly dependent
        // triple whose three columns lie in three DISTINCT blocks is what lets
        // Construction QM_5^2 (Thm 5.4(ii)) run at the next step.
        if !triples.is_empty() {
            let mut spans: Vec<String> = Vec::new();
            let mut three = 0usize;
            for t in &triples {
                let mut bs = [0i64; 3];
                for (slot, value) in [t.0, t.1, t.2].iter().enumerate() {
                    let mut found: Option<i64> = None;
                    for j in 0..n {
                        if columns[j] == *value {
                            found = Some(block_of[j]);
                            break;
                        }
                    }
                    bs[slot] = found.unwrap_or_else(|| {
                        fatal(&format!("{}: triple member {} is not a column", opts.name, value))
                    });
                }
                if bs[0] != bs[1] && bs[1] != bs[2] && bs[0] != bs[2] {
                    three += 1;
                }
                spans.push(format!(
                    "({},{},{}):{}/{}/{}",
                    t.0, t.1, t.2, bs[0], bs[1], bs[2]
                ));
            }
            put(&mut facts, "triples_three_blocks", three.to_string());
            put(&mut facts, "triples_block_map", spans.join(";"));
        }

        put(&mut facts, "partition_blocks", p.to_string());
        put(
            &mut facts,
            "partition_sizes",
            sizes
                .iter()
                .map(|s| s.to_string())
                .collect::<Vec<_>>()
                .join(","),
        );
        put(
            &mut facts,
            "partition_valid",
            if failures == 0 { "1" } else { "0" }.to_string(),
        );
        put(&mut facts, "partition_failures", failures.to_string());
        if failures > 0 {
            fatal(&format!(
                "{}: {} syndromes have no cross-block pair, first is {}",
                opts.name,
                failures,
                first_failure.unwrap()
            ));
        }
    }

    // -- report --------------------------------------------------------------
    facts.sort_by(|a, b| a.0.cmp(&b.0));
    let mut out = String::new();
    for (k, v) in &facts {
        out.push_str(k);
        out.push('\t');
        out.push_str(v);
        out.push('\n');
    }
    print!("{}", out);
    if let Some(path) = opts.emit_flat.as_ref() {
        fs::write(path, out).unwrap_or_else(|e| fatal(&format!("cannot write {}: {}", path, e)));
    }
}
