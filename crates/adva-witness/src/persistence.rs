use crate::{
    ADVA_FILE_SUFFIX_V0, DischargeV0, FillAssignmentV0, FillPlanV0, FrontierSiteV0,
    MechanismAdmissionV0, MechanismFormV0, MechanismInputV0, MechanismOutputV0,
    MechanismSyntaxErrorV0, NeutralCarrierV0, OpenFrontierV0,
};
use adva_ir::CheckStatus;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fs::{self, File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use thiserror::Error;

/// Schema identifier for the research-only neutral-carrier document graph.
pub const ADVA_DOCUMENT_SCHEMA_V0: &str = "adva.neutral-carrier-graph.research";

/// Research document version. This is not `adva.ir` version one.
pub const ADVA_DOCUMENT_VERSION_V0: u32 = 0;

static TEMPORARY_FILE_ORDINAL: AtomicU64 = AtomicU64::new(0);

/// Document-local carrier-table coordinate.
///
/// This number is a storage coordinate only. It is not an `adva.ir` source,
/// occurrence, value, or semantic identity.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct CarrierIdV0(pub u32);

impl CarrierIdV0 {
    #[must_use]
    pub const fn new(value: u32) -> Self {
        Self(value)
    }
}

/// Document-local transition-frame coordinate.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(transparent)]
pub struct FrameIdV0(pub u32);

impl FrameIdV0 {
    #[must_use]
    pub const fn new(value: u32) -> Self {
        Self(value)
    }
}

/// One entry in the neutral carrier table.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoredCarrierV0 {
    pub id: CarrierIdV0,
    pub carrier: NeutralCarrierV0,
}

impl StoredCarrierV0 {
    #[must_use]
    pub const fn new(id: CarrierIdV0, carrier: NeutralCarrierV0) -> Self {
        Self { id, carrier }
    }
}

/// The three carrier references read through the fixed input labels.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameInputV0 {
    pub subject: CarrierIdV0,
    pub method: CarrierIdV0,
    pub object: CarrierIdV0,
}

impl FrameInputV0 {
    #[must_use]
    pub const fn new(
        subject: CarrierIdV0,
        method: CarrierIdV0,
        object: CarrierIdV0,
    ) -> Self {
        Self {
            subject,
            method,
            object,
        }
    }

    const fn ids(self) -> [CarrierIdV0; 3] {
        [self.subject, self.method, self.object]
    }
}

/// The three output ports of a transition frame.
///
/// A ready frame has three `None` values. A recorded frame has three carrier
/// references. Partial recording is rejected, so the three labels remain one
/// indivisible boundary. "Recorded" states only that the references were
/// persisted; it does not certify that a mechanism produced them.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FrameOutputV0 {
    pub history: Option<CarrierIdV0>,
    pub result: Option<CarrierIdV0>,
    pub evidence: Option<CarrierIdV0>,
}

impl FrameOutputV0 {
    #[must_use]
    pub const fn ready() -> Self {
        Self {
            history: None,
            result: None,
            evidence: None,
        }
    }

    #[must_use]
    pub const fn recorded(
        history: CarrierIdV0,
        result: CarrierIdV0,
        evidence: CarrierIdV0,
    ) -> Self {
        Self {
            history: Some(history),
            result: Some(result),
            evidence: Some(evidence),
        }
    }

    fn recorded_ids(
        self,
        frame: FrameIdV0,
    ) -> Result<Option<[CarrierIdV0; 3]>, AdvaPersistenceErrorV0> {
        match (self.history, self.result, self.evidence) {
            (None, None, None) => Ok(None),
            (Some(history), Some(result), Some(evidence)) => {
                Ok(Some([history, result, evidence]))
            }
            _ => Err(AdvaPersistenceErrorV0::PartialFrameOutput(frame)),
        }
    }
}

/// One stored learning assignment whose replacement is resolved through the
/// neutral carrier table.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoredFillAssignmentV0 {
    pub target: FrontierSiteV0,
    pub replacement: CarrierIdV0,
    pub evidence: Option<crate::ArtifactKeyV0>,
}

/// A finite, possibly partial learning proposal stored without duplicating
/// its replacement carriers.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoredFillPlanV0 {
    pub assignments: Vec<StoredFillAssignmentV0>,
}

