#![forbid(unsafe_code)]

use codegauge_application::{
    AnalysisError, Analyzer, FsArtifactReader, ProviderRegistry, canonical_error_json,
    canonical_result_json, format_canonical_number, sha256_hex,
};
use codegauge_core::{CrapInput, calculate_crap};
use codegauge_model::{
    AnalysisStatus, ErrorCode, ErrorDocument, ProfileId, ResultDocument, SymbolResult,
};
use codegauge_provider_jacoco::{DiagnosticCode, JacocoProvider, ProviderObservations, collect};
use schemars::schema_for;
use serde_json::Value;
use std::path::Path;

const VALID_PATH: &str = "../../fixtures/jacoco/valid-methods.xml";
const GOLDEN: &str = include_str!("../../../tests/golden/valid-methods.json");

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

fn observed<'a>(report: &'a ProviderObservations, id: &str) -> &'a SymbolResult {
    report
        .symbols
        .iter()
        .find(|symbol| symbol.symbol.id == id)
        .unwrap_or_else(|| panic!("missing symbol {id}"))
}

fn result_symbol<'a>(result: &'a ResultDocument, id: &str) -> &'a SymbolResult {
    result
        .symbols
        .iter()
        .find(|symbol| symbol.symbol.id == id)
        .unwrap_or_else(|| panic!("missing result symbol {id}"))
}

fn has_diagnostic(report: &ProviderObservations, code: DiagnosticCode) -> bool {
    report
        .diagnostics
        .iter()
        .any(|diagnostic| diagnostic.code == code)
}

fn analyzer() -> Analyzer<FsArtifactReader> {
    let mut registry = ProviderRegistry::new();
    registry.register(JacocoProvider::new());
    Analyzer::new(FsArtifactReader, registry)
}

fn valid_result() -> (ResultDocument, Vec<codegauge_application::Diagnostic>) {
    analyzer()
        .analyze_with_diagnostics(ProfileId::JavaJacocoV1, Path::new(VALID_PATH))
        .unwrap()
}

fn score(complexity: f64, coverage: f64) -> f64 {
    calculate_crap(CrapInput {
        cyclomatic_complexity: complexity,
        coverage,
    })
    .unwrap()
    .value()
}

