//! Native exact addition/multiplication reading of the 0233 twelve-phase fixture.
//!
//! This example runs the periodic addition/multiplication fixture of
//! `docs/research/0233-periodic-programs-before-floquet-observations.md`
//! natively through the exact power--weight carrier of `adva_witness`.
//!
//! The rate reading is the action of the addition generator `A` and the
//! multiplication generator `M` on the annual carrier element. No matrix, no
//! Jacobian, and no matrix product is used anywhere in this example, and no
//! floating point value is constructed or printed: every reported number is an
//! exact rational.
//!
//! The report written to `--output <path>` is deterministic. It contains the
//! schema, the declared fixture, the readings, the controls, the checks, and the
//! scope statement, and nothing else: no timestamp of the run, no duration, no
//! host path, and no host identity.
//!
//! This example creates no stable API, no `ValueType`, no `OperationSpec`, no IR
//! version, no `Seal`, and no terminology home, and it makes no weather or
//! physical claim.

use adva_witness::{
    AdditionInverse, AffineStep, AmElement, AmError, ExactRational, MultiplicationInverse,
    ResonancePolicy, compose_polynomial, evaluate_at,
};
use serde_json::{Value, json};
use std::error::Error;
use std::fs;
use std::path::PathBuf;

/// Schema identifier of the report written by this example.
const REPORT_SCHEMA: &str = "adva.witness.am-variation-reading";

/// Report schema version. Version zero is a research reading, not `adva.ir`.
const REPORT_VERSION: u32 = 0;

/// Number of phases in the declared periodic fixture.
const PHASE_COUNT: usize = 12;

/// The declared 0233 reference path `s_0 .. s_12`.
const REFERENCE_PATH: [i64; 13] = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1, 0, -1, 0];

/// Numerator and denominator of the declared reference shift `1/8`.
const REFERENCE_SHIFT: (i64, i64) = (1, 8);

/// An exact rational built from declared machine-word literals.
fn rational(numerator: i64, denominator: i64) -> Result<ExactRational, AmError> {
    ExactRational::from_parts(numerator, denominator)
}

/// The declared phase dilations `a_0 .. a_11`.
fn declared_dilations() -> Result<Vec<ExactRational>, AmError> {
    let mut values = vec![ExactRational::one(); PHASE_COUNT];
    values[0] = rational(1, 2)?;
    values[1] = rational(3, 4)?;
    Ok(values)
}

/// The declared phase curvatures `q_0 .. q_11`.
fn declared_curvatures() -> Result<Vec<ExactRational>, AmError> {
    let mut values = vec![ExactRational::zero(); PHASE_COUNT];
    values[0] = rational(1, 8)?;
    values[1] = rational(1, 8)?;
    Ok(values)
}

/// The nonlinear-control dilations `a = (3/4, 1/2, 1, ...)`.
fn swapped_dilations() -> Result<Vec<ExactRational>, AmError> {
    let mut values = declared_dilations()?;
    values[0] = rational(3, 4)?;
    values[1] = rational(1, 2)?;
    Ok(values)
}

/// One phase map as a carrier element in the variable `a`:
/// `F_m(a) = s_{m+1} + a_m (a - s_m) + q_m (a - s_m)^2`.
fn phase_element(
    reference: &[i64],
    dilations: &[ExactRational],
    curvatures: &[ExactRational],
    m: usize,
) -> Result<AmElement, AmError> {
    let centered = AmElement::variable_a()
        .subtract(&AmElement::constant(ExactRational::integer(reference[m])));
    let linear = centered.scale(&dilations[m]);
    let quadratic = centered.power(2)?.scale(&curvatures[m]);
    Ok(
        AmElement::constant(ExactRational::integer(reference[m + 1]))
            .add(&linear)
            .add(&quadratic),
    )
}

/// The annual return element: the twelve phase maps composed chronologically in
/// the carrier, phase 0 first, minus the reference endpoint `s_12`.
fn annual_element(
    reference: &[i64],
    dilations: &[ExactRational],
    curvatures: &[ExactRational],
) -> Result<AmElement, AmError> {
    let mut composition = AmElement::variable_a();
    for m in 0..PHASE_COUNT {
        composition = compose_polynomial(
            &phase_element(reference, dilations, curvatures, m)?,
            &composition,
        )?;
    }
    Ok(
        composition.subtract(&AmElement::constant(ExactRational::integer(
            reference[PHASE_COUNT],
        ))),
    )
}