/// Mechanism data placed on a transition edge, never on a neutral carrier.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum FrameMechanismV0 {
    Compute,
    Verify {
        declared_subject: OpenFrontierV0,
        discharges: Vec<DischargeV0>,
    },
    Learn {
        plan: StoredFillPlanV0,
    },
}

/// One three-input/three-output transition frame in a neutral document.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TransitionFrameV0 {
    pub id: FrameIdV0,
    pub input: FrameInputV0,
    pub mechanism: FrameMechanismV0,
    pub output: FrameOutputV0,
}

/// One externally selectable starting frame.
///
/// Names are document-local selectors and allocate no semantic identity.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EntryPointV0 {
    pub name: String,
    pub frame: FrameIdV0,
}

/// A neutral `.adva` document graph.
///
/// Carriers remain neutral vertices. Frames are mechanism-labelled edges, and
/// entry points select which checked edge is unpacked for one step. Every
/// table is stored in canonical order so the document digest is stable.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AdvaDocumentV0 {
    pub schema: String,
    pub version: u32,
    pub carriers: Vec<StoredCarrierV0>,
    pub frames: Vec<TransitionFrameV0>,
    pub entrypoints: Vec<EntryPointV0>,
}

impl AdvaDocumentV0 {
    /// Construct and validate one self-describing research document graph.
    ///
    /// # Errors
    ///
    /// Rejects noncanonical tables, bad references, malformed carrier
    /// frontiers, inadmissible mechanism forms, and missing entry points.
    pub fn new(
        carriers: Vec<StoredCarrierV0>,
        frames: Vec<TransitionFrameV0>,
        entrypoints: Vec<EntryPointV0>,
    ) -> Result<Self, AdvaPersistenceErrorV0> {
        let document = Self {
            schema: ADVA_DOCUMENT_SCHEMA_V0.to_owned(),
            version: ADVA_DOCUMENT_VERSION_V0,
            carriers,
            frames,
            entrypoints,
        };
        document.validate()?;
        Ok(document)
    }

    /// Decode and validate a neutral-carrier graph without selecting an entry.
    ///
    /// # Errors
    ///
    /// Rejects malformed JSON, unknown fields, unsupported versions, and any
    /// invalid graph invariant.
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

    /// Resolve and check one named starting frame.
    ///
    /// # Errors
    ///
    /// Rejects an invalid document, an unknown entry point, or a frame whose
    /// input cannot be admitted by its declared mechanism.
    pub fn load_entrypoint(
        &self,
        entrypoint: &str,
    ) -> Result<LoadedAdvaArtifactV0, AdvaPersistenceErrorV0> {
        let indexes = self.validate()?;
        let entry = self
            .entrypoints
            .iter()
            .find(|entry| entry.name == entrypoint)
            .ok_or_else(|| AdvaPersistenceErrorV0::UnknownEntryPoint(entrypoint.to_owned()))?;
        let frame = indexes
            .frames
            .get(&entry.frame)
            .copied()
            .ok_or(AdvaPersistenceErrorV0::UnknownEntryFrame {
                entrypoint: entry.name.clone(),
                frame: entry.frame,
            })?;
        let transition = resolve_transition(frame, &indexes.carriers)?;
        Ok(LoadedAdvaArtifactV0 {
            transition,
            certificate: AdvaLoadCertificateV0 {
                schema: ADVA_DOCUMENT_SCHEMA_V0.to_owned(),
                version: ADVA_DOCUMENT_VERSION_V0,
                document_digest: self.digest()?,
                entrypoint: entry.name.clone(),
                frame: entry.frame,
                schema_and_version: CheckStatus::Checked,
                canonical_tables: CheckStatus::Checked,
                resolved_references: CheckStatus::Checked,
                mechanism_forms: CheckStatus::Checked,
            },
        })
    }

    fn validate(&self) -> Result<DocumentIndexesV0<'_>, AdvaPersistenceErrorV0> {
        if self.schema != ADVA_DOCUMENT_SCHEMA_V0 || self.version != ADVA_DOCUMENT_VERSION_V0 {
            return Err(AdvaPersistenceErrorV0::UnsupportedDocument {
                schema: self.schema.clone(),
                version: self.version,
            });
        }
        ensure_carriers_canonical(&self.carriers)?;
        ensure_frames_canonical(&self.frames)?;
        ensure_entrypoints_canonical(&self.entrypoints)?;
        if self.entrypoints.is_empty() {
            return Err(AdvaPersistenceErrorV0::MissingEntryPoint);
        }

