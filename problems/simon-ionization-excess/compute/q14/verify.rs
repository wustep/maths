// Independent verifier: an explicit rational Gram matrix, enclosed by
// fixed-point intervals, rather than Python's exact Schur complements of P.
// rustc only; all integer arithmetic checked even in optimized builds.
use std::{collections::BTreeMap, env, fs};

#[derive(Debug)]
enum Json { Object(BTreeMap<String,Json>), Array(Vec<Json>), String(String), Number(String) }
struct Parser { b: Vec<u8>, p: usize }
impl Parser {
    fn ws(&mut self) { while self.p < self.b.len() && self.b[self.p].is_ascii_whitespace() { self.p+=1; } }
    fn take(&mut self, c:u8) { self.ws(); assert_eq!(self.b[self.p],c); self.p+=1; }
    fn string(&mut self)->String {
        self.take(b'"'); let start=self.p;
        while self.b[self.p]!=b'"' { assert!(self.b[self.p]>=32 && self.b[self.p]!=b'\\'); self.p+=1; }
        let out=String::from_utf8(self.b[start..self.p].to_vec()).unwrap(); self.p+=1; out
    }
    fn value(&mut self)->Json {
        self.ws(); match self.b[self.p] {
            b'{' => { self.p+=1; let mut m=BTreeMap::new(); self.ws();
                if self.b[self.p]!=b'}' { loop { let k=self.string(); self.take(b':'); let v=self.value();
                    assert!(m.insert(k,v).is_none(),"duplicate key"); self.ws();
                    if self.b[self.p]!=b',' { break; } self.p+=1;
                }} self.take(b'}'); Json::Object(m) },
            b'[' => { self.p+=1; let mut a=Vec::new(); self.ws();
                if self.b[self.p]!=b']' { loop { a.push(self.value()); self.ws();
                    if self.b[self.p]!=b',' { break; } self.p+=1;
                }} self.take(b']'); Json::Array(a) },
            b'"' => Json::String(self.string()),
            _ => { let start=self.p; while self.p<self.b.len() &&
                    (self.b[self.p].is_ascii_digit() || b"-+.eE".contains(&self.b[self.p])) { self.p+=1; }
                assert!(self.p>start); Json::Number(String::from_utf8(self.b[start..self.p].to_vec()).unwrap()) }
        }
    }
}
impl Json {
    fn get(&self,k:&str)->&Json { if let Json::Object(m)=self { &m[k] } else { panic!("object expected") } }
    fn array(&self)->&Vec<Json> { if let Json::Array(a)=self { a } else { panic!("array expected") } }
    fn text(&self)->&str { match self { Json::String(s)|Json::Number(s)=>s, _=>panic!("scalar expected") } }
    fn integer(&self)->i128 { self.text().parse().unwrap() }
}

const S:i128=1_000_000_000_000_000;
#[derive(Clone,Copy,Debug)]
struct I { l:i128, h:i128 }
fn ceil(n:i128,d:i128)->i128 { -(-n).div_euclid(d) }
impl I {
    fn rat(n:i128,d:i128)->Self { assert!(d>0); Self{l:(n*S).div_euclid(d),h:ceil(n*S,d)} }
    fn int(n:i128)->Self { Self::rat(n,1) }
    fn parse(s:&str)->Self {
        let a:Vec<_>=s.split('/').collect(); assert!(a.len()<=2);
        Self::rat(a[0].parse().unwrap(),if a.len()==2 {a[1].parse().unwrap()} else {1})
    }
    fn add(self,b:Self)->Self { Self{l:self.l+b.l,h:self.h+b.h} }
    fn sub(self,b:Self)->Self { Self{l:self.l-b.h,h:self.h-b.l} }
    fn mul(self,b:Self)->Self {
        let a=[self.l*b.l,self.l*b.h,self.h*b.l,self.h*b.h];
        Self{l:a.iter().min().unwrap().div_euclid(S),h:ceil(*a.iter().max().unwrap(),S)}
    }
    fn div(self,b:Self)->Self { assert!(b.l>0); self.mul(Self{l:(S*S).div_euclid(b.h),h:ceil(S*S,b.l)}) }
    fn pow(self,n:usize)->Self { (0..n).fold(Self::int(1),|a,_|a.mul(self)) }
    fn upper_root(self,n:usize)->Self {
        // A grid search with outward powers proves the returned point is
        // an upper bound for the root of every member of this interval.
        assert!(self.l>=0); let grid=1_000_000_000_i128; let mut lo=0; let mut hi=grid;
        while Self::rat(hi,grid).pow(n).l<self.h { hi*=2; }
        while hi-lo>1 { let m=(lo+hi)/2;
            if Self::rat(m,grid).pow(n).l<self.h {lo=m;} else {hi=m;}
        } Self::rat(hi,grid)
    }
}
fn max(a:I,b:I)->I { I{l:a.l.max(b.l),h:a.h.max(b.h)} }
fn min(a:I,b:I)->I { I{l:a.l.min(b.l),h:a.h.min(b.h)} }
fn h(t:I)->I { t.pow(3).add(I::int(3).mul(t)).sub(I::int(2)) }
fn f(t:I)->I { I::int(1).add(t.pow(3)).div(I::int(1).add(t.pow(2))) }

