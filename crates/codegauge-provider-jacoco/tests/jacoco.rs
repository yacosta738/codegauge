use codegauge_model::SymbolResult;
use codegauge_provider_jacoco::{DiagnosticCode, ProviderObservations, collect};

fn fixture(name: &str) -> &'static [u8] {
    match name {
        "valid" => include_bytes!("../../../fixtures/jacoco/valid-methods.xml"),
        "duplicate" => include_bytes!("../../../fixtures/jacoco/duplicate-identity.xml"),
        "descriptor" => include_bytes!("../../../fixtures/jacoco/invalid-descriptor.xml"),
        "malformed" => include_bytes!("../../../fixtures/jacoco/malformed.xml"),
        "doctype" => include_bytes!("../../../fixtures/jacoco/doctype.xml"),
        "entity" => include_bytes!("../../../fixtures/jacoco/entity.xml"),
        "encoding" => include_bytes!("../../../fixtures/jacoco/unsupported-encoding.xml"),
        _ => panic!("unknown fixture {name}"),
    }
}

fn one<'a>(report: &'a ProviderObservations, id: &str) -> &'a SymbolResult {
    report.symbols.iter().find(|s| s.symbol.id() == id).unwrap()
}

fn has(report: &ProviderObservations, predicate: impl Fn(&SymbolResult) -> bool) -> bool {
    report.symbols.iter().any(predicate)
}

fn diagnostic(report: &ProviderObservations, code: DiagnosticCode) -> bool {
    report.diagnostics.iter().any(|d| d.code == code)
}

fn invalid(input: &[u8]) {
    assert!(collect(input).is_err(), "accepted {} bytes", input.len());
}

#[test]
fn valid_full_zero_partial_and_generated_methods_are_observed_without_crap() {
    let report = collect(fixture("valid")).unwrap();
    assert_eq!(report.symbols.len(), 10);
    for (id, complexity, coverage) in [
        ("java:com/acme/Order#full()V", 7.0, 1.0),
        ("java:com/acme/Order#zero()V", 3.0, 0.0),
        ("java:com/acme/Order#partial(I)V", 7.0, 0.7),
    ] {
        let symbol = one(&report, id);
        assert_eq!(symbol.complexity.as_ref().unwrap().value, complexity);
        assert_eq!(symbol.coverage.as_ref().unwrap().ratio, coverage);
    }
    assert!(report.symbols.iter().all(|s| s.metrics.crap.is_none()));
    for name in ["<init>", "<clinit>", "synthetic", "bridge", "lambda$run$0"] {
        assert!(has(&report, |s| s.symbol.name() == name));
    }
}

#[test]
fn descriptor_overloads_are_distinct_and_aggregate_counters_are_ignored() {
    let report = collect(fixture("valid")).unwrap();
    for id in [
        "java:com/acme/Order#overload()V",
        "java:com/acme/Order#overload(I)V",
    ] {
        assert!(has(&report, |s| s.symbol.id() == id));
    }
    assert!(!has(&report, |s| s.symbol.name() == "aggregate"));
    assert_eq!(report.diagnostics.len(), 4);
}

