use adva_witness::*;
use serde_json::json;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

static NEXT: AtomicU64 = AtomicU64::new(0);

struct TemporaryDirectory(PathBuf);

impl TemporaryDirectory {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!(
            "adva-library-epoch-test-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
    fn path(&self) -> &Path {
        &self.0
    }
}

impl Drop for TemporaryDirectory {
    fn drop(&mut self) {
        // Only this test's newly created, flat directory and generated files.
        for entry in fs::read_dir(&self.0).unwrap() {
            fs::remove_file(entry.unwrap().path()).unwrap();
        }
        fs::remove_dir(&self.0).unwrap();
    }
}

fn budget() -> LibraryBudgetV0 {
    LibraryBudgetV0::new(50_000).unwrap()
}

fn origin() -> LibraryOriginV0 {
    LibraryOriginV0 {
        artifact_blake3: "a".repeat(64),
        case: "synthetic-unit-fixture".into(),
        prior_checker: "test-v0".into(),
        observation_authority: "supplied-calibration-assumptions-not-world-measurements".into(),
    }
}

fn input() -> LibraryInputV0 {
    let x = ExactExprV0::variable("x");
    LibraryInputV0 {
        catalogue: vec![
            x.clone(),
            ExactExprV0::product(ExactExprV0::constant(2), x.clone()),
            ExactExprV0::sum(x.clone(), x.clone()),
            ExactExprV0::product(x.clone(), x),
        ],
        rounds: vec![
            LibraryRoundV0::Observe { input: 0, value: 0 },
            LibraryRoundV0::Revisit,
            LibraryRoundV0::Revisit,
            LibraryRoundV0::Revisit,
            LibraryRoundV0::Observe { input: 1, value: 2 },
        ],
    }
}

fn proposal() -> ExactExprV0 {
    let x = ExactExprV0::variable("x");
    ExactExprV0::product(ExactExprV0::constant(2), ExactExprV0::product(x.clone(), x))
}

fn seed(directory: &Path, ledger: &mut LibraryBudgetV0) -> CheckedLibraryV0 {
    let base = bootstrap_library_v0(origin(), input(), ledger).unwrap();
    publish_library_v0(directory, &base, ledger).unwrap();
    load_library_v0(directory, 0, ledger).unwrap()
}

#[test]
fn publication_reload_rebuilds_existing_native_witness_and_retains_zero_guards() {
    let dir = TemporaryDirectory::new();
    let mut ledger = budget();
    let loaded = seed(dir.path(), &mut ledger);
    assert_eq!(loaded.snapshot().analysis.terminal().active, [1, 2]);
    assert_eq!(loaded.snapshot().words.len(), 1);
    let word = &loaded.snapshot().words[0];
    assert!(matches!(
        word.nodes[0].proof,
        WitnessProofV0::ArithmeticTransition { .. }
    ));
    assert!(matches!(word.nodes[1].proof, WitnessProofV0::Seal { .. }));
    assert_eq!(word.nodes[1].summary.nonzero_obligations.len(), 2);
    let reuse = reuse_library_word_v0(&loaded, 0, 2, &mut ledger).unwrap();
    assert_eq!(reuse.guarded_values, ["4", "4"]);
    assert!(
        reuse_library_word_v0(&loaded, 0, 0, &mut ledger)
            .unwrap_err()
            .to_string()
            .contains("zero")
    );
    assert!(reuse_library_word_v0(&loaded, 1, 2, &mut ledger).is_err());
}

#[test]
fn next_epoch_opens_then_closes_without_changing_old_bytes_or_word() {
    let dir = TemporaryDirectory::new();
    let mut ledger = budget();
    let old = seed(dir.path(), &mut ledger);
    let path = library_snapshot_path_v0(dir.path(), 0).unwrap();
    let old_bytes = fs::read(&path).unwrap();
    let mut expanded = old.snapshot().input.clone();
    expanded.catalogue.push(proposal());
    let open = analyze_library_input_v0(&expanded, &mut ledger).unwrap();
    assert_eq!(open.terminal().active, [1, 2, 4]);
    assert_eq!(open.terminal().status, LibraryStatusV0::Open);
    let next = advance_library_v0(
        &old,
        Some(proposal()),
        LibraryRoundV0::Observe { input: 2, value: 4 },
        &mut ledger,
    )
    .unwrap();
    assert_eq!(next.snapshot().input.catalogue.len(), 5);
    assert_eq!(next.snapshot().input.rounds.len(), 6);
    assert_eq!(next.snapshot().analysis.terminal().active, [1, 2]);
    assert_eq!(next.snapshot().words, old.snapshot().words);
    let refutation = next
        .snapshot()
        .analysis
        .comparisons
        .iter()
        .find(|r| r.candidate == 4 && r.input == 2)
        .unwrap();
    assert_eq!(refutation.predicted, "8");
    assert_eq!(refutation.expected, 4);
    assert!(!refutation.agrees);
    publish_library_v0(dir.path(), &next, &mut ledger).unwrap();
    let fresh_load = load_library_v0(dir.path(), 1, &mut ledger).unwrap();
    assert_eq!(fresh_load.snapshot(), next.snapshot());
    assert_eq!(
        fresh_load.snapshot().parent.as_ref().unwrap().digest,
        old.digest()
    );
    assert_eq!(fs::read(path).unwrap(), old_bytes);
    assert!(!dir.path().join("epoch-0001.pending").exists());
}

#[test]
fn open_and_model_gap_proposals_cannot_be_published() {
    let dir = TemporaryDirectory::new();
    let mut ledger = budget();
    let old = seed(dir.path(), &mut ledger);
    assert!(
        advance_library_v0(&old, Some(proposal()), LibraryRoundV0::Revisit, &mut ledger).is_err()
    );
    let mut gap = old.snapshot().input.clone();
    gap.rounds
        .push(LibraryRoundV0::Observe { input: 2, value: 7 });
    assert_eq!(
        analyze_library_input_v0(&gap, &mut ledger)
            .unwrap()
            .terminal()
            .status,
        LibraryStatusV0::ModelGap
    );
    assert!(
        advance_library_v0(
            &old,
            Some(proposal()),
            LibraryRoundV0::Observe { input: 2, value: 7 },
            &mut ledger
        )
        .is_err()
    );
    assert!(!library_snapshot_path_v0(dir.path(), 1).unwrap().exists());
    assert_eq!(
        load_library_v0(dir.path(), 0, &mut ledger)
            .unwrap()
            .digest(),
        old.digest()
    );
}

#[test]
fn tampered_inputs_readings_witnesses_and_method_fail_native_reload() {
    let dir = TemporaryDirectory::new();
    let mut ledger = budget();
    let old = seed(dir.path(), &mut ledger);
    let path = library_snapshot_path_v0(dir.path(), 0).unwrap();
    for mutation in 0..8 {
        let mut forged = serde_json::to_value(old.snapshot()).unwrap();
        match mutation {
            0 => forged["analysis"]["readings"][5]["features"][0] = json!("forged"),
            1 => forged["input"]["rounds"][4]["Observe"]["value"] = json!(7),
            2 => forged["words"][0]["nodes"][1]["key"] = json!("not-the-native-key"),
            3 => forged["words"][0]["nodes"][1]["summary"]["nonzero_obligations"] = json!([]),
            4 => forged["checker_revision"] = json!("changed"),
            5 => forged["analysis"]["readings"][5]["active"] = json!([1]),
            6 => forged["input"]["catalogue"][0] = json!({"kind":"variable","name":"y"}),
            _ => {
                forged["parent"] =
                    json!({"epoch": 0, "digest": "a".repeat(64), "path": "../../outside"})
            }
        }
        fs::write(&path, serde_json::to_vec(&forged).unwrap()).unwrap();
        assert!(
            load_library_v0(dir.path(), 0, &mut ledger).is_err(),
            "mutation {mutation}"
        );
    }
}

#[test]
fn stale_parent_and_deleted_prefix_are_refused() {
    let dir = TemporaryDirectory::new();
    let mut ledger = budget();
    let old = seed(dir.path(), &mut ledger);
    let next = advance_library_v0(
        &old,
        Some(proposal()),
        LibraryRoundV0::Observe { input: 2, value: 4 },
        &mut ledger,
    )
    .unwrap();
    let path = library_snapshot_path_v0(dir.path(), 1).unwrap();
    for mutation in 0..3 {
        let mut forged = next.snapshot().clone();
        match mutation {
            0 => forged.parent.as_mut().unwrap().digest = "0".repeat(64),
            1 => forged.input.rounds[0] = LibraryRoundV0::Revisit,
            _ => {
                forged.input.catalogue.swap(0, 1);
            }
        }
        fs::write(&path, serde_json::to_vec(&forged).unwrap()).unwrap();
        assert!(load_library_v0(dir.path(), 1, &mut ledger).is_err());
    }
    fs::write(&path, serde_json::to_vec(next.snapshot()).unwrap()).unwrap();
    let mut changed_origin = origin();
    changed_origin.case = "another-valid-root".into();
    let other = bootstrap_library_v0(changed_origin, input(), &mut ledger).unwrap();
    fs::write(
        library_snapshot_path_v0(dir.path(), 0).unwrap(),
        serde_json::to_vec(other.snapshot()).unwrap(),
    )
    .unwrap();
    assert!(load_library_v0(dir.path(), 1, &mut ledger).is_err());
}

#[test]
fn no_clobber_and_partial_files_do_not_become_valid_snapshots() {
    let dir = TemporaryDirectory::new();
    let mut ledger = budget();
    let old = seed(dir.path(), &mut ledger);
    let path = library_snapshot_path_v0(dir.path(), 0).unwrap();
    let bytes = fs::read(&path).unwrap();
    assert!(publish_library_v0(dir.path(), &old, &mut ledger).is_err());
    assert_eq!(fs::read(&path).unwrap(), bytes);
    fs::write(
        library_snapshot_path_v0(dir.path(), 1).unwrap(),
        b"{\"schema\":",
    )
    .unwrap();
    assert!(load_library_v0(dir.path(), 1, &mut ledger).is_err());
    assert!(library_snapshot_path_v0(dir.path(), 4).is_err());
}

#[test]
fn exhausted_shared_account_never_grants_a_second_run_or_write() {
    let dir = TemporaryDirectory::new();
    let old = bootstrap_library_v0(origin(), input(), &mut budget()).unwrap();
    let mut zero = LibraryBudgetV0::new(0).unwrap();
    assert!(matches!(
        publish_library_v0(dir.path(), &old, &mut zero),
        Err(LibraryCheckpointErrorV0::Unknown)
    ));
    assert_eq!(fs::read_dir(dir.path()).unwrap().count(), 0);
    let mut partial = LibraryBudgetV0::new(7).unwrap();
    assert!(matches!(
        bootstrap_library_v0(origin(), input(), &mut partial),
        Err(LibraryCheckpointErrorV0::Unknown)
    ));
    assert_eq!(partial.spent(), 7);
    assert!(matches!(
        bootstrap_library_v0(origin(), input(), &mut partial),
        Err(LibraryCheckpointErrorV0::Unknown)
    ));
    assert_eq!(partial.spent(), 7);
}

#[test]
fn file_expression_and_observation_caps_precede_admission() {
    let dir = TemporaryDirectory::new();
    let path = dir.path().join("large.json");
    fs::write(&path, vec![b' '; 1_048_577]).unwrap();
    assert!(read_library_bytes_v0(&path, &mut budget()).is_err());
    for mutation in 0..6 {
        let mut proposed = input();
        match mutation {
            0 => proposed.catalogue = vec![ExactExprV0::variable("x"); 9],
            1 => proposed.catalogue[0] = ExactExprV0::constant(17),
            2 => proposed.rounds = vec![LibraryRoundV0::Revisit; 17],
            3 => proposed.rounds[0] = LibraryRoundV0::Observe { input: 9, value: 0 },
            4 => {
                proposed.rounds[0] = LibraryRoundV0::Observe {
                    input: 0,
                    value: 1_000_001,
                }
            }
            _ => {
                for _ in 0..9 {
                    proposed.catalogue[0] =
                        ExactExprV0::sum(proposed.catalogue[0].clone(), ExactExprV0::variable("x"));
                }
            }
        }
        assert!(analyze_library_input_v0(&proposed, &mut budget()).is_err());
    }
}

#[cfg(unix)]
#[test]
fn serialized_parent_cannot_redirect_loader_and_symlink_inputs_are_refused() {
    let dir = TemporaryDirectory::new();
    let target = dir.path().join("target.json");
    fs::write(&target, b"{}").unwrap();
    let path = library_snapshot_path_v0(dir.path(), 0).unwrap();
    std::os::unix::fs::symlink(&target, &path).unwrap();
    assert!(read_library_bytes_v0(&path, &mut budget()).is_err());
}
