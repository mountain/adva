use crate::{BoundaryChargeV0, BoundaryCoordinateV0, BoundaryErrorV0, BoundaryTermV0, RoleV0};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use thiserror::Error;

/// The six initial surface terms.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TermGlyphV0 {
    Construction,
    Space,
    Time,
    Unit,
    Add,
    Multiply,
}

impl TermGlyphV0 {
    pub const ALL: [Self; 6] = [
        Self::Construction,
        Self::Space,
        Self::Time,
        Self::Unit,
        Self::Add,
        Self::Multiply,
    ];

    #[must_use]
    pub const fn surface(self) -> &'static str {
        match self {
            Self::Construction => "{}",
            Self::Space => "[]",
            Self::Time => "()",
            Self::Unit => "|",
            Self::Add => ">",
            Self::Multiply => "<",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RelationDirectionV0 {
    Greater,
    Less,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RelationWordV0 {
    pub left: RoleV0,
    pub direction: RelationDirectionV0,
    pub right: RoleV0,
}

impl RelationWordV0 {
    #[must_use]
    pub const fn greater(left: RoleV0, right: RoleV0) -> Self {
        Self {
            left,
            direction: RelationDirectionV0::Greater,
            right,
        }
    }

    #[must_use]
    pub const fn less(left: RoleV0, right: RoleV0) -> Self {
        Self {
            left,
            direction: RelationDirectionV0::Less,
            right,
        }
    }

    #[must_use]
    pub fn surface(self) -> String {
        let arrow = match self.direction {
            RelationDirectionV0::Greater => ">",
            RelationDirectionV0::Less => "<",
        };
        format!("{} {arrow} {}", self.left.surface(), self.right.surface())
    }

    fn oriented_roles(self) -> (RoleV0, RoleV0) {
        match self.direction {
            RelationDirectionV0::Greater => (self.left, self.right),
            RelationDirectionV0::Less => (self.right, self.left),
        }
    }

    fn charge(self) -> Result<BoundaryChargeV0, BoundaryErrorV0> {
        let (source, target) = self.oriented_roles();
        BoundaryChargeV0::from_terms([
            BoundaryTermV0::new(BoundaryCoordinateV0::Role { role: source }, -1),
            BoundaryTermV0::new(BoundaryCoordinateV0::Role { role: target }, 1),
        ])
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum TypeWordV0 {
    Relation { word: RelationWordV0 },
    UnitTriplet,
    AddSlot,
    MultiplySlot,
}

impl TypeWordV0 {
    #[must_use]
    pub fn surface(&self) -> String {
        match self {
            Self::Relation { word } => word.surface(),
            Self::UnitTriplet => "|||".to_owned(),
            Self::AddSlot => "<|>".to_owned(),
            Self::MultiplySlot => ">|<".to_owned(),
        }
    }

    fn charge(&self) -> Result<BoundaryChargeV0, BoundaryErrorV0> {
        match self {
            Self::Relation { word } => word.charge(),
            Self::UnitTriplet => unit_slots([0, 1, 2]),
            Self::AddSlot | Self::MultiplySlot => unit_slots([1]),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ValueWordV0 {
    Relation { word: RelationWordV0 },
    Unit { support: Vec<u8> },
    Add { witness_slot: u8 },
    Multiply { witness_slot: u8 },
}

impl ValueWordV0 {
    #[must_use]
    pub fn surface(&self) -> String {
        match self {
            Self::Relation { word } => word.surface(),
            Self::Unit { .. } => "1".to_owned(),
            Self::Add { .. } => "+".to_owned(),
            Self::Multiply { .. } => "*".to_owned(),
        }
    }

    fn charge(&self) -> Result<BoundaryChargeV0, BoundaryErrorV0> {
        match self {
            Self::Relation { word } => word.charge(),
            Self::Unit { support } => unit_slots(support.iter().copied()),
            Self::Add { witness_slot } | Self::Multiply { witness_slot } => {
                unit_slots([*witness_slot])
            }
        }
    }
}

fn unit_slots(slots: impl IntoIterator<Item = u8>) -> Result<BoundaryChargeV0, BoundaryErrorV0> {
    BoundaryChargeV0::from_terms(
        slots
            .into_iter()
            .map(|slot| BoundaryTermV0::new(BoundaryCoordinateV0::UnitSlot { slot }, 1)),
    )
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SeedRuleV0 {
    pub term: TermGlyphV0,
    pub type_word: TypeWordV0,
    pub value_word: ValueWordV0,
}

impl SeedRuleV0 {
    /// Check the full typed ledger, not the printed scalar glyph alone.
    ///
    /// # Errors
    ///
    /// Returns [`SeedErrorV0::UnbalancedRule`] when the type and value ledgers
    /// differ.
    pub fn verify(&self) -> Result<SeedVerificationV0, SeedErrorV0> {
        let residual = self
            .type_word
            .charge()?
            .checked_sub(&self.value_word.charge()?)?;
        if !residual.is_zero() {
            return Err(SeedErrorV0::UnbalancedRule {
                term: self.term,
                residual,
            });
        }
        Ok(SeedVerificationV0 {
            term: self.term,
            additive_residual: residual,
        })
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SeedVerificationV0 {
    pub term: TermGlyphV0,
    pub additive_residual: BoundaryChargeV0,
}

/// Single source of truth for the corrected six initial declarations.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SeedRegistryV0 {
    rules: [SeedRuleV0; 6],
}

impl SeedRegistryV0 {
    #[must_use]
    pub fn canonical() -> Self {
        use RoleV0::{Construction as K, Space as X, Time as T};
        Self {
            rules: [
                SeedRuleV0 {
                    term: TermGlyphV0::Construction,
                    type_word: TypeWordV0::Relation {
                        word: RelationWordV0::greater(X, T),
                    },
                    value_word: ValueWordV0::Relation {
                        word: RelationWordV0::less(T, X),
                    },
                },
                SeedRuleV0 {
                    term: TermGlyphV0::Space,
                    type_word: TypeWordV0::Relation {
                        word: RelationWordV0::greater(T, K),
                    },
                    value_word: ValueWordV0::Relation {
                        word: RelationWordV0::less(K, T),
                    },
                },
                SeedRuleV0 {
                    term: TermGlyphV0::Time,
                    type_word: TypeWordV0::Relation {
                        word: RelationWordV0::greater(K, X),
                    },
                    value_word: ValueWordV0::Relation {
                        word: RelationWordV0::less(X, K),
                    },
                },
                SeedRuleV0 {
                    term: TermGlyphV0::Unit,
                    type_word: TypeWordV0::UnitTriplet,
                    value_word: ValueWordV0::Unit {
                        support: vec![0, 1, 2],
                    },
                },
                SeedRuleV0 {
                    term: TermGlyphV0::Add,
                    type_word: TypeWordV0::AddSlot,
                    value_word: ValueWordV0::Add { witness_slot: 1 },
                },
                SeedRuleV0 {
                    term: TermGlyphV0::Multiply,
                    type_word: TypeWordV0::MultiplySlot,
                    value_word: ValueWordV0::Multiply { witness_slot: 1 },
                },
            ],
        }
    }

    #[must_use]
    pub fn rules(&self) -> &[SeedRuleV0; 6] {
        &self.rules
    }

    #[must_use]
    pub fn rule(&self, term: TermGlyphV0) -> Option<&SeedRuleV0> {
        self.rules.iter().find(|rule| rule.term == term)
    }

    /// Verify uniqueness, completeness, and every signed seed ledger.
    ///
    /// # Errors
    ///
    /// Returns a seed error for a duplicate, missing, or unbalanced rule.
    pub fn verify_all(&self) -> Result<Vec<SeedVerificationV0>, SeedErrorV0> {
        let terms = self
            .rules
            .iter()
            .map(|rule| rule.term)
            .collect::<BTreeSet<_>>();
        if terms.len() != self.rules.len() {
            return Err(SeedErrorV0::DuplicateTerm);
        }
        for required in TermGlyphV0::ALL {
            if !terms.contains(&required) {
                return Err(SeedErrorV0::MissingTerm(required));
            }
        }
        self.rules.iter().map(SeedRuleV0::verify).collect()
    }
}

#[derive(Clone, Debug, Eq, Error, PartialEq)]
pub enum SeedErrorV0 {
    #[error(transparent)]
    Boundary(#[from] BoundaryErrorV0),
    #[error("the six-word registry repeats a term")]
    DuplicateTerm,
    #[error("the six-word registry is missing {0:?}")]
    MissingTerm(TermGlyphV0),
    #[error("seed {term:?} has nonzero additive residual {residual:?}")]
    UnbalancedRule {
        term: TermGlyphV0,
        residual: BoundaryChargeV0,
    },
}
