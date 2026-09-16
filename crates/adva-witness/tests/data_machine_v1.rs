use adva_witness::*;

fn program(code: Vec<MachineInstructionV1>) -> DataMachineProgramV1 {
    DataMachineProgramV1 {
        schema: DATA_MACHINE_PROGRAM_V1.into(),
        name: "generic-v1-boundaries".into(),
        registers: vec![
            MachineRegisterV1 {
                name: "data".into(),
                kind: MachineTypeV1::Data,
            },
            MachineRegisterV1 {
                name: "index".into(),
                kind: MachineTypeV1::Integer,
            },
            MachineRegisterV1 {
                name: "stack".into(),
                kind: MachineTypeV1::Stack,
            },
            MachineRegisterV1 {
                name: "result".into(),
                kind: MachineTypeV1::Data,
            },
        ],
        code,
    }
}
fn integer(value: i64) -> MachineDataV1 {
    MachineDataV1::Integer { value }
}
fn input() -> MachineDataV1 {
    MachineDataV1::Node {
        tag: 7,
        fields: vec![integer(3), integer(9)],
    }
}

#[test]
fn generic_dynamic_fields_pack_and_lengths_preserve_order_without_consumption() {
    use MachineInstructionV1 as I;
    let p = program(vec![
        I::Input { dst: 0 },
        I::Length { src: 0, dst: 1 },
        I::BoxInteger { src: 1, dst: 3 },
        I::Clear { stack: 2 },
        I::Push { stack: 2, src: 3 },
        I::Constant { dst: 1, value: 1 },
        I::FieldDynamic {
            src: 0,
            index: 1,
            dst: 3,
        },
        I::Push { stack: 2, src: 3 },
        I::Pack {
            stack: 2,
            tag: 77,
            dst: 3,
        },
        I::StackLength { stack: 2, dst: 1 },
        I::Return { src: 3 },
    ]);
    let r = run_data_machine_v1(&p, &input(), 20, 20).unwrap();
    assert_eq!(
        r.state.phase,
        MachinePhaseV1::Returned {
            value: MachineDataV1::Node {
                tag: 77,
                fields: vec![integer(2), integer(9)]
            }
        }
    );
    assert_eq!(
        r.state.registers[1],
        Some(MachineValueV1::Integer { value: 2 })
    );
    assert_eq!(
        r.state.registers[2],
        Some(MachineValueV1::Stack {
            items: vec![integer(2), integer(9)]
        })
    );
    verify_data_machine_run_v1(&p, &input(), 20, &r).unwrap();
}

#[test]
fn invalid_dynamic_access_rolls_back_and_charges_the_failing_instruction() {
    use MachineInstructionV1 as I;
    for (index, data, reason) in [
        (-1, input(), "negative field index"),
        (2, input(), "field index outside node"),
        (0, integer(7), "expected node data"),
    ] {
        let p = program(vec![
            I::Input { dst: 0 },
            I::Constant {
                dst: 1,
                value: index,
            },
            I::FieldDynamic {
                src: 0,
                index: 1,
                dst: 0,
            },
            I::Return { src: 0 },
        ]);
        let prefix = run_data_machine_v1(&p, &data, 20, 2).unwrap();
        let r = resume_data_machine_v1(&p, &data, 20, &prefix, 20).unwrap();
        assert_eq!(r.state.registers, prefix.state.registers);
        assert_eq!(r.state.spent, 3);
        assert_eq!(r.state.pc, 2);
        assert_eq!(
            r.state.phase,
            MachinePhaseV1::Rejected {
                reason: reason.into()
            }
        );
    }
}

#[test]
fn new_operations_validate_all_register_types_before_zero_fuel_execution() {
    use MachineInstructionV1 as I;
    for bad in [
        I::Length { src: 1, dst: 1 },
        I::FieldDynamic {
            src: 0,
            index: 0,
            dst: 0,
        },
        I::Pack {
            stack: 0,
            tag: 0,
            dst: 3,
        },
        I::StackLength { stack: 2, dst: 0 },
    ] {
        let p = program(vec![bad, I::Return { src: 0 }]);
        assert!(run_data_machine_v1(&p, &input(), 0, 0).is_err());
    }
}

#[test]
fn expanded_profile_remains_finite_and_distinct_from_v0() {
    use MachineInstructionV1 as I;
    let p = program(vec![I::Input { dst: 0 }, I::Return { src: 0 }]);
    assert_ne!(data_machine_profile_v0(), data_machine_profile_v1());
    assert!(run_data_machine_v1(&p, &input(), 200001, 0).is_err());
    let wide = MachineDataV1::Node {
        tag: 0,
        fields: vec![integer(0); 2049],
    };
    assert!(run_data_machine_v1(&p, &wide, 0, 0).is_err());
    let mut deep = integer(0);
    for _ in 0..48 {
        deep = MachineDataV1::Node {
            tag: 0,
            fields: vec![deep],
        };
    }
    assert!(run_data_machine_v1(&p, &deep, 0, 0).is_err());
    let prefix = run_data_machine_v1(&p, &input(), 1, 1).unwrap();
    let still = resume_data_machine_v1(&p, &input(), 1, &prefix, 10).unwrap();
    assert_eq!(still.status, DataMachineStatusV1::FuelExhausted);
    assert_eq!(still.trace, prefix.trace);
    assert!(resume_data_machine_v1(&p, &input(), 2, &prefix, 10).is_err());
}
