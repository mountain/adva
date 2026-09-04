use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use thiserror::Error;

/// The three surface roles. These are witness coordinates, not `ValueType`s.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RoleV0 {
    Construction,
    Space,
    Time,
}

impl RoleV0 {
    #[must_use]
    pub const fn surface(self) -> &'static str {
        match self {
            Self::Construction => "{}",
            Self::Space => "[]",
            Self::Time => "()",
        }
    }
}

/// One coordinate in the signed additive formation ledger.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum BoundaryCoordinateV0 {
    Role { role: RoleV0 },
    UnitSlot { slot: u8 },
    HoleOccurrence { hole: u8, occurrence: u32 },
}

/// One nonzero coefficient in a canonical boundary charge.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BoundaryTermV0 {
    pub coordinate: BoundaryCoordinateV0,
    pub coefficient: i32,
}

impl BoundaryTermV0 {
    #[must_use]
    pub const fn new(coordinate: BoundaryCoordinateV0, coefficient: i32) -> Self {
        Self {
            coordinate,
            coefficient,
        }
    }
}

/// Canonical sparse signed ledger used for additive formation.
#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BoundaryChargeV0 {
    terms: Vec<BoundaryTermV0>,
}

impl BoundaryChargeV0 {
    #[must_use]
    pub const fn zero() -> Self {
        Self { terms: Vec::new() }
    }

    /// Canonicalize a finite signed ledger, merging equal coordinates.
    ///
    /// # Errors
    ///
    /// Returns [`BoundaryErrorV0::CoefficientOverflow`] if merging would
    /// exceed the signed 32-bit coefficient range.
    pub fn from_terms(
        terms: impl IntoIterator<Item = BoundaryTermV0>,
    ) -> Result<Self, BoundaryErrorV0> {
        let mut accumulated = BTreeMap::<BoundaryCoordinateV0, i32>::new();
        for term in terms {
            if term.coefficient == 0 {
                continue;
            }
            let current = accumulated.get(&term.coordinate).copied().unwrap_or(0);
            let next = current
                .checked_add(term.coefficient)
                .ok_or(BoundaryErrorV0::CoefficientOverflow)?;
            if next == 0 {
                accumulated.remove(&term.coordinate);
            } else {
                accumulated.insert(term.coordinate, next);
            }
        }
        Ok(Self {
            terms: accumulated
                .into_iter()
                .map(|(coordinate, coefficient)| BoundaryTermV0 {
                    coordinate,
                    coefficient,
                })
                .collect(),
        })
    }

    #[must_use]
    pub fn terms(&self) -> &[BoundaryTermV0] {
        &self.terms
    }

    #[must_use]
    pub fn is_zero(&self) -> bool {
        self.terms.is_empty()
    }

    #[must_use]
    pub fn coefficient(&self, coordinate: &BoundaryCoordinateV0) -> i32 {
        self.terms
            .binary_search_by(|term| term.coordinate.cmp(coordinate))
            .map_or(0, |index| self.terms[index].coefficient)
    }

    /// Add two canonical charges.
    ///
    /// # Errors
    ///
    /// Returns [`BoundaryErrorV0::CoefficientOverflow`] on coefficient
    /// overflow.
    pub fn checked_add(&self, other: &Self) -> Result<Self, BoundaryErrorV0> {
        Self::from_terms(self.terms.iter().chain(&other.terms).cloned())
    }

    /// Subtract `other` from this charge.
    ///
    /// # Errors
    ///
    /// Returns [`BoundaryErrorV0::CoefficientOverflow`] on coefficient
    /// overflow or negation of `i32::MIN`.
    pub fn checked_sub(&self, other: &Self) -> Result<Self, BoundaryErrorV0> {
        let negated = other
            .terms
            .iter()
            .map(|term| {
                term.coefficient
                    .checked_neg()
                    .map(|coefficient| BoundaryTermV0 {
                        coordinate: term.coordinate.clone(),
                        coefficient,
                    })
                    .ok_or(BoundaryErrorV0::CoefficientOverflow)
            })
            .collect::<Result<Vec<_>, _>>()?;
        Self::from_terms(self.terms.iter().cloned().chain(negated))
    }
}

#[derive(Clone, Copy, Debug, Eq, Error, PartialEq)]
pub enum BoundaryErrorV0 {
    #[error("formation-ledger coefficient overflow")]
    CoefficientOverflow,
}
