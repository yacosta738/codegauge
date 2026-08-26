use crate::{
    callable::{Callable, collect_callables, normalize_path},
    istanbul::{IstanbulFileCoverage, IstanbulPosition},
    ownership::{OwnedStatement, OwnershipError, assign_statements},
    parser::ParsedSource,
};
use std::{collections::BTreeMap, error::Error, fmt, path::Path};

pub use crate::ownership::StatementCoverage;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CallableObservation {
    pub callable: Callable,
    pub statements: Vec<StatementCoverage>,
}

impl CallableObservation {
    pub fn covered_statements(&self) -> usize {
        self.statements
            .iter()
            .filter(|statement| statement.count > 0)
            .count()
    }

    pub fn total_statements(&self) -> usize {
        self.statements.len()
    }

    pub fn coverage_ratio(&self) -> f64 {
        let total = self.total_statements();
        if total == 0 {
            0.0
        } else {
            self.covered_statements() as f64 / total as f64
        }
    }
}

pub struct SourceDocument<'source> {
    pub path: String,
    pub parsed: ParsedSource<'source>,
}

impl<'source> SourceDocument<'source> {
    pub fn new(path: impl Into<String>, parsed: ParsedSource<'source>) -> Self {
        Self {
            path: path.into(),
            parsed,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum CorrelationError {
    PathMismatch { coverage: String, source: String },
    DuplicateCoveragePath { path: String },
    AmbiguousSourcePath { path: String },
    UnmatchedCoveragePath { path: String },
    InvalidLocation { id: String, field: String },
    InvalidSpan { id: String },
    DuplicateCallableId { id: String },
    MissingCallable { id: String },
    Ownership(OwnershipError),
}

impl fmt::Display for CorrelationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::PathMismatch { coverage, source } => {
                write!(
                    formatter,
                    "coverage/source path mismatch: {coverage} != {source}"
                )
            }
            Self::DuplicateCoveragePath { path } => {
                write!(formatter, "duplicate coverage path: {path}")
            }
            Self::AmbiguousSourcePath { path } => {
                write!(formatter, "ambiguous source path: {path}")
            }
            Self::UnmatchedCoveragePath { path } => {
                write!(formatter, "unmatched coverage path: {path}")
            }
            Self::InvalidLocation { id, field } => {
                write!(formatter, "invalid Istanbul location for {id}: {field}")
            }
            Self::InvalidSpan { id } => write!(formatter, "invalid correlated span: {id}"),
            Self::DuplicateCallableId { id } => write!(formatter, "duplicate callable id: {id}"),
            Self::MissingCallable { id } => {
                write!(formatter, "missing callable for statement: {id}")
            }
            Self::Ownership(error) => error.fmt(formatter),
        }
    }
}

impl Error for CorrelationError {}

impl From<OwnershipError> for CorrelationError {
    fn from(error: OwnershipError) -> Self {
        Self::Ownership(error)
    }
}

/// Correlate one Istanbul file with one parsed source file.
pub fn correlate_file<'source>(
    coverage: &IstanbulFileCoverage,
    source_path: impl AsRef<Path>,
    parsed: &ParsedSource<'source>,
) -> Result<Vec<CallableObservation>, CorrelationError> {
    let coverage_path = normalize_path(Path::new(&coverage.path));
    let source_path = normalize_path(source_path.as_ref());
    if coverage_path != source_path {
        return Err(CorrelationError::PathMismatch {
            coverage: coverage_path,
            source: source_path,
        });
    }

    let statements = coverage
        .statements
        .iter()
        .map(|statement| {
            let start = location_to_offset(
                parsed.source,
                statement.id.as_str(),
                "start",
                statement.location.start,
            )?;
            let end = location_to_offset(
                parsed.source,
                statement.id.as_str(),
                "end",
                statement.location.end,
            )?;
            if start >= end {
                return Err(CorrelationError::InvalidSpan {
                    id: statement.id.clone(),
                });
            }
            Ok(StatementCoverage {
                id: statement.id.clone(),
                span: crate::SourceSpan { start, end },
                count: statement.count,
            })
        })
        .collect::<Result<Vec<_>, CorrelationError>>()?;

    let callables = collect_callables(parsed, source_path);
    let owned = assign_statements(&callables, &statements)?;
    build_observations(callables, owned)
}

