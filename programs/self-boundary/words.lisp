; Named finite composition, not a self-interpreter or a learned method.
(module self-boundary
  (export learn)
  (def forward (fn ((x Real)) Real (scale 2 (use x))))
  (def reverse (fn ((x Real)) Real (scale 1/2 (use x))))
  (def self (fn ((x Real)) Real (call reverse (call forward (use x)))))
  (def observe (fn ((x Real)) Real (id (use x))))
  (def learn (fn ((x Real)) Real (call observe (call self (use x))))))
