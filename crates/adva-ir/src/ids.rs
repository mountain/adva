use serde::{Deserialize, Serialize};
use std::fmt::{self, Display};

macro_rules! string_id {
    ($name:ident) => {
        #[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
        #[serde(transparent)]
        pub struct $name(pub String);

        impl $name {
            pub fn explicit(value: impl Into<String>) -> Self {
                let value = value.into();
                assert!(
                    !value.is_empty(),
                    concat!(stringify!($name), " must not be empty")
                );
                Self(value)
            }

            pub fn as_str(&self) -> &str {
                &self.0
            }
        }

        impl Display for $name {
            fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                formatter.write_str(&self.0)
            }
        }
    };
}

string_id!(ModuleName);
string_id!(FunctionName);
string_id!(SourceId);
string_id!(OccurrenceId);
string_id!(CellId);
string_id!(CertificateId);
string_id!(GraftFrameId);

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct NodeId(pub u32);

#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct OccurrencePath(pub Vec<u32>);

impl OccurrencePath {
    pub fn root() -> Self {
        Self(Vec::new())
    }

    #[must_use]
    pub fn branch(&self, index: u32) -> Self {
        let mut path = self.0.clone();
        path.push(index);
        Self(path)
    }
}

#[derive(Clone, Debug, Eq, Hash, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct QualifiedName {
    pub module: ModuleName,
    pub function: FunctionName,
}

impl QualifiedName {
    pub fn new(module: impl Into<String>, function: impl Into<String>) -> Self {
        Self {
            module: ModuleName::explicit(module),
            function: FunctionName::explicit(function),
        }
    }
}

impl Display for QualifiedName {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}/{}", self.module, self.function)
    }
}
