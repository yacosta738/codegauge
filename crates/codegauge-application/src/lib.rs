#![forbid(unsafe_code)]

//! Generic artifact orchestration and canonical result serialization.

#[rustfmt::skip]
mod implementation {
use codegauge_core::{CrapInput,calculate_crap};
use codegauge_model::{Analysis,AnalysisInput,AnalysisStatus,CrapSummary,DerivedMetrics,ErrorCode,ErrorDetails,ErrorDocument,ErrorSchemaId,InputArtifact,InputRole,NamedInputArtifact,ProfileId,Provenance,ResultDocument,ResultSchemaId,Sha256Digest,Summary,SymbolResult,ToolInfo,ERROR_SCHEMA_V1,JVM_JACOCO_V1,RESULT_SCHEMA_V1,TYPESCRIPT_OXC_ISTANBUL_V1};
use sha2::{Digest,Sha256};
use std::{collections::{BTreeMap,BTreeSet},fmt,fs::File,io::{self,Read},path::{Path,PathBuf},time::{SystemTime,UNIX_EPOCH}};

pub const TOOL_NAME:&str="codegauge"; pub const TOOL_VERSION:&str=env!("CARGO_PKG_VERSION"); pub const MAX_INPUT_BYTES:usize=64*1024*1024;
#[derive(Clone,Debug,Eq,PartialEq)] pub enum DiagnosticCode{MissingRequiredCounter,InvalidRequiredCounter,ZeroDenominator}
#[derive(Clone,Debug,Eq,PartialEq)] pub struct Diagnostic{pub code:DiagnosticCode,pub symbol_id:Option<String>}
#[derive(Clone,Debug,PartialEq)] pub struct ProviderObservations{pub symbols:Vec<SymbolResult>,pub diagnostics:Vec<Diagnostic>}
#[derive(Clone,Copy,Debug,Eq,PartialEq)] pub enum ProviderError{InvalidInput{message:&'static str}}
#[derive(Clone,Debug,Eq,PartialEq)] pub struct Artifact{pub path:String,pub bytes:Vec<u8>,pub sha256:Sha256Digest}
#[derive(Clone,Debug,Eq,PartialEq)] pub enum ArtifactError{InputNotFound(String),TooLarge(String),Unreadable(String)}
#[derive(Clone,Copy,Debug,Eq,PartialEq)] pub enum InputCardinality{ExactlyOne,OneOrMore}
#[derive(Clone,Copy,Debug,Eq,PartialEq)] pub struct InputRequirement{pub role:InputRole,pub cardinality:InputCardinality}
#[derive(Clone,Debug,Eq,PartialEq)] pub enum InputSetError{EmptyPath{role:InputRole},Duplicate{role:InputRole,path:String},UnknownRole{role:String},UndeclaredRole{role:InputRole},MissingRequired{role:InputRole},TooManyInputs{role:InputRole,count:usize}}
impl fmt::Display for InputSetError{fn fmt(&self,formatter:&mut fmt::Formatter<'_>)->fmt::Result{match self{Self::EmptyPath{role}=>write!(formatter,"empty input path for role {role}"),Self::Duplicate{role,path}=>write!(formatter,"duplicate input: {role}={path}"),Self::UnknownRole{role}=>write!(formatter,"unknown input role: {role}"),Self::UndeclaredRole{role}=>write!(formatter,"input role is not declared by provider: {role}"),Self::MissingRequired{role}=>write!(formatter,"missing required input: {role}"),Self::TooManyInputs{role,count}=>write!(formatter,"too many inputs for role {role}: {count}")}}}
impl std::error::Error for InputSetError{}
#[derive(Clone,Debug,Default,Eq,PartialEq)] pub struct InputSet{by_role:BTreeMap<InputRole,Vec<Artifact>>}
#[allow(clippy::possible_missing_else)]
impl InputSet{pub fn from_artifacts<I>(entries:I)->Result<Self,InputSetError> where I:IntoIterator<Item=(AnalysisInput,Artifact)>{let mut by_role=BTreeMap::new();let mut seen_inputs=BTreeSet::new();let mut seen=BTreeSet::new();for(input,mut artifact)in entries{let input_path=normalize_path(Path::new(&input.path));if input.path.trim().is_empty()||input_path.is_empty(){return Err(InputSetError::EmptyPath{role:input.role});}
if !seen_inputs.insert((input.role,input_path.clone())){return Err(InputSetError::Duplicate{role:input.role,path:input_path});}let path=normalize_path(Path::new(&artifact.path));if path.is_empty(){return Err(InputSetError::EmptyPath{role:input.role});}if !seen.insert((input.role,path.clone())){return Err(InputSetError::Duplicate{role:input.role,path});}artifact.path=path;by_role.entry(input.role).or_insert_with(Vec::new).push(artifact);}for artifacts in by_role.values_mut(){artifacts.sort_by(|a,b|a.path.as_bytes().cmp(b.path.as_bytes()));}Ok(Self{by_role})}pub fn get(&self,role:InputRole)->&[Artifact]{self.by_role.get(&role).map(Vec::as_slice).unwrap_or(&[])}pub fn iter(&self)->impl Iterator<Item=(InputRole,&Artifact)>{self.by_role.iter().flat_map(|(role,artifacts)|artifacts.iter().map(move|artifact|(*role,artifact)))}pub fn validate(&self,requirements:&[InputRequirement])->Result<(),InputSetError>{let declared=requirements.iter().map(|requirement|requirement.role).collect::<BTreeSet<_>>();if let Some(role)=self.by_role.keys().find(|role|!declared.contains(role)){return Err(InputSetError::UndeclaredRole{role:*role});}for requirement in requirements{let count=self.get(requirement.role).len();match(requirement.cardinality,count){(InputCardinality::ExactlyOne,0)|(InputCardinality::OneOrMore,0)=>return Err(InputSetError::MissingRequired{role:requirement.role}),(InputCardinality::ExactlyOne,count)if count>1=>return Err(InputSetError::TooManyInputs{role:requirement.role,count}),_=>{}}}Ok(())}pub fn primary(&self,role:InputRole)->Option<&Artifact>{self.get(role).first()}}
pub trait ArtifactReader{fn read(&self,path:&Path)->Result<Artifact,ArtifactError>;} #[derive(Clone,Copy,Debug,Default,Eq,PartialEq)] pub struct FsArtifactReader;
#[derive(Clone,Copy,Debug,Eq,PartialEq)] pub(crate) enum BoundedReadError{TooLarge,Io}
pub(crate) fn read_bounded<R:Read>(reader:R,max:usize)->Result<Vec<u8>,BoundedReadError>{let mut bytes=Vec::new();reader.take((max as u64).saturating_add(1)).read_to_end(&mut bytes).map_err(|_|BoundedReadError::Io)?;if bytes.len()>max{Err(BoundedReadError::TooLarge)}else{Ok(bytes)}}
impl ArtifactReader for FsArtifactReader{fn read(&self,path:&Path)->Result<Artifact,ArtifactError>{let shown=normalize_path(path);let file=File::open(path).map_err(|error|if error.kind()==io::ErrorKind::NotFound{ArtifactError::InputNotFound(shown.clone())}else{ArtifactError::Unreadable(shown.clone())})?;let metadata=file.metadata().map_err(|_|ArtifactError::Unreadable(shown.clone()))?;if !metadata.is_file(){return Err(ArtifactError::Unreadable(shown));}let bytes=match read_bounded(file,MAX_INPUT_BYTES){Ok(bytes)=>bytes,Err(BoundedReadError::TooLarge)=>return Err(ArtifactError::TooLarge(shown)),Err(BoundedReadError::Io)=>return Err(ArtifactError::Unreadable(shown))};let sha256=sha256_hex(&bytes);Ok(Artifact{path:shown,bytes,sha256})}}
pub fn normalize_path(path:&Path)->String{path.to_string_lossy().replace('\\',"/")}
pub fn sha256_hex(bytes:&[u8])->Sha256Digest{let digest=Sha256::digest(bytes);let mut out=String::with_capacity(64);for byte in digest{out.push_str(&format!("{byte:02x}"));}Sha256Digest::new(out).expect("SHA-256 output is always a lowercase 64-character digest")}
#[derive(Clone,Debug,Eq,PartialEq)] pub struct ProfileDescriptor{pub profile:ProfileId,pub provider:String,pub semantics:Vec<String>,pub required_inputs:Vec<InputRequirement>}
pub struct CollectionRequest<'a>{pub inputs:&'a InputSet} impl<'a> CollectionRequest<'a>{pub fn new(inputs:&'a InputSet)->Self{Self{inputs}}pub fn validated(inputs:&'a InputSet,requirements:&[InputRequirement])->Result<Self,InputSetError>{inputs.validate(requirements)?;Ok(Self::new(inputs))}} pub trait MetricProvider{fn descriptor(&self)->ProfileDescriptor;fn collect(&self,request:CollectionRequest<'_>)->Result<ProviderObservations,ProviderError>;} #[derive(Default)] pub struct ProviderRegistry{providers:Vec<Box<dyn MetricProvider>>}
impl ProviderRegistry{pub fn new()->Self{Self::default()} pub fn register<P:MetricProvider+'static>(&mut self,p:P){self.providers.push(Box::new(p));}pub fn select(&self,profile:ProfileId)->Option<&dyn MetricProvider>{self.providers.iter().map(|p|p.as_ref()).find(|p|p.descriptor().profile==profile)}}
#[derive(Clone,Debug,Eq,PartialEq)] pub struct AnalysisError{code:ErrorCode,message:String,details:ErrorDetails}
impl AnalysisError{fn new(code:ErrorCode,message:impl Into<String>,path:Option<String>,sha256:Option<Sha256Digest>)->Self{Self{code,message:message.into(),details:ErrorDetails{path,sha256}}}pub fn unsupported_profile(p:impl Into<String>)->Self{let p=p.into();Self::new(ErrorCode::UnsupportedProfile,format!("unsupported profile: {p}"),None,None)}fn invalid(a:&Artifact,m:impl Into<String>)->Self{Self::new(ErrorCode::InvalidInput,m,Some(a.path.clone()),Some(a.sha256.clone()))}fn incompatible(a:&Artifact)->Self{Self::new(ErrorCode::IncompatibleMeasurements,"no compatible measurements",Some(a.path.clone()),Some(a.sha256.clone()))}fn not_found(p:String)->Self{Self::new(ErrorCode::InputNotFound,"input not found or unreadable",Some(p),None)}pub fn cli(m:impl Into<String>)->Self{Self::new(ErrorCode::CliError,m,None,None)}pub fn internal(m:impl Into<String>)->Self{Self::new(ErrorCode::InternalError,m,None,None)}pub fn code(&self)->ErrorCode{self.code}pub fn message(&self)->&str{&self.message}pub fn details(&self)->&ErrorDetails{&self.details}pub fn document(&self)->ErrorDocument{ErrorDocument{schema:ErrorSchemaId::V1,tool:ToolInfo{name:TOOL_NAME.into(),version:TOOL_VERSION.into()},code:self.code,message:self.message.clone(),details:self.details.clone()}}}
  pub fn profile_id(name:&str)->Option<ProfileId>{match name{JVM_JACOCO_V1=>Some(ProfileId::JvmJacocoV1),TYPESCRIPT_OXC_ISTANBUL_V1=>Some(ProfileId::TypescriptOxcIstanbulV1),_=>None}} pub fn exit_code_for_error(c:ErrorCode)->i32{match c{ErrorCode::CliError=>2,ErrorCode::InputNotFound=>3,ErrorCode::UnsupportedProfile|ErrorCode::UnsupportedProvider=>4,ErrorCode::InvalidInput=>5,ErrorCode::IncompatibleMeasurements=>6,ErrorCode::InternalError=>10}}
pub trait AnalysisInputSource {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool);
}

impl AnalysisInputSource for &Path {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool) {
        (
            vec![AnalysisInput {
                role: InputRole::Coverage,
                path: self.to_string_lossy().into_owned(),
            }],
            true,
        )
    }
}

impl AnalysisInputSource for &PathBuf {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool) {
        self.as_path().into_analysis_inputs()
    }
}

impl AnalysisInputSource for &[AnalysisInput] {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool) {
        (self.to_vec(), false)
    }
}

impl<const N: usize> AnalysisInputSource for &[AnalysisInput; N] {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool) {
        self.as_slice().into_analysis_inputs()
    }
}