fn mask_timestamp(value: &mut Value) {
    let provenance = value
        .get_mut("provenance")
        .and_then(Value::as_object_mut)
        .expect("result provenance");
    let timestamp = provenance
        .get("analysis_timestamp")
        .and_then(Value::as_str)
        .expect("analysis timestamp");
    assert!(timestamp.contains('T') && timestamp.ends_with('Z'));
    provenance.insert(
        "analysis_timestamp".into(),
        Value::String("<masked>".into()),
    );
}
#[test]
fn valid_vector_covers_edges_overloads_generated_methods_and_core_join() {
    let report = collect(fixture("valid")).unwrap();
    assert_eq!(report.symbols.len(), 10);
    assert_eq!(report.diagnostics.len(), 4);
    assert!(
        report
            .symbols
            .iter()
            .all(|symbol| symbol.metrics.crap.is_none())
    );

    for (id, complexity, coverage, expected) in [
        ("java:com/acme/Order#full()V", 7.0, 1.0, 7.0),
        ("java:com/acme/Order#zero()V", 3.0, 0.0, 12.0),
        ("java:com/acme/Order#partial(I)V", 7.0, 0.7, 8.323),
    ] {
        let symbol = observed(&report, id);
        assert_eq!(symbol.complexity.as_ref().unwrap().value, complexity);
        assert_eq!(symbol.coverage.as_ref().unwrap().ratio, coverage);
        assert_eq!(score(complexity, coverage), expected);
    }
    for name in ["missing", "invalid", "zero-denominator", "optional-only"] {
        assert!(
            !report
                .symbols
                .iter()
                .any(|symbol| symbol.symbol.name == name)
        );
    }
    for id in [
        "java:com/acme/Order#overload()V",
        "java:com/acme/Order#overload(I)V",
    ] {
        assert!(report.symbols.iter().any(|symbol| symbol.symbol.id == id));
    }
    for name in ["<init>", "<clinit>", "synthetic", "bridge", "lambda$run$0"] {
        assert!(
            report
                .symbols
                .iter()
                .any(|symbol| symbol.symbol.name == name)
        );
    }
    for code in [
        DiagnosticCode::MissingRequiredCounter,
        DiagnosticCode::InvalidRequiredCounter,
        DiagnosticCode::ZeroDenominator,
    ] {
        assert!(has_diagnostic(&report, code));
    }

    let (result, _) = valid_result();
    assert_eq!(result.analysis.status, AnalysisStatus::Partial);
    assert_eq!(
        result_symbol(&result, "java:com/acme/Order#full()V")
            .metrics
            .crap,
        Some(score(7.0, 1.0))
    );
    assert!(!canonical_result_json(&result).contains("policy"));
}
#[test]
fn invalid_hostile_and_limit_vectors_are_rejected_or_indeterminate() {
    for name in [
        "duplicate",
        "descriptor",
        "malformed",
        "doctype",
        "entity",
        "encoding",
    ] {
        assert!(collect(fixture(name)).is_err(), "accepted {name}");
    }
    let too_large_count = br#"<report><class name="C"><method name="m" desc="()V"><counter type="COMPLEXITY" missed="1000000001" covered="0"/><counter type="INSTRUCTION" missed="0" covered="1"/></method></class></report>"#;
    let report = collect(too_large_count).unwrap();
    assert!(report.symbols.is_empty());
    assert!(has_diagnostic(
        &report,
        DiagnosticCode::InvalidRequiredCounter
    ));

    let nested = format!(
        "<report>{}</report>",
        (0..128).map(|_| "<x>").collect::<String>() + &(0..128).map(|_| "</x>").collect::<String>()
    );
    assert!(collect(nested.as_bytes()).is_err());
    let classes = (0..100_001)
        .map(|index| format!("<class name=\"C{index}\"/>"))
        .collect::<String>();
    assert!(collect(format!("<report>{classes}</report>").as_bytes()).is_err());
    let methods = (0..100_001)
        .map(|index| format!("<method name=\"m{index}\" desc=\"()V\"/>"))
        .collect::<String>();
    assert!(
        collect(format!("<report><class name=\"C\">{methods}</class></report>").as_bytes())
            .is_err()
    );
    let counters = (0..17)
        .map(|index| format!("<counter type=\"X{index}\" missed=\"0\" covered=\"1\"/>"))
        .collect::<String>();
    assert!(collect(
        format!(
            "<report><class name=\"C\"><method name=\"m\" desc=\"()V\">{counters}</method></class></report>"
        )
        .as_bytes()
    )
    .is_err());
    assert!(collect(&vec![b' '; 64 * 1024 * 1024 + 1]).is_err());
}

#[test]
fn schemas_equal_authoritative_dtos_and_contract_documents_parse() {
    let checked_result: Value = serde_json::from_str(include_str!(
        "../../../schemas/codegauge-result-v1.schema.json"
    ))
    .unwrap();
    let checked_error: Value = serde_json::from_str(include_str!(
        "../../../schemas/codegauge-error-v1.schema.json"
    ))
    .unwrap();
    let mut generated_result = serde_json::to_value(schema_for!(ResultDocument)).unwrap();
    let mut generated_error = serde_json::to_value(schema_for!(ErrorDocument)).unwrap();
    generated_result["$id"] = checked_result["$id"].clone();
    generated_error["$id"] = checked_error["$id"].clone();
    assert_eq!(checked_result["$id"], "codegauge-result/v1");
    assert_eq!(checked_error["$id"], "codegauge-error/v1");
    assert_eq!(checked_result, generated_result);
    assert_eq!(checked_error, generated_error);

    let (result, _) = valid_result();
    let parsed: ResultDocument = serde_json::from_str(&canonical_result_json(&result)).unwrap();
    assert_eq!(parsed.schema, result.schema);
    assert_eq!(parsed.symbols.len(), 10);

    let invalid = analyzer()
        .analyze(
            ProfileId::JavaJacocoV1,
            Path::new("../../fixtures/jacoco/malformed.xml"),
        )
        .unwrap_err();
    assert_eq!(invalid.code(), ErrorCode::InvalidInput);
    assert_eq!(
        invalid.details().path.as_deref(),
        Some("../../fixtures/jacoco/malformed.xml")
    );
    assert_eq!(
        invalid.details().sha256.as_deref(),
        Some(sha256_hex(fixture("malformed")).as_str())
    );
    let parsed: ErrorDocument =
        serde_json::from_str(&canonical_error_json(&invalid.document())).unwrap();
    assert_eq!(parsed, invalid.document());

    let unsupported = AnalysisError::unsupported_profile("unknown-v1");
    assert!(unsupported.details().path.is_none() && unsupported.details().sha256.is_none());
    let unsupported_json = canonical_error_json(&unsupported.document());
    assert!(!unsupported_json.contains("PASS") && !unsupported_json.contains("FAIL"));
}

