// Out-of-tree probe: does relation.rs accept a braid cell whose right word is NOT bab?
use adva_witness::{ArtifactKeyV0, RelationCellV0, RelationFillingV0, RelationGeneratorV0,
                   RelationOrientationV0, RelationPathV0, RelationProfileV0};

fn generator(name: &str) -> RelationGeneratorV0 { RelationGeneratorV0::new(name).unwrap() }
fn path(names: &[&str]) -> RelationPathV0 {
    RelationPathV0::new(names.iter().copied().map(generator)).unwrap()
}
fn key(s: &str) -> ArtifactKeyV0 { ArtifactKeyV0::cache_label(s).unwrap() }

fn main() {
    let cases: [(&str, [&str; 3], [&str; 3]); 3] = [
        ("aba vs bab (the declared word)", ["s1", "s2", "s1"], ["s2", "s1", "s2"]),
        ("aba vs ba-b3 (third label differs)", ["s1", "s2", "s1"], ["s2", "s1", "s3"]),
        ("aba vs ba-a (third label is a)", ["s1", "s2", "s1"], ["s2", "s1", "s1"]),
    ];
    for (label, left, right) in cases {
        let cell = RelationCellV0::new(
            RelationProfileV0::braid_m6(),
            path(&left),
            path(&right),
            RelationFillingV0::Filled {
                orientation: RelationOrientationV0::RightToLeft,
                witness: key("braid-witness"),
                retained_residual: None,
            },
        );
        match cell {
            Ok(c) => match c.check() {
                Ok(f) => println!("ACCEPTED  {label}: boundary_occurrences={}", f.boundary_occurrences),
                Err(e) => println!("REJECTED  {label}: {e}"),
            },
            Err(e) => println!("REJECTED at new() {label}: {e:?}"),
        }
    }
}
