#![forbid(unsafe_code)]

use clap::{Parser, Subcommand};
use codegauge_application::{
    AnalysisError, Analyzer, FsArtifactReader, ProviderRegistry, TOOL_NAME, TOOL_VERSION,
    canonical_error_json, canonical_result_json, exit_code_for_error, profile_id,
};
use codegauge_model::{
    AnalysisInput, AnalysisStatus, InputRole, JVM_JACOCO_V1, TYPESCRIPT_OXC_ISTANBUL_V1,
};
use codegauge_provider_jacoco::JacocoProvider;
use codegauge_provider_typescript::TypescriptProvider;
use std::process;

#[derive(Debug, Parser)]
#[command(name = "codegauge", disable_version_flag = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,
}
#[derive(Debug, Subcommand)]
enum Command {
    Analyze {
        #[arg(long)]
        profile: String,
        #[arg(long, action = clap::ArgAction::Append)]
        input: Vec<String>,
        #[arg(long)]
        format: String,
    },
    Profiles,
    Version,
}

fn main() {
    process::exit(run());
}
fn run() -> i32 {
    let cli = match Cli::try_parse() {
        Ok(cli) => cli,
        Err(error) => {
            eprintln!("{error}");
            return emit_error(AnalysisError::cli("invalid command arguments"));
        }
    };
    match cli.command {
        Some(Command::Profiles) => {
            println!("{JVM_JACOCO_V1}\n{TYPESCRIPT_OXC_ISTANBUL_V1}");
            0
        }
        Some(Command::Version) => {
            println!("{TOOL_NAME} {TOOL_VERSION}");
            0
        }
        Some(Command::Analyze {
            profile,
            input,
            format,
        }) => analyze(profile, input, format),
        None => emit_error(AnalysisError::cli("a command is required")),
    }
}
fn analyze(profile: String, raw_inputs: Vec<String>, format: String) -> i32 {
    if format != "json" {
        eprintln!("unsupported output format: {format}");
        return emit_error(AnalysisError::cli("only json output is supported"));
    }
    let Some(profile) = profile_id(&profile) else {
        return emit_error(AnalysisError::unsupported_profile(profile));
    };
    let inputs = match raw_inputs
        .iter()
        .map(|value| parse_input(value))
        .collect::<Result<Vec<_>, _>>()
    {
        Ok(inputs) => inputs,
        Err(error) => {
            eprintln!("{}", error.message());
            return emit_error(error);
        }
    };
    let mut registry = ProviderRegistry::new();
    registry.register(JacocoProvider::new());
    registry.register(TypescriptProvider::new());
    match Analyzer::new(FsArtifactReader, registry)
        .analyze_with_diagnostics(profile, inputs.as_slice())
    {
        Ok((result, diagnostics)) => {
            for diagnostic in diagnostics {
                eprintln!("diagnostic: {diagnostic:?}");
            }
            print!("{}", canonical_result_json(&result));
            if result.analysis.status == AnalysisStatus::Partial {
                6
            } else {
                0
            }
        }
        Err(error) => {
            eprintln!("{}", error.message());
            emit_error(error)
        }
    }
}
fn parse_input(value: &str) -> Result<AnalysisInput, AnalysisError> {
    let Some((role, path)) = value.split_once('=') else {
        return Err(AnalysisError::cli("input must use ROLE=PATH syntax"));
    };
    if role.is_empty() || path.trim().is_empty() {
        return Err(AnalysisError::cli("input must use ROLE=PATH syntax"));
    }
    let role = role
        .parse::<InputRole>()
        .map_err(|error| AnalysisError::cli(error.to_string()))?;
    Ok(AnalysisInput {
        role,
        path: path.into(),
    })
}
fn emit_error(error: AnalysisError) -> i32 {
    print!("{}", canonical_error_json(&error.document()));
    exit_code_for_error(error.code())
}