/// The annual affine holonomy of the twelve affine parts, composed
/// chronologically with phase 0 first.
fn affine_holonomy(reference: &[i64], dilations: &[ExactRational]) -> Result<AffineStep, AmError> {
    let mut holonomy = AffineStep::identity();
    for m in 0..PHASE_COUNT {
        let translation = ExactRational::integer(reference[m + 1])
            .subtract(&dilations[m].multiply(&ExactRational::integer(reference[m])));
        holonomy = holonomy.then(&AffineStep::new(dilations[m].clone(), translation));
    }
    Ok(holonomy)
}

/// The twelve defects `d_m = F_m(c_m) - c_{m+1}` of the shifted reference
/// `c_m = s_m + 1/8`.
fn shifted_reference_defects(
    reference: &[i64],
    dilations: &[ExactRational],
    curvatures: &[ExactRational],
) -> Result<Vec<ExactRational>, AmError> {
    let shift = rational(REFERENCE_SHIFT.0, REFERENCE_SHIFT.1)?;
    let mut defects = Vec::with_capacity(PHASE_COUNT);
    for m in 0..PHASE_COUNT {
        let declared = ExactRational::integer(reference[m]).add(&shift);
        let next = ExactRational::integer(reference[m + 1]).add(&shift);
        let image = evaluate_at(
            &phase_element(reference, dilations, curvatures, m)?,
            &declared,
        )?;
        defects.push(image.subtract(&next));
    }
    Ok(defects)
}

/// The exact surface readings of a coefficient list.
fn surfaces(values: &[ExactRational]) -> Vec<String> {
    values.iter().map(ExactRational::surface).collect()
}

/// The declared variant name of a typed carrier error.
fn error_variant(error: &AmError) -> &'static str {
    match error {
        AmError::ZeroDenominator => "zero_denominator",
        AmError::DivisionByZero => "division_by_zero",
        AmError::ResonanceUnderOrdinaryOnly { .. } => "resonance_under_ordinary_only",
        AmError::NonPolynomialComposition => "non_polynomial_composition",
        AmError::NonPolynomialEvaluation => "non_polynomial_evaluation",
        AmError::ExponentOverflow => "exponent_overflow",
        AmError::NegativeExponent { .. } => "negative_exponent",
        AmError::DegreeBeyondBound { .. } => "degree_beyond_bound",
        AmError::NonPositiveWitness { .. } => "non_positive_witness",
    }
}

/// The declared kind of an addition-primitive outcome.
fn addition_inverse_kind(outcome: &AdditionInverse) -> &'static str {
    match outcome {
        AdditionInverse::Ordinary(_) => "ordinary",
        AdditionInverse::Logarithmic { .. } => "logarithmic",
    }
}

/// The declared kind of a multiplication-primitive outcome.
fn multiplication_inverse_kind(outcome: &MultiplicationInverse) -> &'static str {
    match outcome {
        MultiplicationInverse::Ordinary(_) => "ordinary",
        MultiplicationInverse::Jordan { .. } => "jordan",
    }
}

/// The declared checks of this run.
struct Checks {
    entries: Vec<Value>,
}

impl Checks {
    /// An empty check list.
    fn new() -> Self {
        Self {
            entries: Vec::new(),
        }
    }

    /// Records one assertion and fails the run when it does not hold.
    fn record(
        &mut self,
        id: &str,
        statement: &str,
        expected: &str,
        observed: &str,
    ) -> Result<(), Box<dyn Error>> {
        let passed = expected == observed;
        self.entries.push(json!({
            "id": id,
            "statement": statement,
            "expected": expected,
            "observed": observed,
            "status": if passed { "pass" } else { "fail" },
        }));
        if passed {
            Ok(())
        } else {
            Err(format!("check {id} failed: expected {expected}, observed {observed}").into())
        }
    }

