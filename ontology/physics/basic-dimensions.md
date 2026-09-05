# Basic Dimensions

Status: proposed physical formation vocabulary.

## Type formation

Introduce the physical type

\[
\vdash_{\mathsf{Physics}}
\mathsf{BasicDimension}
:
\mathsf{PhysicalType}.
\]

A basic dimension is a physical dimension word. It is not a number, unit,
measured value, proposition, or bare metaphysical type.

## First declared basis

Use the seven SI base-quantity dimensions as the first explicit physical
basis:

\[
\begin{aligned}
\vdash_{\mathsf{Physics}}\;&
\mathsf{Length},
\mathsf{Mass},
\mathsf{Time},
\mathsf{ElectricCurrent},
\\
&
\mathsf{ThermodynamicTemperature},
\mathsf{AmountOfSubstance},
\mathsf{LuminousIntensity}
:
\mathsf{BasicDimension}.
\end{aligned}
\]

Write

\[
\mathcal B_{\mathrm{SI}}
=
\{
\mathsf{Length},
\mathsf{Mass},
\mathsf{Time},
\mathsf{ElectricCurrent},
\mathsf{ThermodynamicTemperature},
\mathsf{AmountOfSubstance},
\mathsf{LuminousIntensity}
\}.
\]

This basis is a declared physical presentation. The present ontology does not
claim that it is canonical, irreducible, or metaphysically final. Natural-unit
systems, geometric units, or a later physical theory may provide a different
basis or certified identifications among its members.

## Dimension words

A future mathematical layer should construct a dimension word as a finite
formal exponent assignment on a declared basis:

\[
d:
\mathcal B_{\mathrm{SI}}
\longrightarrow
\mathbb Z,
\qquad
\operatorname{supp}(d)
\text{ finite}.
\]

The familiar multiplicative notation

\[
D
=
\prod_{b\in\mathcal B_{\mathrm{SI}}}
b^{d(b)}
\]

is only a requested mathematical presentation until integer exponents,
composition, inverse, equality, and normalization have been defined and
proved.

A base dimension embeds as the corresponding one-generator dimension word.
The dimensionless word is the zero exponent assignment. It must not be
identified merely by spelling with the metaphysical term
\(1:\mathrm{Number}\).

## Physical quantities

A numerical coordinate becomes a physical quantity only under a certified
dimension word:

\[
x:X_D,
\qquad
D:\mathsf{DimensionWord}
\quad\Longrightarrow\quad
xD:\mathsf{PhysicalQuantity}(D).
\]

The number or coordinate \(x\) does not carry the physical dimension. The
spatial type \(X_D\), the sealed word \(D\), and their formation certificate
supply that structure.

## Required separations

The physical calculus must keep distinct:

- base dimension and derived dimension word;
- dimension and unit;
- unit and numerical coordinate;
- coordinate and measured quantity;
- quantity and observable;
- equality of dimensions and equality of physical states; and
- a change of basis and an ontological identification.

No metre, kilogram, second, ampere, kelvin, mole, candela, conversion factor,
measurement law, or physical constant is introduced in this file.

## Closure obligations

Declaring the seven terms makes them available as open physical vocabulary. A
term becomes a certified semantic word only after the relevant machine and
semantic paths provide:

1. its typed generating machine or primitive declaration;
2. a closure or formation certificate;
3. its allowed scalar or coordinate space;
4. invariance under admitted presentation and chart changes;
5. composition rules for derived dimensions;
6. residual and reopen behavior; and
7. one nontrivial physical model or calibration in its declared scope.

Until then, the basis is a requirement on the future physics calculus, not a
completed physical theory.
