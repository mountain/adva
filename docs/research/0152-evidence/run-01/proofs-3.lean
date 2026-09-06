import Init
theorem adva152e0 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e0
theorem adva152e1 (x : Int) : ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e1
theorem adva152e2 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e2
theorem adva152e3 (x : Int) : ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e3
theorem adva152e4 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e4
theorem adva152e5 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x))))
#print axioms adva152e5
theorem adva152e6 (x : Int) : ((2 : Int) * ((x + x) + (x + x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e6
theorem adva152e7 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x))))
#print axioms adva152e7
theorem adva152e8 (x : Int) : ((2 : Int) * ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (Int.two_mul ((x + x) + (x + x)))
#print axioms adva152e8
theorem adva152e9 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e9
theorem adva152e10 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e10
theorem adva152e11 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e11
theorem adva152e12 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e12
theorem adva152e13 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e13
theorem adva152e14 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e14
theorem adva152e15 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e15
theorem adva152e16 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e16
theorem adva152e17 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e17
theorem adva152e18 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e18
theorem adva152e19 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e19
theorem adva152e20 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e20
theorem adva152e21 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e21
theorem adva152e22 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e22
theorem adva152e23 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e23
theorem adva152e24 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e24
theorem adva152e25 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e25
theorem adva152e26 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e26
theorem adva152e27 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e27
theorem adva152e28 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e28
theorem adva152e29 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e29
theorem adva152e30 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e30
theorem adva152e31 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e31
theorem adva152e32 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e32
theorem adva152e33 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e33
theorem adva152e34 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e34
theorem adva152e35 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e35
theorem adva152e36 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e36
theorem adva152e37 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e37
theorem adva152e38 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e38
theorem adva152e39 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e39
theorem adva152e40 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e40
theorem adva152e41 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e41
theorem adva152e42 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e42
theorem adva152e43 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e43
theorem adva152e44 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e44
theorem adva152e45 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e45
theorem adva152e46 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e46
theorem adva152e47 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e47
theorem adva152e48 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e48
theorem adva152e49 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e49
theorem adva152e50 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e50
theorem adva152e51 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e51
theorem adva152e52 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e52
theorem adva152e53 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e53
theorem adva152e54 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e54
theorem adva152e55 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e55
theorem adva152e56 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e56
theorem adva152e57 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e57
theorem adva152e58 (x : Int) : ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) = ((2 : Int) * ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e58
theorem adva152e59 (x : Int) : ((2 : Int) * ((x + x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (Int.two_mul ((x + x) + ((2 : Int) * x)))
#print axioms adva152e59
theorem adva152e60 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))))
#print axioms adva152e60
theorem adva152e61 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e61
theorem adva152e62 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e62
theorem adva152e63 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e63
theorem adva152e64 (x : Int) : (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul (x + x))))
#print axioms adva152e64
theorem adva152e65 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e65
theorem adva152e66 (x : Int) : (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul (x + x))))
#print axioms adva152e66
theorem adva152e67 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e67
theorem adva152e68 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e68
theorem adva152e69 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e69
theorem adva152e70 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e70
theorem adva152e71 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e71
theorem adva152e72 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e72
theorem adva152e73 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e73
theorem adva152e74 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e74
theorem adva152e75 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e75
theorem adva152e76 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e76
theorem adva152e77 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e77
theorem adva152e78 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e78
theorem adva152e79 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e79
theorem adva152e80 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e80
theorem adva152e81 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e81
theorem adva152e82 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e82
theorem adva152e83 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e83
theorem adva152e84 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e84
theorem adva152e85 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e85
theorem adva152e86 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e86
theorem adva152e87 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e87
theorem adva152e88 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e88
theorem adva152e89 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e89
theorem adva152e90 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e90
theorem adva152e91 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e91
theorem adva152e92 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e92
theorem adva152e93 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e93
theorem adva152e94 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e94
theorem adva152e95 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e95
theorem adva152e96 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e96
theorem adva152e97 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e97
theorem adva152e98 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e98
theorem adva152e99 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e99
theorem adva152e100 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e100
theorem adva152e101 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e101
theorem adva152e102 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e102
theorem adva152e103 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e103
theorem adva152e104 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e104
theorem adva152e105 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e105
theorem adva152e106 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e106
theorem adva152e107 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e107
theorem adva152e108 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e108
theorem adva152e109 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e109
theorem adva152e110 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e110
theorem adva152e111 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e111
theorem adva152e112 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e112
theorem adva152e113 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e113
theorem adva152e114 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e114
theorem adva152e115 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e115
theorem adva152e116 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e116
theorem adva152e117 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e117
theorem adva152e118 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e118
theorem adva152e119 (x : Int) : ((2 : Int) * (((2 : Int) * x) + ((2 : Int) * x))) = ((2 : Int) * ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e119
theorem adva152e120 (x : Int) : ((2 : Int) * ((x + x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (Int.two_mul ((x + x) + ((2 : Int) * x)))
#print axioms adva152e120
theorem adva152e121 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e121
theorem adva152e122 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e122
theorem adva152e123 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e123
theorem adva152e124 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e124
theorem adva152e125 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e125
theorem adva152e126 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e126
theorem adva152e127 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e127
theorem adva152e128 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e128
theorem adva152e129 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e129
theorem adva152e130 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e130
theorem adva152e131 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e131
theorem adva152e132 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e132
theorem adva152e133 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e133
theorem adva152e134 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e134
theorem adva152e135 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e135
theorem adva152e136 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e136
theorem adva152e137 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e137
theorem adva152e138 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e138
theorem adva152e139 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e139
theorem adva152e140 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e140
theorem adva152e141 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e141
theorem adva152e142 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e142
theorem adva152e143 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e143
theorem adva152e144 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e144
theorem adva152e145 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e145
theorem adva152e146 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e146
theorem adva152e147 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e147
theorem adva152e148 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e148
theorem adva152e149 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e149
theorem adva152e150 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e150
theorem adva152e151 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e151
theorem adva152e152 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e152
theorem adva152e153 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e153
theorem adva152e154 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e154
theorem adva152e155 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e155
theorem adva152e156 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e156
theorem adva152e157 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e157
theorem adva152e158 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e158
theorem adva152e159 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e159
theorem adva152e160 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e160
theorem adva152e161 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e161
theorem adva152e162 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e162
theorem adva152e163 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e163
theorem adva152e164 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e164
theorem adva152e165 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e165
theorem adva152e166 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e166
theorem adva152e167 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e167
theorem adva152e168 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e168
theorem adva152e169 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e169
theorem adva152e170 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e170
theorem adva152e171 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e171
theorem adva152e172 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e172
theorem adva152e173 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e173
theorem adva152e174 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e174
theorem adva152e175 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e175
theorem adva152e176 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e176
theorem adva152e177 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))))
#print axioms adva152e177
theorem adva152e178 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e178
theorem adva152e179 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e179
theorem adva152e180 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e180
theorem adva152e181 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e181
theorem adva152e182 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e182
theorem adva152e183 (x : Int) : (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e183
theorem adva152e184 (x : Int) : (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e184
theorem adva152e185 (x : Int) : (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((Int.two_mul (x + x))))
#print axioms adva152e185
theorem adva152e186 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e186
theorem adva152e187 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e187
theorem adva152e188 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e188
theorem adva152e189 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))))
#print axioms adva152e189
theorem adva152e190 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e190
theorem adva152e191 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e191
theorem adva152e192 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e192
theorem adva152e193 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul (x + x))))
#print axioms adva152e193
theorem adva152e194 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e194
theorem adva152e195 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul (x + x))))
#print axioms adva152e195
theorem adva152e196 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e196
theorem adva152e197 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e197
theorem adva152e198 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((2 : Int) * (x + x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e198
theorem adva152e199 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e199
theorem adva152e200 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e200
theorem adva152e201 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e201
theorem adva152e202 (x : Int) : (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e202
theorem adva152e203 (x : Int) : (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul (x + x))))
#print axioms adva152e203
theorem adva152e204 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e204
theorem adva152e205 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e205
theorem adva152e206 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e206
theorem adva152e207 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e207
theorem adva152e208 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((x + x) + (x + x))) = (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e208
theorem adva152e209 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) = (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e209
theorem adva152e210 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e210
theorem adva152e211 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e211
theorem adva152e212 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x)))))
#print axioms adva152e212
theorem adva152e213 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e213
theorem adva152e214 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e214
theorem adva152e215 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((2 : Int) * (((2 : Int) * x) + (x + x))) := (Int.two_mul (((2 : Int) * x) + (x + x))).symm
#print axioms adva152e215
theorem adva152e216 (x : Int) : ((2 : Int) * (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (Int.two_mul (((2 : Int) * x) + (x + x)))
#print axioms adva152e216
theorem adva152e217 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e217
theorem adva152e218 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e218
theorem adva152e219 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e219
theorem adva152e220 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x)))))
#print axioms adva152e220
theorem adva152e221 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = ((2 : Int) * ((x + x) + (x + x))) := (Int.two_mul ((x + x) + (x + x))).symm
#print axioms adva152e221
theorem adva152e222 (x : Int) : ((2 : Int) * ((x + x) + (x + x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e222
theorem adva152e223 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e223
theorem adva152e224 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e224
theorem adva152e225 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul (x + x))))
#print axioms adva152e225
theorem adva152e226 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e226
theorem adva152e227 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e227
theorem adva152e228 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e228
theorem adva152e229 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e229
theorem adva152e230 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((2 : Int) * (((2 : Int) * x) + (x + x))) := (Int.two_mul (((2 : Int) * x) + (x + x))).symm
#print axioms adva152e230
theorem adva152e231 (x : Int) : ((2 : Int) * (((2 : Int) * x) + (x + x))) = ((2 : Int) * ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e231
theorem adva152e232 (x : Int) : ((2 : Int) * ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (Int.two_mul ((x + x) + (x + x)))
#print axioms adva152e232
theorem adva152e233 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e233
theorem adva152e234 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e234
theorem adva152e235 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e235
theorem adva152e236 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e236
theorem adva152e237 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e237
theorem adva152e238 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((x + x) + (x + x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e238
theorem adva152e239 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e239
theorem adva152e240 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e240
theorem adva152e241 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((2 : Int) * (((2 : Int) * x) + (x + x))) := (Int.two_mul (((2 : Int) * x) + (x + x))).symm
#print axioms adva152e241
theorem adva152e242 (x : Int) : ((2 : Int) * (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (Int.two_mul (((2 : Int) * x) + (x + x)))
#print axioms adva152e242
theorem adva152e243 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e243
theorem adva152e244 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e244
theorem adva152e245 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e245
theorem adva152e246 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e246
theorem adva152e247 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e247
theorem adva152e248 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e248
theorem adva152e249 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e249
theorem adva152e250 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e250
theorem adva152e251 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e251
theorem adva152e252 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e252
theorem adva152e253 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e253
theorem adva152e254 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e254
theorem adva152e255 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = (((2 : Int) * (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e255
theorem adva152e256 (x : Int) : (((2 : Int) * (x + x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e256
theorem adva152e257 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e257
theorem adva152e258 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((x + x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e258
theorem adva152e259 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))))
#print axioms adva152e259
theorem adva152e260 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e260
theorem adva152e261 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e261
theorem adva152e262 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e262
theorem adva152e263 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e263
theorem adva152e264 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((Int.two_mul (x + x))))
#print axioms adva152e264
theorem adva152e265 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x)))))
#print axioms adva152e265
theorem adva152e266 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e266
theorem adva152e267 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e267
theorem adva152e268 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e268
theorem adva152e269 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e269
theorem adva152e270 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e270
theorem adva152e271 (x : Int) : (((x + x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e271
theorem adva152e272 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = ((2 : Int) * ((x + x) + (x + x))) := (Int.two_mul ((x + x) + (x + x))).symm
#print axioms adva152e272
theorem adva152e273 (x : Int) : ((2 : Int) * ((x + x) + (x + x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e273
theorem adva152e274 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e274
theorem adva152e275 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e275
theorem adva152e276 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) = (((2 : Int) * (x + x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e276
theorem adva152e277 (x : Int) : (((2 : Int) * (x + x)) + (((2 : Int) * x) + (x + x))) = (((2 : Int) * (x + x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e277
theorem adva152e278 (x : Int) : (((2 : Int) * (x + x)) + ((x + x) + (x + x))) = (((2 : Int) * (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e278
theorem adva152e279 (x : Int) : (((2 : Int) * (x + x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e279
theorem adva152e280 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e280
theorem adva152e281 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e281
theorem adva152e282 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e282
theorem adva152e283 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e283
theorem adva152e284 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e284
theorem adva152e285 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e285
theorem adva152e286 (x : Int) : (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e286
theorem adva152e287 (x : Int) : (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e287
theorem adva152e288 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e288
theorem adva152e289 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e289
theorem adva152e290 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))))
#print axioms adva152e290
theorem adva152e291 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e291
theorem adva152e292 (x : Int) : (((x + x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e292
theorem adva152e293 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e293
theorem adva152e294 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * ((2 : Int) * x))) = (((x + x) + (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e294
theorem adva152e295 (x : Int) : (((x + x) + (x + x)) + ((2 : Int) * (x + x))) = (((2 : Int) * (x + x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e295
theorem adva152e296 (x : Int) : (((2 : Int) * (x + x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e296
theorem adva152e297 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e297
theorem adva152e298 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e298
theorem adva152e299 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e299
theorem adva152e300 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e300
theorem adva152e301 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e301
theorem adva152e302 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))))
#print axioms adva152e302
theorem adva152e303 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => (z + ((x + x) + (x + x)))) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e303
theorem adva152e304 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e304
theorem adva152e305 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e305
theorem adva152e306 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e306
theorem adva152e307 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e307
theorem adva152e308 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e308
theorem adva152e309 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (z + ((2 : Int) * (x + x)))) ((Int.two_mul ((2 : Int) * x)).symm))
#print axioms adva152e309
theorem adva152e310 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e310
theorem adva152e311 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e311
theorem adva152e312 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * (x + x))) = (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e312
theorem adva152e313 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((Int.two_mul ((2 : Int) * x))))
#print axioms adva152e313
theorem adva152e314 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (((2 : Int) * ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))))
#print axioms adva152e314
theorem adva152e315 (x : Int) : (((2 : Int) * ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))
#print axioms adva152e315
theorem adva152e316 (x : Int) : (((2 : Int) * (x + x)) + ((x + x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((Int.two_mul (x + x))))
#print axioms adva152e316
theorem adva152e317 (x : Int) : (((x + x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))
#print axioms adva152e317
theorem adva152e318 (x : Int) : ((((2 : Int) * x) + (x + x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + ((x + x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))))
#print axioms adva152e318
theorem adva152e319 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + ((x + x) + ((2 : Int) * x))) = ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((((2 : Int) * x) + ((2 : Int) * x)) + z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))))
#print axioms adva152e319
theorem adva152e320 (x : Int) : ((((2 : Int) * x) + ((2 : Int) * x)) + (((2 : Int) * x) + ((2 : Int) * x))) = ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x)))))
#print axioms adva152e320
theorem adva152e321 (x : Int) : ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))
#print axioms adva152e321
theorem adva152e322 (x : Int) : (((x + x) + (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) = (((2 : Int) * (x + x)) + (((2 : Int) * x) + ((2 : Int) * x))) := (congrArg (fun (z : Int) => (z + (((2 : Int) * x) + ((2 : Int) * x)))) ((Int.two_mul (x + x)).symm))
#print axioms adva152e322
theorem adva152e323 (x : Int) : (((x + x) + (x + x)) + ((x + x) + (x + x))) = ((2 : Int) * ((x + x) + (x + x))) := (Int.two_mul ((x + x) + (x + x))).symm
#print axioms adva152e323
theorem adva152e324 (x : Int) : ((2 : Int) * ((x + x) + (x + x))) = ((2 : Int) * ((2 : Int) * (x + x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x)).symm))
#print axioms adva152e324
theorem adva152e325 (x : Int) : ((2 : Int) * ((2 : Int) * (x + x))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * x))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))
#print axioms adva152e325
