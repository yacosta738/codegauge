#![forbid(unsafe_code)]

//! Bounded, artifact-only JaCoCo XML adaptation.

use codegauge_application::{CollectionRequest, MetricProvider, ProfileDescriptor};
pub use codegauge_application::{Diagnostic, DiagnosticCode, ProviderError, ProviderObservations};
use codegauge_model::{
    ComplexityMeasurement, CoverageMeasurement, DerivedMetrics, ProfileId, SymbolIdentity,
    SymbolResult,
};
use quick_xml::events::{BytesStart, Event};
use quick_xml::reader::Reader;
use std::collections::HashSet;

#[rustfmt::skip]
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub struct JacocoProvider;

#[rustfmt::skip]
impl JacocoProvider {
    pub const fn new() -> Self { Self }
    pub const fn descriptor(&self) -> ProfileId { ProfileId::JavaJacocoV1 }
    pub fn collect(&self, input: &[u8]) -> Result<ProviderObservations, ProviderError> { collect(input) }
}

impl MetricProvider for JacocoProvider {
    fn descriptor(&self) -> ProfileDescriptor {
        ProfileDescriptor {
            profile: ProfileId::JavaJacocoV1,
            provider: "jacoco".into(),
            semantics: vec!["jacoco-cyclomatic".into(), "jacoco-instruction".into()],
        }
    }
    fn collect(
        &self,
        request: CollectionRequest<'_>,
    ) -> Result<ProviderObservations, ProviderError> {
        parse_report(&request.artifact.bytes)
    }
}

#[rustfmt::skip]
pub fn parse_report(input: &[u8]) -> Result<ProviderObservations, ProviderError> { collect(input) }

#[rustfmt::skip]
pub fn collect(input: &[u8]) -> Result<ProviderObservations, ProviderError> {
    if input.len() > 64 * 1024 * 1024 { return Err(bad()); }
    let input = input.strip_prefix(&[0xef, 0xbb, 0xbf]).unwrap_or(input);
    std::str::from_utf8(input).map_err(|_| bad())?;
    validate_encoding(input)?;
    Parser::new(input).run()
}

#[rustfmt::skip]
fn bad() -> ProviderError { ProviderError::InvalidInput { message: "invalid JaCoCo input" } }

#[rustfmt::skip]
fn validate_encoding(input: &[u8]) -> Result<(), ProviderError> {
    if !input.starts_with(b"<?xml") { return Ok(()); }
    let end = input.windows(2).position(|w| w == b"?>").ok_or_else(bad)?;
    let declaration = std::str::from_utf8(&input[..end + 2]).map_err(|_| bad())?.to_ascii_lowercase();
    let Some(start) = declaration.find("encoding") else { return Ok(()); };
    let rest = declaration[start + 8..].trim_start().strip_prefix('=').map(str::trim_start).ok_or_else(bad)?;
    let quote = rest.as_bytes().first().copied().unwrap_or_default();
    if quote != b'\'' && quote != b'"' { return Err(bad()); }
    let end_quote = rest[1..].find(quote as char).ok_or_else(bad)?;
    if &rest[1..end_quote + 1] != "utf-8" { return Err(bad()); }
    Ok(())
}

#[rustfmt::skip]
struct Parser<'a> {
    input: &'a [u8], stack: Vec<Vec<u8>>, classes: HashSet<String>, identities: HashSet<String>,
    class: Option<String>, method: Option<Method>, class_count: usize, method_count: usize,
    root_seen: bool, symbols: Vec<SymbolResult>, diagnostics: Vec<Diagnostic>,
}

#[rustfmt::skip]
struct Method {
    symbol: SymbolIdentity, counts: [Count; 4], counter_count: usize, counter_types: HashSet<String>,
}

#[rustfmt::skip]
#[derive(Clone, Copy)]
enum Count { Missing, Invalid, Valid(u64) }

#[rustfmt::skip]
impl<'a> Parser<'a> {
    fn new(input: &'a [u8]) -> Self {
        Self { input, stack: Vec::new(), classes: HashSet::new(), identities: HashSet::new(), class: None,
            method: None, class_count: 0, method_count: 0, root_seen: false, symbols: Vec::new(), diagnostics: Vec::new() }
    }

    fn run(mut self) -> Result<ProviderObservations, ProviderError> {
        let mut reader = Reader::from_reader(self.input);
        let config = reader.config_mut();
        config.trim_text(true); config.check_end_names = true; config.allow_unmatched_ends = false;
        config.allow_dangling_amp = false;
        let mut buffer = Vec::new();
        loop {
            buffer.clear();
            let event = reader.read_event_into(&mut buffer).map_err(|_| bad())?;
            match event {
                Event::Eof => break,
                Event::Start(e) => self.element(&e, false)?,
                Event::Empty(e) => self.element(&e, true)?,
                Event::End(e) => self.end(&e)?,
                Event::DocType(_) | Event::GeneralRef(_) => return Err(bad()),
                Event::Text(e) => self.text(e.as_ref())?,
                Event::CData(e) => self.text(e.as_ref())?,
                Event::Decl(_) | Event::Comment(_) | Event::PI(_) => {}
            }
        }
        if !self.root_seen || !self.stack.is_empty() || self.method.is_some() { return Err(bad()); }
        Ok(ProviderObservations { symbols: self.symbols, diagnostics: self.diagnostics })
    }

