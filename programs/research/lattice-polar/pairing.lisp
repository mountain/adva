(module polar-pairing
  (export reference transported wrong-dual)

  (def dot
    (fn ((x1 Real) (x2 Real) (x3 Real)
         (y1 Real) (y2 Real) (y3 Real)) Real
      (add (add (mul (use x1) (use y1))
                (mul (use x2) (use y2)))
           (mul (use x3) (use y3)))))

  (def shear-body
    (fn ((x1 Real) (x2a Real) (x2b Real) (x3 Real))
        (outputs Real Real Real)
      (frontier (add (use x1) (use x2a)) (use x2b) (use x3))))

  (def shear
    (fn ((x1 Real) (x2 Real) (x3 Real)) (outputs Real Real Real)
      (call shear-body (use x1) (copy (use x2)) (use x3))))

  (def dual-body
    (fn ((y1a Real) (y1b Real) (y2 Real) (y3 Real))
        (outputs Real Real Real)
      (frontier (use y1a) (add (use y2) (neg (use y1b))) (use y3))))

  (def dual-shear
    (fn ((y1 Real) (y2 Real) (y3 Real)) (outputs Real Real Real)
      (call dual-body (copy (use y1)) (use y2) (use y3))))

  (def reference
    (fn ((x1 Real) (x2 Real) (x3 Real)
         (y1 Real) (y2 Real) (y3 Real)) Real
      (call dot (use x1) (use x2) (use x3)
                (use y1) (use y2) (use y3))))

  (def transported
    (fn ((x1 Real) (x2 Real) (x3 Real)
         (y1 Real) (y2 Real) (y3 Real)) Real
      (call dot
        (call shear (use x1) (use x2) (use x3))
        (call dual-shear (use y1) (use y2) (use y3)))))

  (def wrong-dual
    (fn ((x1 Real) (x2 Real) (x3 Real)
         (y1 Real) (y2 Real) (y3 Real)) Real
      (call dot
        (call shear (use x1) (use x2) (use x3))
        (call shear (use y1) (use y2) (use y3))))))
