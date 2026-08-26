use codegauge_provider_typescript::{
    callable::{CallableKind, collect_callables},
    complexity::calculate_complexity,
    correlation::{CorrelationError, SourceDocument, correlate_file, correlate_files},
    istanbul::{
        IstanbulError, IstanbulFileCoverage, IstanbulLocation, IstanbulPosition, IstanbulStatement,
        parse_coverage,
    },
    ownership::{StatementCoverage, assign_statements},
    parser::parse_source,
};
use oxc_allocator::Allocator;
use oxc_span::SourceType;

const SOURCE: &str = r#"
const café = 1;

function outer(value: number) {
    const arrow = (next: number) => next + value;
    function nested() {
        return value;
    }
    return arrow(value);
}

const named = function named() {};
const anonymous = function () {};

class Example {
    constructor() {}
    method() {}
    get value() { return 1; }
    set value(next: number) { this._value = next; }
}

const object = {
    objectMethod() {},
    get objectValue() { return 1; },
    set objectValue(next: number) { void next; },
};
"#;

#[test]
fn discovers_callable_kinds_with_normalized_paths_and_unique_span_ids() {
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, SOURCE, SourceType::ts()).expect("valid TypeScript");
    let callables = collect_callables(&parsed, r"src\sample.ts");

    assert_eq!(callables.len(), 12);
    assert!(
        callables
            .iter()
            .all(|callable| callable.path == "src/sample.ts")
    );

    let outer = callables
        .iter()
        .find(|callable| callable.name == "outer")
        .expect("named function");
    assert_eq!(outer.kind, CallableKind::Function);
    assert_eq!(
        outer.id(),
        format!(
            "typescript:src/sample.ts#outer@{}-{}",
            outer.span.start, outer.span.end
        )
    );

    assert_eq!(
        callables
            .iter()
            .filter(|callable| callable.kind == CallableKind::Function)
            .count(),
        4
    );
    assert_eq!(
        callables
            .iter()
            .filter(|callable| callable.kind == CallableKind::Arrow)
            .count(),
        1
    );
    assert_eq!(
        callables
            .iter()
            .filter(|callable| callable.kind == CallableKind::Constructor)
            .count(),
        1
    );
    assert_eq!(
        callables
            .iter()
            .filter(|callable| callable.kind == CallableKind::Method)
            .count(),
        2
    );
    assert_eq!(
        callables
            .iter()
            .filter(|callable| callable.kind == CallableKind::Getter)
            .count(),
        2
    );
    assert_eq!(
        callables
            .iter()
            .filter(|callable| callable.kind == CallableKind::Setter)
            .count(),
        2
    );

    let ids: std::collections::BTreeSet<_> =
        callables.iter().map(|callable| callable.id()).collect();
    assert_eq!(ids.len(), callables.len());
}

#[test]
fn callable_spans_are_utf8_byte_ranges() {
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, SOURCE, SourceType::ts()).expect("valid TypeScript");
    let callables = collect_callables(&parsed, "sample.ts");
    let outer = callables
        .iter()
        .find(|callable| callable.name == "outer")
        .expect("named function");
    let start = SOURCE.find("function outer").expect("outer source span");

    assert_eq!(outer.span.start as usize, start);
    assert_eq!(
        &SOURCE[outer.span.start as usize..outer.span.start as usize + 14],
        "function outer"
    );
    assert!(outer.body_span.start > outer.span.start);
    assert!(outer.body_span.end <= outer.span.end);
}

#[test]
fn calculates_classic_mccabe_and_excludes_nested_callable_bodies() {
    let source = r#"
function outer(value: boolean, values: number[]) {
    if ((value && value) || (value ?? false)) {
        const choice = value ? 1 : 2;
        for (const item of values) { console.log(item); }
        for (const item in values) { console.log(item); }
        for (;;) { break; }
        while (value) { break; }
        do { break; } while (value);
        switch (choice) {
            case 1: break;
            case 2: break;
            default: break;
        }
        try { console.log(choice); } catch (error) { console.error(error); }
    }
    function inner() {
        if (value) { return 1; }
        return 0;
    }
    return inner();
}

function typeOnly<T>(value: T): number {
    const cast = value as unknown as number;
    const optional = (value as { count?: number } | undefined)?.count ?? 0;
    return cast + optional;
}
"#;
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let callables = collect_callables(&parsed, "complexity.ts");

    let complexity = |name: &str| {
        let callable = callables
            .iter()
            .find(|callable| callable.name == name)
            .expect("callable fixture entry");
        calculate_complexity(&parsed, callable)
    };

    assert_eq!(complexity("outer"), 13);
    assert_eq!(complexity("inner"), 2);
    assert_eq!(complexity("typeOnly"), 1);
}

