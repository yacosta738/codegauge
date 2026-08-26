use codegauge_provider_typescript::parser::parse_source;
use oxc_allocator::Allocator;
use oxc_span::SourceType;

#[test]
fn parses_typescript_with_the_pinned_oxc_api() {
    let allocator = Allocator::default();
    let parsed = parse_source(&allocator, "const answer: number = 42;", SourceType::ts())
        .expect("the pinned Oxc parser should accept a TypeScript source file");

    assert_eq!(parsed.program.body.len(), 1);
}
