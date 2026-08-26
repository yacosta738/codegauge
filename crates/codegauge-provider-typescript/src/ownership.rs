use crate::callable::{Callable, SourceSpan};
use std::{collections::BTreeSet, error::Error, fmt};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct StatementCoverage {
    pub id: String,
    pub span: SourceSpan,
    pub count: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct OwnedStatement {
    pub callable_id: String,
    pub statement: StatementCoverage,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum OwnershipError {
    DuplicateStatementId {
        id: String,
    },
    DuplicateStatementSpan {
        start: u32,
        end: u32,
    },
    AmbiguousStatement {
        id: String,
        callable_ids: Vec<String>,
    },
}

impl fmt::Display for OwnershipError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::DuplicateStatementId { id } => write!(formatter, "duplicate statement id: {id}"),
            Self::DuplicateStatementSpan { start, end } => {
                write!(formatter, "duplicate statement span: {start}-{end}")
            }
            Self::AmbiguousStatement { id, callable_ids } => {
                write!(
                    formatter,
                    "ambiguous statement ownership {id}: {}",
                    callable_ids.join(",")
                )
            }
        }
    }
}

impl Error for OwnershipError {}

/// Assign statements to their narrowest containing callable body.
/// Statements outside all callable bodies are intentionally omitted.
pub fn assign_statements(
    callables: &[Callable],
    statements: &[StatementCoverage],
) -> Result<Vec<OwnedStatement>, OwnershipError> {
    let mut statement_ids = BTreeSet::new();
    let mut statement_spans = BTreeSet::new();
    let mut owned = Vec::with_capacity(statements.len());

    for statement in statements {
        if !statement_ids.insert(statement.id.clone()) {
            return Err(OwnershipError::DuplicateStatementId {
                id: statement.id.clone(),
            });
        }
        if !statement_spans.insert((statement.span.start, statement.span.end)) {
            return Err(OwnershipError::DuplicateStatementSpan {
                start: statement.span.start,
                end: statement.span.end,
            });
        }

        let candidates: Vec<_> = callables
            .iter()
            .filter(|callable| contains(callable.body_span, statement.span))
            .collect();
        let deepest: Vec<_> = candidates
            .iter()
            .copied()
            .filter(|candidate| {
                !candidates.iter().any(|other| {
                    candidate.body_span != other.body_span
                        && contains(candidate.body_span, other.body_span)
                })
            })
            .collect();
        if deepest.len() > 1 {
            let mut callable_ids: Vec<_> = deepest.iter().map(|callable| callable.id()).collect();
            callable_ids.sort();
            return Err(OwnershipError::AmbiguousStatement {
                id: statement.id.clone(),
                callable_ids,
            });
        }
        if let Some(callable) = deepest.first() {
            owned.push(OwnedStatement {
                callable_id: callable.id(),
                statement: statement.clone(),
            });
        }
    }

    owned.sort_by(|left, right| {
        left.statement
            .span
            .cmp(&right.statement.span)
            .then_with(|| left.statement.id.cmp(&right.statement.id))
            .then_with(|| left.callable_id.cmp(&right.callable_id))
    });
    Ok(owned)
}

fn contains(outer: SourceSpan, inner: SourceSpan) -> bool {
    inner.start >= outer.start && inner.end <= outer.end
}
