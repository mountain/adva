use crate::{
    ArtifactKeyV0, DomainTransportNameV0, InputLabelV0, InquiryInterfaceV0, M6NamingPlanV0,
    MagicSquareCertificateV0, MechanismV0, OutputLabelV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

pub const HYPOTHESIS_FORMATION_FRONTIER_SCHEMA_V0: &str =
    "adva.hypothesis-formation-frontier.research";
pub const HYPOTHESIS_FORMATION_CONTRACT_SCHEMA_V0: &str =
    "adva.hypothesis-formation-contract.research";
pub const HYPOTHESIS_FORMATION_RESOURCE_SCHEMA_V0: &str =
    "adva.hypothesis-formation-resource.research";
pub const HYPOTHESIS_FORMATION_TRANSITION_SCHEMA_V0: &str =
    "adva.hypothesis-formation-transition.research";
pub const HYPOTHESIS_FORMATION_VERSION_V0: u32 = 0;

const CROSSING_COUNT: usize = 6;
const LINEAR_BIJECTION_COUNT: u64 = 20_160;
const CANDIDATES_PER_CROSSING: u64 = LINEAR_BIJECTION_COUNT / CROSSING_COUNT as u64;
const INPUT_FORMS: [u8; 4] = [1, 2, 4, 8];
const MAGIC_SUM: u16 = 34;

const VOCABULARY: [&str; 22] = [
    "hypothesis-formation",
    "subject",
    "method",
    "object",
    "history",
    "result",
    "evidence",
    "time",
    "space",
    "construction",
    "run",
    "reveal",
    "name",
    "instantiate",
    "resume",
    "compile",
    "linear-bijection",
    "additive-line-closure",
    "characteristic-unit",
    "sixteen-member-orbit",
    "four-xor-construction",
    "finite-boundary",
];

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HypothesisFormationFrontierStateV0 {
    Open,
    Completed,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum HypothesisFormationRunStateV0 {
    Witness,
    NoWitness,
    Suspended,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SearchLexicalClassV0 {
    Verb,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct XorGateV0 {
    pub left: u8,
    pub right: u8,
    pub output: u8,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LinearMagicSquareWitnessV0 {
    pub global_candidate_ordinal: u64,
    pub crossing_candidate_ordinal: u64,
    pub input_forms: [u8; 4],
    pub xor_gates: [XorGateV0; 4],
    pub output_forms: [u8; 4],
    pub cells: [u8; 16],
    pub closure: MagicSquareCertificateV0,
    pub transport_orbit_size: u8,
    pub xor_lower_bound: u8,
    pub xor_gate_count: u8,
}

impl LinearMagicSquareWitnessV0 {
    fn check(&self) -> Result<(), HypothesisFormationErrorV0> {
        if self.input_forms != INPUT_FORMS
            || self.xor_lower_bound != 4
            || self.xor_gate_count != 4
            || self.transport_orbit_size != 16
        {
            return Err(invalid("unsupported four-XOR witness coordinates"));
        }
        if self.crossing_candidate_ordinal != self.global_candidate_ordinal / CROSSING_COUNT as u64
        {
            return Err(invalid(
                "global and crossing-local candidate ordinals diverge",
            ));
        }
        let mut available = INPUT_FORMS.into_iter().collect::<BTreeSet<_>>();
        for gate in &self.xor_gates {
            if gate.left >= gate.right
                || !available.contains(&gate.left)
                || !available.contains(&gate.right)
                || gate.output != gate.left ^ gate.right
                || gate.output == 0
                || !available.insert(gate.output)
            {
                return Err(invalid("the XOR construction does not replay"));
            }
        }
        let output_set = self.output_forms.into_iter().collect::<BTreeSet<_>>();
        if output_set.len() != 4
            || output_set.iter().any(|form| INPUT_FORMS.contains(form))
            || !output_set.iter().all(|form| available.contains(form))
        {
            return Err(invalid(
                "the four distinct non-input output forms are not constructed",
            ));
        }
        if !linearly_independent(self.output_forms)
            || self.cells != cells_from_linear_forms(self.output_forms)
        {
            return Err(invalid("the linear bijection does not replay"));
        }
        self.closure
            .check()
            .map_err(HypothesisFormationErrorV0::MagicSquare)?;
        if self.closure.content.cells != self.cells || raw_transport_orbit(self.cells).len() != 16 {
            return Err(invalid("the exact closure or its orbit does not replay"));
        }
        // In the frozen fanout model, each gate creates at most one new form.
        // Four distinct outputs that are absent from the input basis therefore
        // require at least four XOR gates; the retained trace realizes four.
        Ok(())
    }

    fn digest(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SearchWordV0 {
    pub local_name: String,
    pub display_name_zh: String,
    pub lexical_class: SearchLexicalClassV0,
    pub occurrence: ArtifactKeyV0,
    pub definition: String,
    pub crossing: DomainTransportNameV0,
    pub retained_vocabulary: Vec<String>,
    pub introduced_vocabulary: Vec<String>,
    pub witness: LinearMagicSquareWitnessV0,
    pub witness_digest: String,
}

impl SearchWordV0 {
    fn check_against(
        &self,
        method: &HypothesisFormationContractV0,
    ) -> Result<(), HypothesisFormationErrorV0> {
        if self.local_name != "search"
            || self.display_name_zh != "搜索"
            || self.lexical_class != SearchLexicalClassV0::Verb
            || self.occurrence.as_str().is_empty()
            || self.definition != method.search_word_definition
            || self.retained_vocabulary != method.retained_vocabulary
            || self.introduced_vocabulary != vec!["search".to_owned()]
            || self.witness_digest != self.witness.digest()?
        {
            return Err(invalid(
                "the derived search word does not retain its formation",
            ));
        }
        let crossing_index = method
            .crossing_order
            .iter()
            .position(|crossing| crossing == &self.crossing)
            .ok_or_else(|| invalid("the search word names no declared crossing"))?;
        if self.witness.global_candidate_ordinal % CROSSING_COUNT as u64 != crossing_index as u64 {
            return Err(invalid("the search witness escaped its declared shard"));
        }
        Ok(())
    }

    fn digest(
        &self,
        method: &HypothesisFormationContractV0,
    ) -> Result<String, HypothesisFormationErrorV0> {
        self.check_against(method)?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SearchWordReferenceV0 {
    pub local_name: String,
    pub occurrence: ArtifactKeyV0,
    pub crossing: DomainTransportNameV0,
    pub witness_digest: String,
    pub word_digest: String,
}

impl SearchWordReferenceV0 {
    fn from_word(
        word: &SearchWordV0,
        method: &HypothesisFormationContractV0,
    ) -> Result<Self, HypothesisFormationErrorV0> {
        word.check_against(method)?;
        Ok(Self {
            local_name: word.local_name.clone(),
            occurrence: word.occurrence.clone(),
            crossing: word.crossing.clone(),
            witness_digest: word.witness_digest.clone(),
            word_digest: word.digest(method)?,
        })
    }

    fn check(
        &self,
        method: &HypothesisFormationContractV0,
    ) -> Result<(), HypothesisFormationErrorV0> {
        if self.local_name != "search" || self.occurrence.as_str().is_empty() {
            return Err(invalid("a search-word reference lost its word coordinate"));
        }
        if !method
            .crossing_order
            .iter()
            .any(|crossing| crossing == &self.crossing)
        {
            return Err(invalid("a search-word reference names no declared crossing"));
        }
        check_digest(&self.witness_digest)?;
        check_digest(&self.word_digest)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationFrontierV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub sequence: u64,
    pub state: HypothesisFormationFrontierStateV0,
    pub next_crossing: u8,
    pub crossing_cursor: u64,
    pub formed_words: Vec<SearchWordReferenceV0>,
    pub parent_digest: Option<String>,
}

impl HypothesisFormationFrontierV0 {
    #[must_use]
    pub fn initial() -> Self {
        Self {
            schema: HYPOTHESIS_FORMATION_FRONTIER_SCHEMA_V0.to_owned(),
            version: HYPOTHESIS_FORMATION_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            sequence: 0,
            state: HypothesisFormationFrontierStateV0::Open,
            next_crossing: 0,
            crossing_cursor: 0,
            formed_words: Vec::new(),
            parent_digest: None,
        }
    }

    pub fn check(&self) -> Result<(), HypothesisFormationErrorV0> {
        check_header(
            &self.schema,
            self.version,
            HYPOTHESIS_FORMATION_FRONTIER_SCHEMA_V0,
            &self.interface,
        )?;
        if self.next_crossing as usize > CROSSING_COUNT
            || self.crossing_cursor > CANDIDATES_PER_CROSSING
        {
            return Err(invalid(
                "frontier crossing coordinate is outside the finite space",
            ));
        }
        match self.state {
            HypothesisFormationFrontierStateV0::Open
                if self.next_crossing as usize == CROSSING_COUNT =>
            {
                return Err(invalid("an open frontier must retain a crossing"));
            }
            HypothesisFormationFrontierStateV0::Completed
                if self.next_crossing as usize != CROSSING_COUNT || self.crossing_cursor != 0 =>
            {
                return Err(invalid(
                    "a completed frontier must be past all six crossings",
                ));
            }
            _ => {}
        }
        if self.sequence == 0 {
            if self != &Self::initial() {
                return Err(invalid("sequence-zero formation frontier drifted"));
            }
        } else if self.parent_digest.is_none() {
            return Err(invalid("a continued frontier must retain its parent"));
        }
        let method = HypothesisFormationContractV0::first();
        for word in &self.formed_words {
            word.check(&method)?;
        }
        let occurrences = self
            .formed_words
            .iter()
            .map(|word| word.occurrence.as_str())
            .collect::<BTreeSet<_>>();
        if occurrences.len() != self.formed_words.len() {
            return Err(invalid("search-word occurrences must remain distinct"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, HypothesisFormationErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| HypothesisFormationErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub program_name: String,
    pub display_name_zh: String,
    pub hypothesis: String,
    pub candidate_family: String,
    pub enumeration: String,
    pub shard_rule: String,
    pub cost_model: String,
    pub crossing_order: [DomainTransportNameV0; 6],
    pub retained_vocabulary: Vec<String>,
    pub search_word_definition: String,
}

impl HypothesisFormationContractV0 {
    #[must_use]
    pub fn first() -> Self {
        let names = M6NamingPlanV0::first_calibration();
        Self {
            schema: HYPOTHESIS_FORMATION_CONTRACT_SCHEMA_V0.to_owned(),
            version: HYPOTHESIS_FORMATION_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            program_name: "hypothesis-formation".to_owned(),
            display_name_zh: "假设形成".to_owned(),
            hypothesis: "at least one of six directed finite shards contains an exact order-four magic square generated by a minimum four-XOR linear bijection".to_owned(),
            candidate_family: "GL(4,2): all 20160 ordered invertible four-by-four binary linear maps, with input x=row*4+column and output value=1+A*x".to_owned(),
            enumeration: "lexicographic ordered nonzero row forms; reject dependent rows; no affine offset".to_owned(),
            shard_rule: "global candidate ordinal modulo six in the declared crossing order".to_owned(),
            cost_model: "two-input XOR creates one new nonzero linear form; input basis and fanout are free; constants and affine offsets are forbidden".to_owned(),
            // Pair every direction immediately with its reverse. This order is
            // presentation metadata for the six disjoint shards.
            crossing_order: [
                names.forward[0].clone(),
                names.conjugate[2].clone(),
                names.forward[1].clone(),
                names.conjugate[1].clone(),
                names.forward[2].clone(),
                names.conjugate[0].clone(),
            ],
            retained_vocabulary: VOCABULARY.into_iter().map(str::to_owned).collect(),
            search_word_definition: "a bounded learn edge that partitions a declared finite candidate family, retains its exact path and vocabulary, and admits a result only with an independently replayable witness".to_owned(),
        }
    }

    pub fn check(&self) -> Result<(), HypothesisFormationErrorV0> {
        check_header(
            &self.schema,
            self.version,
            HYPOTHESIS_FORMATION_CONTRACT_SCHEMA_V0,
            &self.interface,
        )?;
        if self != &Self::first() {
            return Err(invalid("the hypothesis-formation contract drifted"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, HypothesisFormationErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| HypothesisFormationErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationResourceV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub candidate_fuel: u64,
}

impl HypothesisFormationResourceV0 {
    #[must_use]
    pub fn first() -> Self {
        Self {
            schema: HYPOTHESIS_FORMATION_RESOURCE_SCHEMA_V0.to_owned(),
            version: HYPOTHESIS_FORMATION_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            candidate_fuel: CANDIDATES_PER_CROSSING,
        }
    }

    pub fn check(&self) -> Result<(), HypothesisFormationErrorV0> {
        check_header(
            &self.schema,
            self.version,
            HYPOTHESIS_FORMATION_RESOURCE_SCHEMA_V0,
            &self.interface,
        )?;
        if self.candidate_fuel == 0 || self.candidate_fuel > CANDIDATES_PER_CROSSING {
            return Err(invalid("candidate fuel must fit exactly one finite shard"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, HypothesisFormationErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| HypothesisFormationErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationInputV0 {
    pub subject: HypothesisFormationFrontierV0,
    pub method: HypothesisFormationContractV0,
    pub object: HypothesisFormationResourceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationHistoryV0 {
    pub mechanism: MechanismV0,
    pub crossing: DomainTransportNameV0,
    pub subject_digest: String,
    pub method_digest: String,
    pub object_digest: String,
    pub cursor_before: u64,
    pub cursor_after: u64,
    pub candidates_examined: u64,
    pub four_xor_candidates: u64,
    pub exact_closures_examined: u64,
    pub unvisited_candidates: u64,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationResultV0 {
    pub state: HypothesisFormationRunStateV0,
    pub search_word: Option<SearchWordV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationEvidenceV0 {
    pub six_shards_partition_20160_candidates: CheckStatus,
    pub candidate_is_linear_bijection: CheckStatus,
    pub additive_lines_close: CheckStatus,
    pub characteristic_residual_is_one: CheckStatus,
    pub orbit_has_sixteen_members: CheckStatus,
    pub four_xor_trace_replays: CheckStatus,
    pub four_xor_lower_bound: CheckStatus,
    pub vocabulary_retained: CheckStatus,
    pub next_frontier: HypothesisFormationFrontierV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationOutputV0 {
    pub history: HypothesisFormationHistoryV0,
    pub result: HypothesisFormationResultV0,
    pub evidence: HypothesisFormationEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HypothesisFormationTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub input: HypothesisFormationInputV0,
    pub output: HypothesisFormationOutputV0,
}

impl HypothesisFormationTransitionV0 {
    pub fn check(&self) -> Result<(), HypothesisFormationErrorV0> {
        if self.schema != HYPOTHESIS_FORMATION_TRANSITION_SCHEMA_V0
            || self.version != HYPOTHESIS_FORMATION_VERSION_V0
        {
            return Err(invalid(
                "unsupported hypothesis-formation transition header",
            ));
        }
        self.input.subject.check()?;
        self.input.method.check()?;
        self.input.object.check()?;
        if self.input.subject.state != HypothesisFormationFrontierStateV0::Open {
            return Err(invalid("hypothesis formation requires an open frontier"));
        }
        if self.output != derive_output(&self.input)? {
            return Err(invalid(
                "the stored hypothesis-formation output does not replay",
            ));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, HypothesisFormationErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| HypothesisFormationErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, HypothesisFormationErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

pub fn run_hypothesis_formation_v0(
    subject: &HypothesisFormationFrontierV0,
    method: &HypothesisFormationContractV0,
    object: &HypothesisFormationResourceV0,
) -> Result<HypothesisFormationTransitionV0, HypothesisFormationErrorV0> {
    let input = HypothesisFormationInputV0 {
        subject: subject.clone(),
        method: method.clone(),
        object: object.clone(),
    };
    subject.check()?;
    method.check()?;
    object.check()?;
    if subject.state != HypothesisFormationFrontierStateV0::Open {
        return Err(invalid("hypothesis formation requires an open frontier"));
    }
    let transition = HypothesisFormationTransitionV0 {
        schema: HYPOTHESIS_FORMATION_TRANSITION_SCHEMA_V0.to_owned(),
        version: HYPOTHESIS_FORMATION_VERSION_V0,
        output: derive_output(&input)?,
        input,
    };
    transition.check()?;
    Ok(transition)
}

fn derive_output(
    input: &HypothesisFormationInputV0,
) -> Result<HypothesisFormationOutputV0, HypothesisFormationErrorV0> {
    let crossing_index = usize::from(input.subject.next_crossing);
    let crossing = input.method.crossing_order[crossing_index].clone();
    let circuits = four_xor_circuits();
    let mut global_ordinal = 0_u64;
    let mut local_ordinal = 0_u64;
    let mut examined = 0_u64;
    let mut four_xor_candidates = 0_u64;
    let mut exact_closures = 0_u64;
    let mut found = None;

    'rows: for row0 in 1_u8..16 {
        for row1 in 1_u8..16 {
            for row2 in 1_u8..16 {
                for row3 in 1_u8..16 {
                    let rows = [row0, row1, row2, row3];
                    if rows.into_iter().collect::<BTreeSet<_>>().len() != 4
                        || !linearly_independent(rows)
                    {
                        continue;
                    }
                    if global_ordinal % CROSSING_COUNT as u64 == crossing_index as u64 {
                        if local_ordinal >= input.subject.crossing_cursor {
                            if examined == input.object.candidate_fuel {
                                break 'rows;
                            }
                            examined += 1;
                            let target_mask = form_set_mask(INPUT_FORMS) | form_set_mask(rows);
                            if let Some(gates) = circuits.get(&target_mask) {
                                four_xor_candidates += 1;
                                let cells = cells_from_linear_forms(rows);
                                if is_magic(&cells) {
                                    exact_closures += 1;
                                    if raw_transport_orbit(cells).len() == 16 {
                                        let closure = MagicSquareCertificateV0::from_cells(
                                            cells,
                                            format!(
                                                "experiment:0121:search:{}:{}",
                                                crossing.name,
                                                input.subject.sequence + 1
                                            ),
                                        )?;
                                        let witness = LinearMagicSquareWitnessV0 {
                                            global_candidate_ordinal: global_ordinal,
                                            crossing_candidate_ordinal: local_ordinal,
                                            input_forms: INPUT_FORMS,
                                            xor_gates: gates.clone().try_into().map_err(|_| {
                                                invalid("four-XOR construction has wrong length")
                                            })?,
                                            output_forms: rows,
                                            cells,
                                            closure,
                                            transport_orbit_size: 16,
                                            xor_lower_bound: 4,
                                            xor_gate_count: 4,
                                        };
                                        witness.check()?;
                                        found = Some(witness);
                                        break 'rows;
                                    }
                                }
                            }
                        }
                        local_ordinal += 1;
                    }
                    global_ordinal += 1;
                }
            }
        }
    }

    let cursor_after = input.subject.crossing_cursor + examined;
    let shard_exhausted = cursor_after == CANDIDATES_PER_CROSSING;
    let state = if found.is_some() {
        HypothesisFormationRunStateV0::Witness
    } else if shard_exhausted {
        HypothesisFormationRunStateV0::NoWitness
    } else {
        HypothesisFormationRunStateV0::Suspended
    };
    let search_word = found
        .map(|witness| {
            let witness_digest = witness.digest()?;
            Ok::<SearchWordV0, HypothesisFormationErrorV0>(SearchWordV0 {
                local_name: "search".to_owned(),
                display_name_zh: "搜索".to_owned(),
                lexical_class: SearchLexicalClassV0::Verb,
                occurrence: key(format!(
                    "experiment:0121:search-word:{}",
                    input.subject.sequence + 1
                ))?,
                definition: input.method.search_word_definition.clone(),
                crossing: crossing.clone(),
                retained_vocabulary: input.method.retained_vocabulary.clone(),
                introduced_vocabulary: vec!["search".to_owned()],
                witness,
                witness_digest,
            })
        })
        .transpose()?;
    if let Some(word) = &search_word {
        word.check_against(&input.method)?;
    }

    let terminal = state != HypothesisFormationRunStateV0::Suspended;
    let next_crossing = if terminal {
        input.subject.next_crossing + 1
    } else {
        input.subject.next_crossing
    };
    let next_state = if usize::from(next_crossing) == CROSSING_COUNT {
        HypothesisFormationFrontierStateV0::Completed
    } else {
        HypothesisFormationFrontierStateV0::Open
    };
    let mut formed_words = input.subject.formed_words.clone();
    if let Some(word) = &search_word {
        formed_words.push(SearchWordReferenceV0::from_word(word, &input.method)?);
    }
    let next_frontier = HypothesisFormationFrontierV0 {
        schema: HYPOTHESIS_FORMATION_FRONTIER_SCHEMA_V0.to_owned(),
        version: HYPOTHESIS_FORMATION_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        sequence: input.subject.sequence + 1,
        state: next_state,
        next_crossing,
        crossing_cursor: if terminal { 0 } else { cursor_after },
        formed_words,
        parent_digest: Some(input.subject.digest()?),
    };
    next_frontier.check()?;

    let checked = if search_word.is_some() {
        CheckStatus::Checked
    } else {
        CheckStatus::Unchecked
    };
    Ok(HypothesisFormationOutputV0 {
        history: HypothesisFormationHistoryV0 {
            mechanism: MechanismV0::Learn,
            crossing,
            subject_digest: input.subject.digest()?,
            method_digest: input.method.digest()?,
            object_digest: input.object.digest()?,
            cursor_before: input.subject.crossing_cursor,
            cursor_after,
            candidates_examined: examined,
            four_xor_candidates,
            exact_closures_examined: exact_closures,
            unvisited_candidates: CANDIDATES_PER_CROSSING.saturating_sub(cursor_after),
        },
        result: HypothesisFormationResultV0 { state, search_word },
        evidence: HypothesisFormationEvidenceV0 {
            six_shards_partition_20160_candidates: CheckStatus::Checked,
            candidate_is_linear_bijection: checked,
            additive_lines_close: checked,
            characteristic_residual_is_one: checked,
            orbit_has_sixteen_members: checked,
            four_xor_trace_replays: checked,
            four_xor_lower_bound: checked,
            vocabulary_retained: checked,
            next_frontier,
        },
    })
}

fn four_xor_circuits() -> BTreeMap<u16, Vec<XorGateV0>> {
    let mut states = BTreeMap::from([(form_set_mask(INPUT_FORMS), Vec::new())]);
    for _ in 0..4 {
        let mut next = BTreeMap::new();
        for (available_mask, gates) in states {
            let available = (1_u8..16)
                .filter(|form| available_mask & (1_u16 << *form) != 0)
                .collect::<Vec<_>>();
            for (left_index, left) in available.iter().enumerate() {
                for right in available.iter().skip(left_index + 1) {
                    let output = *left ^ *right;
                    let output_bit = 1_u16 << output;
                    if output == 0 || available_mask & output_bit != 0 {
                        continue;
                    }
                    let mut trace = gates.clone();
                    trace.push(XorGateV0 {
                        left: *left,
                        right: *right,
                        output,
                    });
                    next.entry(available_mask | output_bit).or_insert(trace);
                }
            }
        }
        states = next;
    }
    states
}

fn form_set_mask(forms: [u8; 4]) -> u16 {
    forms
        .into_iter()
        .fold(0_u16, |mask, form| mask | (1_u16 << form))
}

fn linearly_independent(rows: [u8; 4]) -> bool {
    let mut rows = rows;
    let mut rank = 0_usize;
    for bit in [8_u8, 4, 2, 1] {
        let Some(pivot) = (rank..4).find(|index| rows[*index] & bit != 0) else {
            continue;
        };
        rows.swap(rank, pivot);
        for index in 0..4 {
            if index != rank && rows[index] & bit != 0 {
                rows[index] ^= rows[rank];
            }
        }
        rank += 1;
    }
    rank == 4
}

fn cells_from_linear_forms(forms: [u8; 4]) -> [u8; 16] {
    std::array::from_fn(|input| {
        let input = u8::try_from(input).expect("four-bit input");
        let output = forms.iter().enumerate().fold(0_u8, |value, (bit, form)| {
            value | (((form & input).count_ones() as u8 & 1) << bit)
        });
        output + 1
    })
}

fn is_magic(cells: &[u8; 16]) -> bool {
    (0..4).all(|row| {
        (0..4)
            .map(|column| u16::from(cells[row * 4 + column]))
            .sum::<u16>()
            == MAGIC_SUM
    }) && (0..4).all(|column| {
        (0..4)
            .map(|row| u16::from(cells[row * 4 + column]))
            .sum::<u16>()
            == MAGIC_SUM
    }) && (0..4).map(|index| u16::from(cells[index * 5])).sum::<u16>() == MAGIC_SUM
        && (0..4)
            .map(|index| u16::from(cells[3 + index * 3]))
            .sum::<u16>()
            == MAGIC_SUM
}

fn raw_transport_orbit(seed: [u8; 16]) -> BTreeSet<[u8; 16]> {
    let mut orbit = BTreeSet::from([seed]);
    let mut pending = vec![seed];
    while let Some(cells) = pending.pop() {
        for target in [rotate(cells), reflect(cells), complement(cells)] {
            if orbit.insert(target) {
                pending.push(target);
            }
        }
    }
    orbit
}

fn rotate(source: [u8; 16]) -> [u8; 16] {
    let mut target = [0_u8; 16];
    for row in 0..4 {
        for column in 0..4 {
            target[column * 4 + (3 - row)] = source[row * 4 + column];
        }
    }
    target
}

fn reflect(source: [u8; 16]) -> [u8; 16] {
    let mut target = [0_u8; 16];
    for row in 0..4 {
        for column in 0..4 {
            target[row * 4 + (3 - column)] = source[row * 4 + column];
        }
    }
    target
}

fn complement(source: [u8; 16]) -> [u8; 16] {
    source.map(|value| 17 - value)
}

pub fn load_hypothesis_formation_frontier_v0(
    path: impl AsRef<Path>,
) -> Result<HypothesisFormationFrontierV0, HypothesisFormationErrorV0> {
    load_checked(path, HypothesisFormationFrontierV0::from_json)
}

pub fn load_hypothesis_formation_contract_v0(
    path: impl AsRef<Path>,
) -> Result<HypothesisFormationContractV0, HypothesisFormationErrorV0> {
    load_checked(path, HypothesisFormationContractV0::from_json)
}

pub fn load_hypothesis_formation_resource_v0(
    path: impl AsRef<Path>,
) -> Result<HypothesisFormationResourceV0, HypothesisFormationErrorV0> {
    load_checked(path, HypothesisFormationResourceV0::from_json)
}

pub fn load_hypothesis_formation_transition_v0(
    path: impl AsRef<Path>,
) -> Result<HypothesisFormationTransitionV0, HypothesisFormationErrorV0> {
    load_checked(path, HypothesisFormationTransitionV0::from_json)
}

pub fn save_hypothesis_formation_frontier_v0(
    path: impl AsRef<Path>,
    frontier: &HypothesisFormationFrontierV0,
) -> Result<crate::InquirySaveReceiptV0, HypothesisFormationErrorV0> {
    save_checked(path, frontier.to_json()?)
}

pub fn save_hypothesis_formation_transition_v0(
    path: impl AsRef<Path>,
    transition: &HypothesisFormationTransitionV0,
) -> Result<crate::InquirySaveReceiptV0, HypothesisFormationErrorV0> {
    save_checked(path, transition.to_json()?)
}

fn check_header(
    schema: &str,
    version: u32,
    expected_schema: &str,
    interface: &InquiryInterfaceV0,
) -> Result<(), HypothesisFormationErrorV0> {
    if schema != expected_schema
        || version != HYPOTHESIS_FORMATION_VERSION_V0
        || interface != &InquiryInterfaceV0::canonical()
        || interface.inputs != InputLabelV0::ALL
        || interface.outputs != OutputLabelV0::ALL
    {
        return Err(invalid(
            "unsupported hypothesis-formation schema, version, or three-port interface",
        ));
    }
    Ok(())
}

fn key(value: impl Into<String>) -> Result<ArtifactKeyV0, HypothesisFormationErrorV0> {
    ArtifactKeyV0::cache_label(value)
        .map_err(|error| HypothesisFormationErrorV0::InvalidArtifact(error.to_string()))
}

fn pretty_json<T: Serialize>(value: &T) -> Result<String, HypothesisFormationErrorV0> {
    serde_json::to_string_pretty(value)
        .map_err(|error| HypothesisFormationErrorV0::Json(error.to_string()))
}

fn check_digest(digest: &str) -> Result<(), HypothesisFormationErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(invalid("a search-word reference must use a BLAKE3 coordinate"));
    };
    if hex.len() != 64
        || !hex
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(invalid(
            "a search-word reference must use a lowercase BLAKE3 coordinate",
        ));
    }
    Ok(())
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, HypothesisFormationErrorV0> {
    let encoded = format!("{}\n", pretty_json(value)?);
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn invalid(detail: impl Into<String>) -> HypothesisFormationErrorV0 {
    HypothesisFormationErrorV0::InvalidArtifact(detail.into())
}

fn load_checked<T>(
    path: impl AsRef<Path>,
    decode: impl FnOnce(&str) -> Result<T, HypothesisFormationErrorV0>,
) -> Result<T, HypothesisFormationErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| HypothesisFormationErrorV0::Persistence(error.to_string()))?;
    let source = fs::read_to_string(path).map_err(|error| HypothesisFormationErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })?;
    decode(&source)
}

fn save_checked(
    path: impl AsRef<Path>,
    json: String,
) -> Result<crate::InquirySaveReceiptV0, HypothesisFormationErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| HypothesisFormationErrorV0::Persistence(error.to_string()))?;
    let encoded = format!("{json}\n");
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| HypothesisFormationErrorV0::Persistence(error.to_string()))?;
    Ok(crate::InquirySaveReceiptV0 {
        path: path.to_path_buf(),
        artifact_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

#[derive(Debug, Error)]
pub enum HypothesisFormationErrorV0 {
    #[error("invalid hypothesis-formation artifact: {0}")]
    InvalidArtifact(String),
    #[error("hypothesis-formation magic-square error: {0}")]
    MagicSquare(#[from] crate::MagicSquareErrorV0),
    #[error("hypothesis-formation JSON error: {0}")]
    Json(String),
    #[error("hypothesis-formation persistence error: {0}")]
    Persistence(String),
    #[error("hypothesis-formation I/O error at {path}: {detail}")]
    Io { path: PathBuf, detail: String },
}
