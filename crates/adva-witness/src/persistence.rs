use crate::{
    ADVA_FILE_SUFFIX_V0, InputLabelV0, MechanismInputV0, MechanismOutputV0,
    MechanismSyntaxErrorV0, NeutralCarrierV0, OpenFrontierV0, OutputLabelV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs::{self, File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use thiserror::Error;

/// Schema identifier for the research-only neutral-carrier document.
pub const ADVA_DOCUMENT_SCHEMA_V0: &str = "adva.neutral-carrier.research";

/// Research document version. This is not `adva.ir` version one.
pub const ADVA_DOCUMENT_VERSION_V0: u32 = 0;

static TEMPORARY_FILE_ORDINAL: AtomicU64 = AtomicU64::new(0);

/// One self-describing research document containing the three persisted output
/// slots.
///
/// The document stores neutral carrier references. It does not install
/// program, proof, or model as a persistent kind, and it does not resolve the
/// referenced witness artifacts by itself.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AdvaDocumentV0 {
    pub schema: String,
    pub version: u32,
    pub output: MechanismOutputV0,
}

impl AdvaDocumentV0 {
    /// Pack three checked output slots into a versioned document.
    ///
    /// # Errors
    ///
    /// Rejects empty artifact coordinates and noncanonical open frontiers.
    pub fn from_output(output: MechanismOutputV0) -> Result<Self, AdvaPersistenceErrorV0> {
        let document = Self {
            schema: ADVA_DOCUMENT_SCHEMA_V0.to_owned(),
            version: ADVA_DOCUMENT_VERSION_V0,
            output,
        };
        document.validate()?;
        Ok(document)
    }

    /// Decode and validate a neutral-carrier document without selecting an
    /// input reading.
    ///
    /// # Errors
    ///
    /// Rejects malformed JSON, unknown fields, unsupported schema versions,
    /// empty artifact coordinates, and noncanonical open frontiers.
    pub fn from_json(source: &str) -> Result<Self, AdvaPersistenceErrorV0> {
        let document: Self = serde_json::from_str(source)?;
        document.validate()?;
        Ok(document)
    }

    /// Encode a validated document deterministically as pretty JSON.
    ///
    /// # Errors
    ///
    /// Rejects an invalid in-memory document or a serialization failure.
    pub fn to_json(&self) -> Result<String, AdvaPersistenceErrorV0> {
        self.validate()?;
        Ok(serde_json::to_string_pretty(self)?)
    }

    /// Re-label the three stored output slots as the three input slots under
    /// one explicit bijection.
    ///
    /// # Errors
    ///
    /// Rejects an invalid document or a route plan that copies, drops, or
    /// reuses a slot.
    pub fn reload(
        &self,
        plan: &ReloadPlanV0,
    ) -> Result<ReloadArtifactV0, AdvaPersistenceErrorV0> {
        self.validate()?;
        let routes = plan.canonical_routes()?;
        let subject = source_for_input(&self.output, &routes, InputLabelV0::Subject)?;
        let method = source_for_input(&self.output, &routes, InputLabelV0::Method)?;
        let object = source_for_input(&self.output, &routes, InputLabelV0::Object)?;
        Ok(ReloadArtifactV0 {
            input: MechanismInputV0 {
                subject,
                method,
                object,
            },
            certificate: ReloadCertificateV0 {
                schema: ADVA_DOCUMENT_SCHEMA_V0.to_owned(),
                version: ADVA_DOCUMENT_VERSION_V0,
                document_digest: self.digest()?,
                routes,
                schema_and_version: CheckStatus::Checked,
                canonical_frontiers: CheckStatus::Checked,
                exact_slot_bijection: CheckStatus::Checked,
            },
        })
    }

    fn validate(&self) -> Result<(), AdvaPersistenceErrorV0> {
        if self.schema != ADVA_DOCUMENT_SCHEMA_V0 || self.version != ADVA_DOCUMENT_VERSION_V0 {
            return Err(AdvaPersistenceErrorV0::UnsupportedDocument {
                schema: self.schema.clone(),
                version: self.version,
            });
        }
        for (label, carrier) in output_slots(&self.output) {
            validate_carrier(label, carrier)?;
        }
        Ok(())
    }

    fn digest(&self) -> Result<String, AdvaPersistenceErrorV0> {
        let canonical = serde_json::to_vec(self)?;
        Ok(format!("blake3:{}", blake3::hash(&canonical).to_hex()))
    }
}

/// One exact relabelling from a stored output slot to a loaded input slot.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CarrierRouteV0 {
    pub from: OutputLabelV0,
    pub to: InputLabelV0,
}

