#![forbid(unsafe_code)]

//! Canonical, policy-free CodeGauge contracts shared by providers and consumers.

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

pub const JAVA_JACOCO_V1: &str = "java-jacoco-v1";
pub const CRAP_ORIGINAL_V1: &str = "crap-original-v1";
pub const RESULT_SCHEMA_V1: &str = "codegauge-result/v1";
pub const ERROR_SCHEMA_V1: &str = "codegauge-error/v1";

#[derive(Clone, Copy, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ProfileId {
    JavaJacocoV1,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub enum ResultSchemaId {
    #[serde(rename = "codegauge-result/v1")]
    V1,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub enum ErrorSchemaId {
    #[serde(rename = "codegauge-error/v1")]
    V1,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum AnalysisStatus {
    Complete,
    Partial,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ErrorCode {
    CliError,
    InputNotFound,
    InvalidInput,
    UnsupportedProfile,
    UnsupportedProvider,
    IncompatibleMeasurements,
    InternalError,
}

#[derive(Clone, Debug, Deserialize, Eq, Hash, JsonSchema, PartialEq, Serialize)]
pub struct SymbolIdentity {
    pub id: String,
    pub language: String,
    pub kind: String,
    pub class_vm: String,
    pub name: String,
    pub descriptor: String,
}

impl SymbolIdentity {
    pub fn java_method(
        class_vm: impl Into<String>,
        name: impl Into<String>,
        descriptor: impl Into<String>,
    ) -> Self {
        let class_vm = class_vm.into();
        let name = name.into();
        let descriptor = descriptor.into();
        Self {
            id: format!("java:{class_vm}#{name}{descriptor}"),
            language: "java".into(),
            kind: "method".into(),
            class_vm,
            name,
            descriptor,
        }
    }
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct ComplexityMeasurement {
    pub value: f64,
    pub metric: String,
    pub semantics: String,
    pub provider: String,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct CoverageMeasurement {
    pub ratio: f64,
    pub covered: u64,
    pub missed: u64,
    pub metric: String,
    pub semantics: String,
    pub provider: String,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct DerivedMetrics {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub crap: Option<f64>,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct SymbolResult {
    pub symbol: SymbolIdentity,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub complexity: Option<ComplexityMeasurement>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub coverage: Option<CoverageMeasurement>,
    pub metrics: DerivedMetrics,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct ToolInfo {
    pub name: String,
    pub version: String,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct Analysis {
    pub status: AnalysisStatus,
    pub symbols: u64,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct CrapSummary {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mean: Option<f64>,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct Summary {
    pub crap: CrapSummary,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct InputArtifact {
    pub path: String,
    pub sha256: String,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct Provenance {
    pub provider: String,
    pub semantics: Vec<String>,
    pub input: InputArtifact,
    pub analysis_timestamp: String,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct ResultDocument {
    pub schema: ResultSchemaId,
    pub tool: ToolInfo,
    pub profile: ProfileId,
    pub analysis: Analysis,
    pub summary: Summary,
    pub symbols: Vec<SymbolResult>,
    pub provenance: Provenance,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct ErrorDetails {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub path: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sha256: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct ErrorDocument {
    pub schema: ErrorSchemaId,
    pub tool: ToolInfo,
    pub code: ErrorCode,
    pub message: String,
    pub details: ErrorDetails,
}
