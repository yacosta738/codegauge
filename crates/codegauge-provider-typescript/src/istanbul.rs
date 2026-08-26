use crate::callable::normalize_path;
use serde_json::{Map, Value};
use std::{collections::BTreeSet, error::Error, fmt, path::Path};

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct IstanbulPosition {
    pub line: u32,
    pub column: u32,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct IstanbulLocation {
    pub start: IstanbulPosition,
    pub end: IstanbulPosition,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct IstanbulStatement {
    pub id: String,
    pub location: IstanbulLocation,
    pub count: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct IstanbulFileCoverage {
    pub path: String,
    pub statements: Vec<IstanbulStatement>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum IstanbulError {
    InvalidJson(String),
    InvalidRoot,
    UnsupportedFormat,
    EmptyBundle,
    MissingField { field: String },
    InvalidField { field: String },
    MissingStatementCount { id: String },
    ExtraStatementCount { id: String },
    InvalidPosition { id: String, field: String },
    InvalidSpan { id: String },
    DuplicateStatementSpan { id: String },
    PathKeyMismatch { key: String, path: String },
    DuplicatePath { path: String },
}

impl fmt::Display for IstanbulError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidJson(message) => write!(formatter, "invalid Istanbul JSON: {message}"),
            Self::InvalidRoot => write!(formatter, "Istanbul coverage root must be an object"),
            Self::UnsupportedFormat => write!(formatter, "unsupported raw V8 coverage format"),
            Self::EmptyBundle => write!(formatter, "Istanbul coverage bundle is empty"),
            Self::MissingField { field } => write!(formatter, "missing Istanbul field: {field}"),
            Self::InvalidField { field } => write!(formatter, "invalid Istanbul field: {field}"),
            Self::MissingStatementCount { id } => {
                write!(formatter, "missing Istanbul statement count: {id}")
            }
            Self::ExtraStatementCount { id } => {
                write!(formatter, "Istanbul count has no statement map entry: {id}")
            }
            Self::InvalidPosition { id, field } => {
                write!(
                    formatter,
                    "invalid Istanbul position for statement {id}: {field}"
                )
            }
            Self::InvalidSpan { id } => write!(formatter, "invalid Istanbul span: {id}"),
            Self::DuplicateStatementSpan { id } => {
                write!(formatter, "duplicate Istanbul statement span: {id}")
            }
            Self::PathKeyMismatch { key, path } => {
                write!(
                    formatter,
                    "Istanbul path key does not match path: {key} != {path}"
                )
            }
            Self::DuplicatePath { path } => write!(formatter, "duplicate Istanbul path: {path}"),
        }
    }
}

impl Error for IstanbulError {}

/// Parse either one Istanbul `FileCoverage` object or a `coverage-final.json` file map.
pub fn parse_coverage(input: &[u8]) -> Result<Vec<IstanbulFileCoverage>, IstanbulError> {
    let value: Value = serde_json::from_slice(input)
        .map_err(|error| IstanbulError::InvalidJson(error.to_string()))?;
    let root = value.as_object().ok_or(IstanbulError::InvalidRoot)?;

    if is_raw_v8(root) {
        return Err(IstanbulError::UnsupportedFormat);
    }

    if has_file_coverage_fields(root) {
        return Ok(vec![parse_file_coverage(root, None)?]);
    }

    if root.is_empty() {
        return Err(IstanbulError::EmptyBundle);
    }

    let mut files = Vec::with_capacity(root.len());
    let mut paths = BTreeSet::new();
    for (key, value) in root {
        let object = value
            .as_object()
            .ok_or_else(|| IstanbulError::InvalidField { field: key.clone() })?;
        let file = parse_file_coverage(object, Some(key))?;
        if !paths.insert(file.path.clone()) {
            return Err(IstanbulError::DuplicatePath { path: file.path });
        }
        files.push(file);
    }
    files.sort_by(|left, right| left.path.cmp(&right.path));
    Ok(files)
}

fn parse_file_coverage(
    object: &Map<String, Value>,
    bundle_key: Option<&str>,
) -> Result<IstanbulFileCoverage, IstanbulError> {
    let raw_path =
        object
            .get("path")
            .and_then(Value::as_str)
            .ok_or_else(|| IstanbulError::MissingField {
                field: "path".into(),
            })?;
    if raw_path.is_empty() {
        return Err(IstanbulError::InvalidField {
            field: "path".into(),
        });
    }
    let path = normalize_path(Path::new(raw_path));
    if let Some(key) = bundle_key {
        let normalized_key = normalize_path(Path::new(key));
        if normalized_key != path {
            return Err(IstanbulError::PathKeyMismatch {
                key: normalized_key,
                path,
            });
        }
    }

    let statement_map = object
        .get("statementMap")
        .and_then(Value::as_object)
        .ok_or_else(|| IstanbulError::MissingField {
            field: "statementMap".into(),
        })?;
    let counts = object
        .get("s")
        .and_then(Value::as_object)
        .ok_or_else(|| IstanbulError::MissingField { field: "s".into() })?;

    let mut statements = Vec::with_capacity(statement_map.len());
    let mut locations = BTreeSet::new();
    for (id, location) in statement_map {
        let location = parse_location(id, location)?;
        if !locations.insert(location) {
            return Err(IstanbulError::DuplicateStatementSpan { id: id.clone() });
        }
        let count = counts
            .get(id)
            .ok_or_else(|| IstanbulError::MissingStatementCount { id: id.clone() })?;
        let count = count.as_u64().ok_or_else(|| IstanbulError::InvalidField {
            field: format!("s.{id}"),
        })?;
        statements.push(IstanbulStatement {
            id: id.clone(),
            location,
            count,
        });
    }
    for id in counts.keys() {
        if !statement_map.contains_key(id) {
            return Err(IstanbulError::ExtraStatementCount { id: id.clone() });
        }
    }
    statements.sort_by(|left, right| {
        left.location
            .cmp(&right.location)
            .then_with(|| left.id.cmp(&right.id))
    });
    Ok(IstanbulFileCoverage { path, statements })
}

fn parse_location(id: &str, value: &Value) -> Result<IstanbulLocation, IstanbulError> {
    let object = value
        .as_object()
        .ok_or_else(|| IstanbulError::InvalidPosition {
            id: id.into(),
            field: "location".into(),
        })?;
    let start = parse_position(id, "start", object.get("start"))?;
    let end = parse_position(id, "end", object.get("end"))?;
    if start >= end {
        return Err(IstanbulError::InvalidSpan { id: id.into() });
    }
    Ok(IstanbulLocation { start, end })
}

fn parse_position(
    id: &str,
    field: &str,
    value: Option<&Value>,
) -> Result<IstanbulPosition, IstanbulError> {
    let object =
        value
            .and_then(Value::as_object)
            .ok_or_else(|| IstanbulError::InvalidPosition {
                id: id.into(),
                field: field.into(),
            })?;
    let line = object
        .get("line")
        .and_then(Value::as_u64)
        .and_then(|value| u32::try_from(value).ok())
        .filter(|line| *line > 0)
        .ok_or_else(|| IstanbulError::InvalidPosition {
            id: id.into(),
            field: format!("{field}.line"),
        })?;
    let column = object
        .get("column")
        .and_then(Value::as_u64)
        .and_then(|value| u32::try_from(value).ok())
        .ok_or_else(|| IstanbulError::InvalidPosition {
            id: id.into(),
            field: format!("{field}.column"),
        })?;
    Ok(IstanbulPosition { line, column })
}

fn has_file_coverage_fields(root: &Map<String, Value>) -> bool {
    root.contains_key("path") || root.contains_key("statementMap") || root.contains_key("s")
}

fn is_raw_v8(root: &Map<String, Value>) -> bool {
    root.get("functions").is_some_and(Value::is_array)
        || root.get("result").is_some_and(Value::is_array)
        || root.get("ranges").is_some_and(Value::is_array)
        || root.contains_key("scriptId")
}