    /// Records one assertion over an exact coefficient list.
    fn record_coefficients(
        &mut self,
        id: &str,
        statement: &str,
        expected: &[&str],
        observed: &[ExactRational],
    ) -> Result<(), Box<dyn Error>> {
        let observed = surfaces(observed).join(",");
        self.record(id, statement, &expected.join(","), &observed)
    }

    /// The recorded entries.
    fn into_value(self) -> Value {
        Value::Array(self.entries)
    }
}

/// A reported finite-difference reading.
struct FiniteDifference {
    input: ExactRational,
    value: ExactRational,
    residual: ExactRational,
}

/// Builds the deterministic report, together with its short summary lines.
fn build_report() -> Result<(Value, Vec<String>), Box<dyn Error>> {
    let reference = REFERENCE_PATH;
    let dilations = declared_dilations()?;
    let curvatures = declared_curvatures()?;
    let mut checks = Checks::new();

    // Reading 1: the annual affine holonomy of the twelve affine parts.
    let holonomy = affine_holonomy(&reference, &dilations)?;
    checks.record(
        "holonomy_dilation",
        "the chronological composite of the twelve affine parts has dilation 3/8",
        "3/8",
        &holonomy.dilation.surface(),
    )?;
    checks.record(
        "holonomy_translation",
        "the accumulated translation of the twelve affine parts is 0",
        "0",
        &holonomy.translation.surface(),
    )?;

    // Reading 2: the annual return element in the carrier variable a.
    let annual = annual_element(&reference, &dilations, &curvatures)?;
    let annual_coefficients = annual.polynomial_coefficients()?;
    checks.record_coefficients(
        "annual_return_coefficients",
        "the annual return element has ascending coefficients 0, 3/8, 1/8, 1/64, 1/512",
        &["0", "3/8", "1/8", "1/64", "1/512"],
        &annual_coefficients,
    )?;

    // Reading 3: the rate readings as generator actions, not a Jacobian.
    let addition_reading = annual.apply_a()?;
    let addition_coefficients = addition_reading.polynomial_coefficients()?;
    checks.record_coefficients(
        "addition_reading_coefficients",
        "A(annual) has ascending coefficients 3/8, 1/4, 3/64, 1/128",
        &["3/8", "1/4", "3/64", "1/128"],
        &addition_coefficients,
    )?;
    let addition_at_reference = evaluate_at(&addition_reading, &ExactRational::zero())?;
    checks.record(
        "addition_reading_at_reference",
        "A(annual) evaluated at the reference a = 0 is 3/8",
        "3/8",
        &addition_at_reference.surface(),
    )?;
    checks.record(
        "holonomy_cross_check",
        "the generator reading at the reference equals the affine holonomy dilation",
        &holonomy.dilation.surface(),
        &addition_at_reference.surface(),
    )?;
    let multiplication_reading = annual.apply_m();
    let multiplication_coefficients = multiplication_reading.polynomial_coefficients()?;
    checks.record_coefficients(
        "multiplication_reading_coefficients",
        "M(annual) has the weight reading 0, 3/8, 1/4, 3/64, 1/128",
        &["0", "3/8", "1/4", "3/64", "1/128"],
        &multiplication_coefficients,
    )?;

    // Reading 4: exact finite differences from native evaluation.
    let mut finite_differences = Vec::with_capacity(4);
    let declared_inputs = [
        rational(1, 2)?,
        rational(1, 4)?,
        rational(-1, 4)?,
        rational(-1, 2)?,
    ];
    let declared_values = ["1809/8192", "13345/131072", "-11295/131072", "-1295/8192"];
    let declared_residuals = ["273/8192", "1057/131072", "993/131072", "241/8192"];
    for (index, input) in declared_inputs.iter().enumerate() {
        let value = evaluate_at(&annual, input)?;
        let residual = value.subtract(&holonomy.dilation.multiply(input));
        checks.record(
            &format!(
                "finite_difference_value_h_{}",
                input.surface().replace('/', "_")
            ),
            "the annual element has the declared exact value at this finite amplitude",
            declared_values[index],
            &value.surface(),
        )?;
        checks.record(
            &format!(
                "finite_difference_residual_h_{}",
                input.surface().replace('/', "_")
            ),
            "the finite-difference residual E(h) - (3/8)h has the declared exact value",
            declared_residuals[index],
            &residual.surface(),
        )?;
        finite_differences.push(FiniteDifference {
            input: input.clone(),
            value,
            residual,
        });
    }

    // Control 1: swapped nonlinear phases.
    let swapped = annual_element(&reference, &swapped_dilations()?, &curvatures)?;
    let swapped_holonomy = affine_holonomy(&reference, &swapped_dilations()?)?;
    checks.record(
        "swapped_holonomy_dilation",
        "swapping the two nonlinear phases retains the holonomy dilation 3/8",
        "3/8",
        &swapped_holonomy.dilation.surface(),
    )?;
    let swapped_coefficients = swapped.polynomial_coefficients()?;
    checks.record_coefficients(
        "swapped_annual_coefficients",
        "the swapped annual return has ascending coefficients 0, 3/8, 17/128, 3/128, 1/512",
        &["0", "3/8", "17/128", "3/128", "1/512"],
        &swapped_coefficients,
    )?;

    // Control 2: the shifted periodic reference and its defects.
    let defects = shifted_reference_defects(&reference, &dilations, &curvatures)?;
    checks.record_coefficients(
        "shifted_reference_defects",
        "the shifted reference has defects -31/512, -15/512 and zero elsewhere",
        &[
            "-31/512", "-15/512", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        ],
        &defects,
    )?;

    // Control 3: the exp completion forced by a declared multiplicative flow.
    let flow_labels = [(0_usize, rational(1, 2)?), (1_usize, rational(-1, 3)?)];
    let mut dilation_product = AmElement::one();
    let mut phase_labels = Vec::with_capacity(PHASE_COUNT);
    for m in 0..PHASE_COUNT {
        let atom = match flow_labels.iter().find(|(index, _)| *index == m) {
            Some((_, label)) => AmElement::exp_atom(label.clone()),
            None => AmElement::constant(ExactRational::one()),
        };
        phase_labels.push(json!({
            "phase": m,
            "dilation_reading": atom.surface(),
            "exp_label": atom
                .terms()
                .keys()
                .next()
                .map(|key| key.2.surface())
                .unwrap_or_else(|| ExactRational::zero().surface()),
        }));
        dilation_product = dilation_product.multiply(&atom)?;
    }
    let composed_term = dilation_product
        .terms()
        .iter()
        .next()
        .ok_or("the composed exp reading is empty")?;
    checks.record(
        "exp_label_composition",
        "the two declared flow labels compose to the single exact label e^{1/6}",
        "1/6",
        &composed_term.0.2.surface(),
    )?;
    checks.record(
        "exp_reading_term_count",
        "the composed exp reading is a single carrier term",
        "1",
        &dilation_product.term_count().to_string(),
    )?;
    checks.record(
        "exp_reading_coefficient",
        "the composed exp reading has coefficient 1",
        "1",
        &composed_term.1.surface(),
    )?;
    let polynomial_refusal = dilation_product
        .polynomial_coefficients()
        .err()
        .ok_or("the exp reading must not be readable as a rational polynomial")?;
    checks.record(
        "exp_reading_refused_by_polynomial_module",
        "the fixed rational polynomial module refuses the exp reading with a typed error",
        "non_polynomial_evaluation",
        error_variant(&polynomial_refusal),
    )?;
    let flow_linear = AmElement::exp_atom(rational(1, 2)?).multiply(&AmElement::variable_a())?;
    let flow_linear_refusal = compose_polynomial(&flow_linear, &AmElement::variable_a())
        .err()
        .ok_or("the exp-carrying phase must not be composable in the polynomial module")?;
    checks.record(
        "exp_phase_refused_by_polynomial_composition",
        "an exp-carrying phase element is refused by polynomial composition",
        "non_polynomial_composition",
        error_variant(&flow_linear_refusal),
    )?;

    // Control 4: the two resonances under both policies.
    let resonant_a = AmElement::monomial(-1, rational(2, 1)?, rational(1, 3)?, rational(-3, 4)?);
    let declared_a = resonant_a.apply_a_inverse(ResonancePolicy::DeclaredExtension)?;
    let (logarithmic_surface, witness_surface, extension_weight, witness_positive) =
        match &declared_a {
            AdditionInverse::Logarithmic { extension, .. } => {
                let contribution = extension
                    .contributions()
                    .first()
                    .ok_or("the logarithmic extension carries no contribution")?;
                (
                    extension.surface(),
                    extension.witness_a().surface(),
                    contribution.extension_weight().surface(),
                    extension.witness_a().is_positive(),
                )
            }
            AdditionInverse::Ordinary(ordinary) => {
                return Err(format!(
                    "expected a logarithmic extension, got the ordinary element {}",
                    ordinary.surface()
                )
                .into());
            }
        };
    checks.record(
        "resonance_addition_declared_extension",
        "A^-1 at nu = -1 yields the typed logarithmic extension rather than an ordinary element",
        "logarithmic",
        addition_inverse_kind(&declared_a),
    )?;
    checks.record(
        "resonance_addition_witness_positive",
        "the logarithmic extension carries the required witness a > 0",
        "true",
        if witness_positive { "true" } else { "false" },
    )?;
    checks.record(
        "resonance_addition_extension_weight",
        "the extension exponent weight is w + 1 = 3 for the resonant w = 2 term",
        "3",
        &extension_weight,
    )?;
    let ordinary_a = resonant_a.apply_a_inverse(ResonancePolicy::OrdinaryOnly);
    let ordinary_a_variant = match &ordinary_a {
        Err(error) => error_variant(error),
        Ok(_) => "ordinary",
    };
    checks.record(
        "resonance_addition_ordinary_only",
        "A^-1 at nu = -1 fails closed with a typed error under OrdinaryOnly",
        "resonance_under_ordinary_only",
        ordinary_a_variant,
    )?;
    let ordinary_a_surface = match &ordinary_a {
        Err(error) => error.to_string(),
        Ok(_) => String::new(),
    };

    let resonant_m =
        AmElement::monomial(2, ExactRational::zero(), rational(1, 5)?, rational(7, 2)?);
    let declared_m = resonant_m.apply_m_inverse(ResonancePolicy::DeclaredExtension)?;
    let (jordan_surface, jordan_shape) = match &declared_m {
        MultiplicationInverse::Jordan { extension, .. } => {
            let contribution = extension
                .contributions()
                .first()
                .ok_or("the Jordan extension carries no contribution")?;
            (
                extension.surface(),
                format!("v * Phi_{{{},0}}", contribution.nu()),
            )
        }
        MultiplicationInverse::Ordinary(ordinary) => {
            return Err(format!(
                "expected a Jordan extension, got the ordinary element {}",
                ordinary.surface()
            )
            .into());
        }
    };
    checks.record(
        "resonance_multiplication_declared_extension",
        "M^-1 at w = 0 yields the typed Jordan extension rather than an ordinary element",
        "jordan",
        multiplication_inverse_kind(&declared_m),
    )?;
    checks.record(
        "resonance_multiplication_jordan_shape",
        "the Jordan extension of the resonant nu = 2 term is the shape v * Phi_{2,0}",
        "v * Phi_{2,0}",
        &jordan_shape,
    )?;
    let ordinary_m = resonant_m.apply_m_inverse(ResonancePolicy::OrdinaryOnly);
    let ordinary_m_variant = match &ordinary_m {
        Err(error) => error_variant(error),
        Ok(_) => "ordinary",
    };
    checks.record(
        "resonance_multiplication_ordinary_only",
        "M^-1 at w = 0 fails closed with a typed error under OrdinaryOnly",
        "resonance_under_ordinary_only",
        ordinary_m_variant,
    )?;
    let ordinary_m_surface = match &ordinary_m {
        Err(error) => error.to_string(),
        Ok(_) => String::new(),
    };

    // An extra native identity check on the annual element itself.
    checks.record(
        "pbw_residual_on_annual_element",
        "the PBW residual M^2 A^3 - A^3 (M - 3)^2 is the zero element on the annual element",
        "0",
        &annual.pbw_residual(3, 2)?.surface(),
    )?;

    let total = checks.entries.len();
    let checks_value = checks.into_value();

    let fixture = json!({
        "reference_path": reference
            .iter()
            .map(|value| value.to_string())
            .collect::<Vec<String>>(),
        "phase_count": PHASE_COUNT,
        "phase_rule": "F_m(x) = s_{m+1} + a_m (x - s_m) + q_m (x - s_m)^2",
        "phase_dilations": surfaces(&dilations),
        "phase_curvatures": surfaces(&curvatures),
        "chronological_order": "phase 0 executes first",
        "carrier_term": "c * e^q * Phi_{nu,w} with Phi_{nu,w} = a^nu * e^{(w - nu) v}",
        "generators": {
            "addition": "A(Phi_{nu,w}) = nu * Phi_{nu-1,w-1}",
            "multiplication": "M(Phi_{nu,w}) = w * Phi_{nu,w}",
            "shifted": "(M - m) acts by the exact factor w - m",
            "pbw": "M^n A^m = A^m (M - m)^n",
        },
    });

    let readings = json!({
        "annual_affine_holonomy": {
            "dilation": holonomy.dilation.surface(),
            "translation": holonomy.translation.surface(),
            "normal_form": format!(
                "T_{} D_{}",
                holonomy.translation.surface(),
                holonomy.dilation.surface()
            ),
            "composition": "phase 0 first, then phase 1, ... then phase 11",
        },
        "annual_return_element": {
            "carrier_variable": "a (the anomaly h)",
            "coefficients_ascending": surfaces(&annual_coefficients),
            "surface": annual.surface(),
            "construction": "twelve phase maps composed in the carrier, minus the reference endpoint s_12",
        },
        "generator_readings": {
            "addition_generator_coefficients_ascending": surfaces(&addition_coefficients),
            "addition_generator_at_reference": addition_at_reference.surface(),
            "addition_generator_at_reference_equals_holonomy": addition_at_reference
                == holonomy.dilation,
            "multiplication_generator_coefficients_ascending": surfaces(&multiplication_coefficients),
            "multiplication_generator_rule": "the weight reading k * c_k",
            "no_matrix_or_jacobian": "the readings are generator actions on the carrier, not a Jacobian and not a matrix product",
        },
        "finite_differences": finite_differences
            .iter()
            .map(|difference| json!({
                "h": difference.input.surface(),
                "value": difference.value.surface(),
                "residual": difference.residual.surface(),
                "residual_rule": "E(h) - (3/8) * h",
            }))
            .collect::<Vec<Value>>(),
    });

    let controls = json!({
        "swapped_nonlinear_phases": {
            "dilations": surfaces(&swapped_dilations()?),
            "holonomy_dilation": swapped_holonomy.dilation.surface(),
            "holonomy_translation": swapped_holonomy.translation.surface(),
            "coefficients_ascending": surfaces(&swapped_coefficients),
            "reading": "the same first-degree holonomy with a different quadratic coefficient",
        },
        "shifted_reference": {
            "shift": rational(REFERENCE_SHIFT.0, REFERENCE_SHIFT.1)?.surface(),
            "defects": surfaces(&defects),
            "defect_rule": "d_m = F_m(c_m) - c_{m+1} with c_m = s_m + 1/8",
            "reading": "a periodic reference does not give a homogeneous anomaly equation",
        },
        "exp_completion": {
            "declared_flow_labels": flow_labels
                .iter()
                .map(|(phase, label)| json!({
                    "phase": phase,
                    "flow": format!("e^{}", label.surface()),
                }))
                .collect::<Vec<Value>>(),
            "phase_readings": phase_labels,
            "composed_exp_label": composed_term.0.2.surface(),
            "composed_surface": dilation_product.surface(),
            "composed_coefficient": composed_term.1.surface(),
            "exp_carrying_phase_element": flow_linear.surface(),
            "polynomial_module_refusal": {
                "variant": error_variant(&polynomial_refusal),
                "message": polynomial_refusal.to_string(),
            },
            "composition_refusal": {
                "variant": error_variant(&flow_linear_refusal),
                "message": flow_linear_refusal.to_string(),
            },
            "reading": "the fixed rational polynomial module cannot hold this reading; the carrier with exact rational exp labels can",
        },
        "resonances": {
            "addition_inverse": {
                "declared_input": resonant_a.surface(),
                "declared_extension": logarithmic_surface,
                "witness_a": witness_surface,
                "witness_positive": witness_surface == "1",
                "ordinary_only": {
                    "variant": ordinary_a_variant,
                    "message": ordinary_a_surface,
                },
                "shape": "e^{(w+1)v} * log(a) on the declared stratum a > 0",
            },
            "multiplication_inverse": {
                "declared_input": resonant_m.surface(),
                "declared_extension": jordan_surface,
                "ordinary_only": {
                    "variant": ordinary_m_variant,
                    "message": ordinary_m_surface,
                },
                "shape": "v * Phi_{nu,0}",
            },
            "default_policy": format!("{:?}", ResonancePolicy::default()),
            "reading": "both resonances are typed; OrdinaryOnly fails closed with a typed error",
        },
    });

    let scope = json!({
        "statement": "This report is a bounded exact-arithmetic reading of one declared rational fixture. It certifies only the assertions listed under checks, on this fixture, with exact rational arithmetic.",
        "no_matrix_or_jacobian": "no matrix and no Jacobian is used anywhere in this report; the rate readings are the actions of the addition and multiplication generators on the power-weight carrier",
        "no_floating_point": "no floating point value is constructed, stored, or printed anywhere in this report; every number is an exact rational",
        "no_stable_api": "no stable API, ValueType, OperationSpec, IR version, Seal, or terminology home is created",
        "no_physical_claim": "no weather claim and no physical claim is made",
    });

    let report = json!({
        "schema": REPORT_SCHEMA,
        "version": REPORT_VERSION,
        "fixture": fixture,
        "readings": readings,
        "controls": controls,
        "checks": checks_value,
        "check_summary": {
            "total": total,
            "passed": total,
            "failed": 0,
        },
        "scope": scope,
    });

    let summary = vec![
        "0233 periodic fixture: native exact addition/multiplication reading".to_owned(),
        format!(
            "  fixture             12 phases, reference ({}), dilations a_0..a_11 = ({}), curvatures q_0..q_11 = ({})",
            reference
                .iter()
                .map(|value| value.to_string())
                .collect::<Vec<String>>()
                .join(","),
            surfaces(&dilations).join(","),
            surfaces(&curvatures).join(","),
        ),
        format!(
            "  annual holonomy     dilation {} translation {}   (normal form {})",
            holonomy.dilation.surface(),
            holonomy.translation.surface(),
            format!(
                "T_{} D_{}",
                holonomy.translation.surface(),
                holonomy.dilation.surface()
            ),
        ),
        format!(
            "  annual element      {}",
            surfaces(&annual_coefficients).join(", ")
        ),
        format!(
            "  A(annual)           {}   at a = 0: {} (equals the holonomy dilation)",
            surfaces(&addition_coefficients).join(", "),
            addition_at_reference.surface(),
        ),
        format!(
            "  M(annual)           {}   (weight reading k * c_k)",
            surfaces(&multiplication_coefficients).join(", "),
        ),
        format!(
            "  finite differences  {}",
            finite_differences
                .iter()
                .map(|difference| format!(
                    "h={} -> {} (residual {})",
                    difference.input.surface(),
                    difference.value.surface(),
                    difference.residual.surface()
                ))
                .collect::<Vec<String>>()
                .join("; "),
        ),
        format!(
            "  swapped control     dilation {}, coefficients {}",
            swapped_holonomy.dilation.surface(),
            surfaces(&swapped_coefficients).join(", "),
        ),
        format!(
            "  shifted reference   defects {}",
            surfaces(&defects).join(", "),
        ),
        format!(
            "  exp completion      e^1/2 * e^-1/3 = e^{} ({}), refused by the rational polynomial module with {}",
            composed_term.0.2.surface(),
            dilation_product.surface(),
            error_variant(&polynomial_refusal),
        ),
        format!(
            "  resonances          A^-1 at nu = -1: {} (witness a = {}); M^-1 at w = 0: {}; OrdinaryOnly: {}",
            logarithmic_surface, witness_surface, jordan_surface, ordinary_a_variant,
        ),
        format!("  checks              {total} passed, 0 failed"),
    ];

    Ok((report, summary))
}

