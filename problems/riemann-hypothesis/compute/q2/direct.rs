//! Independent direct finite functional: merge the d*m streams, convolve
//! before taking absolute values, and sum every term without Taylor moments.
//! Reads no upstream code, row, moments, or coefficient artifact.
use std::ffi::{c_char,c_void,CStr};
type Ptr = *mut c_void;
extern "C" {
    fn ball_new() -> Ptr;
    fn ball_free(a:Ptr);
    fn ball_int(a:Ptr,n:i64);
    fn ball_pi(a:Ptr,bits:i64);
    fn ball_add(r:Ptr,a:Ptr,b:Ptr,bits:i64);
    fn ball_sub(r:Ptr,a:Ptr,b:Ptr,bits:i64);
    fn ball_mul(r:Ptr,a:Ptr,b:Ptr,bits:i64);
    fn ball_div(r:Ptr,a:Ptr,b:Ptr,bits:i64);
    fn ball_max(r:Ptr,a:Ptr,b:Ptr,bits:i64);
    fn ball_log(r:Ptr,a:Ptr,bits:i64);
    fn ball_exp(r:Ptr,a:Ptr,bits:i64);
    fn ball_expm1(r:Ptr,a:Ptr,bits:i64);
    fn ball_sqrt(r:Ptr,a:Ptr,bits:i64);
    fn ball_abs(r:Ptr,a:Ptr);
    fn ball_gt(a:Ptr,b:Ptr)->i32;
    fn ball_finite(a:Ptr)->i32;
    fn ball_text(a:Ptr)->*mut c_char;
    fn ball_text_free(a:*mut c_char);
}
struct B { p:Ptr, bits:i64 }
impl Drop for B { fn drop(&mut self) { unsafe { ball_free(self.p) } } }
impl B {
    fn int(n:i64,bits:i64)->B {
        let p=unsafe{ball_new()}; unsafe{ball_int(p,n)}; B{p,bits}
    }
    fn q(n:i64,d:i64,bits:i64)->B { Self::int(n,bits).div(&Self::int(d,bits)) }
    fn binary(&self,b:&B,f:unsafe extern "C" fn(Ptr,Ptr,Ptr,i64))->B {
        let r=B::int(0,self.bits); unsafe{f(r.p,self.p,b.p,self.bits)}; r
    }
    fn unary(&self,f:unsafe extern "C" fn(Ptr,Ptr,i64))->B {
        let r=B::int(0,self.bits); unsafe{f(r.p,self.p,self.bits)}; r
    }
    fn add(&self,b:&B)->B {self.binary(b,ball_add)}
    fn sub(&self,b:&B)->B {self.binary(b,ball_sub)}
    fn mul(&self,b:&B)->B {self.binary(b,ball_mul)}
    fn div(&self,b:&B)->B {self.binary(b,ball_div)}
    fn max(&self,b:&B)->B {self.binary(b,ball_max)}
    fn log(&self)->B {self.unary(ball_log)}
    fn exp(&self)->B {self.unary(ball_exp)}
    fn expm1(&self)->B {self.unary(ball_expm1)}
    fn sqrt(&self)->B {self.unary(ball_sqrt)}
    fn abs(&self)->B {let r=B::int(0,self.bits); unsafe{ball_abs(r.p,self.p)}; r}
    fn gt(&self,b:&B)->bool {unsafe{ball_gt(self.p,b.p)!=0}}
    fn finite(&self)->bool {unsafe{ball_finite(self.p)!=0}}
    fn text(&self)->String {
        unsafe {let p=ball_text(self.p); let s=CStr::from_ptr(p).to_string_lossy().into_owned(); ball_text_free(p); s}
    }
}
struct Stream { d:u64, m:u64, lambda:B }
fn main() {
    let args:Vec<_>=std::env::args().collect();
    assert!(args.len()==4,"usage: direct N number_of_primes precision_bits");
    let cutoff:u64=args[1].parse().unwrap();
    let k:usize=args[2].parse().unwrap();
    let bits:i64=args[3].parse().unwrap();
    assert!((2..=5).contains(&k) && (128..=1024).contains(&bits));
    assert!((2..=3_840_000).contains(&cutoff));
    let z=B::int(0,bits); let one=B::int(1,bits);
    let two=B::int(2,bits); let four=B::int(4,bits);
    let t=B::q(129,800,bits); let y=B::q(87677,2500000,bits).sqrt();
    let pi=B::int(0,bits); unsafe{ball_pi(pi.p,bits)};
    let n0=B::int(cutoff as i64,bits);
    let q=n0.mul(&n0).sub(&t.div(&B::int(16,bits)));
    let x=four.mul(&pi).mul(&q);
    let x2=x.mul(&x);
    let clip=one.sub(&B::int(3,bits).mul(&y))
        .add(&four.mul(&y).mul(&one.add(&y)).div(&x2)).max(&z);
    let sigma=one.add(&y).div(&two).add(&t.mul(&q.log()).div(&four))
        .sub(&t.mul(&clip).div(&two.mul(&x2)));
    let gamma=y.mul(&B::q(1,50,bits).sub(&q.log().div(&two))).exp();
    let rho=t.mul(&y).div(&two.mul(&x.sub(&B::int(6,bits))));
    let primes=[2,3,5,7,11];
    let mut streams=Vec::new();
    let mut normalizer=B::int(0,bits);
    for mask in 0usize..(1usize<<k) {
        let mut d=1u64;
        let mut sumsq=B::int(0,bits);
        let mut sign=1;
        for (j,&p) in primes.iter().take(k).enumerate() {
            if mask&(1<<j)!=0 {
                d*=p; sign=-sign;
                let lp=B::int(p as i64,bits).log(); sumsq=sumsq.add(&lp.mul(&lp));
            }
        }
        let lambda=B::int(sign,bits).mul(&t.mul(&sumsq).div(&four).exp());
        let decay=z.sub(&sigma.mul(&B::int(d as i64,bits).log())).exp();
        normalizer=normalizer.add(&lambda.abs().mul(&decay));
        streams.push(Stream{d,m:1,lambda});
    }
    let mut mass=B::int(0,bits); let mut correction=B::int(0,bits);
    let mut pairs=0u64; let mut terms=0u64;
    loop {
        let next=streams.iter().filter(|s|s.m<=cutoff).map(|s|s.d*s.m).min();
        let n=match next {Some(n)=>n,None=>break};
        let mut a=B::int(0,bits); let mut b=B::int(0,bits);
        for s in &mut streams {
            if s.m<=cutoff && s.d*s.m==n {
                let lm=B::int(s.m as i64,bits).log();
                let heat=t.mul(&lm.mul(&lm)).div(&four).exp();
                let coeff=s.lambda.mul(&heat);
                b=b.add(&coeff); a=a.add(&coeff.mul(&y.mul(&lm).exp()));
                if s.d==1 && n>=2 {
                    let weight=y.sub(&sigma).mul(&lm).exp();
                    correction=correction.add(&heat.mul(&rho.mul(&lm).expm1()).mul(&weight));
                }
                pairs+=1; s.m+=1;
            }
        }
        if n>=2 {
            let weight=z.sub(&sigma.mul(&B::int(n as i64,bits).log())).exp();
            mass=mass.add(&b.abs().add(&gamma.mul(&a.abs())).mul(&weight));
            terms+=1;
        }
        if pairs%(1<<20)==0 {eprintln!("pairs={pairs} n={n}");}
    }
    assert_eq!(pairs,cutoff*(1u64<<k));
    assert!(streams.iter().all(|s|s.m==cutoff+1));
    let lower=one.sub(&gamma).sub(&mass).div(&normalizer).sub(&gamma.mul(&correction));
    assert!(lower.finite(),"nonfinite output");
    println!("N={cutoff} primes={k} bits={bits} pairs={pairs} nonconstant_terms={terms}");
    println!("direct_native_functional={}",lower.text());
    println!("gamma={} mass={} normalizer={} correction={}",gamma.text(),mass.text(),normalizer.text(),gamma.mul(&correction).text());
    // This checks only this fixed N at the exact y0 and t0.
    let error=B::q(233494905213,1_000_000_000_000_000_000,bits);
    if cutoff>=690988 {
        assert!(lower.gt(&error),"fixed-row functional did not exceed error bound");
        println!("FIXED ROW EXCEEDS 233494905213/10^18; NOT A LAMBDA CERTIFICATE");
    }
}
