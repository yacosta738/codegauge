#[rustfmt::skip]
mod tests {
use codegauge_application::{AnalysisError,Analyzer,Artifact,ArtifactError,ArtifactReader,CollectionRequest,Diagnostic,DiagnosticCode,FsArtifactReader,InputCardinality,InputRequirement,InputSet,InputSetError,MetricProvider,ProfileDescriptor,ProviderObservations,ProviderRegistry,canonical_error_json,canonical_result_json,format_canonical_number,format_timestamp,normalize_path,profile_id,sha256_hex};
use codegauge_model::{AnalysisInput,AnalysisStatus,ComplexityMeasurement,CoverageMeasurement,DerivedMetrics,ErrorCode,InputRole,ProfileId,Sha256Digest,SymbolIdentity,SymbolResult,TYPESCRIPT_OXC_ISTANBUL_V1};
use std::{cell::RefCell,path::Path,rc::Rc,time::SystemTime};

#[test] fn reader_hashes_exact_bytes_and_normalizes_only_display_path() {
  assert_eq!(sha256_hex(b"abc").as_str(),"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
 assert_eq!(normalize_path(Path::new(r"reports\jacoco\report.xml")),"reports/jacoco/report.xml");
 let a=FsArtifactReader.read(Path::new("../../fixtures/jacoco/valid-methods.xml")).unwrap();
  assert_eq!((a.path,a.sha256),("../../fixtures/jacoco/valid-methods.xml".into(),Sha256Digest::new("6deddb631c24f78d5fe7eff07009a4d7c6714c2317689139bd4111e0cfd0bf2e").unwrap()));
 }

 #[test] fn reader_rejects_non_regular_paths(){let error=FsArtifactReader.read(Path::new("../../fixtures")).unwrap_err();assert!(matches!(error,ArtifactError::Unreadable(path) if path=="../../fixtures"));}

#[test] fn analyzer_uses_core_sorts_summarizes_and_sets_status() {
 let r=analyze(ProviderObservations{symbols:vec![sym("java:a",3.0,0.5),sym("java:B",7.0,0.83)],diagnostics:vec![]}).unwrap();
  assert_eq!(r.analysis.status,AnalysisStatus::Complete); assert_eq!(r.symbols.iter().map(|s|s.symbol.id()).collect::<Vec<_>>(),["java:B","java:a"]);
 let(a,b)=(r.symbols[0].metrics.crap.unwrap(),r.symbols[1].metrics.crap.unwrap()); assert_eq!(a,7.240737); assert_eq!(r.summary.crap,codegauge_model::CrapSummary{max:Some(a),mean:Some((a+b)/2.0)});
 let p=analyze(ProviderObservations{symbols:vec![sym("java:a",1.0,1.0)],diagnostics:vec![Diagnostic{code:DiagnosticCode::MissingRequiredCounter,symbol_id:None}]}).unwrap(); assert_eq!(p.analysis.status,AnalysisStatus::Partial); assert!(!canonical_result_json(&p).contains("PASS"));
 let e=analyze(ProviderObservations{symbols:vec![],diagnostics:vec![]}).unwrap_err(); assert_eq!(e.code(),ErrorCode::IncompatibleMeasurements); assert!(e.details().sha256.is_some());
}