#[test]
fn parses_istanbul_statement_counts_without_using_function_or_branch_hits() {
    let json = br#"
    {
      "path": "src/sample.ts",
      "statementMap": {
        "0": {"start": {"line": 3, "column": 4}, "end": {"line": 3, "column": 19}},
        "1": {"start": {"line": 4, "column": 4}, "end": {"line": 4, "column": 20}}
      },
      "fnMap": {"0": {"name": "ignored", "loc": {"start": {"line": 3, "column": 0}, "end": {"line": 4, "column": 1}}}},
      "branchMap": {"0": {"type": "if", "locations": []}},
      "s": {"0": 2, "1": 0},
      "f": {"0": 0},
      "b": {"0": [0, 1]}
    }
    "#;

    let files = parse_coverage(json).expect("valid Istanbul coverage");
    assert_eq!(files.len(), 1);
    assert_eq!(files[0].path, "src/sample.ts");
    assert_eq!(files[0].statements.len(), 2);
    assert_eq!(files[0].statements[0].id, "0");
    assert_eq!(files[0].statements[0].count, 2);
    assert_eq!(files[0].statements[1].count, 0);
}

#[test]
fn rejects_raw_v8_and_malformed_istanbul_coverage() {
    let raw_v8 = br#"{
        "scriptId": "1",
        "url": "file:///sample.js",
        "functions": [{"functionName": "sample", "ranges": [], "isBlockCoverage": true}]
    }"#;
    let raw_v8_error = parse_coverage(raw_v8).expect_err("raw V8 must be rejected");
    assert!(matches!(raw_v8_error, IstanbulError::UnsupportedFormat));

    let malformed = br#"{
        "path": "sample.ts",
        "statementMap": {"0": {"start": {"line": 1, "column": 0}, "end": {"line": 1, "column": 1}}}
    }"#;
    let malformed_error = parse_coverage(malformed).expect_err("missing counts must be rejected");
    assert!(malformed_error.to_string().contains("s"));
}

#[test]
fn parses_coverage_final_bundles_with_normalized_path_keys() {
    let bundle = br#"{
        "src\\sample.ts": {
            "path": "src/sample.ts",
            "statementMap": {},
            "s": {}
        }
    }"#;
    let files = parse_coverage(bundle).expect("valid coverage-final bundle");
    assert_eq!(files.len(), 1);
    assert_eq!(files[0].path, "src/sample.ts");
    assert!(files[0].statements.is_empty());

    let mismatched = br#"{
        "src/sample.ts": {
            "path": "other.ts",
            "statementMap": {},
            "s": {}
        }
    }"#;
    assert!(matches!(
        parse_coverage(mismatched),
        Err(IstanbulError::PathKeyMismatch { .. })
    ));
}

#[test]
fn assigns_nested_statements_to_the_deepest_callable_only() {
    let source = r#"
function outer() {
    const before = 1;
    function inner() {
        return before;
    }
    return inner();
}
"#;
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let callables = collect_callables(&parsed, "sample.ts");
    let outer = callables
        .iter()
        .find(|callable| callable.name == "outer")
        .unwrap();
    let inner = callables
        .iter()
        .find(|callable| callable.name == "inner")
        .unwrap();

    let before_start = source.find("const before").unwrap() as u32;
    let before_end = before_start + "const before = 1;".len() as u32;
    let nested_start = source.find("return before").unwrap() as u32;
    let nested_end = nested_start + "return before;".len() as u32;
    let statements = vec![
        StatementCoverage {
            id: "before".into(),
            span: codegauge_provider_typescript::SourceSpan {
                start: before_start,
                end: before_end,
            },
            count: 0,
        },
        StatementCoverage {
            id: "nested".into(),
            span: codegauge_provider_typescript::SourceSpan {
                start: nested_start,
                end: nested_end,
            },
            count: 1,
        },
    ];

    let owned = assign_statements(&callables, &statements).expect("unambiguous ownership");
    assert_eq!(owned.len(), 2);
    assert_eq!(owned[0].callable_id, outer.id());
    assert_eq!(owned[1].callable_id, inner.id());
}

#[test]
fn correlates_istanbul_utf16_columns_to_oxc_utf8_byte_spans() {
    let source = "function read() {\n    const emoji = \"😀\"; const after = emoji;\n}\nfunction unused() {}\n";
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let statement = "const after = emoji;";
    let start = source.find(statement).expect("statement in source");
    let end = start + statement.len();
    let coverage = IstanbulFileCoverage {
        path: "src/sample.ts".into(),
        statements: vec![IstanbulStatement {
            id: "0".into(),
            location: location_for(source, start, end),
            count: 1,
        }],
    };

    let observations = correlate_file(&coverage, r"src\sample.ts", &parsed)
        .expect("Istanbul location should correlate");
    assert_eq!(observations.len(), 1);
    assert_eq!(observations[0].statements[0].span.start as usize, start);
    assert_eq!(observations[0].statements[0].span.end as usize, end);
    assert_eq!(observations[0].covered_statements(), 1);
    assert_eq!(observations[0].total_statements(), 1);
    assert_eq!(observations[0].callable.name, "read");
}