        let carriers = self
            .carriers
            .iter()
            .map(|stored| (stored.id, &stored.carrier))
            .collect::<BTreeMap<_, _>>();
        let frames = self
            .frames
            .iter()
            .map(|frame| (frame.id, frame))
            .collect::<BTreeMap<_, _>>();

        for stored in &self.carriers {
            validate_carrier(stored.id, &stored.carrier)?;
        }
        for frame in &self.frames {
            resolve_transition(frame, &carriers)?;
        }
        for entry in &self.entrypoints {
            if entry.name.is_empty() {
                return Err(AdvaPersistenceErrorV0::EmptyEntryPointName);
            }
            if !frames.contains_key(&entry.frame) {
                return Err(AdvaPersistenceErrorV0::UnknownEntryFrame {
                    entrypoint: entry.name.clone(),
                    frame: entry.frame,
                });
            }
        }
        Ok(DocumentIndexesV0 { carriers, frames })
    }

    fn digest(&self) -> Result<String, AdvaPersistenceErrorV0> {
        let canonical = serde_json::to_vec(self)?;
        Ok(format!("blake3:{}", blake3::hash(&canonical).to_hex()))
    }
}

struct DocumentIndexesV0<'a> {
    carriers: BTreeMap<CarrierIdV0, &'a NeutralCarrierV0>,
    frames: BTreeMap<FrameIdV0, &'a TransitionFrameV0>,
}

/// Whether a loaded frame is ready or merely has a complete stored output
/// triple. Recording is not an execution-validity judgment.
#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LoadedFrameStateV0 {
    Ready,
    Recorded,
}

/// One selected frame after carrier resolution and mechanism admission.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LoadedTransitionV0 {
    pub frame: FrameIdV0,
    pub form: MechanismFormV0,
    pub admission: MechanismAdmissionV0,
    pub state: LoadedFrameStateV0,
    pub recorded_output: Option<MechanismOutputV0>,
}

/// Successful loading of one named transition together with its audit record.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LoadedAdvaArtifactV0 {
    pub transition: LoadedTransitionV0,
    pub certificate: AdvaLoadCertificateV0,
}

/// Audit record returned only after document, graph, and mechanism checks.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AdvaLoadCertificateV0 {
    pub schema: String,
    pub version: u32,
    pub document_digest: String,
    pub entrypoint: String,
    pub frame: FrameIdV0,
    pub schema_and_version: CheckStatus,
    pub canonical_tables: CheckStatus,
    pub resolved_references: CheckStatus,
    pub mechanism_forms: CheckStatus,
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
/// No example or initial program is created by this API. A caller must supply
/// the complete document graph and explicitly invoke the save operation.
///
/// # Errors
///
/// Rejects a non-`.adva` path, an invalid graph, or an I/O failure.
pub fn save_adva_document_v0(
    path: impl AsRef<Path>,
    document: AdvaDocumentV0,
) -> Result<SaveReceiptV0, AdvaPersistenceErrorV0> {
    let path = path.as_ref();
    require_adva_extension(path)?;
    let encoded = format!("{}\n", document.to_json()?);
    write_atomically(path, encoded.as_bytes())?;
    Ok(SaveReceiptV0 {
        path: path.to_path_buf(),
        document_digest: document.digest()?,
        bytes_written: u64::try_from(encoded.len()).unwrap_or(u64::MAX),
    })
}

/// Read and validate one `.adva` document, then select a named transition.
///
/// # Errors
///
/// Rejects a non-`.adva` path, unreadable or malformed content, an invalid
/// graph, an unknown entry point, or an inadmissible mechanism form.
pub fn load_adva_document_v0(
    path: impl AsRef<Path>,
    entrypoint: &str,
) -> Result<LoadedAdvaArtifactV0, AdvaPersistenceErrorV0> {
    let path = path.as_ref();
    require_adva_extension(path)?;
    let source = fs::read_to_string(path).map_err(|source| AdvaPersistenceErrorV0::Io {
        path: path.to_path_buf(),
        source,
    })?;
    AdvaDocumentV0::from_json(&source)?.load_entrypoint(entrypoint)
}