impl AnalysisInputSource for &Vec<AnalysisInput> {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool) {
        self.as_slice().into_analysis_inputs()
    }
}

impl AnalysisInputSource for Vec<AnalysisInput> {
    fn into_analysis_inputs(self) -> (Vec<AnalysisInput>, bool) {
        (self, false)
    }
}

pub struct Analyzer<R> {
    reader: R,
    registry: ProviderRegistry,
}

impl<R: ArtifactReader> Analyzer<R> {
    pub fn new(reader: R, registry: ProviderRegistry) -> Self {
        Self { reader, registry }
    }

    pub fn analyze<I: AnalysisInputSource>(
        &self,
        profile: ProfileId,
        inputs: I,
    ) -> Result<ResultDocument, AnalysisError> {
        self.analyze_with_diagnostics(profile, inputs)
            .map(|(result, _)| result)
    }

    pub fn analyze_with_diagnostics<I: AnalysisInputSource>(
        &self,
        profile: ProfileId,
        inputs: I,
    ) -> Result<(ResultDocument, Vec<Diagnostic>), AnalysisError> {
        let (inputs, legacy_provenance) = inputs.into_analysis_inputs();
        self.analyze_collected(profile, inputs, legacy_provenance)
    }

    pub fn analyze_inputs(
        &self,
        profile: ProfileId,
        inputs: &[AnalysisInput],
    ) -> Result<ResultDocument, AnalysisError> {
        self.analyze(profile, inputs)
    }