/// Correlate a deterministic Istanbul file bundle with source documents.
pub fn correlate_files<'source>(
    coverage: &[IstanbulFileCoverage],
    sources: &[SourceDocument<'source>],
) -> Result<Vec<CallableObservation>, CorrelationError> {
    let mut sources_by_path = BTreeMap::new();
    for source in sources {
        let path = normalize_path(Path::new(&source.path));
        if sources_by_path.insert(path.clone(), source).is_some() {
            return Err(CorrelationError::AmbiguousSourcePath { path });
        }
    }

    let mut observations = Vec::new();
    let mut seen_coverage = BTreeMap::new();
    for file in coverage {
        let path = normalize_path(Path::new(&file.path));
        if seen_coverage.insert(path.clone(), file).is_some() {
            return Err(CorrelationError::DuplicateCoveragePath { path });
        }
        let source = sources_by_path
            .get(&path)
            .ok_or_else(|| CorrelationError::UnmatchedCoveragePath { path: path.clone() })?;
        observations.extend(correlate_file(file, &path, &source.parsed)?);
    }
    observations.sort_by_key(|observation| observation.callable.id());
    Ok(observations)
}

fn build_observations(
    callables: Vec<Callable>,
    owned: Vec<OwnedStatement>,
) -> Result<Vec<CallableObservation>, CorrelationError> {
    let mut callable_by_id = BTreeMap::new();
    for callable in callables {
        let id = callable.id();
        if callable_by_id.insert(id.clone(), callable).is_some() {
            return Err(CorrelationError::DuplicateCallableId { id });
        }
    }

    let mut statements_by_callable: BTreeMap<String, Vec<StatementCoverage>> = BTreeMap::new();
    for owned_statement in owned {
        if !callable_by_id.contains_key(&owned_statement.callable_id) {
            return Err(CorrelationError::MissingCallable {
                id: owned_statement.callable_id,
            });
        }
        statements_by_callable
            .entry(owned_statement.callable_id)
            .or_default()
            .push(owned_statement.statement);
    }

    let mut observations = Vec::with_capacity(statements_by_callable.len());
    for (id, mut statements) in statements_by_callable {
        statements.sort_by(|left, right| {
            left.span
                .cmp(&right.span)
                .then_with(|| left.id.cmp(&right.id))
        });
        let callable = callable_by_id
            .remove(&id)
            .ok_or_else(|| CorrelationError::MissingCallable { id: id.clone() })?;
        observations.push(CallableObservation {
            callable,
            statements,
        });
    }
    Ok(observations)
}

fn location_to_offset(
    source: &str,
    id: &str,
    field: &str,
    position: IstanbulPosition,
) -> Result<u32, CorrelationError> {
    let ranges = line_ranges(source);
    if position.line == 0 {
        return Err(CorrelationError::InvalidLocation {
            id: id.into(),
            field: format!("{field}.line"),
        });
    }
    let line_index =
        usize::try_from(position.line - 1).map_err(|_| CorrelationError::InvalidLocation {
            id: id.into(),
            field: format!("{field}.line"),
        })?;
    let (line_start, line_end) =
        ranges
            .get(line_index)
            .copied()
            .ok_or_else(|| CorrelationError::InvalidLocation {
                id: id.into(),
                field: format!("{field}.line"),
            })?;
    let line = &source[line_start..line_end];
    let target_column =
        usize::try_from(position.column).map_err(|_| CorrelationError::InvalidLocation {
            id: id.into(),
            field: format!("{field}.column"),
        })?;
    // Istanbul locations originate in JavaScript parsers whose columns count
    // UTF-16 code units; Oxc's spans are UTF-8 byte offsets.
    let mut utf16_column = 0usize;
    for (byte_offset, character) in line.char_indices() {
        if utf16_column == target_column {
            return u32::try_from(line_start + byte_offset).map_err(|_| {
                CorrelationError::InvalidLocation {
                    id: id.into(),
                    field: format!("{field}.offset"),
                }
            });
        }
        utf16_column += character.len_utf16();
        if utf16_column > target_column {
            return Err(CorrelationError::InvalidLocation {
                id: id.into(),
                field: format!("{field}.column"),
            });
        }
    }
    if utf16_column == target_column {
        return u32::try_from(line_end).map_err(|_| CorrelationError::InvalidLocation {
            id: id.into(),
            field: format!("{field}.offset"),
        });
    }
    Err(CorrelationError::InvalidLocation {
        id: id.into(),
        field: format!("{field}.column"),
    })
}

fn line_ranges(source: &str) -> Vec<(usize, usize)> {
    let bytes = source.as_bytes();
    let mut ranges = Vec::new();
    let mut line_start = 0;
    let mut index = 0;
    while index < bytes.len() {
        match bytes[index] {
            b'\n' => {
                ranges.push((line_start, index));
                line_start = index + 1;
            }
            b'\r' => {
                ranges.push((line_start, index));
                if bytes.get(index + 1) == Some(&b'\n') {
                    index += 1;
                }
                line_start = index + 1;
            }
            _ => {}
        }
        index += 1;
    }
    ranges.push((line_start, bytes.len()));
    ranges
}