/// Parses the required `--output <path>` argument.
fn parse_output_argument() -> Result<PathBuf, Box<dyn Error>> {
    let mut arguments = std::env::args_os().skip(1);
    let flag = arguments
        .next()
        .ok_or("usage: am_variation_reading --output <fresh path>")?;
    if flag.to_str() != Some("--output") {
        return Err(format!(
            "unexpected argument {flag:?}; usage: am_variation_reading --output <fresh path>"
        )
        .into());
    }
    let path = arguments.next().ok_or("--output needs a path")?;
    if arguments.next().is_some() {
        return Err("expected exactly one --output <path>".into());
    }
    Ok(PathBuf::from(path))
}

fn main() -> Result<(), Box<dyn Error>> {
    let output = parse_output_argument()?;
    if output.exists() {
        return Err(format!(
            "refusing to overwrite the existing path {}",
            output.display()
        )
        .into());
    }
    let (report, summary) = build_report()?;
    let encoded = format!("{}\n", serde_json::to_string_pretty(&report)?);
    fs::write(&output, encoded.as_bytes())?;
    for line in summary {
        println!("{line}");
    }
    println!(
        "  report              {REPORT_SCHEMA} version {REPORT_VERSION}, {} bytes written to {}",
        encoded.len(),
        output.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn payload() -> Value {
        build_report()
            .expect("the declared twelve-phase fixture must build")
            .0
    }

    /// The declared readings, asserted as this calibration's gate.
    #[test]
    fn the_declared_twelve_phase_readings_are_reproduced() {
        let report = payload();
        assert_eq!(report["schema"], json!(REPORT_SCHEMA));
        assert_eq!(report["version"], json!(REPORT_VERSION));
        let summary = &report["check_summary"];
        assert_eq!(summary["total"], json!(31), "the frozen check count moved");
        assert_eq!(summary["passed"], json!(31));
        assert_eq!(summary["failed"], json!(0));

        let holonomy = &report["readings"]["annual_affine_holonomy"];
        assert_eq!(holonomy["dilation"], json!("3/8"));
        assert_eq!(holonomy["translation"], json!("0"));
        assert_eq!(
            report["readings"]["annual_return_element"]["coefficients_ascending"],
            json!(["0", "3/8", "1/8", "1/64", "1/512"])
        );

        let generators = &report["readings"]["generator_readings"];
        let no_matrix = generators["no_matrix_or_jacobian"]
            .as_str()
            .expect("the reading must state what it is not");
        assert!(
            no_matrix.contains("not a Jacobian"),
            "the reading must refuse the matrix ontology: {no_matrix}"
        );
        assert_eq!(generators["addition_generator_at_reference"], json!("3/8"));
        assert_eq!(
            generators["addition_generator_at_reference_equals_holonomy"],
            json!(true)
        );
        assert_eq!(
            generators["addition_generator_coefficients_ascending"],
            json!(["3/8", "1/4", "3/64", "1/128"])
        );
        assert_eq!(
            generators["multiplication_generator_coefficients_ascending"],
            json!(["0", "3/8", "1/4", "3/64", "1/128"])
        );
    }

    /// The controls that forbid reading the first-degree number as the process.
    #[test]
    fn the_controls_separate_the_first_degree_reading_from_the_process() {
        let report = payload();
        let controls = &report["controls"];
        assert_eq!(
            controls["swapped_nonlinear_phases"]["holonomy_dilation"],
            json!("3/8")
        );
        assert_eq!(
            controls["swapped_nonlinear_phases"]["coefficients_ascending"],
            json!(["0", "3/8", "17/128", "3/128", "1/512"])
        );
        assert_eq!(
            controls["shifted_reference"]["defects"],
            json!([
                "-31/512", "-15/512", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"
            ])
        );
        assert_eq!(
            controls["exp_completion"]["composed_exp_label"],
            json!("1/6")
        );
        assert_eq!(
            controls["resonances"]["default_policy"],
            json!("OrdinaryOnly")
        );
        let scope = report["scope"]
            .as_object()
            .expect("the report must carry its own scope");
        for key in [
            "no_floating_point",
            "no_matrix_or_jacobian",
            "no_physical_claim",
            "no_stable_api",
        ] {
            let statement = scope
                .get(key)
                .and_then(Value::as_str)
                .unwrap_or_else(|| panic!("the scope must state {key}"));
            assert!(!statement.is_empty(), "the scope statement {key} is empty");
        }
    }
}
