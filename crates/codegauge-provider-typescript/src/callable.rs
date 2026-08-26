use crate::parser::ParsedSource;
use oxc_ast::ast::{
    ArrowFunctionExpression, Expression, Function, MethodDefinition, MethodDefinitionKind,
    ObjectProperty, PropertyKey, PropertyKind,
};
use oxc_ast_visit::{Visit, walk};
use oxc_span::{GetSpan, Span as OxcSpan};
use oxc_syntax::scope::ScopeFlags;
use std::{collections::HashSet, path::Path};

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub enum CallableKind {
    Function,
    Arrow,
    Method,
    Constructor,
    Getter,
    Setter,
}

impl CallableKind {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Function => "function",
            Self::Arrow => "arrow",
            Self::Method => "method",
            Self::Constructor => "constructor",
            Self::Getter => "getter",
            Self::Setter => "setter",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub struct SourceSpan {
    pub start: u32,
    pub end: u32,
}

impl From<OxcSpan> for SourceSpan {
    fn from(span: OxcSpan) -> Self {
        Self {
            start: span.start,
            end: span.end,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Callable {
    pub path: String,
    pub name: String,
    pub kind: CallableKind,
    pub span: SourceSpan,
    pub body_span: SourceSpan,
}

impl Callable {
    pub fn id(&self) -> String {
        format!(
            "typescript:{}#{}@{}-{}",
            self.path, self.name, self.span.start, self.span.end
        )
    }
}

/// Collect executable functions and class methods in deterministic source order.
pub fn collect_callables(parsed: &ParsedSource<'_>, path: impl AsRef<Path>) -> Vec<Callable> {
    let mut visitor = CallableVisitor {
        path: normalize_path(path.as_ref()),
        callables: Vec::new(),
    };
    visitor.visit_program(&parsed.program);

    let method_bodies: HashSet<_> = visitor
        .callables
        .iter()
        .filter(|callable| {
            matches!(
                callable.kind,
                CallableKind::Method
                    | CallableKind::Constructor
                    | CallableKind::Getter
                    | CallableKind::Setter
            )
        })
        .map(|callable| callable.body_span)
        .collect();

    visitor.callables.retain(|callable| {
        !(callable.kind == CallableKind::Function && method_bodies.contains(&callable.body_span))
    });
    visitor.callables.sort_by(|left, right| {
        left.span
            .cmp(&right.span)
            .then_with(|| left.kind.cmp(&right.kind))
            .then_with(|| left.name.as_bytes().cmp(right.name.as_bytes()))
    });
    visitor.callables
}

pub fn normalize_path(path: &Path) -> String {
    path.to_string_lossy().replace('\\', "/")
}

struct CallableVisitor {
    path: String,
    callables: Vec<Callable>,
}

impl<'a> Visit<'a> for CallableVisitor {
    fn visit_function(&mut self, function: &Function<'a>, flags: ScopeFlags) {
        if let Some(body) = function.body.as_ref() {
            self.callables.push(Callable {
                path: self.path.clone(),
                name: function
                    .id
                    .as_ref()
                    .map(|id| id.name.as_str().to_owned())
                    .unwrap_or_else(|| "<anonymous>".into()),
                kind: CallableKind::Function,
                span: function.span.into(),
                body_span: body.span.into(),
            });
        }
        walk::walk_function(self, function, flags);
    }

    fn visit_arrow_function_expression(&mut self, arrow: &ArrowFunctionExpression<'a>) {
        self.callables.push(Callable {
            path: self.path.clone(),
            name: "<arrow>".into(),
            kind: CallableKind::Arrow,
            span: arrow.span.into(),
            body_span: arrow.body.span().into(),
        });
        walk::walk_arrow_function_expression(self, arrow);
    }

    fn visit_method_definition(&mut self, method: &MethodDefinition<'a>) {
        if let Some(body) = method.value.body.as_ref() {
            self.push_callable(
                property_key_name(&method.key),
                method_kind(method.kind),
                method.span.into(),
                body.span.into(),
            );
        }
        walk::walk_method_definition(self, method);
    }

    fn visit_object_property(&mut self, property: &ObjectProperty<'a>) {
        if let Expression::FunctionExpression(function) = &property.value {
            let kind = match property.kind {
                PropertyKind::Get => Some(CallableKind::Getter),
                PropertyKind::Set => Some(CallableKind::Setter),
                PropertyKind::Init if property.method => Some(CallableKind::Method),
                PropertyKind::Init => None,
            };
            if let (Some(kind), Some(body)) = (kind, function.body.as_ref()) {
                self.push_callable(
                    property_key_name(&property.key),
                    kind,
                    property.span.into(),
                    body.span.into(),
                );
            }
        }
        walk::walk_object_property(self, property);
    }
}

impl CallableVisitor {
    fn push_callable(
        &mut self,
        name: String,
        kind: CallableKind,
        span: SourceSpan,
        body_span: SourceSpan,
    ) {
        self.callables.push(Callable {
            path: self.path.clone(),
            name,
            kind,
            span,
            body_span,
        });
    }
}

fn method_kind(kind: MethodDefinitionKind) -> CallableKind {
    match kind {
        MethodDefinitionKind::Constructor => CallableKind::Constructor,
        MethodDefinitionKind::Method => CallableKind::Method,
        MethodDefinitionKind::Get => CallableKind::Getter,
        MethodDefinitionKind::Set => CallableKind::Setter,
    }
}

fn property_key_name<'a>(key: &PropertyKey<'a>) -> String {
    match key {
        PropertyKey::StaticIdentifier(identifier) => identifier.name.as_str().to_owned(),
        PropertyKey::PrivateIdentifier(identifier) => {
            format!("#{}", identifier.name.as_str())
        }
        PropertyKey::StringLiteral(literal) => literal.value.as_str().to_owned(),
        _ => "<computed>".into(),
    }
}