fn ensure_carriers_canonical(carriers: &[StoredCarrierV0]) -> Result<(), AdvaPersistenceErrorV0> {
    for pair in carriers.windows(2) {
        if pair[0].id >= pair[1].id {
            return Err(AdvaPersistenceErrorV0::NonCanonicalCarrierTable {
                previous: pair[0].id,
                current: pair[1].id,
            });
        }
    }
    Ok(())
}

fn ensure_frames_canonical(frames: &[TransitionFrameV0]) -> Result<(), AdvaPersistenceErrorV0> {
    for pair in frames.windows(2) {
        if pair[0].id >= pair[1].id {
            return Err(AdvaPersistenceErrorV0::NonCanonicalFrameTable {
                previous: pair[0].id,
                current: pair[1].id,
            });
        }
    }
    Ok(())
}

fn ensure_entrypoints_canonical(
    entrypoints: &[EntryPointV0],
) -> Result<(), AdvaPersistenceErrorV0> {
    for pair in entrypoints.windows(2) {
        if pair[0].name >= pair[1].name {
            return Err(AdvaPersistenceErrorV0::NonCanonicalEntryPointTable {
                previous: pair[0].name.clone(),
                current: pair[1].name.clone(),
            });
        }
    }
    Ok(())
}

fn validate_carrier(
    id: CarrierIdV0,
    carrier: &NeutralCarrierV0,
) -> Result<(), AdvaPersistenceErrorV0> {
    if carrier.structure.as_str().is_empty() {
        return Err(AdvaPersistenceErrorV0::EmptyArtifactKey(id));
    }
    let canonical = OpenFrontierV0::from_sites(carrier.frontier.sites().iter().cloned())?;
    if canonical != carrier.frontier {
        return Err(AdvaPersistenceErrorV0::NonCanonicalFrontier(id));
    }
    Ok(())
}

fn resolve_transition(
    frame: &TransitionFrameV0,
    carriers: &BTreeMap<CarrierIdV0, &NeutralCarrierV0>,
) -> Result<LoadedTransitionV0, AdvaPersistenceErrorV0> {
    ensure_distinct_carriers(frame.id, "input", &frame.input.ids())?;
    let input = MechanismInputV0 {
        subject: resolve_carrier(frame.id, "subject", frame.input.subject, carriers)?,
        method: resolve_carrier(frame.id, "method", frame.input.method, carriers)?,
        object: resolve_carrier(frame.id, "object", frame.input.object, carriers)?,
    };
    let form = match &frame.mechanism {
        FrameMechanismV0::Compute => MechanismFormV0::Compute { input },
        FrameMechanismV0::Verify {
            declared_subject,
            discharges,
        } => {
            let canonical =
                OpenFrontierV0::from_sites(declared_subject.sites().iter().cloned())?;
            if canonical != *declared_subject {
                return Err(AdvaPersistenceErrorV0::NonCanonicalDeclaredSubject(
                    frame.id,
                ));
            }
            for discharge in discharges {
                ensure_artifact_key(frame.id, "verification discharge", &discharge.witness)?;
            }
            MechanismFormV0::Verify {
                input,
                declared_subject: declared_subject.clone(),
                discharges: discharges.clone(),
            }
        }
        FrameMechanismV0::Learn { plan } => {
            let assignments = plan
                .assignments
                .iter()
                .map(|assignment| {
                    if let Some(evidence) = &assignment.evidence {
                        ensure_artifact_key(frame.id, "learning evidence", evidence)?;
                    }
                    Ok(FillAssignmentV0 {
                        target: assignment.target.clone(),
                        replacement: resolve_carrier(
                            frame.id,
                            "learning replacement",
                            assignment.replacement,
                            carriers,
                        )?,
                        evidence: assignment.evidence.clone(),
                    })
                })
                .collect::<Result<Vec<_>, AdvaPersistenceErrorV0>>()?;
            MechanismFormV0::Learn {
                input,
                plan: FillPlanV0 { assignments },
            }
        }
    };
    let admission = form.check()?;

    let recorded_output = match frame.output.recorded_ids(frame.id)? {
        None => None,
        Some(ids) => {
            ensure_distinct_carriers(frame.id, "output", &ids)?;
            Some(MechanismOutputV0 {
                history: resolve_carrier(frame.id, "history", ids[0], carriers)?,
                result: resolve_carrier(frame.id, "result", ids[1], carriers)?,
                evidence: resolve_carrier(frame.id, "evidence", ids[2], carriers)?,
            })
        }
    };
    let state = if recorded_output.is_some() {
        LoadedFrameStateV0::Recorded
    } else {
        LoadedFrameStateV0::Ready
    };
    Ok(LoadedTransitionV0 {
        frame: frame.id,
        form,
        admission,
        state,
        recorded_output,
    })
}

