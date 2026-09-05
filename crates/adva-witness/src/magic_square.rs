use crate::{
    ArtifactKeyV0, ClosureFindingClassV0, ExactExprV0, InputLabelV0, InquiryInterfaceV0,
    InquirySaveReceiptV0, MechanismV0, MultiplicativeResidualV0, OutputLabelV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

pub const MAGIC_SQUARE_FRONTIER_SCHEMA_V0: &str = "adva.magic-square-frontier.research";
pub const MAGIC_SQUARE_SEARCH_CONTRACT_SCHEMA_V0: &str =
    "adva.magic-square-search-contract.research";
pub const MAGIC_SQUARE_RESOURCE_SCHEMA_V0: &str = "adva.magic-square-resource.research";
pub const MAGIC_SQUARE_TRANSITION_SCHEMA_V0: &str = "adva.magic-square-transition.research";
pub const MAGIC_SQUARE_CERTIFICATE_SCHEMA_V0: &str = "adva.magic-square-certificate.research";
pub const MAGIC_SQUARE_VERSION_V0: u32 = 0;

const CELL_COUNT: usize = 16;
const ORDER: u8 = 4;
const MAGIC_SUM: i16 = 34;
const MAX_FUEL: u64 = 1_000_000;
const CHARACTERISTIC_VARIABLE: &str = "t";

const LINES: [(&str, [usize; 4]); 10] = [
    ("row_0", [0, 1, 2, 3]),
    ("row_1", [4, 5, 6, 7]),
    ("row_2", [8, 9, 10, 11]),
    ("row_3", [12, 13, 14, 15]),
    ("column_0", [0, 4, 8, 12]),
    ("column_1", [1, 5, 9, 13]),
    ("column_2", [2, 6, 10, 14]),
    ("column_3", [3, 7, 11, 15]),
    ("diagonal_main", [0, 5, 10, 15]),
    ("diagonal_anti", [3, 6, 9, 12]),
];

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MagicSquareSearchStateV0 {
    Frontier,
    Identity,
    Exhausted,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareSearchNodeV0 {
    pub cells: [u8; CELL_COUNT],
}

impl MagicSquareSearchNodeV0 {
    #[must_use]
    pub const fn empty() -> Self {
        Self {
            cells: [0; CELL_COUNT],
        }
    }

    fn check(&self) -> Result<(), MagicSquareErrorV0> {
        if !partial_admissible(&self.cells) {
            return Err(invalid(
                "a pending search node is not arithmetically admissible",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareFrontierV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub sequence: u64,
    pub state: MagicSquareSearchStateV0,
    pub pending: Vec<MagicSquareSearchNodeV0>,
    pub closure: Option<MagicSquareClosureReferenceV0>,
    pub parent_digest: Option<String>,
}

impl MagicSquareFrontierV0 {
    #[must_use]
    pub fn initial() -> Self {
        Self {
            schema: MAGIC_SQUARE_FRONTIER_SCHEMA_V0.to_owned(),
            version: MAGIC_SQUARE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            sequence: 0,
            state: MagicSquareSearchStateV0::Frontier,
            pending: vec![MagicSquareSearchNodeV0::empty()],
            closure: None,
            parent_digest: None,
        }
    }

    pub fn check(&self) -> Result<(), MagicSquareErrorV0> {
        check_header(
            &self.schema,
            self.version,
            MAGIC_SQUARE_FRONTIER_SCHEMA_V0,
            &self.interface,
        )?;
        match (self.sequence, self.parent_digest.as_deref()) {
            (0, None) => {}
            (0, Some(_)) => return Err(invalid("the initial frontier cannot have a parent")),
            (_, Some(parent)) => check_digest(parent)?,
            (_, None) => return Err(invalid("a continued frontier must retain its parent")),
        }
        let mut nodes = BTreeSet::new();
        for node in &self.pending {
            node.check()?;
            if !nodes.insert(node) {
                return Err(invalid(
                    "the search frontier contains a repeated pending node",
                ));
            }
        }
        match self.state {
            MagicSquareSearchStateV0::Frontier => {
                if self.pending.is_empty() || self.closure.is_some() {
                    return Err(invalid(
                        "an open search frontier needs pending work and no closure",
                    ));
                }
            }
            MagicSquareSearchStateV0::Identity => {
                self.closure
                    .as_ref()
                    .ok_or_else(|| invalid("an identity frontier must retain its closure"))?
                    .check()?;
            }
            MagicSquareSearchStateV0::Exhausted => {
                if !self.pending.is_empty() || self.closure.is_some() {
                    return Err(invalid(
                        "an exhausted frontier cannot retain work or a closure",
                    ));
                }
            }
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, MagicSquareErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| MagicSquareErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareSearchContractV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub mechanism: MechanismV0,
    pub order: u8,
    pub cell_selection: String,
    pub value_order: String,
    pub pruning: String,
    pub stop_condition: String,
}

impl MagicSquareSearchContractV0 {
    #[must_use]
    pub fn first() -> Self {
        Self {
            schema: MAGIC_SQUARE_SEARCH_CONTRACT_SCHEMA_V0.to_owned(),
            version: MAGIC_SQUARE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            name: "first:normal-order-four-characteristic-search".to_owned(),
            mechanism: MechanismV0::Learn,
            order: ORDER,
            cell_selection: "first_open_cell_row_major".to_owned(),
            value_order: "unused_values_ascending".to_owned(),
            pruning: "exact_completed_lines_and_remaining_sum_bounds".to_owned(),
            stop_condition:
                "first_exact_closure_with_sixteen_member_symmetry_orbit_or_fuel_exhaustion"
                    .to_owned(),
        }
    }

    pub fn check(&self) -> Result<(), MagicSquareErrorV0> {
        if self != &Self::first() {
            return Err(invalid("the magic-square search method has drifted"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, MagicSquareErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| MagicSquareErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareResourceV0 {
    pub schema: String,
    pub version: u32,
    pub interface: InquiryInterfaceV0,
    pub name: String,
    pub fuel: u64,
}

impl MagicSquareResourceV0 {
    #[must_use]
    pub fn new(fuel: u64) -> Self {
        Self {
            schema: MAGIC_SQUARE_RESOURCE_SCHEMA_V0.to_owned(),
            version: MAGIC_SQUARE_VERSION_V0,
            interface: InquiryInterfaceV0::canonical(),
            name: format!("recorded:exact-node-fuel:{fuel}"),
            fuel,
        }
    }

    #[must_use]
    pub fn first() -> Self {
        Self::new(15_000)
    }

    pub fn check(&self) -> Result<(), MagicSquareErrorV0> {
        check_header(
            &self.schema,
            self.version,
            MAGIC_SQUARE_RESOURCE_SCHEMA_V0,
            &self.interface,
        )?;
        if self.fuel == 0 || self.fuel > MAX_FUEL {
            return Err(invalid(
                "magic-square fuel must be between one and one million",
            ));
        }
        if self.name != format!("recorded:exact-node-fuel:{}", self.fuel) {
            return Err(invalid("the resource name must exactly record its fuel"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, MagicSquareErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| MagicSquareErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicLineWitnessV0 {
    pub name: String,
    pub cells: [u8; 4],
    pub values: [u8; 4],
    pub sum: i16,
    pub additive_residual: i16,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareClosureContentV0 {
    pub finding: ClosureFindingClassV0,
    pub cells: [u8; CELL_COUNT],
    pub line_witnesses: Vec<MagicLineWitnessV0>,
    pub characteristic_before: ExactExprV0,
    pub characteristic_after: ExactExprV0,
    pub characteristic_residual: MultiplicativeResidualV0,
}

impl MagicSquareClosureContentV0 {
    pub fn from_cells(cells: [u8; CELL_COUNT]) -> Result<Self, MagicSquareErrorV0> {
        let line_witnesses = line_witnesses(&cells);
        let characteristic_before = characteristic_expression(cells);
        let characteristic_after = characteristic_expression(1..=16);
        let characteristic_residual = MultiplicativeResidualV0::from_transition(
            &characteristic_before,
            &characteristic_after,
        )?;
        let value = Self {
            finding: ClosureFindingClassV0::Identity,
            cells,
            line_witnesses,
            characteristic_before,
            characteristic_after,
            characteristic_residual,
        };
        value.check()?;
        Ok(value)
    }

    pub fn check(&self) -> Result<(), MagicSquareErrorV0> {
        if self.finding != ClosureFindingClassV0::Identity || !complete_magic(&self.cells) {
            return Err(invalid(
                "a magic-square identity must be a complete exact closure",
            ));
        }
        if self.line_witnesses != line_witnesses(&self.cells) {
            return Err(invalid(
                "magic-square line witnesses do not match the cells",
            ));
        }
        let before = characteristic_expression(self.cells);
        let after = characteristic_expression(1..=16);
        let residual = MultiplicativeResidualV0::from_transition(&before, &after)?;
        if self.characteristic_before != before
            || self.characteristic_after != after
            || self.characteristic_residual != residual
            || !residual.is_one()
        {
            return Err(invalid(
                "the characteristic polynomial does not certify the complete value multiset",
            ));
        }
        Ok(())
    }

    pub fn digest(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareCertificateV0 {
    pub schema: String,
    pub version: u32,
    pub occurrence: ArtifactKeyV0,
    pub content: MagicSquareClosureContentV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareClosureReferenceV0 {
    pub occurrence: ArtifactKeyV0,
    pub cells: [u8; CELL_COUNT],
    pub content_digest: String,
}

impl MagicSquareClosureReferenceV0 {
    fn from_certificate(
        certificate: &MagicSquareCertificateV0,
    ) -> Result<Self, MagicSquareErrorV0> {
        certificate.check()?;
        Ok(Self {
            occurrence: certificate.occurrence.clone(),
            cells: certificate.content.cells,
            content_digest: certificate.content.digest()?,
        })
    }

    fn check(&self) -> Result<(), MagicSquareErrorV0> {
        if self.occurrence.as_str().is_empty() {
            return Err(invalid("a closure reference must retain its occurrence"));
        }
        let content = MagicSquareClosureContentV0::from_cells(self.cells)?;
        if self.content_digest != content.digest()? {
            return Err(invalid("a closure reference does not match its content"));
        }
        Ok(())
    }
}

impl MagicSquareCertificateV0 {
    pub fn from_cells(
        cells: [u8; CELL_COUNT],
        occurrence: impl Into<String>,
    ) -> Result<Self, MagicSquareErrorV0> {
        let value = Self {
            schema: MAGIC_SQUARE_CERTIFICATE_SCHEMA_V0.to_owned(),
            version: MAGIC_SQUARE_VERSION_V0,
            occurrence: key(occurrence)?,
            content: MagicSquareClosureContentV0::from_cells(cells)?,
        };
        value.check()?;
        Ok(value)
    }

    pub fn check(&self) -> Result<(), MagicSquareErrorV0> {
        if self.schema != MAGIC_SQUARE_CERTIFICATE_SCHEMA_V0
            || self.version != MAGIC_SQUARE_VERSION_V0
            || self.occurrence.as_str().is_empty()
        {
            return Err(invalid("unsupported magic-square certificate header"));
        }
        self.content.check()
    }

    pub fn digest(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicAssignmentV0 {
    pub ordinal: u8,
    pub cell: u8,
    pub value: u8,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareFillTraceV0 {
    pub name: String,
    pub assignments: Vec<MagicAssignmentV0>,
    pub remaining_factor_digests: Vec<String>,
    pub endpoint_content_digest: String,
}

impl MagicSquareFillTraceV0 {
    fn from_order(
        name: &str,
        order: impl IntoIterator<Item = u8>,
        content: &MagicSquareClosureContentV0,
    ) -> Result<Self, MagicSquareErrorV0> {
        let mut partial = [0_u8; CELL_COUNT];
        let mut remaining_factor_digests = vec![remaining_factor_digest(&partial)?];
        let mut assignments = Vec::new();
        for (ordinal, cell) in order.into_iter().enumerate() {
            let index = usize::from(cell);
            if index >= CELL_COUNT || partial[index] != 0 {
                return Err(invalid(
                    "a fill schedule repeats or exceeds a cell coordinate",
                ));
            }
            partial[index] = content.cells[index];
            if !partial_admissible(&partial) {
                return Err(invalid("a fill schedule leaves the exact feasible region"));
            }
            assignments.push(MagicAssignmentV0 {
                ordinal: u8::try_from(ordinal).map_err(|_| invalid("fill ordinal overflow"))?,
                cell,
                value: content.cells[index],
            });
            remaining_factor_digests.push(remaining_factor_digest(&partial)?);
        }
        if partial != content.cells {
            return Err(invalid(
                "a fill schedule does not reach the claimed endpoint",
            ));
        }
        Ok(Self {
            name: name.to_owned(),
            assignments,
            remaining_factor_digests,
            endpoint_content_digest: content.digest()?,
        })
    }

    fn check_against(
        &self,
        content: &MagicSquareClosureContentV0,
    ) -> Result<(), MagicSquareErrorV0> {
        let expected = Self::from_order(
            &self.name,
            self.assignments.iter().map(|assignment| assignment.cell),
            content,
        )?;
        if self != &expected || self.assignments.len() != CELL_COUNT {
            return Err(invalid("a retained fill trace does not replay exactly"));
        }
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MagicSquareTransportMapV0 {
    RotateClockwise,
    ReflectVertical,
    ComplementSeventeen,
}

const TRANSPORT_GENERATORS: [MagicSquareTransportMapV0; 3] = [
    MagicSquareTransportMapV0::RotateClockwise,
    MagicSquareTransportMapV0::ReflectVertical,
    MagicSquareTransportMapV0::ComplementSeventeen,
];

impl MagicSquareTransportMapV0 {
    fn as_str(self) -> &'static str {
        match self {
            Self::RotateClockwise => "rotate-clockwise",
            Self::ReflectVertical => "reflect-vertical",
            Self::ComplementSeventeen => "complement-seventeen",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareTransportReceiptV0 {
    pub map: MagicSquareTransportMapV0,
    pub source_certificate_digest: String,
    pub source_occurrence: ArtifactKeyV0,
    pub target: MagicSquareClosureReferenceV0,
    pub additive_closure_preserved: CheckStatus,
    pub characteristic_identity_preserved: CheckStatus,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareFamilyMemberV0 {
    pub ordinal: u8,
    pub first_word: Vec<MagicSquareTransportMapV0>,
    pub closure: MagicSquareClosureReferenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareFamilyEdgeV0 {
    pub source: u8,
    pub generator: MagicSquareTransportMapV0,
    pub target: u8,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareCoherenceV0 {
    pub name: String,
    pub left: Vec<MagicSquareTransportMapV0>,
    pub right: Vec<MagicSquareTransportMapV0>,
    pub checked_members: u8,
    pub status: CheckStatus,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicLineContentV0 {
    pub values: [u8; 4],
    pub additive_residual: i16,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicLineInfluenceV0 {
    pub left: String,
    pub right: String,
    pub shared_cells: Vec<u8>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareClosureFamilyV0 {
    pub seed_content_digest: String,
    pub members: Vec<MagicSquareFamilyMemberV0>,
    pub edges: Vec<MagicSquareFamilyEdgeV0>,
    pub coherences: Vec<MagicSquareCoherenceV0>,
    pub line_occurrences: u16,
    pub unique_line_contents: Vec<MagicLineContentV0>,
    pub influences: Vec<MagicLineInfluenceV0>,
}

impl MagicSquareClosureFamilyV0 {
    fn derive(seed: &MagicSquareCertificateV0) -> Result<Self, MagicSquareErrorV0> {
        seed.check()?;
        let mut members = vec![MagicSquareFamilyMemberV0 {
            ordinal: 0,
            first_word: Vec::new(),
            closure: MagicSquareClosureReferenceV0::from_certificate(seed)?,
        }];
        let mut member_by_cells = BTreeMap::from([(seed.content.cells, 0_u8)]);
        let mut edges = Vec::new();
        let mut cursor = 0_usize;
        while cursor < members.len() {
            let source_ordinal = members[cursor].ordinal;
            let source_cells = members[cursor].closure.cells;
            let source_word = members[cursor].first_word.clone();
            for generator in TRANSPORT_GENERATORS {
                let target_cells = transport_cells(source_cells, generator);
                let target_ordinal = if let Some(ordinal) = member_by_cells.get(&target_cells) {
                    *ordinal
                } else {
                    let ordinal = u8::try_from(members.len())
                        .map_err(|_| invalid("the closure family ordinal overflowed"))?;
                    let mut first_word = source_word.clone();
                    first_word.push(generator);
                    let certificate = MagicSquareCertificateV0::from_cells(
                        target_cells,
                        format!("experiment:0119:family-occurrence:{ordinal}"),
                    )?;
                    members.push(MagicSquareFamilyMemberV0 {
                        ordinal,
                        first_word,
                        closure: MagicSquareClosureReferenceV0::from_certificate(&certificate)?,
                    });
                    member_by_cells.insert(target_cells, ordinal);
                    ordinal
                };
                edges.push(MagicSquareFamilyEdgeV0 {
                    source: source_ordinal,
                    generator,
                    target: target_ordinal,
                });
            }
            cursor += 1;
        }

        let relation_words = [
            (
                "rotation_order_four",
                vec![
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::RotateClockwise,
                ],
                Vec::new(),
            ),
            (
                "reflection_order_two",
                vec![
                    MagicSquareTransportMapV0::ReflectVertical,
                    MagicSquareTransportMapV0::ReflectVertical,
                ],
                Vec::new(),
            ),
            (
                "complement_order_two",
                vec![
                    MagicSquareTransportMapV0::ComplementSeventeen,
                    MagicSquareTransportMapV0::ComplementSeventeen,
                ],
                Vec::new(),
            ),
            (
                "complement_rotation_interchange",
                vec![
                    MagicSquareTransportMapV0::ComplementSeventeen,
                    MagicSquareTransportMapV0::RotateClockwise,
                ],
                vec![
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::ComplementSeventeen,
                ],
            ),
            (
                "complement_reflection_interchange",
                vec![
                    MagicSquareTransportMapV0::ComplementSeventeen,
                    MagicSquareTransportMapV0::ReflectVertical,
                ],
                vec![
                    MagicSquareTransportMapV0::ReflectVertical,
                    MagicSquareTransportMapV0::ComplementSeventeen,
                ],
            ),
            (
                "reflection_rotation_conjugacy",
                vec![
                    MagicSquareTransportMapV0::ReflectVertical,
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::ReflectVertical,
                ],
                vec![
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::RotateClockwise,
                    MagicSquareTransportMapV0::RotateClockwise,
                ],
            ),
        ];
        let checked_members = u8::try_from(members.len())
            .map_err(|_| invalid("the closure family cardinality overflowed"))?;
        let coherences = relation_words
            .into_iter()
            .map(|(name, left, right)| {
                let status = if members.iter().all(|member| {
                    apply_transport_word(member.closure.cells, &left)
                        == apply_transport_word(member.closure.cells, &right)
                }) {
                    CheckStatus::Checked
                } else {
                    CheckStatus::Unchecked
                };
                MagicSquareCoherenceV0 {
                    name: name.to_owned(),
                    left,
                    right,
                    checked_members,
                    status,
                }
            })
            .collect::<Vec<_>>();

        let mut unique_line_contents = BTreeSet::new();
        for member in &members {
            for line in line_witnesses(&member.closure.cells) {
                let mut values = line.values;
                values.sort_unstable();
                unique_line_contents.insert(MagicLineContentV0 {
                    values,
                    additive_residual: line.additive_residual,
                });
            }
        }
        let influences = line_influences();
        let family = Self {
            seed_content_digest: seed.content.digest()?,
            line_occurrences: u16::try_from(members.len() * LINES.len())
                .map_err(|_| invalid("the line occurrence count overflowed"))?,
            members,
            edges,
            coherences,
            unique_line_contents: unique_line_contents.into_iter().collect(),
            influences,
        };
        family.check_against(seed)?;
        Ok(family)
    }

    fn check_against(&self, seed: &MagicSquareCertificateV0) -> Result<(), MagicSquareErrorV0> {
        if self.members.len() != 16
            || self.edges.len() != self.members.len() * TRANSPORT_GENERATORS.len()
            || self.line_occurrences != 160
            || self.coherences.len() != 6
            || self
                .coherences
                .iter()
                .any(|coherence| coherence.status != CheckStatus::Checked)
        {
            return Err(invalid(
                "the selected closure did not generate the frozen finite family",
            ));
        }
        if self.seed_content_digest != seed.content.digest()?
            || self.members.first().map(|member| &member.closure)
                != Some(&MagicSquareClosureReferenceV0::from_certificate(seed)?)
        {
            return Err(invalid("the closure family has lost its seed"));
        }
        for (ordinal, member) in self.members.iter().enumerate() {
            if usize::from(member.ordinal) != ordinal {
                return Err(invalid("closure family member ordinals are not canonical"));
            }
            member.closure.check()?;
            if apply_transport_word(seed.content.cells, &member.first_word) != member.closure.cells
            {
                return Err(invalid("a closure family word does not reach its member"));
            }
        }
        for edge in &self.edges {
            let source = self
                .members
                .get(usize::from(edge.source))
                .ok_or_else(|| invalid("a closure family edge has an unknown source"))?;
            let target = self
                .members
                .get(usize::from(edge.target))
                .ok_or_else(|| invalid("a closure family edge has an unknown target"))?;
            if transport_cells(source.closure.cells, edge.generator) != target.closure.cells {
                return Err(invalid("a closure family edge does not replay"));
            }
        }
        if self.influences != line_influences() {
            return Err(invalid("the local line influence graph has drifted"));
        }
        Ok(())
    }
}

impl MagicSquareTransportReceiptV0 {
    fn derive(
        source: &MagicSquareCertificateV0,
        map: MagicSquareTransportMapV0,
    ) -> Result<Self, MagicSquareErrorV0> {
        let cells = transport_cells(source.content.cells, map);
        let target_certificate = MagicSquareCertificateV0::from_cells(
            cells,
            format!("experiment:0119:occurrence:{}", map.as_str()),
        )?;
        let target = MagicSquareClosureReferenceV0::from_certificate(&target_certificate)?;
        Ok(Self {
            map,
            source_certificate_digest: source.digest()?,
            source_occurrence: source.occurrence.clone(),
            target,
            additive_closure_preserved: CheckStatus::Checked,
            characteristic_identity_preserved: CheckStatus::Checked,
        })
    }

    fn check_against(&self, source: &MagicSquareCertificateV0) -> Result<(), MagicSquareErrorV0> {
        let expected = Self::derive(source, self.map)?;
        if self != &expected || self.source_occurrence == self.target.occurrence {
            return Err(invalid(
                "a symmetry transport receipt does not replay exactly",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareSeparationV0 {
    pub class: ClosureFindingClassV0,
    pub cells: [u8; CELL_COUNT],
    pub characteristic_residual: MultiplicativeResidualV0,
    pub failed_lines: Vec<MagicLineWitnessV0>,
}

impl MagicSquareSeparationV0 {
    fn derive(source: &MagicSquareCertificateV0) -> Result<Self, MagicSquareErrorV0> {
        let mut cells = source.content.cells;
        cells.swap(0, 4);
        let before = characteristic_expression(cells);
        let after = characteristic_expression(1..=16);
        let characteristic_residual = MultiplicativeResidualV0::from_transition(&before, &after)?;
        let failed_lines = line_witnesses(&cells)
            .into_iter()
            .filter(|line| line.additive_residual != 0)
            .collect::<Vec<_>>();
        if !characteristic_residual.is_one() || failed_lines.is_empty() {
            return Err(invalid(
                "the frozen negative control is not a strict separation",
            ));
        }
        Ok(Self {
            class: ClosureFindingClassV0::Separation,
            cells,
            characteristic_residual,
            failed_lines,
        })
    }

    fn check_against(&self, source: &MagicSquareCertificateV0) -> Result<(), MagicSquareErrorV0> {
        if self != &Self::derive(source)? || self.class != ClosureFindingClassV0::Separation {
            return Err(invalid("the magic-square separation control has drifted"));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareInputV0 {
    pub subject: MagicSquareFrontierV0,
    pub method: MagicSquareSearchContractV0,
    pub object: MagicSquareResourceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareHistoryV0 {
    pub mechanism: MechanismV0,
    pub subject_digest: String,
    pub method_digest: String,
    pub object_digest: String,
    pub nodes_expanded: u64,
    pub branches_cut: u64,
    pub unselected_closure_digests: Vec<String>,
    pub row_major_trace: Option<MagicSquareFillTraceV0>,
    pub column_major_trace: Option<MagicSquareFillTraceV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareResultV0 {
    pub state: MagicSquareSearchStateV0,
    pub solution: Option<MagicSquareCertificateV0>,
    pub adversarial_separation: Option<MagicSquareSeparationV0>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareEvidenceV0 {
    pub additive_lines_closed: CheckStatus,
    pub multiplicative_characteristic_is_one: CheckStatus,
    pub common_endpoint_retained: CheckStatus,
    pub distinct_histories_retained: CheckStatus,
    pub separation_preserves_multiset_only: CheckStatus,
    pub transports: Vec<MagicSquareTransportReceiptV0>,
    pub closure_family: Option<MagicSquareClosureFamilyV0>,
    pub next_frontier: MagicSquareFrontierV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareOutputV0 {
    pub history: MagicSquareHistoryV0,
    pub result: MagicSquareResultV0,
    pub evidence: MagicSquareEvidenceV0,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MagicSquareTransitionV0 {
    pub schema: String,
    pub version: u32,
    pub input: MagicSquareInputV0,
    pub output: MagicSquareOutputV0,
}

impl MagicSquareTransitionV0 {
    pub fn check(&self) -> Result<(), MagicSquareErrorV0> {
        if self.schema != MAGIC_SQUARE_TRANSITION_SCHEMA_V0
            || self.version != MAGIC_SQUARE_VERSION_V0
        {
            return Err(invalid("unsupported magic-square transition header"));
        }
        self.input.subject.check()?;
        self.input.method.check()?;
        self.input.object.check()?;
        if self.input.subject.state != MagicSquareSearchStateV0::Frontier {
            return Err(invalid("search can continue only from an open frontier"));
        }
        let expected = derive_output(&self.input)?;
        if self.output != expected {
            return Err(invalid("the stored magic-square output does not replay"));
        }
        Ok(())
    }

    pub fn from_json(source: &str) -> Result<Self, MagicSquareErrorV0> {
        let value: Self = serde_json::from_str(source)
            .map_err(|error| MagicSquareErrorV0::Json(error.to_string()))?;
        value.check()?;
        Ok(value)
    }

    pub fn to_json(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        pretty_json(self)
    }

    pub fn digest(&self) -> Result<String, MagicSquareErrorV0> {
        self.check()?;
        digest_serialized(self)
    }
}

/// Run one deterministic, fuel-bounded search transition.
///
/// The existential problem closes at the first exact solution. Any unvisited
/// branches remain in the output frontier as retained alternatives rather
/// than being silently identified with the discovered closure.
pub fn run_magic_square_search_v0(
    subject: &MagicSquareFrontierV0,
    method: &MagicSquareSearchContractV0,
    object: &MagicSquareResourceV0,
) -> Result<MagicSquareTransitionV0, MagicSquareErrorV0> {
    let input = MagicSquareInputV0 {
        subject: subject.clone(),
        method: method.clone(),
        object: object.clone(),
    };
    subject.check()?;
    method.check()?;
    object.check()?;
    if subject.state != MagicSquareSearchStateV0::Frontier {
        return Err(invalid("search can continue only from an open frontier"));
    }
    let transition = MagicSquareTransitionV0 {
        schema: MAGIC_SQUARE_TRANSITION_SCHEMA_V0.to_owned(),
        version: MAGIC_SQUARE_VERSION_V0,
        output: derive_output(&input)?,
        input,
    };
    transition.check()?;
    Ok(transition)
}

fn derive_output(input: &MagicSquareInputV0) -> Result<MagicSquareOutputV0, MagicSquareErrorV0> {
    let mut pending = input.subject.pending.clone();
    let mut nodes_expanded = 0_u64;
    let mut branches_cut = 0_u64;
    let mut found = None;
    let mut unselected_closure_digests = Vec::new();

    while nodes_expanded < input.object.fuel {
        let Some(node) = pending.pop() else {
            break;
        };
        nodes_expanded += 1;
        if node.cells.iter().all(|value| *value != 0) {
            if complete_magic(&node.cells) {
                let content = MagicSquareClosureContentV0::from_cells(node.cells)?;
                if raw_transport_orbit(node.cells).len() == 16 {
                    found = Some(node.cells);
                    break;
                }
                unselected_closure_digests.push(content.digest()?);
                continue;
            }
            branches_cut += 1;
            continue;
        }
        let cell = node
            .cells
            .iter()
            .position(|value| *value == 0)
            .ok_or_else(|| invalid("an incomplete node has no open cell"))?;
        let used = node
            .cells
            .iter()
            .copied()
            .filter(|value| *value != 0)
            .collect::<BTreeSet<_>>();
        for value in (1_u8..=16).rev() {
            if used.contains(&value) {
                continue;
            }
            let mut child = node.cells;
            child[cell] = value;
            if partial_admissible(&child) {
                pending.push(MagicSquareSearchNodeV0 { cells: child });
            } else {
                branches_cut += 1;
            }
        }
    }

    let subject_digest = input.subject.digest()?;
    let solution = found
        .map(|cells| {
            MagicSquareCertificateV0::from_cells(
                cells,
                format!(
                    "experiment:0119:search-occurrence:{}",
                    input.subject.sequence + 1
                ),
            )
        })
        .transpose()?;
    let state = if solution.is_some() {
        MagicSquareSearchStateV0::Identity
    } else if pending.is_empty() {
        MagicSquareSearchStateV0::Exhausted
    } else {
        MagicSquareSearchStateV0::Frontier
    };
    let row_major_trace = solution
        .as_ref()
        .map(|certificate| {
            MagicSquareFillTraceV0::from_order("row-major", 0_u8..16, &certificate.content)
        })
        .transpose()?;
    let column_major_order =
        (0_u8..4).flat_map(|column| (0_u8..4).map(move |row| row * 4 + column));
    let column_major_trace = solution
        .as_ref()
        .map(|certificate| {
            MagicSquareFillTraceV0::from_order(
                "column-major",
                column_major_order,
                &certificate.content,
            )
        })
        .transpose()?;
    if let (Some(row), Some(column), Some(certificate)) =
        (&row_major_trace, &column_major_trace, &solution)
    {
        row.check_against(&certificate.content)?;
        column.check_against(&certificate.content)?;
        if row == column || row.endpoint_content_digest != column.endpoint_content_digest {
            return Err(invalid(
                "the two schedules do not retain distinct common-endpoint histories",
            ));
        }
    }
    let adversarial_separation = solution
        .as_ref()
        .map(MagicSquareSeparationV0::derive)
        .transpose()?;
    if let (Some(separation), Some(certificate)) = (&adversarial_separation, &solution) {
        separation.check_against(certificate)?;
    }
    let transports = if let Some(certificate) = &solution {
        [
            MagicSquareTransportMapV0::RotateClockwise,
            MagicSquareTransportMapV0::ReflectVertical,
            MagicSquareTransportMapV0::ComplementSeventeen,
        ]
        .into_iter()
        .map(|map| MagicSquareTransportReceiptV0::derive(certificate, map))
        .collect::<Result<Vec<_>, _>>()?
    } else {
        Vec::new()
    };
    if let Some(certificate) = &solution {
        for receipt in &transports {
            receipt.check_against(certificate)?;
        }
    }
    let closure_family = solution
        .as_ref()
        .map(MagicSquareClosureFamilyV0::derive)
        .transpose()?;
    let next_frontier = MagicSquareFrontierV0 {
        schema: MAGIC_SQUARE_FRONTIER_SCHEMA_V0.to_owned(),
        version: MAGIC_SQUARE_VERSION_V0,
        interface: InquiryInterfaceV0::canonical(),
        sequence: input.subject.sequence + 1,
        state,
        pending,
        closure: solution
            .as_ref()
            .map(MagicSquareClosureReferenceV0::from_certificate)
            .transpose()?,
        parent_digest: Some(subject_digest.clone()),
    };
    next_frontier.check()?;
    let checked = if solution.is_some() {
        CheckStatus::Checked
    } else {
        CheckStatus::Unchecked
    };
    Ok(MagicSquareOutputV0 {
        history: MagicSquareHistoryV0 {
            mechanism: MechanismV0::Learn,
            subject_digest,
            method_digest: input.method.digest()?,
            object_digest: input.object.digest()?,
            nodes_expanded,
            branches_cut,
            unselected_closure_digests,
            row_major_trace,
            column_major_trace,
        },
        result: MagicSquareResultV0 {
            state,
            solution,
            adversarial_separation,
        },
        evidence: MagicSquareEvidenceV0 {
            additive_lines_closed: checked,
            multiplicative_characteristic_is_one: checked,
            common_endpoint_retained: checked,
            distinct_histories_retained: checked,
            separation_preserves_multiset_only: checked,
            transports,
            closure_family,
            next_frontier,
        },
    })
}

fn partial_admissible(cells: &[u8; CELL_COUNT]) -> bool {
    let mut used = BTreeSet::new();
    for value in cells.iter().copied().filter(|value| *value != 0) {
        if value > 16 || !used.insert(value) {
            return false;
        }
    }
    let unused = (1_u8..=16)
        .filter(|value| !used.contains(value))
        .collect::<Vec<_>>();
    for (_, line) in LINES {
        let values = line.map(|cell| cells[cell]);
        let sum = values.iter().map(|value| i16::from(*value)).sum::<i16>();
        let holes = values.iter().filter(|value| **value == 0).count();
        if holes == 0 {
            if sum != MAGIC_SUM {
                return false;
            }
            continue;
        }
        let minimum = unused
            .iter()
            .take(holes)
            .map(|value| i16::from(*value))
            .sum::<i16>();
        let maximum = unused
            .iter()
            .rev()
            .take(holes)
            .map(|value| i16::from(*value))
            .sum::<i16>();
        if sum + minimum > MAGIC_SUM || sum + maximum < MAGIC_SUM {
            return false;
        }
    }
    true
}

fn complete_magic(cells: &[u8; CELL_COUNT]) -> bool {
    cells.iter().all(|value| *value != 0)
        && partial_admissible(cells)
        && line_witnesses(cells)
            .iter()
            .all(|line| line.additive_residual == 0)
}

fn line_witnesses(cells: &[u8; CELL_COUNT]) -> Vec<MagicLineWitnessV0> {
    LINES
        .iter()
        .map(|(name, indices)| {
            let cell_coordinates = indices.map(|cell| u8::try_from(cell).expect("cell fits u8"));
            let values = indices.map(|cell| cells[cell]);
            let sum = values.iter().map(|value| i16::from(*value)).sum::<i16>();
            MagicLineWitnessV0 {
                name: (*name).to_owned(),
                cells: cell_coordinates,
                values,
                sum,
                additive_residual: sum - MAGIC_SUM,
            }
        })
        .collect()
}

fn characteristic_expression(values: impl IntoIterator<Item = u8>) -> ExactExprV0 {
    values
        .into_iter()
        .map(|value| {
            ExactExprV0::sum(
                ExactExprV0::variable(CHARACTERISTIC_VARIABLE),
                ExactExprV0::constant(-i64::from(value)),
            )
        })
        .reduce(ExactExprV0::product)
        .unwrap_or_else(|| ExactExprV0::constant(1))
}

fn remaining_factor_digest(cells: &[u8; CELL_COUNT]) -> Result<String, MagicSquareErrorV0> {
    let used = cells
        .iter()
        .copied()
        .filter(|value| *value != 0)
        .collect::<BTreeSet<_>>();
    let expression = characteristic_expression((1_u8..=16).filter(|value| !used.contains(value)));
    digest_serialized(&expression)
}

fn transport_cells(source: [u8; CELL_COUNT], map: MagicSquareTransportMapV0) -> [u8; CELL_COUNT] {
    let mut target = [0_u8; CELL_COUNT];
    match map {
        MagicSquareTransportMapV0::RotateClockwise => {
            for row in 0..4 {
                for column in 0..4 {
                    target[column * 4 + (3 - row)] = source[row * 4 + column];
                }
            }
        }
        MagicSquareTransportMapV0::ReflectVertical => {
            for row in 0..4 {
                for column in 0..4 {
                    target[row * 4 + (3 - column)] = source[row * 4 + column];
                }
            }
        }
        MagicSquareTransportMapV0::ComplementSeventeen => {
            for (target, source) in target.iter_mut().zip(source) {
                *target = 17 - source;
            }
        }
    }
    target
}

fn apply_transport_word(
    mut cells: [u8; CELL_COUNT],
    word: &[MagicSquareTransportMapV0],
) -> [u8; CELL_COUNT] {
    for map in word {
        cells = transport_cells(cells, *map);
    }
    cells
}

fn raw_transport_orbit(seed: [u8; CELL_COUNT]) -> BTreeSet<[u8; CELL_COUNT]> {
    let mut orbit = BTreeSet::from([seed]);
    let mut pending = vec![seed];
    while let Some(cells) = pending.pop() {
        for generator in TRANSPORT_GENERATORS {
            let target = transport_cells(cells, generator);
            if orbit.insert(target) {
                pending.push(target);
            }
        }
    }
    orbit
}

fn line_influences() -> Vec<MagicLineInfluenceV0> {
    let mut influences = Vec::new();
    for (left_index, (left_name, left_cells)) in LINES.iter().enumerate() {
        for (right_name, right_cells) in LINES.iter().skip(left_index + 1) {
            let shared_cells = left_cells
                .iter()
                .filter(|cell| right_cells.contains(cell))
                .map(|cell| u8::try_from(*cell).expect("cell fits u8"))
                .collect::<Vec<_>>();
            if !shared_cells.is_empty() {
                influences.push(MagicLineInfluenceV0 {
                    left: (*left_name).to_owned(),
                    right: (*right_name).to_owned(),
                    shared_cells,
                });
            }
        }
    }
    influences
}

pub fn load_magic_square_frontier_v0(
    path: impl AsRef<Path>,
) -> Result<MagicSquareFrontierV0, MagicSquareErrorV0> {
    load_checked(path, MagicSquareFrontierV0::from_json)
}

pub fn load_magic_square_search_contract_v0(
    path: impl AsRef<Path>,
) -> Result<MagicSquareSearchContractV0, MagicSquareErrorV0> {
    load_checked(path, MagicSquareSearchContractV0::from_json)
}

pub fn load_magic_square_resource_v0(
    path: impl AsRef<Path>,
) -> Result<MagicSquareResourceV0, MagicSquareErrorV0> {
    load_checked(path, MagicSquareResourceV0::from_json)
}

pub fn load_magic_square_transition_v0(
    path: impl AsRef<Path>,
) -> Result<MagicSquareTransitionV0, MagicSquareErrorV0> {
    load_checked(path, MagicSquareTransitionV0::from_json)
}

pub fn save_magic_square_frontier_v0(
    path: impl AsRef<Path>,
    frontier: &MagicSquareFrontierV0,
) -> Result<InquirySaveReceiptV0, MagicSquareErrorV0> {
    save_checked(path, frontier.to_json()?)
}

pub fn save_magic_square_transition_v0(
    path: impl AsRef<Path>,
    transition: &MagicSquareTransitionV0,
) -> Result<InquirySaveReceiptV0, MagicSquareErrorV0> {
    save_checked(path, transition.to_json()?)
}

fn check_header(
    schema: &str,
    version: u32,
    expected_schema: &str,
    interface: &InquiryInterfaceV0,
) -> Result<(), MagicSquareErrorV0> {
    if schema != expected_schema
        || version != MAGIC_SQUARE_VERSION_V0
        || interface != &InquiryInterfaceV0::canonical()
        || interface.inputs != InputLabelV0::ALL
        || interface.outputs != OutputLabelV0::ALL
    {
        return Err(invalid(
            "unsupported magic-square schema, version, or three-port interface",
        ));
    }
    Ok(())
}

fn key(value: impl Into<String>) -> Result<ArtifactKeyV0, MagicSquareErrorV0> {
    ArtifactKeyV0::cache_label(value)
        .map_err(|error| MagicSquareErrorV0::InvalidArtifact(error.to_string()))
}

fn check_digest(digest: &str) -> Result<(), MagicSquareErrorV0> {
    let Some(hex) = digest.strip_prefix("blake3:") else {
        return Err(invalid("a magic-square digest must be a BLAKE3 coordinate"));
    };
    if hex.len() != 64
        || !hex
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(invalid(
            "a magic-square digest must be a lowercase BLAKE3 coordinate",
        ));
    }
    Ok(())
}

fn pretty_json<T: Serialize>(value: &T) -> Result<String, MagicSquareErrorV0> {
    serde_json::to_string_pretty(value).map_err(|error| MagicSquareErrorV0::Json(error.to_string()))
}

fn digest_serialized<T: Serialize>(value: &T) -> Result<String, MagicSquareErrorV0> {
    let encoded = format!("{}\n", pretty_json(value)?);
    Ok(format!(
        "blake3:{}",
        blake3::hash(encoded.as_bytes()).to_hex()
    ))
}

fn invalid(detail: impl Into<String>) -> MagicSquareErrorV0 {
    MagicSquareErrorV0::InvalidArtifact(detail.into())
}

fn load_checked<T>(
    path: impl AsRef<Path>,
    decode: impl FnOnce(&str) -> Result<T, MagicSquareErrorV0>,
) -> Result<T, MagicSquareErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| MagicSquareErrorV0::Persistence(error.to_string()))?;
    let source = fs::read_to_string(path).map_err(|error| MagicSquareErrorV0::Io {
        path: path.to_path_buf(),
        detail: error.to_string(),
    })?;
    decode(&source)
}

fn save_checked(
    path: impl AsRef<Path>,
    json: String,
) -> Result<InquirySaveReceiptV0, MagicSquareErrorV0> {
    let path = path.as_ref();
    crate::persistence::require_adva_extension(path)
        .map_err(|error| MagicSquareErrorV0::Persistence(error.to_string()))?;
    let encoded = format!("{json}\n");
    crate::persistence::write_atomically(path, encoded.as_bytes())
        .map_err(|error| MagicSquareErrorV0::Persistence(error.to_string()))?;
    Ok(InquirySaveReceiptV0 {
        path: path.to_path_buf(),
        artifact_digest: format!("blake3:{}", blake3::hash(encoded.as_bytes()).to_hex()),
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

#[derive(Debug, Error)]
pub enum MagicSquareErrorV0 {
    #[error("invalid magic-square artifact: {0}")]
    InvalidArtifact(String),
    #[error("magic-square arithmetic error: {0}")]
    Arithmetic(#[from] crate::ArithmeticErrorV0),
    #[error("magic-square JSON error: {0}")]
    Json(String),
    #[error("magic-square persistence error: {0}")]
    Persistence(String),
    #[error("magic-square I/O error at {path}: {detail}")]
    Io { path: PathBuf, detail: String },
}
