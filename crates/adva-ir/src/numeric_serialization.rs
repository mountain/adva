//! Standard JSON cannot round-trip nonfinite scalars. Refuse rather than
//! allowing serde_json to silently write null beside a structural certificate.
use serde::{Serialize, Serializer, ser::Error};
use std::collections::BTreeMap;

pub(crate) fn values<S: Serializer>(values: &[f64], serializer: S) -> Result<S::Ok, S::Error> {
    if values.iter().any(|value| !value.is_finite()) {
        return Err(S::Error::custom("nonfinite scalar cannot be serialized"));
    }
    values.serialize(serializer)
}

pub(crate) fn jacobian<S: Serializer>(
    rows: &[BTreeMap<String, f64>],
    serializer: S,
) -> Result<S::Ok, S::Error> {
    if rows
        .iter()
        .flat_map(BTreeMap::values)
        .any(|value| !value.is_finite())
    {
        return Err(S::Error::custom(
            "nonfinite derivative cannot be serialized",
        ));
    }
    rows.serialize(serializer)
}