#[test]
fn missing_invalid_zero_denominator_and_oversized_counts_are_indeterminate() {
    let report = collect(fixture("valid")).unwrap();
    for name in ["missing", "invalid", "zero-denominator", "optional-only"] {
        assert!(!has(&report, |s| s.symbol.name() == name));
    }
    for code in [
        DiagnosticCode::MissingRequiredCounter,
        DiagnosticCode::InvalidRequiredCounter,
        DiagnosticCode::ZeroDenominator,
    ] {
        assert!(diagnostic(&report, code));
    }
    let oversized = collect(br#"<report><class name="C"><method name="m" desc="()V"><counter type="COMPLEXITY" missed="1000000001" covered="0"/><counter type="INSTRUCTION" missed="0" covered="1"/></method></class></report>"#).unwrap();
    assert!(oversized.symbols.is_empty());
    assert!(diagnostic(
        &oversized,
        DiagnosticCode::InvalidRequiredCounter
    ));
}

#[test]
fn duplicate_missing_identity_and_invalid_descriptor_are_fatal() {
    invalid(fixture("duplicate"));
    invalid(fixture("descriptor"));
    let inputs: &[&[u8]] = &[
        b"<report><class name=\"C\"><method desc=\"()V\"/></class></report>",
        b"<report><class name=\"C\"><method name=\"m\"/></class></report>",
        b"<report><class><method name=\"m\" desc=\"()V\"/></class></report>",
    ];
    for input in inputs {
        invalid(input);
    }
}

#[test]
fn descriptor_parameter_slots_enforce_the_jvm_limit() {
    let too_many_parameters = format!("{}D", "J".repeat(127));
    let too_many = format!(
        "<report><class name=\"C\"><method name=\"m\" desc=\"({too_many_parameters})V\"/></class></report>"
    );
    invalid(too_many.as_bytes());

    let boundary_parameters = format!("{}DI", "J".repeat(126));
    let boundary = format!(
        "<report><class name=\"C\"><method name=\"m\" desc=\"({boundary_parameters})V\"/></class></report>"
    );
    assert!(collect(boundary.as_bytes()).is_ok());
}

#[test]
fn malformed_hostile_encoding_bom_and_limits_follow_the_boundary() {
    for name in ["malformed", "doctype", "entity", "encoding"] {
        invalid(fixture(name));
    }
    let mut bom = vec![0xef, 0xbb, 0xbf];
    bom.extend_from_slice(fixture("valid"));
    assert_eq!(collect(&bom).unwrap().symbols.len(), 10);

    let groups = "<group>".repeat(129);
    let closing_groups = "</group>".repeat(129);
    invalid(format!("<report>{groups}{closing_groups}</report>").as_bytes());
    let classes = (0..100_001)
        .map(|i| format!("<class name=\"C{i}\"/>"))
        .collect::<String>();
    invalid(format!("<report>{classes}</report>").as_bytes());
    let methods = (0..100_001)
        .map(|i| format!("<method name=\"m{i}\" desc=\"()V\"/>"))
        .collect::<String>();
    invalid(format!("<report><class name=\"C\">{methods}</class></report>").as_bytes());
    let counters = (0..17)
        .map(|i| format!("<counter type=\"X{i}\" missed=\"0\" covered=\"1\"/>"))
        .collect::<String>();
    invalid(format!("<report><class name=\"C\"><method name=\"m\" desc=\"()V\">{counters}</method></class></report>").as_bytes());
    invalid(&vec![b' '; 64 * 1024 * 1024 + 1]);
}

#[test]
fn raw_invalid_utf8_in_comment_and_processing_instruction_is_rejected() {
    let suffix = br#"<class name="C"><method name="m" desc="()V"><counter type="COMPLEXITY" missed="0" covered="1"/><counter type="INSTRUCTION" missed="0" covered="1"/></method></class></report>"#;

    let mut comment = b"<report><!--".to_vec();
    comment.push(0xff);
    comment.extend_from_slice(b"-->");
    comment.extend_from_slice(suffix);
    invalid(&comment);

    let mut processing_instruction = b"<report><?codegauge ".to_vec();
    processing_instruction.push(0xff);
    processing_instruction.extend_from_slice(b"?>");
    processing_instruction.extend_from_slice(suffix);
    invalid(&processing_instruction);
}

#[test]
fn unknown_wrappers_and_incompatible_jacoco_parents_are_rejected() {
    let method = br#"<class name="C"><method name="m" desc="()V"><counter type="COMPLEXITY" missed="0" covered="1"/><counter type="INSTRUCTION" missed="0" covered="1"/></method></class>"#;
    let mut unknown_wrapper = b"<report><unknown>".to_vec();
    unknown_wrapper.extend_from_slice(method);
    unknown_wrapper.extend_from_slice(b"</unknown></report>");
    invalid(&unknown_wrapper);
    invalid(b"<report><class name=\"C\"><package/></class></report>");
}

#[test]
fn predefined_attribute_entities_keep_canonical_method_identity() {
    let report = collect(
        br#"<report><class name="com/acme/&lt;Order&gt;"><method name="run" desc="()V"><counter type="COMPLEXITY" missed="0" covered="1"/><counter type="INSTRUCTION" missed="0" covered="1"/></method></class></report>"#,
    )
    .unwrap();

    assert_eq!(report.symbols.len(), 1);
    assert_eq!(
        report.symbols[0].symbol.id(),
        "java:com/acme/<Order>#run()V"
    );
}
