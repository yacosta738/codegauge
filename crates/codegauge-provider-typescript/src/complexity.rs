use crate::{
    callable::{Callable, SourceSpan, collect_callables},
    parser::ParsedSource,
};
use oxc_ast::ast::{
    CatchClause, ConditionalExpression, DoWhileStatement, ForInStatement, ForOfStatement,
    ForStatement, IfStatement, LogicalExpression, SwitchCase, WhileStatement,
};
use oxc_ast_visit::{Visit, walk};
use oxc_span::Span;
use oxc_syntax::operator::LogicalOperator;

/// Calculate classic McCabe v1 complexity for a single callable.
pub fn calculate_complexity(parsed: &ParsedSource<'_>, callable: &Callable) -> u32 {
    let nested_bodies = collect_callables(parsed, &callable.path)
        .into_iter()
        .map(|nested| nested.body_span)
        .filter(|body| *body != callable.body_span)
        .filter(|body| contains(callable.body_span, *body))
        .collect();
    let mut visitor = ComplexityVisitor {
        target: callable.body_span,
        nested_bodies,
        value: 1,
    };
    visitor.visit_program(&parsed.program);
    visitor.value
}

struct ComplexityVisitor {
    target: SourceSpan,
    nested_bodies: Vec<SourceSpan>,
    value: u32,
}

impl ComplexityVisitor {
    fn count(&mut self, span: Span) {
        let span = SourceSpan {
            start: span.start,
            end: span.end,
        };
        if contains(self.target, span)
            && !self
                .nested_bodies
                .iter()
                .copied()
                .any(|nested| contains(nested, span))
        {
            self.value = self.value.saturating_add(1);
        }
    }
}

impl<'a> Visit<'a> for ComplexityVisitor {
    fn visit_if_statement(&mut self, statement: &IfStatement<'a>) {
        self.count(statement.span);
        walk::walk_if_statement(self, statement);
    }

    fn visit_do_while_statement(&mut self, statement: &DoWhileStatement<'a>) {
        self.count(statement.span);
        walk::walk_do_while_statement(self, statement);
    }

    fn visit_for_statement(&mut self, statement: &ForStatement<'a>) {
        self.count(statement.span);
        walk::walk_for_statement(self, statement);
    }

    fn visit_for_in_statement(&mut self, statement: &ForInStatement<'a>) {
        self.count(statement.span);
        walk::walk_for_in_statement(self, statement);
    }

    fn visit_for_of_statement(&mut self, statement: &ForOfStatement<'a>) {
        self.count(statement.span);
        walk::walk_for_of_statement(self, statement);
    }

    fn visit_while_statement(&mut self, statement: &WhileStatement<'a>) {
        self.count(statement.span);
        walk::walk_while_statement(self, statement);
    }

    fn visit_switch_case(&mut self, case: &SwitchCase<'a>) {
        if case.test.is_some() {
            self.count(case.span);
        }
        walk::walk_switch_case(self, case);
    }

    fn visit_catch_clause(&mut self, clause: &CatchClause<'a>) {
        self.count(clause.span);
        walk::walk_catch_clause(self, clause);
    }

    fn visit_logical_expression(&mut self, expression: &LogicalExpression<'a>) {
        if matches!(
            expression.operator,
            LogicalOperator::And | LogicalOperator::Or
        ) {
            self.count(expression.span);
        }
        walk::walk_logical_expression(self, expression);
    }

    fn visit_conditional_expression(&mut self, expression: &ConditionalExpression<'a>) {
        self.count(expression.span);
        walk::walk_conditional_expression(self, expression);
    }
}

fn contains(outer: SourceSpan, inner: SourceSpan) -> bool {
    inner.start >= outer.start && inner.end <= outer.end
}
