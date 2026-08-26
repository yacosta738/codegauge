use oxc_allocator::Allocator;
use oxc_ast::ast::Program;
use oxc_parser::{Parser, ParserReturn};
use oxc_span::SourceType;
use std::{error::Error, fmt};

/// The parsed Oxc program and its allocator-backed lifetime.
pub struct ParsedSource<'a> {
    pub source: &'a str,
    pub program: Program<'a>,
}

/// Syntax diagnostics produced while parsing a source artifact.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ParseError {
    diagnostics: Vec<String>,
}

impl ParseError {
    pub fn diagnostics(&self) -> &[String] {
        &self.diagnostics
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "TypeScript source parsing failed")?;
        if !self.diagnostics.is_empty() {
            write!(formatter, ": {}", self.diagnostics.join("; "))?;
        }
        Ok(())
    }
}

impl Error for ParseError {}

/// Parse a JavaScript or TypeScript source using the pinned Oxc parser.
pub fn parse_source<'a>(
    allocator: &'a Allocator,
    source: &'a str,
    source_type: SourceType,
) -> Result<ParsedSource<'a>, ParseError> {
    let ParserReturn {
        program,
        diagnostics,
        panicked,
        ..
    } = Parser::new(allocator, source, source_type).parse();

    if panicked || !diagnostics.is_empty() {
        return Err(ParseError {
            diagnostics: diagnostics
                .into_iter()
                .map(|diagnostic| format!("{diagnostic:?}"))
                .collect(),
        });
    }

    Ok(ParsedSource { source, program })
}
