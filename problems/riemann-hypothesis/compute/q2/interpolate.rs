//! Independent all-index verification by polynomial interpolation of positive
//! Laplace sums. See INTERPOLATION.md for the remainder and cutoff updates.
//! No upstream row, moment, or frozen gamma weight is used.
include!("ball.rs");
use std::io::{self,BufWriter,Write};

struct Params { t:B,y:B,pi:B,z:B,one:B,two:B,four:B }
impl Params {
    fn new(bits:i64)->Self {
        let pi=B::int(0,bits); unsafe{ball_pi(pi.p,bits)};
        Self {t:B::q(129,800,bits),y:B::q(87677,2500000,bits).sqrt(),pi,
              z:B::int(0,bits),one:B::int(1,bits),two:B::int(2,bits),four:B::int(4,bits)}
    }
    fn constants(&self,n:u64)->(B,B,B) {
        let bits=self.t.bits;
        let n0=B::int(n as i64,bits);
        let q=n0.mul(&n0).sub(&self.t.div(&B::int(16,bits)));
        let x=self.four.mul(&self.pi).mul(&q); let x2=x.mul(&x);
        let clip=self.one.sub(&B::int(3,bits).mul(&self.y))
            .add(&self.four.mul(&self.y).mul(&self.one.add(&self.y)).div(&x2)).max(&self.z);
        let sigma=self.one.add(&self.y).div(&self.two).add(&self.t.mul(&q.log()).div(&self.four))
            .sub(&self.t.mul(&clip).div(&self.two.mul(&x2)));
        let gamma=self.y.mul(&B::q(1,50,bits).sub(&q.log().div(&self.two))).exp();
        let rho=self.t.mul(&self.y).div(&self.two.mul(&x.sub(&B::int(6,bits))));
        (sigma,gamma,rho)
    }
    fn heat_y(&self,n:u64)->(B,B,B) {
        let l=B::int(n as i64,self.t.bits).log();
        let heat=self.t.mul(&l.mul(&l)).div(&self.four).exp();
        let hy=heat.mul(&self.y.mul(&l).exp());
        (l,heat,hy)
    }
}
struct Divisor {d:u64,lambda:B,logd:B}
fn divisors(k:usize,p:&Params)->Vec<Divisor> {
    let mut ds=Vec::new(); let bits=p.t.bits;
    for mask in 0usize..1usize<<k {
        let mut d=1; let mut sign=1; let mut sq=B::int(0,bits);
        for (j,prime) in [2,3,5,7,11].iter().take(k).enumerate() {
            if mask&(1<<j)!=0 {
                d*=prime; sign=-sign;
                let lp=B::int(*prime as i64,bits).log(); sq=sq.add(&lp.mul(&lp));
            }
        }
        let lambda=B::int(sign,bits).mul(&p.t.mul(&sq).div(&p.four).exp());
        ds.push(Divisor{d,lambda,logd:B::int(d as i64,bits).log()});
    }
    ds
}
struct Grid {a:B,nodes:Vec<B>,denom_inverse:Vec<B>,factorial:B}
impl Grid {
    fn new(a:B,b:B,m:usize,p:&Params)->Self {
        assert!(b.gt(&a));
        let mut nodes=Vec::new(); let bits=a.bits;
        for j in 0..m {
            let theta=p.pi.mul(&B::q((2*j+1) as i64,(2*m) as i64,bits));
            nodes.push(a.add(&b.sub(&a).mul(&p.one.sub(&theta.cos())).div(&p.two)));
        }
        let mut inverses=Vec::new();
        for j in 0..m {
            let mut den=B::int(1,bits);
            for k in 0..m {if j!=k {den=den.mul(&nodes[j].sub(&nodes[k]));}}
            assert!(den.abs().gt(&p.z),"node separation");
            inverses.push(p.one.div(&den));
        }
        let mut fact=B::int(1,bits);
        for j in 1..=m {fact=fact.mul(&B::int(j as i64,bits));}
        Self{a,nodes,denom_inverse:inverses,factorial:fact}
    }
    fn weights_and_remainder(&self,s:&B,log_support:&B)->(Vec<B>,B) {
        let m=self.nodes.len(); let bits=s.bits;
        let mut prefix=vec![B::int(1,bits)];
        for j in 0..m {prefix.push(prefix[j].mul(&s.sub(&self.nodes[j])));}
        let mut suffix=B::int(1,bits);
        let mut weights:Vec<B>=(0..m).map(|_|B::int(0,bits)).collect();
        for j in (0..m).rev() {
            weights[j]=prefix[j].mul(&suffix).mul(&self.denom_inverse[j]);
            suffix=suffix.mul(&s.sub(&self.nodes[j]));
        }
        let mut lm=B::int(1,bits);
        for _ in 0..m {lm=lm.mul(log_support);}
        let shift=self.nodes[0].sub(&self.a).mul(log_support).exp();
        let factor=prefix[m].abs().mul(&lm).mul(&shift).div(&self.factorial);
        assert!(factor.finite());
        (weights,factor)
    }
}
struct Sums {b:Vec<B>,a:Vec<B>,u:Vec<B>}
impl Sums {
    fn new(m:usize,bits:i64)->Self {
        Self{b:(0..m).map(|_|B::int(0,bits)).collect(),
             a:(0..m).map(|_|B::int(0,bits)).collect(),
             u:(0..m).map(|_|B::int(0,bits)).collect()}
    }
    fn add(&mut self,logn:&B,db:&B,da:&B,du:&B,grid:&Grid,p:&Params) {
        for j in 0..grid.nodes.len() {
            let w=p.z.sub(&grid.nodes[j].mul(logn)).exp();
            self.b[j]=self.b[j].add(&w.mul(db));
            self.a[j]=self.a[j].add(&w.mul(da));
            self.u[j]=self.u[j].add(&w.mul(du));
        }
    }
    fn value(v:&[B],weights:&[B],factor:&B,p:&Params)->B {
        let mut sum=B::int(0,p.t.bits);
        for j in 0..v.len() {sum=sum.add(&v[j].mul(&weights[j]));}
        // All exact coefficients are nonnegative even though an update
        // delta can be negative. The interval encloses the telescoped sum.
        assert!(v[0].gt(&p.z),"positive derivative majorant");
        sum.inflate(&factor.mul(&v[0])); sum
    }
}
fn initialize(n0:u64,ds:&[Divisor],grid:&Grid,p:&Params)->Sums {
    let mut next=vec![1u64;ds.len()]; let mut pairs=0;
    let mut sums=Sums::new(grid.nodes.len(),p.t.bits);
    loop {
        let n=ds.iter().zip(&next).filter(|(_,m)|**m<=n0).map(|(d,m)|d.d*m).min();
        let n=match n {Some(n)=>n,None=>break};
        let mut b=B::int(0,p.t.bits); let mut a=B::int(0,p.t.bits); let mut u=B::int(0,p.t.bits);
        for j in 0..ds.len() {
            if next[j]<=n0 && ds[j].d*next[j]==n {
                let (l,heat,hy)=p.heat_y(next[j]);
                b=b.add(&ds[j].lambda.mul(&heat));
                a=a.add(&ds[j].lambda.mul(&hy));
                if ds[j].d==1 && n>=2 {u=hy.mul(&l);}
                next[j]+=1; pairs+=1;
            }
        }
        if n>=2 {sums.add(&B::int(n as i64,p.t.bits).log(),&b.abs(),&a.abs(),&u,grid,p);}
    }
    assert_eq!(pairs,n0*ds.len() as u64);
    eprintln!("initialized N={n0} convolution_pairs={pairs}");
    sums
}
fn advance(n:u64,ds:&[Divisor],grid:&Grid,p:&Params,sums:&mut Sums) {
    let (ln,heat,hy)=p.heat_y(n);
    for d in ds {
        let index=d.d*n;
        let mut oldb=B::int(0,p.t.bits); let mut olda=B::int(0,p.t.bits);
        for e in ds {
            if index%e.d==0 && index/e.d<n {
                let (_,h,ay)=p.heat_y(index/e.d);
                oldb=oldb.add(&e.lambda.mul(&h)); olda=olda.add(&e.lambda.mul(&ay));
            }
        }
        // At this index exactly the divisor d activates at the new cutoff.
        let newb=oldb.add(&d.lambda.mul(&heat)); let newa=olda.add(&d.lambda.mul(&hy));
        let u=if d.d==1 {hy.mul(&ln)} else {B::int(0,p.t.bits)};
        sums.add(&B::int(index as i64,p.t.bits).log(),
                 &newb.abs().sub(&oldb.abs()),&newa.abs().sub(&olda.abs()),&u,grid,p);
    }
}
fn main() {
    let args:Vec<_>=std::env::args().collect();
    assert_eq!(args.len(),6,"usage: interpolate first_N last_N primes nodes bits");
    let lo:u64=args[1].parse().unwrap(); let hi:u64=args[2].parse().unwrap();
    let k:usize=args[3].parse().unwrap(); let m:usize=args[4].parse().unwrap(); let bits:i64=args[5].parse().unwrap();
    assert!(lo>=2 && lo<hi && hi<=3840000 && (2..=5).contains(&k));
    assert!((4..=20).contains(&m) && (128..=1024).contains(&bits));
    let p=Params::new(bits); let ds=divisors(k,&p);
    let dmax=ds.iter().map(|d|d.d).max().unwrap();
    let grid=Grid::new(p.constants(lo).0,p.constants(hi).0,m,&p);
    let mut sums=initialize(lo,&ds,&grid,&p);
    let mut out=BufWriter::new(io::stdout().lock());
    writeln!(out,"INTERPOLATION first={lo} last={hi} primes={k} nodes={m} bits={bits} t=129/800 y2=87677/2500000").unwrap();
    let mut minimum=i64::MAX; let mut at=lo;
    for n in lo..=hi {
        if n>lo {advance(n,&ds,&grid,&p,&mut sums);}
        let (sigma,gamma,rho)=p.constants(n);
        let support=B::int((dmax*n) as i64,bits).log();
        let (weights,error)=grid.weights_and_remainder(&sigma,&support);
        let sb=Sums::value(&sums.b,&weights,&error,&p);
        let sa=Sums::value(&sums.a,&weights,&error,&p);
        let su=Sums::value(&sums.u,&weights,&error,&p);
        let mut norm=B::int(0,bits);
        for d in &ds {norm=norm.add(&d.lambda.abs().mul(&p.z.sub(&sigma.mul(&d.logd)).exp()));}
        let correction=gamma.mul(&rho).mul(&rho.mul(&B::int(n as i64,bits).log()).exp()).mul(&su);
        let result=p.one.sub(&gamma).sub(&sb).sub(&gamma.mul(&sa)).div(&norm).sub(&correction);
        let floor=result.floor12();
        if lo>=690988 {assert!(floor>233495,"independent finite gate failed at N={n}: {}",result.text());}
        if floor<minimum {minimum=floor; at=n;}
        writeln!(out,"N {n} LOWER12 {floor}").unwrap();
        if n==lo || n==hi {eprintln!("N={n} enclosure={}",result.text());}
        if n%10000==0 {out.flush().unwrap(); eprintln!("covered through {n}");}
    }
    writeln!(out,"COMPLETE rows={} minimum12={minimum} at={at}",hi-lo+1).unwrap();
    out.flush().unwrap();
}
