use crate::{
    callable::normalize_path,
    complexity::calculate_complexity,
    correlation::{CallableObservation, correlate_file},
    istanbul::parse_coverage,
    parser::parse_source,
};
use codegauge_application::{
    CollectionRequest, InputCardinality, InputRequirement, MetricProvider, ProfileDescriptor,
    ProviderError, ProviderObservations,
};
use codegauge_model::{
    ComplexityMeasurement, CoverageMeasurement, DerivedMetrics, InputRole, ProfileId,
    SymbolIdentity, SymbolResult,
};
use oxc_allocator::Allocator;
use oxc_span::SourceType;
use std::{collections::BTreeSet, path::Path, str};

const PROVIDER: &str = "typescript-oxc-istanbul";
const COMPLEXITY_SEMANTICS: &str = "typescript-oxc-mccabe-v1";
const COVERAGE_SEMANTICS: &str = "istanbul-statement";

#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct TypescriptProvider;

impl TypescriptProvider {
    pub const fn new() -> Self {
        Self
    }

    pub const fn descriptor(&self) -> ProfileId {
        ProfileId::TypescriptOxcIstanbulV1
    }

    pub fn collect(
        &self,
        request: CollectionRequest<'_>,
    ) -> Result<ProviderObservations, ProviderError> {
        collect_request(request)
    }
}

impl MetricProvider for TypescriptProvider {
    fn descriptor(&self) -> ProfileDescriptor {
        ProfileDescriptor {
            profile: ProfileId::TypescriptOxcIstanbulV1,
            provider: PROVIDER.into(),
            semantics: vec![COMPLEXITY_SEMANTICS.into(), COVERAGE_SEMANTICS.into()],
            required_inputs: vec![
                InputRequirement {
                    role: InputRole::Coverage,
                    cardinality: InputCardinality::ExactlyOne,
                },
                InputRequirement {
                    role: InputRole::Source,
                    cardinality: InputCardinality::OneOrMore,
                },
            ],
        }
    }

    fn collect(
        &self,
        request: CollectionRequest<'_>,
    ) -> Result<ProviderObservations, ProviderError> {
        collect_request(request)
    }
}

fn collect_request(request: CollectionRequest<'_>) -> Result<ProviderObservations, ProviderError> {
    let descriptor = TypescriptProvider::new();
    let requirements = <TypescriptProvider as MetricProvider>::descriptor(&descriptor);
    request
        .inputs
        .validate(&requirements.required_inputs)
        .map_err(|_| invalid())?;

    let coverage = request
        .inputs
        .primary(InputRole::Coverage)
        .ok_or_else(invalid)?;
    let files = parse_coverage(&coverage.bytes).map_err(|_| invalid())?;
    let sources = request.inputs.get(InputRole::Source);
    let mut symbols = Vec::new();
    let mut identities = BTreeSet::new();

    for file in &files {
        let coverage_path = normalize_path(Path::new(&file.path));
        let source = sources
            .iter()
            .find(|source| normalize_path(Path::new(&source.path)) == coverage_path)
            .ok_or_else(invalid)?;
        let source_text = str::from_utf8(&source.bytes).map_err(|_| invalid())?;
        let allocator = Allocator::default();
        let parsed = parse_source(&allocator, source_text, source_type_for_path(&source.path))
            .map_err(|_| invalid())?;
        let observations = correlate_file(file, &source.path, &parsed).map_err(|_| invalid())?;

        for observation in observations {
            let symbol = to_symbol_result(&parsed, &observation).map_err(|_| invalid())?;
            if !identities.insert(symbol.symbol.id().to_owned()) {
                return Err(invalid());
            }
            symbols.push(symbol);
        }
    }

    symbols.sort_by(|left, right| {
        left.symbol
            .id()
            .as_bytes()
            .cmp(right.symbol.id().as_bytes())
    });
    Ok(ProviderObservations {
        symbols,
        diagnostics: Vec::new(),
    })
}

fn to_symbol_result(
    parsed: &crate::parser::ParsedSource<'_>,
    observation: &CallableObservation,
) -> Result<SymbolResult, ()> {
    let callable = &observation.callable;
    let symbol = SymbolIdentity::new(
        callable.id(),
        "typescript",
        callable.kind.as_str(),
        callable.path.clone(),
        callable.name.clone(),
        format!("{}-{}", callable.span.start, callable.span.end),
    )
    .map_err(|_| ())?;
    let total = u64::try_from(observation.total_statements()).map_err(|_| ())?;
    let covered = u64::try_from(observation.covered_statements()).map_err(|_| ())?;
    if total == 0 || covered > total {
        return Err(());
    }
    let complexity = calculate_complexity(parsed, callable) as f64;
    let ratio = covered as f64 / total as f64;
    if !complexity.is_finite() || !ratio.is_finite() {
        return Err(());
    }
    Ok(SymbolResult {
        symbol,
        complexity: Some(ComplexityMeasurement {
            value: complexity,
            metric: "cyclomatic".into(),
            semantics: COMPLEXITY_SEMANTICS.into(),
            provider: PROVIDER.into(),
        }),
        coverage: Some(CoverageMeasurement {
            ratio,
            covered,
            missed: total - covered,
            metric: "statement".into(),
            semantics: COVERAGE_SEMANTICS.into(),
            provider: PROVIDER.into(),
        }),
        metrics: DerivedMetrics { crap: None },
    })
}

fn source_type_for_path(path: &str) -> SourceType {
    if path.to_ascii_lowercase().ends_with(".tsx") {
        SourceType::tsx()
    } else {
        SourceType::ts()
    }
}

fn invalid() -> ProviderError {
    ProviderError::InvalidInput {
        message: "invalid TypeScript Istanbul input",
    }
}
