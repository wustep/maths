# compute — simon-lieb-thirring

Replay of published comparison constants. This folder does not claim
a new Lieb–Thirring bound.

```bash
sh run_all.sh
```

`lt_constants.py` rebuilds the classical constant from the Gamma
formula, checks Lcl(1,1) = 2/(3π) and Lcl(3/2,1) = 3/16 against
those closed forms, records the Frank–Hundertmark–Jex–Nam ratio
1.456 and the conjectured one-bound-state ratio 2/√3, and evaluates
Pöschl–Teller sech² witnesses. Those witnesses are lower bounds on
L(γ,1). They sit below 1.456. That is required, not a beat.

Output: `record.json`.
