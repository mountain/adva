import Init
theorem adva152e0 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * ((2 : Int) * x)))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))))))
#print axioms adva152e0
theorem adva152e1 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * (x + x)))) = ((2 : Int) * ((2 : Int) * ((x + x) + (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x))))))
#print axioms adva152e1
theorem adva152e2 (x : Int) : ((2 : Int) * ((2 : Int) * ((x + x) + (x + x)))) = ((2 : Int) * ((2 : Int) * (((2 : Int) * x) + (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x).symm))))))
#print axioms adva152e2
theorem adva152e3 (x : Int) : ((2 : Int) * ((2 : Int) * (((2 : Int) * x) + (x + x)))) = ((2 : Int) * ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (((2 : Int) * x) + (x + x)))))
#print axioms adva152e3
theorem adva152e4 (x : Int) : ((2 : Int) * ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x)))) = (((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) + ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x)))) := (Int.two_mul ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))))
#print axioms adva152e4
theorem adva152e5 (x : Int) : (((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) + ((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x)))) = (((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) + (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x)))) := (congrArg (fun (z : Int) => (((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) + z)) ((congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))))
#print axioms adva152e5
theorem adva152e6 (x : Int) : (((((2 : Int) * x) + (x + x)) + (((2 : Int) * x) + (x + x))) + (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x)))) = ((((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) + (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x)))) := (congrArg (fun (z : Int) => (z + (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))))) ((congrArg (fun (z : Int) => (z + (((2 : Int) * x) + (x + x)))) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))))
#print axioms adva152e6
theorem adva152e7 (x : Int) : ((((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) + (((x + x) + (x + x)) + (((2 : Int) * x) + (x + x)))) = ((((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) + (((x + x) + (x + x)) + ((x + x) + (x + x)))) := (congrArg (fun (z : Int) => ((((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) + z)) ((congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))))
#print axioms adva152e7
theorem adva152e8 (x : Int) : ((((x + x) + (x + x)) + (((2 : Int) * x) + (x + x))) + (((x + x) + (x + x)) + ((x + x) + (x + x)))) = ((((x + x) + (x + x)) + ((x + x) + (x + x))) + (((x + x) + (x + x)) + ((x + x) + (x + x)))) := (congrArg (fun (z : Int) => (z + (((x + x) + (x + x)) + ((x + x) + (x + x))))) ((congrArg (fun (z : Int) => (((x + x) + (x + x)) + z)) ((congrArg (fun (z : Int) => (z + (x + x))) ((Int.two_mul x)))))))
#print axioms adva152e8
theorem adva152e9 (x : Int) : ((((x + x) + (x + x)) + ((x + x) + (x + x))) + (((x + x) + (x + x)) + ((x + x) + (x + x)))) = ((2 : Int) * (((x + x) + (x + x)) + ((x + x) + (x + x)))) := (Int.two_mul (((x + x) + (x + x)) + ((x + x) + (x + x)))).symm
#print axioms adva152e9
theorem adva152e10 (x : Int) : ((2 : Int) * (((x + x) + (x + x)) + ((x + x) + (x + x)))) = ((2 : Int) * ((2 : Int) * ((x + x) + (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((x + x) + (x + x))).symm))
#print axioms adva152e10
theorem adva152e11 (x : Int) : ((2 : Int) * ((2 : Int) * ((x + x) + (x + x)))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul (x + x)).symm))))
#print axioms adva152e11
theorem adva152e12 (x : Int) : ((2 : Int) * ((2 : Int) * ((2 : Int) * (x + x)))) = ((2 : Int) * (((2 : Int) * (x + x)) + ((2 : Int) * (x + x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * (x + x)))))
#print axioms adva152e12
theorem adva152e13 (x : Int) : ((2 : Int) * (((2 : Int) * (x + x)) + ((2 : Int) * (x + x)))) = ((2 : Int) * (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => (((2 : Int) * (x + x)) + z)) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))))
#print axioms adva152e13
theorem adva152e14 (x : Int) : ((2 : Int) * (((2 : Int) * (x + x)) + ((2 : Int) * ((2 : Int) * x)))) = ((2 : Int) * (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((congrArg (fun (z : Int) => (z + ((2 : Int) * ((2 : Int) * x)))) ((congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))))))
#print axioms adva152e14
theorem adva152e15 (x : Int) : ((2 : Int) * (((2 : Int) * ((2 : Int) * x)) + ((2 : Int) * ((2 : Int) * x)))) = ((2 : Int) * ((2 : Int) * ((2 : Int) * ((2 : Int) * x)))) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul ((2 : Int) * ((2 : Int) * x))).symm))
#print axioms adva152e15
