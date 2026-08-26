use codegauge_model::{
    Analysis, AnalysisInput, AnalysisStatus, CRAP_ORIGINAL_V1, ComplexityMeasurement,
    CoverageMeasurement, CrapSummary, DerivedMetrics, ErrorCode, ErrorDetails, ErrorDocument,
    ErrorSchemaId, InputArtifact, InputRole, JVM_JACOCO_V1, ProfileId, Provenance, ResultDocument,
    ResultSchemaId, Sha256Digest, Summary, SymbolIdentity, SymbolResult,
    TYPESCRIPT_OXC_ISTANBUL_V1, ToolInfo,
};
use std::collections::HashSet;
use std::str::FromStr;

fn complexity() -> ComplexityMeasurement {
    ComplexityMeasurement {
        value: 7.0,
        metric: "cyclomatic".into(),
        semantics: "jacoco-cyclomatic".into(),
        provider: "jacoco".into(),
    }
}

fn coverage() -> CoverageMeasurement {
    CoverageMeasurement {
        ratio: 1.0,
        covered: 10,
        missed: 0,
        metric: "instruction".into(),
        semantics: "jacoco-instruction".into(),
        provider: "jacoco".into(),
    }
}

#[test]
fn ids_identity_and_measurements_are_stable() {
    assert_eq!(JVM_JACOCO_V1, "jvm-jacoco-v1");
    assert_eq!(CRAP_ORIGINAL_V1, "crap-original-v1");
    assert_eq!(
        serde_json::to_string(&ProfileId::JvmJacocoV1).unwrap(),
        "\"jvm-jacoco-v1\""
    );
    assert_eq!(TYPESCRIPT_OXC_ISTANBUL_V1, "typescript-oxc-istanbul-v1");
    assert_eq!(
        serde_json::to_string(&ProfileId::TypescriptOxcIstanbulV1).unwrap(),
        "\"typescript-oxc-istanbul-v1\""
    );
    assert!(serde_json::from_str::<ProfileId>("\"java-jacoco-v1\"").is_err());
    assert!(serde_json::from_str::<ProfileId>("\"kotlin-jacoco-v1\"").is_err());
    assert_eq!(
        serde_json::to_string(&ResultSchemaId::V1).unwrap(),
        "\"codegauge-result/v1\""
    );
    assert_eq!(
        serde_json::to_string(&ErrorSchemaId::V1).unwrap(),
        "\"codegauge-error/v1\""
    );
    let first = SymbolIdentity::java_method("com/acme/Order", "run", "()V");
    let second = SymbolIdentity::java_method("com/acme/Order", "run", "(I)V");
    assert_eq!(first.id(), "java:com/acme/Order#run()V");
    assert_eq!((first.language(), first.kind()), ("java", "method"));
    assert_ne!(first.id(), second.id());
    assert_eq!(complexity().semantics, "jacoco-cyclomatic");
    assert_eq!(coverage().ratio, 1.0);
}

#[test]
fn java_method_identity_rejects_inconsistent_construction_and_deserialization() {
    assert!(
        SymbolIdentity::new(
            "java:com/acme/Order#run()V",
            "java",
            "method",
            "com/acme/Order",
            "run",
            "(I)V",
        )
        .is_err()
    );

    let mismatch = r#"{
        "id": "java:com/acme/Order#run()V",
        "language": "java",
        "kind": "method",
        "class_vm": "com/acme/Order",
        "name": "run",
        "descriptor": "(I)V"
    }"#;
    assert!(serde_json::from_str::<SymbolIdentity>(mismatch).is_err());

    let canonical = SymbolIdentity::java_method("com/acme/Order", "run", "(I)V");
    assert_eq!(canonical.id(), "java:com/acme/Order#run(I)V");
}

#[test]
fn sha256_digest_accepts_lowercase_hex_and_rejects_other_strings() {
    let valid = Sha256Digest::new("a".repeat(64)).unwrap();
    assert_eq!(valid.as_str(), "a".repeat(64));
    assert_eq!(
        serde_json::to_string(&valid).unwrap(),
        format!("\"{}\"", "a".repeat(64))
    );

    for invalid in [
        "A".repeat(64),
        "a".repeat(63),
        "a".repeat(65),
        format!("{}g", "a".repeat(63)),
    ] {
        assert!(serde_json::from_str::<Sha256Digest>(&format!("\"{invalid}\"")).is_err());
    }
}

