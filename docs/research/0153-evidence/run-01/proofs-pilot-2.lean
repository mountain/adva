import Init
theorem adva152e0 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e0
theorem adva152e1 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e1
theorem adva152e2 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e2
theorem adva152e3 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e3
theorem adva152e4 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x))
#print axioms adva152e4
theorem adva152e5 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))
#print axioms adva152e5
theorem adva152e6 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e6
theorem adva152e7 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e7
theorem adva152e8 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e8
theorem adva152e9 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e9
theorem adva152e10 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e10
theorem adva152e11 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x))
#print axioms adva152e11
theorem adva152e12 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x)))
#print axioms adva152e12
theorem adva152e13 (x : Int) : (((2 : Int) * x) + (x + x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))
#print axioms adva152e13
theorem adva152e14 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x))
#print axioms adva152e14
theorem adva152e15 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))
#print axioms adva152e15
theorem adva152e16 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e16
theorem adva152e17 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x))
#print axioms adva152e17
theorem adva152e18 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))
#print axioms adva152e18
theorem adva152e19 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e19
theorem adva152e20 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e20
theorem adva152e21 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e21
theorem adva152e22 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e22
theorem adva152e23 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e23
theorem adva152e24 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e24
theorem adva152e25 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e25
theorem adva152e26 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e26
theorem adva152e27 (x : Int) : (((2 : Int) * x) + (x + x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e27
theorem adva152e28 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))
#print axioms adva152e28
theorem adva152e29 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e29
theorem adva152e30 (x : Int) : ((x + x) + (x + x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e30
theorem adva152e31 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e31
theorem adva152e32 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e32
theorem adva152e33 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e33
theorem adva152e34 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e34
theorem adva152e35 (x : Int) : (((2 : Int) * x) + (x + x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e35
theorem adva152e36 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x)))
#print axioms adva152e36
theorem adva152e37 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e37
theorem adva152e38 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e38
theorem adva152e39 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e39
theorem adva152e40 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e40
theorem adva152e41 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e41
theorem adva152e42 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e42
theorem adva152e43 (x : Int) : (((2 : Int) * x) + (x + x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))
#print axioms adva152e43
theorem adva152e44 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e44
theorem adva152e45 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e45
theorem adva152e46 (x : Int) : ((x + x) + (x + x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e46
theorem adva152e47 (x : Int) : ((x + x) + ((2 : Int) * x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (z + ((2 : Int) * x))) ((Int.two_mul x).symm))
#print axioms adva152e47
theorem adva152e48 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x)))
#print axioms adva152e48
theorem adva152e49 (x : Int) : (((2 : Int) * x) + (x + x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))
#print axioms adva152e49
theorem adva152e50 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e50
theorem adva152e51 (x : Int) : (((2 : Int) * x) + (x + x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))
#print axioms adva152e51
theorem adva152e52 (x : Int) : ((x + x) + (x + x)) = ((x + x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e52
theorem adva152e53 (x : Int) : ((x + x) + ((2 : Int) * x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => ((x + x) + z)) ((Int.two_mul x)))
#print axioms adva152e53
theorem adva152e54 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e54
theorem adva152e55 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e55
theorem adva152e56 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e56
theorem adva152e57 (x : Int) : (((2 : Int) * x) + (x + x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e57
theorem adva152e58 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((2 : Int) * ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x)).symm
#print axioms adva152e58
theorem adva152e59 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e59
theorem adva152e60 (x : Int) : (((2 : Int) * x) + (x + x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e60
theorem adva152e61 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((2 : Int) * ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x)).symm
#print axioms adva152e61
theorem adva152e62 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e62
theorem adva152e63 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e63
theorem adva152e64 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e64
theorem adva152e65 (x : Int) : (((2 : Int) * x) + (x + x)) = ((x + x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))
#print axioms adva152e65
theorem adva152e66 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e66
theorem adva152e67 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e67
theorem adva152e68 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e68
theorem adva152e69 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e69
theorem adva152e70 (x : Int) : ((x + x) + (x + x)) = (((2 : Int) * x) + (x + x)) := (congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))
#print axioms adva152e70
theorem adva152e71 (x : Int) : (((2 : Int) * x) + (x + x)) = (((2 : Int) * x) + ((2 : Int) * x)) := (congrArg (fun (z : Int) => (((2 : Int) * x) + z)) ((Int.two_mul x).symm))
#print axioms adva152e71
theorem adva152e72 (x : Int) : (((2 : Int) * x) + ((2 : Int) * x)) = ((2 : Int) * ((2 : Int) * x)) := (Int.two_mul ((2 : Int) * x)).symm
#print axioms adva152e72
theorem adva152e73 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e73
theorem adva152e74 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e74