#[test] fn timestamp_and_json_are_utc_fixed_order_utf8_and_half_even() {
 assert_eq!(format_timestamp(SystemTime::UNIX_EPOCH),"1970-01-01T00:00:00Z"); for(v,e)in[(0.0000000000005,"0"),(0.0000000000015,"0.000000000002"),(12.340000000000,"12.34"),(-0.0,"0")]{assert_eq!(format_canonical_number(v),e);}
 let mut r=analyze(ProviderObservations{symbols:vec![sym("java:é",1.0,1.0)],diagnostics:vec![]}).unwrap(); r.provenance.analysis_timestamp="1970-01-01T00:00:00Z".into(); r.symbols[0].complexity.as_mut().unwrap().value=0.0000000000015; let j=canonical_result_json(&r);
 assert!(std::str::from_utf8(j.as_bytes()).is_ok()&&j.ends_with('\n')); assert!(j.starts_with("{\"schema\":\"codegauge-result/v1\",\"tool\":{\"name\":\"codegauge\"")); assert!(j.contains("\"value\":0.000000000002")&&j.contains("analysis_timestamp")); assert!(canonical_error_json(&AnalysisError::unsupported_profile("x").document()).ends_with('\n'));
}

 fn sym(id:&str,cc:f64,ratio:f64)->SymbolResult{SymbolResult{symbol:SymbolIdentity::new(id,"test","symbol","C","m","()V").unwrap(),complexity:Some(ComplexityMeasurement{value:cc,metric:"cyclomatic".into(),semantics:"jacoco-cyclomatic".into(),provider:"jacoco".into()}),coverage:Some(CoverageMeasurement{ratio,covered:1,missed:0,metric:"instruction".into(),semantics:"jacoco-instruction".into(),provider:"jacoco".into()}),metrics:DerivedMetrics{crap:Some(-1.0)}}}
