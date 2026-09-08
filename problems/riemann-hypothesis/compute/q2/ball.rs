// Arb arithmetic interface shared by the independent interpolation code.
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
    fn ball_cos(r:Ptr,a:Ptr,bits:i64);
    fn ball_inflate(r:Ptr,error:Ptr);
    fn ball_floor12(out:*mut i64,a:Ptr,bits:i64)->i32;
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
    fn cos(&self)->B {self.unary(ball_cos)}
    fn inflate(&mut self,error:&B) {unsafe{ball_inflate(self.p,error.p)}}
    fn floor12(&self)->i64 {let mut n=0i64; assert!(unsafe{ball_floor12(&mut n,self.p,self.bits)}!=0); n}
    fn abs(&self)->B {let r=B::int(0,self.bits); unsafe{ball_abs(r.p,self.p)}; r}
    fn gt(&self,b:&B)->bool {unsafe{ball_gt(self.p,b.p)!=0}}
    fn finite(&self)->bool {unsafe{ball_finite(self.p)!=0}}
    fn text(&self)->String {
        unsafe {let p=ball_text(self.p); let s=CStr::from_ptr(p).to_string_lossy().into_owned(); ball_text_free(p); s}
    }
}