    fn text(&self, bytes: &[u8]) -> Result<(), ProviderError> {
        if bytes.iter().all(u8::is_ascii_whitespace) { Ok(()) } else { Err(bad()) }
    }

    fn element(&mut self, element: &BytesStart<'_>, empty: bool) -> Result<(), ProviderError> {
        let tag = element.name().as_ref().to_vec();
        self.hierarchy(&tag, empty)?;
        attr(element, b"\0")?;
        self.root(&tag)?;
        match tag.as_slice() {
            b"class" => self.begin_class(element)?,
            b"method" => { self.begin_method(element)?; if empty { self.finish(); } }
            b"counter" if self.stack.last().map(Vec::as_slice) == Some(b"method") => self.counter(element)?,
            _ => {}
        }
        if empty { if tag.as_slice() == b"class" { self.class = None; } return Ok(()); }
        if self.stack.len() >= 128 { return Err(bad()); }
        self.stack.push(tag); Ok(())
    }

    fn hierarchy(&self, tag: &[u8], empty: bool) -> Result<(), ProviderError> {
        if self.stack.is_empty() {
            if self.root_seen || tag != b"report" { return Err(bad()); }
        } else {
            let parent = self.stack.last().map(Vec::as_slice).unwrap();
            let allowed = match parent {
                b"report" => matches!(tag, b"sessioninfo" | b"group" | b"package" | b"class" | b"counter"),
                b"group" => matches!(tag, b"group" | b"package" | b"counter"),
                b"package" => matches!(tag, b"sourcefile" | b"class" | b"counter"),
                b"sourcefile" => matches!(tag, b"line" | b"counter"),
                b"class" => matches!(tag, b"method" | b"counter"),
                b"method" => tag == b"counter",
                _ => false,
            };
            if !allowed { return Err(bad()); }
        }
        if !empty && matches!(tag, b"sessioninfo" | b"line" | b"counter") { return Err(bad()); }
        Ok(())
    }

    fn root(&mut self, tag: &[u8]) -> Result<(), ProviderError> {
        if self.stack.is_empty() {
            if self.root_seen || tag != b"report" { return Err(bad()); }
            self.root_seen = true;
        }
        Ok(())
    }

    fn begin_class(&mut self, e: &BytesStart<'_>) -> Result<(), ProviderError> {
        if self.class.is_some() || self.method.is_some() { return Err(bad()); }
        self.class_count += 1;
        if self.class_count > 100_000 { return Err(bad()); }
        let name = required(e, b"name")?;
        if name.is_empty() || !self.classes.insert(name.clone()) { return Err(bad()); }
        self.class = Some(name); Ok(())
    }

    fn begin_method(&mut self, e: &BytesStart<'_>) -> Result<(), ProviderError> {
        if self.stack.last().map(Vec::as_slice) != Some(b"class") || self.class.is_none() || self.method.is_some() { return Err(bad()); }
        self.method_count += 1;
        if self.method_count > 100_000 { return Err(bad()); }
        let name = required(e, b"name")?;
        let descriptor = required(e, b"desc")?;
        if name.is_empty() || !valid_descriptor(&descriptor) { return Err(bad()); }
        let symbol = SymbolIdentity::java_method(self.class.as_ref().unwrap(), name, descriptor);
        if !self.identities.insert(symbol.id().into()) { return Err(bad()); }
        self.method = Some(Method { symbol, counts: [Count::Missing; 4], counter_count: 0, counter_types: HashSet::new() });
        Ok(())
    }

    fn counter(&mut self, e: &BytesStart<'_>) -> Result<(), ProviderError> {
        let method = self.method.as_mut().ok_or_else(bad)?;
        method.counter_count += 1;
        if method.counter_count > 16 { return Err(bad()); }
        let Some(kind) = attr(e, b"type")? else { return Ok(()); };
        if !method.counter_types.insert(kind.clone()) { return Err(bad()); }
        let values = [count(attr(e, b"missed")?.as_deref()), count(attr(e, b"covered")?.as_deref())];
        match kind.as_str() {
            "COMPLEXITY" => method.counts[..2].copy_from_slice(&values),
            "INSTRUCTION" => method.counts[2..].copy_from_slice(&values),
            _ => {}
        }
        Ok(())
    }

    fn end(&mut self, e: &quick_xml::events::BytesEnd<'_>) -> Result<(), ProviderError> {
        let binding = e.name(); let name = binding.as_ref();
        let open = self.stack.pop().ok_or_else(bad)?;
        if open.as_slice() != name { return Err(bad()); }
        match name { b"method" => self.finish(), b"class" => self.class = None, _ => {} }
        Ok(())
    }

