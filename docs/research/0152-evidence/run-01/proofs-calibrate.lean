import Init
theorem adva152cal0 (x : Int) : ((2 : Int) * x) = (x + x) := (Int.two_mul x)
#print axioms adva152cal0
theorem adva152cal1 (x : Int) : (x + x) = ((2 : Int) * x) := (Int.two_mul x).symm
#print axioms adva152cal1
theorem adva152cal2 (x : Int) : (((2 : Int) * x) + x) = ((x + x) + x) := (congrArg (fun (z : Int) => (z + x)) ((Int.two_mul x)))
#print axioms adva152cal2
theorem adva152cal3 (x : Int) : ((2 : Int) * ((2 : Int) * x)) = ((2 : Int) * (x + x)) := (congrArg (fun (z : Int) => ((2 : Int) * z)) ((Int.two_mul x)))
#print axioms adva152cal3