#[test]
fn descriptor_identity_is_a_hashable_join_key() {
    let mut identities = HashSet::new();
    identities.insert(SymbolIdentity::java_method("com/acme/Order", "run", "()V"));
    identities.insert(SymbolIdentity::java_method("com/acme/Order", "run", "(I)V"));

    assert_eq!(identities.len(), 2);
    assert!(identities.contains(&SymbolIdentity::java_method(
        "com/acme/Order",
        "run",
        "(I)V",
    )));
}

#[test]
fn result_and_error_dtos_round_trip_without_policy_statuses() {
    let result = ResultDocument {
        schema: ResultSchemaId::V1,
        tool: ToolInfo {
            name: "codegauge".into(),
            version: "0.3.0".into(), // x-release-please-version
        },
        profile: ProfileId::JvmJacocoV1,
        analysis: Analysis {
            status: AnalysisStatus::Complete,
            symbols: 1,
        },
        summary: Summary {
            crap: CrapSummary {
                max: Some(7.0),
                mean: Some(7.0),
            },
        },
        symbols: vec![SymbolResult {
            symbol: SymbolIdentity::java_method("com/acme/Order", "run", "()V"),
            complexity: Some(complexity()),
            coverage: Some(coverage()),
            metrics: DerivedMetrics { crap: Some(7.0) },
        }],
        provenance: Provenance {
            provider: "jacoco".into(),
            semantics: vec!["jacoco-cyclomatic".into(), "jacoco-instruction".into()],
            input: InputArtifact {
                path: "report.xml".into(),
                sha256: Sha256Digest::new("a".repeat(64)).unwrap(),
            },
            inputs: Vec::new(),
            analysis_timestamp: "2026-08-10T12:00:00Z".into(),
        },
    };
    let encoded = serde_json::to_string(&result).unwrap();
    assert!(!encoded.contains("PASS") && !encoded.contains("FAIL"));
    assert_eq!(
        serde_json::from_str::<ResultDocument>(&encoded).unwrap(),
        result
    );
    let mut invalid_result = serde_json::to_value(&result).unwrap();
    invalid_result["provenance"]["input"]["sha256"] = serde_json::Value::String("A".repeat(64));
    assert!(serde_json::from_value::<ResultDocument>(invalid_result).is_err());
    let error = ErrorDocument {
        schema: ErrorSchemaId::V1,
        tool: ToolInfo {
            name: "codegauge".into(),
            version: "0.3.0".into(), // x-release-please-version
        },
        code: ErrorCode::InvalidInput,
        message: "invalid report".into(),
        details: ErrorDetails {
            path: Some("report.xml".into()),
            sha256: Some(Sha256Digest::new("b".repeat(64)).unwrap()),
        },
    };
    let mut invalid_error = serde_json::to_value(&error).unwrap();
    invalid_error["details"]["sha256"] = serde_json::Value::String("g".repeat(64));
    assert!(serde_json::from_value::<ErrorDocument>(invalid_error).is_err());
    assert_eq!(
        serde_json::from_str::<ErrorDocument>(&serde_json::to_string(&error).unwrap()).unwrap(),
        error
    );
}

#[test]
fn typed_input_roles_are_stable_and_unknown_roles_are_rejected() {
    assert_eq!(
        serde_json::to_string(&InputRole::Coverage).unwrap(),
        "\"coverage\""
    );
    assert_eq!(
        serde_json::to_string(&InputRole::Source).unwrap(),
        "\"source\""
    );
    assert_eq!(
        InputRole::from_str("coverage").unwrap(),
        InputRole::Coverage
    );
    assert_eq!(InputRole::from_str("source").unwrap(), InputRole::Source);

    let error = InputRole::from_str("covrage").unwrap_err();
    assert_eq!(error.to_string(), "unknown input role: covrage");

    let input = AnalysisInput {
        role: InputRole::Coverage,
        path: "reports/jacoco.xml".into(),
    };
    assert_eq!(input.role, InputRole::Coverage);
    assert_eq!(input.path, "reports/jacoco.xml");
}

#[test]
fn role_tagged_provenance_round_trips_without_changing_legacy_json() {
    let input = AnalysisInput {
        role: InputRole::Source,
        path: "src/lib.ts".into(),
    };
    assert_eq!(serde_json::to_value(input).unwrap()["role"], "source");
}