fn resolve_carrier(
    frame: FrameIdV0,
    slot: &'static str,
    id: CarrierIdV0,
    carriers: &BTreeMap<CarrierIdV0, &NeutralCarrierV0>,
) -> Result<NeutralCarrierV0, AdvaPersistenceErrorV0> {
    carriers
        .get(&id)
        .map(|carrier| (**carrier).clone())
        .ok_or(AdvaPersistenceErrorV0::UnknownCarrierReference { frame, slot, id })
}

fn ensure_distinct_carriers(
    frame: FrameIdV0,
    boundary: &'static str,
    ids: &[CarrierIdV0; 3],
) -> Result<(), AdvaPersistenceErrorV0> {
    let mut unique = BTreeSet::new();
    for id in ids {
        if !unique.insert(*id) {
            return Err(AdvaPersistenceErrorV0::RepeatedBoundaryCarrier {
                frame,
                boundary,
                id: *id,
            });
        }
    }
    Ok(())
}

fn ensure_artifact_key(
    frame: FrameIdV0,
    field: &'static str,
    key: &crate::ArtifactKeyV0,
) -> Result<(), AdvaPersistenceErrorV0> {
    if key.as_str().is_empty() {
        return Err(AdvaPersistenceErrorV0::EmptyFrameArtifactKey { frame, field });
    }
    Ok(())
}

fn require_adva_extension(path: &Path) -> Result<(), AdvaPersistenceErrorV0> {
    if path.extension().and_then(|extension| extension.to_str()) != Some(ADVA_FILE_SUFFIX_V0) {
        return Err(AdvaPersistenceErrorV0::InvalidExtension(path.to_path_buf()));
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
    let temporary = parent.join(format!(".{file_name}.tmp-{}-{ordinal}", std::process::id()));
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
    #[error("carrier {0:?} has an empty artifact cache coordinate")]
    EmptyArtifactKey(CarrierIdV0),
    #[error("carrier {0:?} has a noncanonical frontier order")]
    NonCanonicalFrontier(CarrierIdV0),
    #[error("carrier table is not strictly ordered: {previous:?} before {current:?}")]
    NonCanonicalCarrierTable {
        previous: CarrierIdV0,
        current: CarrierIdV0,
    },
    #[error("frame table is not strictly ordered: {previous:?} before {current:?}")]
    NonCanonicalFrameTable {
        previous: FrameIdV0,
        current: FrameIdV0,
    },
    #[error("entry-point table is not strictly ordered: {previous:?} before {current:?}")]
    NonCanonicalEntryPointTable { previous: String, current: String },
    #[error("an Adva document must declare at least one entry point")]
    MissingEntryPoint,
    #[error("entry-point names must not be empty")]
    EmptyEntryPointName,
    #[error("unknown Adva entry point {0:?}")]
    UnknownEntryPoint(String),
    #[error("entry point {entrypoint:?} references unknown frame {frame:?}")]
    UnknownEntryFrame {
        entrypoint: String,
        frame: FrameIdV0,
    },
    #[error("frame {frame:?} {slot} slot references unknown carrier {id:?}")]
    UnknownCarrierReference {
        frame: FrameIdV0,
        slot: &'static str,
        id: CarrierIdV0,
    },
    #[error("frame {frame:?} {boundary} boundary uses carrier {id:?} more than once")]
    RepeatedBoundaryCarrier {
        frame: FrameIdV0,
        boundary: &'static str,
        id: CarrierIdV0,
    },
    #[error("frame {0:?} has a partially recorded output boundary")]
    PartialFrameOutput(FrameIdV0),
    #[error("frame {0:?} has a noncanonical declared verification frontier")]
    NonCanonicalDeclaredSubject(FrameIdV0),
    #[error("frame {frame:?} has an empty artifact cache coordinate in {field}")]
    EmptyFrameArtifactKey {
        frame: FrameIdV0,
        field: &'static str,
    },
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
