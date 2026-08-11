#![forbid(unsafe_code)]

//! Pure, deterministic CodeGauge metric calculations.

pub use codegauge_model::CRAP_ORIGINAL_V1;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CrapInput {
    pub cyclomatic_complexity: f64,
    pub coverage: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CrapScore(f64);

impl CrapScore {
    pub const fn value(self) -> f64 {
        self.0
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum MetricError {
    InvalidInput,
}

pub fn calculate_crap(input: CrapInput) -> Result<CrapScore, MetricError> {
    if !input.cyclomatic_complexity.is_finite() || input.cyclomatic_complexity < 1.0 {
        return Err(MetricError::InvalidInput);
    }
    if !input.coverage.is_finite() || !(0.0..=1.0).contains(&input.coverage) {
        return Err(MetricError::InvalidInput);
    }
    let score = input.cyclomatic_complexity.powi(2) * (1.0 - input.coverage).powi(3)
        + input.cyclomatic_complexity;
    if !score.is_finite() {
        return Err(MetricError::InvalidInput);
    }
    Ok(CrapScore(score))
}