impl CarrierRouteV0 {
    #[must_use]
    pub const fn new(from: OutputLabelV0, to: InputLabelV0) -> Self {
        Self { from, to }
    }
}

/// Three explicit routes used at one reload boundary.
///
/// A valid plan is a bijection: every stored output and every loaded input
/// occurs exactly once. The route order is not semantically significant.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ReloadPlanV0 {
    pub routes: [CarrierRouteV0; 3],
}

impl ReloadPlanV0 {
    /// Construct and validate an output-to-input slot bijection.
    ///
    /// # Errors
    ///
    /// Rejects repeated output slots or repeated input slots.
    pub fn from_routes(
        routes: [CarrierRouteV0; 3],
    ) -> Result<Self, AdvaPersistenceErrorV0> {
        let plan = Self { routes };
        plan.canonical_routes()?;
        Ok(plan)
    }

    fn canonical_routes(
        &self,
    ) -> Result<[CarrierRouteV0; 3], AdvaPersistenceErrorV0> {
        let mut outputs = BTreeSet::new();
        let mut inputs = BTreeSet::new();
        for route in self.routes {
            if !outputs.insert(route.from) {
                return Err(AdvaPersistenceErrorV0::RepeatedOutputRoute(route.from));
            }
            if !inputs.insert(route.to) {
                return Err(AdvaPersistenceErrorV0::RepeatedInputRoute(route.to));
            }
        }
        let mut routes = self.routes;
        routes.sort_by_key(|route| route.to);
        Ok(routes)
    }
}

/// Successful exact relabelling of one loaded document.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ReloadArtifactV0 {
    pub input: MechanismInputV0,
    pub certificate: ReloadCertificateV0,
}

/// Audit record returned only after document and route validation succeeds.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ReloadCertificateV0 {
    pub schema: String,
    pub version: u32,
    pub document_digest: String,
    pub routes: [CarrierRouteV0; 3],
    pub schema_and_version: CheckStatus,
    pub canonical_frontiers: CheckStatus,
    pub exact_slot_bijection: CheckStatus,
}

/// Receipt for one completed atomic file save.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SaveReceiptV0 {
    pub path: PathBuf,
    pub document_digest: String,
    pub bytes_written: u64,
}