#[test]
fn golden_order_summary_digest_and_numbers_are_stable_except_timestamp() {
    let (result, _) = valid_result();
    let encoded = canonical_result_json(&result);
    assert!(encoded.ends_with('\n'));
    assert_eq!(result.provenance.input.sha256, sha256_hex(fixture("valid")));
    assert!(
        result
            .symbols
            .windows(2)
            .all(|pair| pair[0].symbol.id.as_bytes() <= pair[1].symbol.id.as_bytes())
    );
    let scores = result
        .symbols
        .iter()
        .map(|symbol| symbol.metrics.crap.unwrap())
        .collect::<Vec<_>>();
    assert_eq!(
        result.summary.crap.max,
        scores.iter().copied().reduce(f64::max)
    );
    assert_eq!(
        result.summary.crap.mean,
        Some(scores.iter().sum::<f64>() / scores.len() as f64)
    );
    for (value, expected) in [
        (0.0000000000005, "0"),
        (0.0000000000015, "0.000000000002"),
        (12.340000000000, "12.34"),
        (-0.0, "0"),
    ] {
        assert_eq!(format_canonical_number(value), expected);
    }

    let mut actual: Value = serde_json::from_str(&encoded).unwrap();
    mask_timestamp(&mut actual);
    assert_eq!(actual, serde_json::from_str::<Value>(GOLDEN).unwrap());
    assert!(!encoded.contains("PASS") && !encoded.contains("FAIL"));
}

#[test]
fn bounded_formula_properties_hold_for_all_test_domain_values() {
    for complexity in (1..=32).map(f64::from) {
        let scores = (0..=64)
            .map(|step| score(complexity, step as f64 / 64.0))
            .collect::<Vec<_>>();
        assert!(scores.windows(2).all(|pair| pair[0] >= pair[1]));
        assert_eq!(score(complexity, 1.0), complexity);
    }
    for coverage in (0..=64).map(|step| step as f64 / 64.0) {
        let scores = (1..=32)
            .map(|complexity| score(complexity as f64, coverage))
            .collect::<Vec<_>>();
        assert!(scores.windows(2).all(|pair| pair[0] <= pair[1]));
    }
}

#[test]
fn repeatability_and_descriptor_identity_have_no_path_range_or_policy_fallback() {
    let (first, _) = valid_result();
    let (second, _) = valid_result();
    assert_eq!(
        first.provenance.input.sha256,
        second.provenance.input.sha256
    );
    let mut first_json: Value = serde_json::from_str(&canonical_result_json(&first)).unwrap();
    let mut second_json: Value = serde_json::from_str(&canonical_result_json(&second)).unwrap();
    mask_timestamp(&mut first_json);
    mask_timestamp(&mut second_json);
    assert_eq!(first_json, second_json);

    let report = collect(fixture("valid")).unwrap();
    let overloads = report
        .symbols
        .iter()
        .filter(|symbol| symbol.symbol.name == "overload")
        .map(|symbol| symbol.symbol.id.as_str())
        .collect::<Vec<_>>();
    assert_eq!(
        overloads,
        [
            "java:com/acme/Order#overload()V",
            "java:com/acme/Order#overload(I)V"
        ]
    );
    for symbol in report.symbols {
        let identity = serde_json::to_value(symbol.symbol).unwrap();
        assert!(identity.get("path").is_none());
        assert!(identity.get("start_line").is_none());
        assert!(identity.get("range").is_none());
    }
}