    fn finish(&mut self) {
        let Some(method) = self.method.take() else { return; };
        let id = Some(bound_id(method.symbol.id()));
        if method.counts.iter().any(|v| matches!(v, Count::Missing)) { self.diagnose(DiagnosticCode::MissingRequiredCounter, id); return; }
        if method.counts.iter().any(|v| matches!(v, Count::Invalid)) { self.diagnose(DiagnosticCode::InvalidRequiredCounter, id); return; }
        let [Count::Valid(cm), Count::Valid(cc), Count::Valid(im), Count::Valid(ic)] = method.counts else { return; };
        let complexity = cm + cc; let denominator = im + ic;
        if complexity == 0 || denominator == 0 { self.diagnose(DiagnosticCode::ZeroDenominator, id); return; }
        self.symbols.push(SymbolResult { symbol: method.symbol,
            complexity: Some(ComplexityMeasurement { value: complexity as f64, metric: "cyclomatic".into(), semantics: "jacoco-cyclomatic".into(), provider: "jacoco".into() }),
            coverage: Some(CoverageMeasurement { ratio: ic as f64 / denominator as f64, covered: ic, missed: im, metric: "instruction".into(), semantics: "jacoco-instruction".into(), provider: "jacoco".into() }),
            metrics: DerivedMetrics { crap: None } });
    }

    fn diagnose(&mut self, code: DiagnosticCode, symbol_id: Option<String>) {
        if self.diagnostics.len() < 1024 { self.diagnostics.push(Diagnostic { code, symbol_id }); }
    }
}

#[rustfmt::skip]
fn attr(e: &BytesStart<'_>, wanted: &[u8]) -> Result<Option<String>, ProviderError> {
    let mut seen = HashSet::new(); let mut found = None;
    for item in e.attributes() {
        if seen.len() >= 64 { return Err(bad()); }
        let a = item.map_err(|_| bad())?; let key = a.key.as_ref(); let raw = a.value.as_ref();
        if key.len() > 4096 || raw.len() > 4096 || !seen.insert(key.to_vec()) || forbidden(raw) { return Err(bad()); }
        let value = a
            .normalized_value(quick_xml::XmlVersion::Implicit1_0)
            .map_err(|_| bad())?
            .into_owned();
        if value.len() > 4096 || value.contains('&') { return Err(bad()); }
        if key == wanted { found = Some(value); }
    }
    Ok(found)
}

#[rustfmt::skip]
fn required(e: &BytesStart<'_>, name: &[u8]) -> Result<String, ProviderError> {
    attr(e, name)?.filter(|v| !v.is_empty()).ok_or_else(bad)
}

#[rustfmt::skip]
fn count(value: Option<&str>) -> Count {
    let Some(value) = value else { return Count::Missing; }; let bytes = value.as_bytes();
    if bytes.is_empty() || bytes.len() > 10 || (bytes.len() > 1 && bytes[0] == b'0') || !bytes.iter().all(u8::is_ascii_digit) { return Count::Invalid; }
    match value.parse::<u64>() { Ok(value) if value <= 1_000_000_000 => Count::Valid(value), _ => Count::Invalid }
}

#[rustfmt::skip]
fn forbidden(value: &[u8]) -> bool {
    let allowed = [b"&lt;".as_slice(), b"&gt;", b"&amp;", b"&apos;", b"&quot;"]; let mut i = 0;
    while i < value.len() { if value[i] != b'&' { i += 1; continue; } let Some(entity) = allowed.iter().find(|e| value[i..].starts_with(e)) else { return true; }; i += entity.len(); }
    false
}

#[rustfmt::skip]
fn bound_id(id: &str) -> String { if id.len() <= 256 { id.into() } else { id.chars().take(256).collect() } }

#[rustfmt::skip]
fn valid_descriptor(value: &str) -> bool {
    let b = value.as_bytes(); if b.first() != Some(&b'(') { return false; } let mut i = 1; let mut parameter_slots = 0usize;
    while i < b.len() && b[i] != b')' { let parameter_start = i; if !field_type(b, &mut i) { return false; } let slots = match b.get(parameter_start) { Some(b'J') | Some(b'D') => 2, Some(b'[') => 1, Some(_) => 1, None => return false }; if parameter_slots + slots > 255 { return false; } parameter_slots += slots; }
    if b.get(i) != Some(&b')') { return false; } i += 1;
    if b.get(i) == Some(&b'V') { i += 1; } else if !field_type(b, &mut i) { return false; } i == b.len()
}

#[rustfmt::skip]
fn field_type(b: &[u8], i: &mut usize) -> bool {
    let mut dimensions = 0; while b.get(*i) == Some(&b'[') { *i += 1; dimensions += 1; if dimensions > 255 { return false; } }
    let Some(byte) = b.get(*i).copied() else { return false; };
    if b"BCDFIJSZ".contains(&byte) { *i += 1; return true; } else if byte != b'L' { return false; }
    *i += 1; let start = *i;
    while let Some(byte) = b.get(*i) { if *byte == b';' { let name = &b[start..*i]; *i += 1; return !name.is_empty() && name.iter().all(|c| !b".;[]() \t\r\n".contains(c)); } *i += 1; }
    false
}