#[test]
fn correlates_normalized_paths_and_requires_one_to_one_matches() {
    let source = "function sample() { return 1; }\n";
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let statement = "return 1;";
    let start = source.find(statement).unwrap();
    let coverage = IstanbulFileCoverage {
        path: "src/sample.ts".into(),
        statements: vec![IstanbulStatement {
            id: "0".into(),
            location: location_for(source, start, start + statement.len()),
            count: 1,
        }],
    };

    let sources = vec![SourceDocument::new(r"src\sample.ts", parsed)];
    let observations = correlate_files(std::slice::from_ref(&coverage), &sources)
        .expect("normalized source path should match");
    assert_eq!(observations.len(), 1);

    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let unmatched = vec![SourceDocument::new("other.ts", parsed)];
    let error = correlate_files(std::slice::from_ref(&coverage), &unmatched)
        .expect_err("unmatched coverage must fail");
    assert!(matches!(
        error,
        CorrelationError::UnmatchedCoveragePath { .. }
    ));
}

#[test]
fn rejects_duplicate_and_ambiguous_paths_and_invalid_boundaries() {
    let source = "function sample() { return 1; }\n";
    let statement = "return 1;";
    let start = source.find(statement).unwrap();
    let coverage = IstanbulFileCoverage {
        path: "sample.ts".into(),
        statements: vec![IstanbulStatement {
            id: "0".into(),
            location: location_for(source, start, start + statement.len()),
            count: 1,
        }],
    };
    let invalid = IstanbulFileCoverage {
        path: "sample.ts".into(),
        statements: vec![IstanbulStatement {
            id: "bad".into(),
            location: IstanbulLocation {
                start: IstanbulPosition {
                    line: 99,
                    column: 0,
                },
                end: IstanbulPosition {
                    line: 99,
                    column: 1,
                },
            },
            count: 1,
        }],
    };
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let invalid_error =
        correlate_file(&invalid, "sample.ts", &parsed).expect_err("out-of-range line must fail");
    assert!(matches!(
        invalid_error,
        CorrelationError::InvalidLocation { .. }
    ));

    let invalid_line = IstanbulFileCoverage {
        path: "sample.ts".into(),
        statements: vec![IstanbulStatement {
            id: "zero-line".into(),
            location: IstanbulLocation {
                start: IstanbulPosition { line: 0, column: 0 },
                end: IstanbulPosition { line: 0, column: 1 },
            },
            count: 1,
        }],
    };
    let zero_line_error = correlate_file(&invalid_line, "sample.ts", &parsed)
        .expect_err("zero-based Istanbul lines must fail");
    assert!(matches!(
        zero_line_error,
        CorrelationError::InvalidLocation { .. }
    ));

    let allocator = Allocator::default();
    let parsed_a = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let parsed_b = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let ambiguous_sources = vec![
        SourceDocument::new("sample.ts", parsed_a),
        SourceDocument::new("sample.ts", parsed_b),
    ];
    let ambiguous = correlate_files(std::slice::from_ref(&coverage), &ambiguous_sources)
        .expect_err("duplicate normalized source paths must fail");
    assert!(matches!(
        ambiguous,
        CorrelationError::AmbiguousSourcePath { .. }
    ));

    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, source, SourceType::ts()).expect("valid TypeScript");
    let sources = vec![SourceDocument::new("sample.ts", parsed)];
    let duplicate = correlate_files(&[coverage.clone(), coverage], &sources)
        .expect_err("duplicate coverage paths must fail");
    assert!(matches!(
        duplicate,
        CorrelationError::DuplicateCoveragePath { .. }
    ));
}

fn location_for(source: &str, start: usize, end: usize) -> IstanbulLocation {
    IstanbulLocation {
        start: position_for(source, start),
        end: position_for(source, end),
    }
}

fn position_for(source: &str, offset: usize) -> IstanbulPosition {
    let line_start = source[..offset].rfind('\n').map_or(0, |index| index + 1);
    IstanbulPosition {
        line: source[..offset]
            .bytes()
            .filter(|byte| *byte == b'\n')
            .count() as u32
            + 1,
        column: source[line_start..offset].encode_utf16().count() as u32,
    }
}