    pub fn analyze_with_diagnostics_inputs(
        &self,
        profile: ProfileId,
        inputs: &[AnalysisInput],
    ) -> Result<(ResultDocument, Vec<Diagnostic>), AnalysisError> {
        self.analyze_with_diagnostics(profile, inputs)
    }

    fn analyze_collected(
        &self,
        profile: ProfileId,
        inputs: Vec<AnalysisInput>,
        legacy_provenance: bool,
    ) -> Result<(ResultDocument, Vec<Diagnostic>), AnalysisError> {
        let provider = self
            .registry
            .select(profile)
            .ok_or_else(|| AnalysisError::unsupported_profile(format!("{profile:?}")))?;
        let descriptor = provider.descriptor();
        let inputs = sort_inputs(inputs).map_err(|error| {
            AnalysisError::new(ErrorCode::InvalidInput, error.to_string(), None, None)
        })?;
        validate_input_requirements(&inputs, &descriptor.required_inputs).map_err(|error| {
            AnalysisError::new(ErrorCode::InvalidInput, error.to_string(), None, None)
        })?;
        let mut entries = Vec::with_capacity(inputs.len());
        for input in &inputs {
            let artifact = self.reader.read(Path::new(&input.path)).map_err(|error| {
                match error {
                    ArtifactError::InputNotFound(path) | ArtifactError::Unreadable(path) => {
                        AnalysisError::not_found(path)
                    }
                    ArtifactError::TooLarge(path) => AnalysisError::new(
                        ErrorCode::InvalidInput,
                        "input exceeds 64 MiB",
                        Some(path),
                        None,
                    ),
                }
            })?;
            entries.push((input.clone(), artifact));
        }
        let input_set = InputSet::from_artifacts(entries).map_err(|error| {
            AnalysisError::new(ErrorCode::InvalidInput, error.to_string(), None, None)
        })?;
        let request = CollectionRequest::validated(&input_set, &descriptor.required_inputs)
            .map_err(|error| {
                AnalysisError::new(ErrorCode::InvalidInput, error.to_string(), None, None)
            })?;
        let primary = input_set
            .primary(InputRole::Coverage)
            .or_else(|| input_set.iter().map(|(_, artifact)| artifact).next())
            .ok_or_else(|| AnalysisError::new(ErrorCode::InvalidInput, "no inputs", None, None))?;
        let observations = provider.collect(request).map_err(|error| match error {
            ProviderError::InvalidInput { message } => AnalysisError::invalid(primary, message),
        })?;
        let mut diagnostics = observations.diagnostics;
        let mut symbols = Vec::with_capacity(observations.symbols.len());
        for mut symbol in observations.symbols {
            symbol.metrics = DerivedMetrics { crap: None };
            let Some(complexity) = symbol.complexity.as_ref() else {
                diagnostics.push(Diagnostic {
                    code: DiagnosticCode::MissingRequiredCounter,
                    symbol_id: Some(symbol.symbol.id().into()),
                });
                continue;
            };
            let Some(coverage) = symbol.coverage.as_ref() else {
                diagnostics.push(Diagnostic {
                    code: DiagnosticCode::MissingRequiredCounter,
                    symbol_id: Some(symbol.symbol.id().into()),
                });
                continue;
            };
            let score = calculate_crap(CrapInput {
                cyclomatic_complexity: complexity.value,
                coverage: coverage.ratio,
            })
            .map_err(|_| AnalysisError::invalid(primary, "incompatible metric values"))?;
            symbol.metrics.crap = Some(score.value());
            symbols.push(symbol);
        }
        if symbols.is_empty() {
            return Err(AnalysisError::incompatible(primary));
        }
        symbols.sort_by(|a, b| a.symbol.id().as_bytes().cmp(b.symbol.id().as_bytes()));
        let scores: Vec<f64> = symbols.iter().filter_map(|symbol| symbol.metrics.crap).collect();
        let max = scores
            .iter()
            .copied()
            .reduce(f64::max)
            .ok_or_else(|| AnalysisError::incompatible(primary))?;
        let mean = scores.iter().sum::<f64>() / scores.len() as f64;
        if !mean.is_finite() {
            return Err(AnalysisError::internal("non-finite summary"));
        }
        let role_inputs = if legacy_provenance {
            Vec::new()
        } else {
            input_set
                .iter()
                .map(|(role, artifact)| NamedInputArtifact {
                    role,
                    path: artifact.path.clone(),
                    sha256: artifact.sha256.clone(),
                })
                .collect()
        };
        let result = ResultDocument {
            schema: ResultSchemaId::V1,
            tool: ToolInfo {
                name: TOOL_NAME.into(),
                version: TOOL_VERSION.into(),
            },
            profile,
            analysis: Analysis {
                status: if diagnostics.is_empty() {
                    AnalysisStatus::Complete
                } else {
                    AnalysisStatus::Partial
                },
                symbols: symbols.len() as u64,
            },
            summary: Summary {
                crap: CrapSummary {
                    max: Some(max),
                    mean: Some(mean),
                },
            },
            symbols,
            provenance: Provenance {
                provider: descriptor.provider,
                semantics: descriptor.semantics,
                input: InputArtifact {
                    path: primary.path.clone(),
                    sha256: primary.sha256.clone(),
                },
                inputs: role_inputs,
                analysis_timestamp: format_timestamp(SystemTime::now()),
            },
        };
        Ok((result, diagnostics))
    }
}

