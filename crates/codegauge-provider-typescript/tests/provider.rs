use codegauge_application::{Artifact, CollectionRequest, InputSet, MetricProvider, sha256_hex};
use codegauge_model::{AnalysisInput, InputRole, ProfileId};
use codegauge_provider_typescript::TypescriptProvider;
use serde_json::json;

#[test]
fn provider_descriptor_and_collection_emit_typescript_measurements() {
    let source = "function add(value: number) {\n    return value + 1;\n}\n";
    let coverage = json!({
        "path": "src/add.ts",
        "statementMap": {
            "0": {"start": {"line": 2, "column": 4}, "end": {"line": 2, "column": 21}}
        },
        "s": {"0": 1}
    });
    let coverage_bytes = serde_json::to_vec(&coverage).unwrap();
    let inputs = InputSet::from_artifacts(vec![
        (
            AnalysisInput {
                role: InputRole::Coverage,
                path: "coverage.json".into(),
            },
            Artifact {
                path: "coverage.json".into(),
                sha256: sha256_hex(&coverage_bytes),
                bytes: coverage_bytes,
            },
        ),
        (
            AnalysisInput {
                role: InputRole::Source,
                path: "src/add.ts".into(),
            },
            Artifact {
                path: "src/add.ts".into(),
                sha256: sha256_hex(source.as_bytes()),
                bytes: source.as_bytes().to_vec(),
            },
        ),
    ])
    .unwrap();

    let provider = TypescriptProvider::new();
    let descriptor = <TypescriptProvider as MetricProvider>::descriptor(&provider);
    assert_eq!(descriptor.profile, ProfileId::TypescriptOxcIstanbulV1);
    assert_eq!(descriptor.provider, "typescript-oxc-istanbul");
    assert_eq!(descriptor.required_inputs.len(), 2);
    let observations = provider
        .collect(CollectionRequest::new(&inputs))
        .expect("valid TypeScript Istanbul evidence");

    assert_eq!(observations.symbols.len(), 1);
    let symbol = &observations.symbols[0];
    assert_eq!(symbol.symbol.language(), "typescript");
    assert_eq!(symbol.complexity.as_ref().unwrap().value, 1.0);
    assert_eq!(symbol.coverage.as_ref().unwrap().ratio, 1.0);
}