struct Reader(Artifact); impl ArtifactReader for Reader{fn read(&self,_:&Path)->Result<Artifact,ArtifactError>{Ok(self.0.clone())}}
 struct Provider(ProviderObservations); impl MetricProvider for Provider{fn descriptor(&self)->ProfileDescriptor{ProfileDescriptor{profile:ProfileId::JvmJacocoV1,provider:"mock".into(),semantics:vec!["mock".into()],required_inputs:vec![InputRequirement{role:InputRole::Coverage,cardinality:InputCardinality::ExactlyOne}]}} fn collect(&self,_:CollectionRequest<'_>)->Result<ProviderObservations,codegauge_application::ProviderError>{Ok(self.0.clone())}}
 fn analyze(o:ProviderObservations)->Result<codegauge_model::ResultDocument,AnalysisError>{let mut r=ProviderRegistry::new();r.register(Provider(o));Analyzer::new(Reader(Artifact{path:"report.xml".into(),bytes:b"report".into(),sha256:sha256_hex(b"report")}),r).analyze(ProfileId::JvmJacocoV1,Path::new("report.xml"))}

 #[test] fn input_set_is_sorted_and_rejects_duplicate_role_paths(){
   let set=InputSet::from_artifacts(vec![
     (AnalysisInput{role:InputRole::Source,path:"z.ts".into()},artifact("z.ts")),
     (AnalysisInput{role:InputRole::Coverage,path:"coverage.xml".into()},artifact("coverage.xml")),
     (AnalysisInput{role:InputRole::Source,path:"a.ts".into()},artifact("a.ts")),
   ]).unwrap();
   let ordered=set.iter().map(|(role,artifact)|(role.to_string(),artifact.path.clone())).collect::<Vec<_>>();
   assert_eq!(ordered,vec![("coverage".into(),"coverage.xml".into()),("source".into(),"a.ts".into()),("source".into(),"z.ts".into())]);
   let error=InputSet::from_artifacts(vec![
     (AnalysisInput{role:InputRole::Coverage,path:"coverage.xml".into()},artifact("coverage.xml")),
     (AnalysisInput{role:InputRole::Coverage,path:"coverage.xml".into()},artifact("coverage.xml")),
   ]).unwrap_err();
   assert_eq!(error,InputSetError::Duplicate{role:InputRole::Coverage,path:"coverage.xml".into()});
   let normalized=InputSet::from_artifacts(vec![
     (AnalysisInput{role:InputRole::Coverage,path:r"reports\coverage.xml".into()},artifact("first")),
     (AnalysisInput{role:InputRole::Coverage,path:"reports/coverage.xml".into()},artifact("second")),
   ]).unwrap_err();
   assert_eq!(normalized,InputSetError::Duplicate{role:InputRole::Coverage,path:"reports/coverage.xml".into()});
 }

 #[test] fn input_set_reports_missing_cardinality_and_undeclared_roles_deterministically(){
   let empty=InputSet::from_artifacts(Vec::<(AnalysisInput,Artifact)>::new()).unwrap();
   assert_eq!(empty.validate(&[InputRequirement{role:InputRole::Coverage,cardinality:InputCardinality::ExactlyOne}]).unwrap_err(),InputSetError::MissingRequired{role:InputRole::Coverage});
   let source=InputSet::from_artifacts(vec![(AnalysisInput{role:InputRole::Source,path:"src.ts".into()},artifact("src.ts"))]).unwrap();
   assert_eq!(source.validate(&[InputRequirement{role:InputRole::Coverage,cardinality:InputCardinality::ExactlyOne}]).unwrap_err(),InputSetError::UndeclaredRole{role:InputRole::Source});
 }

 #[test] fn analyzer_passes_multiple_typed_inputs_and_role_provenance_to_provider(){
   let seen=Rc::new(RefCell::new(Vec::new()));
   let mut registry=ProviderRegistry::new(); registry.register(RecordingProvider{seen:seen.clone()});
   let analyzer=Analyzer::new(RecordingReader,registry);
   let result=analyzer.analyze(ProfileId::JvmJacocoV1,&[
     AnalysisInput{role:InputRole::Source,path:"src.ts".into()},
     AnalysisInput{role:InputRole::Coverage,path:"coverage.xml".into()},
   ][..]).unwrap();
   assert_eq!(*seen.borrow(),vec![(InputRole::Coverage,"coverage.xml".into()),(InputRole::Source,"src.ts".into())]);
   assert_eq!(result.provenance.inputs.len(),2);
   assert_eq!(result.provenance.inputs[0].role,InputRole::Coverage);
   assert_eq!(result.provenance.inputs[1].role,InputRole::Source);
   let encoded=canonical_result_json(&result);
   assert!(encoded.contains("\"inputs\":[{\"role\":\"coverage\""));
 }

 #[test] fn analyzer_rejects_missing_required_roles_before_reading(){
   let reads=Rc::new(RefCell::new(0));
   let mut registry=ProviderRegistry::new(); registry.register(RecordingProvider{seen:Rc::new(RefCell::new(Vec::new()))});
   let analyzer=Analyzer::new(CountingReader{reads:reads.clone()},registry);
   let error=analyzer.analyze(ProfileId::JvmJacocoV1,&[AnalysisInput{role:InputRole::Source,path:"src.ts".into()}][..]).unwrap_err();
   assert_eq!(error.code(),ErrorCode::InvalidInput);
   assert_eq!(*reads.borrow(),0);
 }

  fn artifact(path:&str)->Artifact{Artifact{path:path.into(),bytes:path.as_bytes().to_vec(),sha256:sha256_hex(path.as_bytes())}}

  #[test] fn profile_registry_lookup_includes_typescript_oxc_istanbul(){
    assert_eq!(profile_id(TYPESCRIPT_OXC_ISTANBUL_V1),Some(ProfileId::TypescriptOxcIstanbulV1));
  }

  struct RecordingReader;
 impl ArtifactReader for RecordingReader{fn read(&self,path:&Path)->Result<Artifact,ArtifactError>{Ok(artifact(&normalize_path(path)))}}
 struct CountingReader{reads:Rc<RefCell<usize>>}
 impl ArtifactReader for CountingReader{fn read(&self,path:&Path)->Result<Artifact,ArtifactError>{*self.reads.borrow_mut()+=1;Ok(artifact(&normalize_path(path)))}}
 struct RecordingProvider{seen:Rc<RefCell<Vec<(InputRole,String)>>>}
 impl MetricProvider for RecordingProvider{
   fn descriptor(&self)->ProfileDescriptor{ProfileDescriptor{profile:ProfileId::JvmJacocoV1,provider:"recording".into(),semantics:vec!["mock".into()],required_inputs:vec![InputRequirement{role:InputRole::Coverage,cardinality:InputCardinality::ExactlyOne},InputRequirement{role:InputRole::Source,cardinality:InputCardinality::OneOrMore}]}}
   fn collect(&self,request:CollectionRequest<'_>)->Result<ProviderObservations,codegauge_application::ProviderError>{self.seen.borrow_mut().extend(request.inputs.iter().map(|(role,artifact)|(role,artifact.path.clone())));Ok(ProviderObservations{symbols:vec![sym("java:one",1.0,1.0)],diagnostics:vec![]})}
 }
}