fn sort_inputs(mut inputs: Vec<AnalysisInput>) -> Result<Vec<AnalysisInput>, InputSetError> {
    for input in &inputs {
        if input.path.trim().is_empty() || normalize_path(Path::new(&input.path)).is_empty() {
            return Err(InputSetError::EmptyPath { role: input.role });
        }
    }
    inputs.sort_by(|left, right| {
        left.role
            .cmp(&right.role)
            .then_with(|| {
                normalize_path(Path::new(&left.path))
                    .as_bytes()
                    .cmp(normalize_path(Path::new(&right.path)).as_bytes())
            })
    });
    for pair in inputs.windows(2) {
        let left = &pair[0];
        let right = &pair[1];
        let left_path = normalize_path(Path::new(&left.path));
        let right_path = normalize_path(Path::new(&right.path));
        if left.role == right.role && left_path == right_path {
            return Err(InputSetError::Duplicate {
                role: left.role,
                path: left_path,
            });
        }
    }
    Ok(inputs)
}

fn validate_input_requirements(
    inputs: &[AnalysisInput],
    requirements: &[InputRequirement],
) -> Result<(), InputSetError> {
    let declared = requirements
        .iter()
        .map(|requirement| requirement.role)
        .collect::<BTreeSet<_>>();
    let mut counts = BTreeMap::new();
    for input in inputs {
        if !declared.contains(&input.role) {
            return Err(InputSetError::UndeclaredRole { role: input.role });
        }
        *counts.entry(input.role).or_insert(0usize) += 1;
    }
    for requirement in requirements {
        let count = counts.get(&requirement.role).copied().unwrap_or(0);
        match (requirement.cardinality, count) {
            (InputCardinality::ExactlyOne, 0) | (InputCardinality::OneOrMore, 0) => {
                return Err(InputSetError::MissingRequired {
                    role: requirement.role,
                });
            }
            (InputCardinality::ExactlyOne, count) if count > 1 => {
                return Err(InputSetError::TooManyInputs {
                    role: requirement.role,
                    count,
                });
            }
            _ => {}
        }
    }
    Ok(())
}
pub fn format_timestamp(t:SystemTime)->String{let s=t.duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();let days=(s/86400)as i64;let ds=s%86400;let z=days+719468;let era=(if z>=0{z}else{z-146096})/146097;let doe=z-era*146097;let yoe=(doe-doe/1460+doe/36524-doe/146096)/365;let y=yoe+era*400;let doy=doe-(365*yoe+yoe/4-yoe/100);let mp=(5*doy+2)/153;let d=doy-(153*mp+2)/5+1;let m=mp+if mp<10{3}else{-9};let year=y+if m<=2{1}else{0};format!("{year:04}-{m:02}-{d:02}T{:02}:{:02}:{:02}Z",ds/3600,(ds/60)%60,ds%60)}
pub fn format_canonical_number(v:f64)->String{assert!(v.is_finite());let mut s=format!("{v:.12}");if s=="-0.000000000000"{return "0".into();}
if s.contains('.') {while s.ends_with('0'){s.pop();}if s.ends_with('.'){s.pop();}
if s=="-0"{return "0".into();}}
s}
fn quote(s:&str,o:&mut String){o.push_str(&serde_json::to_string(s).unwrap());}fn num(v:f64,o:&mut String){o.push_str(&format_canonical_number(v));}fn opt(k:&str,v:Option<f64>,o:&mut String){if let Some(v)=v{o.push_str(k);num(v,o);}}
  pub fn canonical_result_json(d:&ResultDocument)->String{let mut o=String::from("{\"schema\":");quote(RESULT_SCHEMA_V1,&mut o);o.push_str(",\"tool\":{\"name\":");quote(&d.tool.name,&mut o);o.push_str(",\"version\":");quote(&d.tool.version,&mut o);o.push_str("},\"profile\":");quote(d.profile.as_str(),&mut o);o.push_str(",\"analysis\":{\"status\":");quote(if d.analysis.status==AnalysisStatus::Complete{"COMPLETE"}else{"PARTIAL"},&mut o);o.push_str(",\"symbols\":");o.push_str(&d.analysis.symbols.to_string());o.push_str("},\"summary\":{\"crap\":{");opt("\"max\":",d.summary.crap.max,&mut o);if d.summary.crap.mean.is_some(){if d.summary.crap.max.is_some(){o.push(',');}opt("\"mean\":",d.summary.crap.mean,&mut o);}o.push_str("}},\"symbols\":[");for(i,s)in d.symbols.iter().enumerate(){if i>0{o.push(',');}o.push_str("{\"symbol\":{");symbol_json(&s.symbol,&mut o);if let Some(c)=&s.complexity{o.push_str(",\"complexity\":{\"value\":");num(c.value,&mut o);o.push_str(",\"metric\":");quote(&c.metric,&mut o);o.push_str(",\"semantics\":");quote(&c.semantics,&mut o);o.push_str(",\"provider\":");quote(&c.provider,&mut o);o.push('}');}
 if let Some(c)=&s.coverage{o.push_str(",\"coverage\":{\"ratio\":");num(c.ratio,&mut o);o.push_str(",\"covered\":");o.push_str(&c.covered.to_string());o.push_str(",\"missed\":");o.push_str(&c.missed.to_string());o.push_str(",\"metric\":");quote(&c.metric,&mut o);o.push_str(",\"semantics\":");quote(&c.semantics,&mut o);o.push_str(",\"provider\":");quote(&c.provider,&mut o);o.push('}');}o.push_str(",\"metrics\":{");opt("\"crap\":",s.metrics.crap,&mut o);o.push_str("}}");}o.push_str("],\"provenance\":{\"provider\":");quote(&d.provenance.provider,&mut o);o.push_str(",\"semantics\":[");for(i,s)in d.provenance.semantics.iter().enumerate(){if i>0{o.push(',');}quote(s,&mut o);}o.push_str("],\"input\":{\"path\":");quote(&d.provenance.input.path,&mut o);o.push_str(",\"sha256\":");quote(d.provenance.input.sha256.as_str(),&mut o);if d.provenance.inputs.is_empty(){o.push_str("},\"analysis_timestamp\":");}else{o.push_str("},\"inputs\":[");for(i,input)in d.provenance.inputs.iter().enumerate(){if i>0{o.push(',');}o.push_str("{\"role\":");quote(input.role.as_str(),&mut o);o.push_str(",\"path\":");quote(&input.path,&mut o);o.push_str(",\"sha256\":");quote(input.sha256.as_str(),&mut o);o.push('}');}o.push_str("],\"analysis_timestamp\":");}quote(&d.provenance.analysis_timestamp,&mut o);o.push_str("}}\n");o}