fn main() {
    let path=env::args().nth(1).expect("certificate.json argument required");
    let mut parser=Parser{b:fs::read(path).unwrap(),p:0}; let cert=parser.value(); parser.ws();
    assert_eq!(parser.p,parser.b.len());
    let n=cert.get("n").integer() as usize; assert_eq!(n,37);
    assert_eq!(cert.get("phi").text(),"114/125");
    assert_eq!(cert.get("f_floor").text(),"8941/10000");
    let phi=I::rat(114,125); let floor=I::rat(8941,10000);
    assert!(I::int(1).sub(floor).sub(I::rat(4,27).mul(floor.pow(3))).l>0);
    let tlo=I::rat(596,1000); let thi=I::rat(5961,10000);
    assert!(h(tlo).h<0 && h(thi).l>0);
    let edges=cert.get("edges").array(); assert_eq!(edges.len(),n+1);
    assert_eq!(edges[0].text(),"1"); assert_eq!(edges[n].text(),"10");
    let e:Vec<I>=edges.iter().map(|x|I::parse(x.text())).collect();
    for i in 0..n { assert!(e[i].h<e[i+1].l); }
    let bden=cert.get("B_denominator").integer(); assert!(bden>0);
    let rows=cert.get("B_numerators").array(); assert_eq!(rows.len(),n);
    let b:Vec<Vec<I>>=rows.iter().map(|r| { assert_eq!(r.array().len(),n);
        r.array().iter().map(|x|I::rat(x.integer(),bden)).collect() }).collect();
    let c:Vec<I>=(0..n).map(|i|e[i].mul(e[i+1])).collect();
    let d:Vec<I>=(0..n).map(|i|e[i].add(e[i+1]).mul(I::rat(1,2))).collect();
    let mut smallest=i128::MAX;
    for i in 0..n { for j in 0..n {
        // Ordered bins give the extreme ratios directly. This construction
        // is independent of Python's four-corner reconstruction.
        let (u,v)=if i<=j {(i,j)} else {(j,i)};
        let lo=e[u].div(e[v+1]);
        let hi=if u==v || u+1==v {I::int(1)} else {e[u+1].div(e[v])};
        let fij=if hi.h<=tlo.l {f(hi)} else if lo.l>=thi.h {f(lo)} else {floor};
        let m=fij.sub(phi).mul(c[i].add(c[j])).mul(I::rat(1,2)).div(d[i]).div(d[j]);
        // B B^T is PSD for real vectors, by the sum-of-squares identity.
        let gram=(0..n).fold(I::int(0),|a,k|a.add(b[i][k].mul(b[j][k])));
        let residual=m.sub(gram); assert!(residual.l>0,"Gram residual at {i},{j}");
        smallest=smallest.min(residual.l);
    }}
    assert!(smallest>I::rat(1,100000).h);
    let q=(0..n).map(|i|e[i+1].div(e[i])).reduce(max).unwrap();
    // Independently confirm the exact compact gamma printed in PROOF.md.
    // All stored edges are multiples of 10^-12; compare neighboring ratios
    // by integer cross-products, then clear the scalar denominators.
    let ticks:Vec<i128>=edges.iter().map(|edge| {
        let pair:Vec<_>=edge.text().split('/').collect();
        let numerator:i128=pair[0].parse().unwrap();
        let denominator:i128=if pair.len()==2 {pair[1].parse().unwrap()} else {1};
        assert!(denominator>0 && 1_000_000_000_000_i128%denominator==0);
        numerator*(1_000_000_000_000_i128/denominator)
    }).collect();
    let (mut qn,mut qd)=(1_i128,1_i128);
    for k in 0..n { if ticks[k+1]*qd>qn*ticks[k] {qn=ticks[k+1]; qd=ticks[k];} }
    let gn=114*10000*(qn+qd)-125*1059*(qn-qd);
    let gd=125*10000*(qn+qd);
    assert_eq!(gn*6382236648346000_i128,gd*5799575951378799_i128);
    let tv=q.sub(I::int(1)).div(q.add(I::int(1)));
    let gamma=phi.sub(tv.mul(I::int(1).sub(floor)));
    let beta=I::rat(9087,10000);
    assert!(min(gamma,I::rat(10,11)).l>beta.h);
    let inv=I::int(1).div(beta);
    assert!(inv.h<I::rat(11005,10000).l);
    assert!(I::rat(11005,10000).h<I::rat(11006,10000).l);
    // Different scalar route: coarse rational ceilings, checked by powers.
    let hc=I::rat(15855,10000);
    let c6=I::rat(4096,27).mul(I::rat(2,9).mul(I::rat(1456,1000)).pow(2));
    assert!(hc.pow(6).l>c6.h);
    let a=I::int(3).mul(I::rat(3,10).upper_root(3));
    let left=a.mul(inv).add(hc.mul(inv.upper_root(3)));
    let right=a.mul(I::rat(9,4).mul(inv.pow(2)).upper_root(3))
        .add(hc.mul(I::rat(16,81).mul(inv.pow(3)).upper_root(3)));
    let a1=max(left,right);
    let a2=inv.mul(I::rat(1,84));
    let a3=hc.mul(I::rat(1,5)).mul(I::rat(25,144).mul(inv).upper_root(3));
    let a4=hc.mul(I::rat(1,84)).mul(inv.upper_root(3));
    let rem=a1.add(a2.mul(I::rat(1,4).upper_root(3)))
        .add(a3.mul(I::rat(1,16).upper_root(3))).add(a4.mul(I::rat(1,4)));
    assert!(rem.h<I::rat(3933,1000).l);
    assert!(I::rat(5,48).h<I::rat(1,8).l);
    let rootlo=I::rat(2,3).div(I::rat(11185,10000));
    let roothi=I::rat(2,3).div(I::rat(11184,10000));
    assert!(h(rootlo).h<0 && h(roothi).l>0);
    println!("Rust PASS: 1369 Gram residuals > 1/100000; beta_3 >= 9087/10000");
    println!("Rust PASS: HPS remainder < 3.933; N_c(Z) < 1.1005 Z + 3.933 Z^(1/3), Z >= 4");
    println!("outward integer diagnostics: residual_min={smallest}/{S}, remainder_hi={}/{S}",rem.h);
}
