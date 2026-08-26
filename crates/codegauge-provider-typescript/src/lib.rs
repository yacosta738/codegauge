#![forbid(unsafe_code)]

//! TypeScript source parsing and syntactic complexity primitives.

pub mod callable;
pub mod complexity;
pub mod correlation;
pub mod istanbul;
pub mod ownership;
pub mod parser;
pub mod provider;

pub use callable::{Callable, CallableKind, SourceSpan, collect_callables};
pub use complexity::calculate_complexity;
pub use correlation::{
    CallableObservation, CorrelationError, SourceDocument, correlate_file, correlate_files,
};
pub use istanbul::{
    IstanbulError, IstanbulFileCoverage, IstanbulLocation, IstanbulPosition, IstanbulStatement,
    parse_coverage,
};
pub use ownership::{OwnedStatement, OwnershipError, StatementCoverage, assign_statements};
pub use parser::{ParseError, ParsedSource, parse_source};
pub use provider::TypescriptProvider;
