use codegauge_core::{CrapInput, calculate_crap};

fn score(cc: f64, coverage: f64) -> f64 {
    calculate_crap(CrapInput {
        cyclomatic_complexity: cc,
        coverage,
    })
    .unwrap()
    .value()
}

#[test]
fn formula_edges_golden_and_determinism() {
    assert_eq!(score(7.0, 1.0), 7.0);
    assert_eq!(score(7.0, 0.0), 56.0);
    assert!((score(7.0, 0.83) - 7.240737).abs() < f64::EPSILON);
    let input = CrapInput {
        cyclomatic_complexity: 3.0,
        coverage: 0.25,
    };
    assert_eq!(calculate_crap(input), calculate_crap(input));
}

#[test]
fn invariants_and_monotonicity_hold() {
    for (cc, coverage) in [
        (0.0, 0.5),
        (1.0, -0.1),
        (1.0, 1.1),
        (f64::NAN, 0.5),
        (f64::INFINITY, 0.5),
    ] {
        assert!(
            calculate_crap(CrapInput {
                cyclomatic_complexity: cc,
                coverage
            })
            .is_err()
        );
    }
    let coverage = [0.0, 0.2, 0.5, 0.8, 1.0].map(|value| score(4.0, value));
    assert!(coverage.windows(2).all(|pair| pair[0] >= pair[1]));
    let complexity = [1.0, 2.0, 4.0].map(|value| score(value, 0.5));
    assert!(complexity.windows(2).all(|pair| pair[0] <= pair[1]));
}
