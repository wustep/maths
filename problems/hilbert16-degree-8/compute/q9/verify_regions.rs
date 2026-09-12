// Independent verifier: exact lower faces, then a signed graph on vertices.
// No prepared complex, triangle union-find, or search-engine code is used.
// Input: d n f; n lines x y integer_height sign; f lines vertex indices.
use std::collections::{BTreeMap, BTreeSet};
use std::io::{self, Read};

type Point = (i128, i128);

fn det(a: Point, b: Point, c: Point) -> i128 {
    (b.0-a.0)*(c.1-a.1) - (b.1-a.1)*(c.0-a.0)
}

fn tree(v: usize, parent: usize, adj: &[BTreeSet<usize>]) -> u64 {
    let mut children: Vec<u64> = adj[v].iter().filter(|&&w| w != parent)
        .map(|&w| tree(w, v, adj)).collect();
    children.sort_unstable();
    let mut code = 1u64;
    for child in children {
        let width = 64 - child.leading_zeros();
        assert!((64 - code.leading_zeros()) + width + 1 <= 63);
        code = (code << width) | child;
    }
    code << 1
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut words = input.split_whitespace();
    let mut next = || words.next().unwrap().parse::<i128>().unwrap();
    assert_eq!(next(), 8);
    assert_eq!(next(), 45);
    assert_eq!(next(), 64);
    let mut pts = Vec::new();
    let mut height = Vec::new();
    let mut sign = Vec::new();
    for _ in 0..45 {
        let (x,y,h,s) = (next(),next(),next(),next());
        assert!(x>=0 && y>=0 && x+y<=8);
        // Bound arithmetic explicitly; every intermediate is safe in i128.
        assert!(h.abs() <= 1_000_000_000_000_000_000);
        assert!(s == 1 || s == -1);
        pts.push((x,y)); height.push(h); sign.push(s);
    }
    assert_eq!(pts.iter().collect::<BTreeSet<_>>().len(), 45);
    let mut tris = Vec::new();
    for _ in 0..64 {
        let mut t = [next() as usize, next() as usize, next() as usize];
        t.sort_unstable();
        assert!(t[2]<45 && t[0]<t[1] && t[1]<t[2]);
        tris.push(t);
    }
    assert!(words.next().is_none(), "trailing input");
    assert_eq!(tris.iter().collect::<BTreeSet<_>>().len(), 64);
    // Barycentric determinants, instead of the Python plane solver.
    // Strict lower facets cannot overlap. 64 primitive facets have the
    // full area of 8 Delta_2, so their union is the whole triangle.
    let mut used = BTreeSet::new();
    for &[a,b,c] in &tris {
        used.extend([a,b,c]);
        let area = det(pts[a],pts[b],pts[c]);
        assert_eq!(area.abs(), 1, "nonprimitive triangle");
        for k in 0..45 {
            if k == a || k == b || k == c {continue;}
            let gap = area*height[k] - det(pts[k],pts[b],pts[c])*height[a]
                - det(pts[a],pts[k],pts[c])*height[b]
                - det(pts[a],pts[b],pts[k])*height[c];
            assert!(gap*area>0, "strict lifting failed");
        }
    }
    assert_eq!(used.len(),45);

    // Reflect the mesh in the two axes. Region connectivity and
    // orientation-reversing loops are detected by monochromatic edges.
    let mut vertices = BTreeMap::new();
    for x in -8i128..=8 {
        for y in -8i128..=8 {
            if x.abs()+y.abs()<=8 {
                let id = vertices.len(); vertices.insert((x,y),id);
            }
        }
    }
    let mut signs = vec![0;vertices.len()];
    for (&(x,y),&v) in &vertices {
        let k = pts.iter().position(|&p|p==(x.abs(),y.abs())).unwrap();
        let flip = (x<0 && x.abs()%2==1) ^ (y<0 && y.abs()%2==1);
        signs[v] = if flip {-sign[k]} else {sign[k]};
    }
    let mut edges = BTreeSet::new();
    for t in &tris {
        for sx in [-1,1] {
            for sy in [-1,1] {
                for j in 0..3 {
                    let p=pts[t[j]]; let q=pts[t[(j+1)%3]];
                    let a=vertices[&(sx*p.0,sy*p.1)];
                    let b=vertices[&(sx*q.0,sy*q.1)];
                    edges.insert((a.min(b),a.max(b)));
                }
            }
        }
    }
    // The parity 1 on antipodal identifications records the orientation
    // double cover. An odd-parity cycle identifies the outside region.
    let mut mono = vec![Vec::new();vertices.len()];
    for &(a,b) in &edges {
        if signs[a] == signs[b] {
            mono[a].push((b,0u8)); mono[b].push((a,0u8));
        }
    }
    for (&(x,y),&a) in &vertices {
        if x.abs()+y.abs()==8 {
            let b=vertices[&(-x,-y)];
            assert_eq!(signs[a],signs[b]);
            mono[a].push((b,1u8));
        }
    }
    let mut region=vec![usize::MAX;vertices.len()];
    let mut parity=vec![0;vertices.len()];
    let mut roots=Vec::new();
    let mut nr=0;
    for v in 0..vertices.len() {
        if region[v] != usize::MAX {continue;}
        region[v]=nr;
        let mut stack=vec![v];
        let mut nonorientable=false;
        while let Some(a)=stack.pop() {
            for &(b,twist) in &mono[a] {
                let want=parity[a]^twist;
                if region[b] == usize::MAX {
                    region[b]=nr; parity[b]=want; stack.push(b);
                } else {
                    assert_eq!(region[b],nr);
                    nonorientable |= parity[b] != want;
                }
            }
        }
        if nonorientable {roots.push(nr);}
        nr+=1;
    }
    assert_eq!(roots.len(),1,"outside region is not unique");
    let mut adj=vec![BTreeSet::new();nr];
    for &(a,b) in &edges {
        if signs[a] != signs[b] {
            let (u,v)=(region[a],region[b]);
            assert_ne!(u,v);
            adj[u].insert(v); adj[v].insert(u);
        }
    }
    assert_eq!(adj.iter().map(|a|a.len()).sum::<usize>(),2*(nr-1));
    let mut seen=BTreeSet::new();
    let mut stack=vec![roots[0]];
    while let Some(v)=stack.pop() {
        if seen.insert(v) {stack.extend(adj[v].iter().copied());}
    }
    assert_eq!(seen.len(),nr,"region adjacency is disconnected");
    assert!(nr<=23,"more than 22 ovals");
    println!("{} {}",nr-1,tree(roots[0],usize::MAX,&adj));
}