/// Validate, encode, and atomically replace one `.adva` research document.
///
/// The temporary file is written in the destination directory and renamed
/// only after its contents have been flushed. No example or initial program is
/// created by this API until a caller supplies output carriers and invokes it.
///
/// # Errors
///
/// Rejects a non-`.adva` path, an invalid output carrier, or an I/O failure.
pub fn save_adva_document_v0(
    path: impl AsRef<Path>,
    output: MechanismOutputV0,
) -> Result<SaveReceiptV0, AdvaPersistenceErrorV0> {
    let path = path.as_ref();
    require_adva_extension(path)?;
    let document = AdvaDocumentV0::from_output(output)?;
    let encoded = format!("{}\n", document.to_json()?);
    write_atomically(path, encoded.as_bytes())?;
    Ok(SaveReceiptV0 {
        path: path.to_path_buf(),
        document_digest: document.digest()?,
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

/// Read and validate one `.adva` document, then apply an explicit three-slot
/// reload plan.
///
/// # Errors
///
/// Rejects a non-`.adva` path, unreadable or malformed content, an unsupported
/// schema, an invalid carrier frontier, or a non-bijective route plan.
pub fn load_adva_document_v0(
    path: impl AsRef<Path>,
    plan: &ReloadPlanV0,
) -> Result<ReloadArtifactV0, AdvaPersistenceErrorV0> {
    let path = path.as_ref();
    require_adva_extension(path)?;
    let source = fs::read_to_string(path).map_err(|source| AdvaPersistenceErrorV0::Io {
        path: path.to_path_buf(),
        source,
    })?;
    AdvaDocumentV0::from_json(&source)?.reload(plan)
}

fn output_slots(output: &MechanismOutputV0) -> [(OutputLabelV0, &NeutralCarrierV0); 3] {
    [
        (OutputLabelV0::History, &output.history),
        (OutputLabelV0::Result, &output.result),
        (OutputLabelV0::Evidence, &output.evidence),
    ]
}

fn validate_carrier(
    label: OutputLabelV0,
    carrier: &NeutralCarrierV0,
) -> Result<(), AdvaPersistenceErrorV0> {
    if carrier.structure.as_str().is_empty() {
        return Err(AdvaPersistenceErrorV0::EmptyArtifactKey(label));
    }
    let canonical =
        OpenFrontierV0::from_sites(carrier.frontier.sites().iter().cloned())?;
    if canonical != carrier.frontier {
        return Err(AdvaPersistenceErrorV0::NonCanonicalFrontier(label));
    }
    Ok(())
}

fn source_for_input(
    output: &MechanismOutputV0,
    routes: &[CarrierRouteV0; 3],
    input: InputLabelV0,
) -> Result<NeutralCarrierV0, AdvaPersistenceErrorV0> {
    let source = routes
        .iter()
        .find_map(|route| (route.to == input).then_some(route.from))
        .ok_or(AdvaPersistenceErrorV0::MissingInputRoute(input))?;
    Ok(match source {
        OutputLabelV0::History => output.history.clone(),
        OutputLabelV0::Result => output.result.clone(),
        OutputLabelV0::Evidence => output.evidence.clone(),
    })
}

fn require_adva_extension(path: &Path) -> Result<(), AdvaPersistenceErrorV0> {
    if path.extension().and_then(|extension| extension.to_str()) != Some(ADVA_FILE_SUFFIX_V0) {
        return Err(AdvaPersistenceErrorV0::InvalidExtension(
            path.to_path_buf(),
        ));
    }
    Ok(())
}

fn write_atomically(path: &Path, bytes: &[u8]) -> Result<(), AdvaPersistenceErrorV0> {
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    let file_name = path
        .file_name()
        .and_then(|name| name.to_str())
        .ok_or_else(|| AdvaPersistenceErrorV0::InvalidFileName(path.to_path_buf()))?;
    let ordinal = TEMPORARY_FILE_ORDINAL.fetch_add(1, Ordering::Relaxed);
    let temporary = parent.join(format!(
        ".{file_name}.tmp-{}-{ordinal}",
        std::process::id()
    ));
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&temporary)
        .map_err(|source| AdvaPersistenceErrorV0::Io {
            path: temporary.clone(),
            source,
        })?;
    if let Err(source) = file.write_all(bytes).and_then(|()| file.sync_all()) {
        drop(file);
        let _ = fs::remove_file(&temporary);
        return Err(AdvaPersistenceErrorV0::Io {
            path: temporary,
            source,
        });
    }
    drop(file);
    if let Err(source) = fs::rename(&temporary, path) {
        let _ = fs::remove_file(&temporary);
        return Err(AdvaPersistenceErrorV0::Io {
            path: path.to_path_buf(),
            source,
        });
    }
    sync_parent(parent)
}

#[cfg(unix)]
fn sync_parent(parent: &Path) -> Result<(), AdvaPersistenceErrorV0> {
    File::open(parent)
        .and_then(|directory| directory.sync_all())
        .map_err(|source| AdvaPersistenceErrorV0::Io {
            path: parent.to_path_buf(),
            source,
        })
}

#[cfg(not(unix))]
fn sync_parent(_parent: &Path) -> Result<(), AdvaPersistenceErrorV0> {
    Ok(())
}

#[derive(Debug, Error)]
pub enum AdvaPersistenceErrorV0 {
    #[error("path must use the .adva suffix: {0:?}")]
    InvalidExtension(PathBuf),
    #[error("path has no usable UTF-8 file name: {0:?}")]
    InvalidFileName(PathBuf),
    #[error("unsupported Adva research document {schema:?} version {version}")]
    UnsupportedDocument { schema: String, version: u32 },
    #[error("stored output slot {0:?} has an empty artifact cache coordinate")]
    EmptyArtifactKey(OutputLabelV0),
    #[error("stored output slot {0:?} has a noncanonical frontier order")]
    NonCanonicalFrontier(OutputLabelV0),
    #[error("reload plan uses output slot {0:?} more than once")]
    RepeatedOutputRoute(OutputLabelV0),
    #[error("reload plan fills input slot {0:?} more than once")]
    RepeatedInputRoute(InputLabelV0),
    #[error("reload plan does not fill input slot {0:?}")]
    MissingInputRoute(InputLabelV0),
    #[error(transparent)]
    Mechanism(#[from] MechanismSyntaxErrorV0),
    #[error("Adva document JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("I/O error at {path:?}: {source}")]
    Io {
        path: PathBuf,
        #[source]
        source: io::Error,
    },
}