fn symbol_json(s:&codegauge_model::SymbolIdentity,o:&mut String){o.push_str("\"id\":");quote(s.id(),o);o.push_str(",\"language\":");quote(s.language(),o);o.push_str(",\"kind\":");quote(s.kind(),o);o.push_str(",\"class_vm\":");quote(s.class_vm(),o);o.push_str(",\"name\":");quote(s.name(),o);o.push_str(",\"descriptor\":");quote(s.descriptor(),o);o.push('}');}
pub fn canonical_error_json(d:&ErrorDocument)->String{let mut o=String::from("{\"schema\":");quote(ERROR_SCHEMA_V1,&mut o);o.push_str(",\"tool\":{\"name\":");quote(&d.tool.name,&mut o);o.push_str(",\"version\":");quote(&d.tool.version,&mut o);o.push_str("},\"code\":");o.push_str(&serde_json::to_string(&d.code).unwrap());o.push_str(",\"message\":");quote(&d.message,&mut o);o.push_str(",\"details\":{");if let Some(v)=&d.details.path{o.push_str("\"path\":");quote(v,&mut o);}
 if let Some(v)=&d.details.sha256{if d.details.path.is_some(){o.push(',');}o.push_str("\"sha256\":");quote(v.as_str(),&mut o);}o.push_str("}}\n");o}
}
pub use implementation::*;

#[cfg(test)]
mod tests {
    use super::implementation::{BoundedReadError, read_bounded};
    use std::io::{self, Read};

    struct CountingReader {
        bytes: Vec<u8>,
        position: usize,
    }

    impl Read for CountingReader {
        fn read(&mut self, buffer: &mut [u8]) -> io::Result<usize> {
            let remaining = &self.bytes[self.position..];
            let amount = remaining.len().min(buffer.len());
            buffer[..amount].copy_from_slice(&remaining[..amount]);
            self.position += amount;
            Ok(amount)
        }
    }

    #[test]
    fn bounded_reader_rejects_after_one_extra_byte_without_consuming_the_rest() {
        let mut reader = CountingReader {
            bytes: b"012345".to_vec(),
            position: 0,
        };

        assert!(matches!(
            read_bounded(&mut reader, 3),
            Err(BoundedReadError::TooLarge)
        ));
        assert_eq!(reader.position, 4);
    }
}
