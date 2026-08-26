#![forbid(unsafe_code)]

//! Canonical, policy-free CodeGauge contracts shared by providers and consumers.

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::fmt;
use std::str::FromStr;

pub const JVM_JACOCO_V1: &str = "jvm-jacoco-v1";
pub const TYPESCRIPT_OXC_ISTANBUL_V1: &str = "typescript-oxc-istanbul-v1";
pub const CRAP_ORIGINAL_V1: &str = "crap-original-v1";
pub const RESULT_SCHEMA_V1: &str = "codegauge-result/v1";
pub const ERROR_SCHEMA_V1: &str = "codegauge-error/v1";

#[derive(
    Clone, Copy, Debug, Deserialize, Eq, Hash, JsonSchema, Ord, PartialEq, PartialOrd, Serialize,
)]
#[serde(rename_all = "kebab-case")]
pub enum InputRole {
    Coverage,
    Source,
}

impl InputRole {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Coverage => "coverage",
            Self::Source => "source",
        }
    }
}

impl fmt::Display for InputRole {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(self.as_str())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct InputRoleError {
    role: String,
}

impl InputRoleError {
    pub fn role(&self) -> &str {
        &self.role
    }
}

impl fmt::Display for InputRoleError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "unknown input role: {}", self.role)
    }
}

impl std::error::Error for InputRoleError {}

impl FromStr for InputRole {
    type Err = InputRoleError;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "coverage" => Ok(Self::Coverage),
            "source" => Ok(Self::Source),
            _ => Err(InputRoleError { role: value.into() }),
        }
    }
}

impl TryFrom<&str> for InputRole {
    type Error = InputRoleError;

    fn try_from(value: &str) -> Result<Self, Self::Error> {
        value.parse()
    }
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct AnalysisInput {
    pub role: InputRole,
    pub path: String,
}

#[derive(Clone, Copy, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ProfileId {
    JvmJacocoV1,
    TypescriptOxcIstanbulV1,
}

impl ProfileId {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::JvmJacocoV1 => JVM_JACOCO_V1,
            Self::TypescriptOxcIstanbulV1 => TYPESCRIPT_OXC_ISTANBUL_V1,
        }
    }
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

#[derive(Clone, Debug, Eq, Hash, JsonSchema, PartialEq, Serialize)]
pub struct SymbolIdentity {
    id: String,
    language: String,
    kind: String,
    class_vm: String,
    name: String,
    descriptor: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum SymbolIdentityError {
    InconsistentJavaMethodId { expected: String, actual: String },
}

impl fmt::Display for SymbolIdentityError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InconsistentJavaMethodId { expected, actual } => write!(
                formatter,
                "inconsistent Java method id: expected {expected:?}, got {actual:?}"
            ),
        }
    }
}

impl std::error::Error for SymbolIdentityError {}

impl SymbolIdentity {
    pub fn new(
        id: impl Into<String>,
        language: impl Into<String>,
        kind: impl Into<String>,
        class_vm: impl Into<String>,
        name: impl Into<String>,
        descriptor: impl Into<String>,
    ) -> Result<Self, SymbolIdentityError> {
        let identity = Self {
            id: id.into(),
            language: language.into(),
            kind: kind.into(),
            class_vm: class_vm.into(),
            name: name.into(),
            descriptor: descriptor.into(),
        };
        identity.validate()?;
        Ok(identity)
    }

    pub fn java_method(
        class_vm: impl Into<String>,
        name: impl Into<String>,
        descriptor: impl Into<String>,
    ) -> Self {
        let class_vm = class_vm.into();
        let name = name.into();
        let descriptor = descriptor.into();
        Self::new(
            format!("java:{class_vm}#{name}{descriptor}"),
            "java",
            "method",
            class_vm,
            name,
            descriptor,
        )
        .expect("java_method always creates a canonical identity")
    }

    fn validate(&self) -> Result<(), SymbolIdentityError> {
        if self.language == "java" && self.kind == "method" {
            let expected = format!("java:{}#{}{}", self.class_vm, self.name, self.descriptor);
            if self.id != expected {
                return Err(SymbolIdentityError::InconsistentJavaMethodId {
                    expected,
                    actual: self.id.clone(),
                });
            }
        }
        Ok(())
    }

    pub fn id(&self) -> &str {
        &self.id
    }

    pub fn language(&self) -> &str {
        &self.language
    }

    pub fn kind(&self) -> &str {
        &self.kind
    }

    pub fn class_vm(&self) -> &str {
        &self.class_vm
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn descriptor(&self) -> &str {
        &self.descriptor
    }
}

impl<'de> Deserialize<'de> for SymbolIdentity {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        #[derive(Deserialize)]
        struct SymbolIdentityFields {
            id: String,
            language: String,
            kind: String,
            class_vm: String,
            name: String,
            descriptor: String,
        }

        let fields = SymbolIdentityFields::deserialize(deserializer)?;
        Self::new(
            fields.id,
            fields.language,
            fields.kind,
            fields.class_vm,
            fields.name,
            fields.descriptor,
        )
        .map_err(serde::de::Error::custom)
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

#[derive(Clone, Debug, Eq, Hash, JsonSchema, PartialEq, Serialize)]
#[schemars(transparent)]
pub struct Sha256Digest(#[schemars(pattern(r"^[0-9a-f]{64}$"))] String);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Sha256DigestError;

impl fmt::Display for Sha256DigestError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str("expected a lowercase 64-character hexadecimal SHA-256 digest")
    }
}

impl std::error::Error for Sha256DigestError {}

impl Sha256Digest {
    pub fn new(value: impl Into<String>) -> Result<Self, Sha256DigestError> {
        let value = value.into();
        if value.len() == 64
            && value
                .as_bytes()
                .iter()
                .all(|byte| matches!(*byte, b'0'..=b'9' | b'a'..=b'f'))
        {
            Ok(Self(value))
        } else {
            Err(Sha256DigestError)
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl<'de> Deserialize<'de> for Sha256Digest {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        Self::new(String::deserialize(deserializer)?).map_err(serde::de::Error::custom)
    }
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct InputArtifact {
    pub path: String,
    pub sha256: Sha256Digest,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct NamedInputArtifact {
    pub role: InputRole,
    pub path: String,
    pub sha256: Sha256Digest,
}

#[derive(Clone, Debug, Deserialize, JsonSchema, PartialEq, Serialize)]
pub struct Provenance {
    pub provider: String,
    pub semantics: Vec<String>,
    pub input: InputArtifact,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub inputs: Vec<NamedInputArtifact>,
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
    pub sha256: Option<Sha256Digest>,
}

#[derive(Clone, Debug, Deserialize, Eq, JsonSchema, PartialEq, Serialize)]
pub struct ErrorDocument {
    pub schema: ErrorSchemaId,
    pub tool: ToolInfo,
    pub code: ErrorCode,
    pub message: String,
    pub details: ErrorDetails,
}
