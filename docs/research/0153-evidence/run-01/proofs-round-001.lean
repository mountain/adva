import Init
theorem adva152e0 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152e0
theorem adva152e1 (x : Int) : ((2 : Int) * (x + x)) = ((x + x) + (x + x)) := (Int.two_mul (x + x))
#print axioms adva152e1
theorem adva152e2 (x : Int) : ((x + x) + (x + x)) = ((2 : Int) * (x + x)) := (Int.two_mul (x + x)).symm
#print axioms adva152e2
theorem adva152e3 (x : Int) : ((2 : Int) * (x + x)) = ((2 : Int) * ((2 : Int) * x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x).symm))
#print axioms adva152e3
