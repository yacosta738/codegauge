use codegauge_model::{ErrorDocument, ResultDocument};
use schemars::schema_for;
use serde_json::Value;

#[test]
fn checked_in_schemas_match_authoritative_dtos() {
    let result: Value = serde_json::from_str(include_str!(
        "../../../schemas/codegauge-result-v1.schema.json"
    ))
    .unwrap();
    let error: Value = serde_json::from_str(include_str!(
        "../../../schemas/codegauge-error-v1.schema.json"
    ))
    .unwrap();
    assert_eq!(result["$id"], "codegauge-result/v1");
    assert_eq!(error["$id"], "codegauge-error/v1");
    let mut generated_result = serde_json::to_value(schema_for!(ResultDocument)).unwrap();
    let mut generated_error = serde_json::to_value(schema_for!(ErrorDocument)).unwrap();
    generated_result["$id"] = result["$id"].clone();
    generated_error["$id"] = error["$id"].clone();
    assert_eq!(result, generated_result);
    assert_eq!(error, generated_error);
}
