import assert from "node:assert/strict";
import {
  analyzeSource, summarize, buildReport, MAX_FILE_BYTES,
  ENGINE_VERSION, ACCEPTED
} from "../site/source-analysis-core.mjs";

const src = [
  "import service from './api.js'",
  "const url = '/api/verify/abc123';",
  "const endpoint = 'local_form/read_doc_company';",
  "el.innerHTML = userContent;",
  "localStorage.setItem('token', authToken);",
  "eval(inboundCode);"
].join("\n");
const result = analyzeSource("src/sample.js",src,"test-hash");
assert.equal(result.relative_path,"src/sample.js");
assert.equal(result.sha256,"test-hash");
assert.equal(result.classification,"JS_SOURCE");
assert.equal(result.engine_version,ENGINE_VERSION);
assert.deepEqual(result.api_paths,["/api/verify/abc123","local_form/read_doc_company"]);
assert.ok(result.imports.includes("./api.js"));
assert.ok(result.storage.includes("token"));
assert.deepEqual(new Set(result.findings.map(x=>x.rule_id)),new Set(["SC-HTML","SC-STORAGE","SC-EVAL"]));
assert.ok(result.findings.some(x=>x.line===4 && x.rule_id==="SC-HTML"));
assert.equal(result.severity_score,36);
assert.equal(result.secret_candidates.length,0);
const sampleSecret = "sk-proj-" + "A".repeat(30);
const secretResult = analyzeSource("unsafe.ts","const key = '" + sampleSecret + "';\n");
assert.equal(secretResult.secret_candidates.length,1);
assert.equal(secretResult.secret_candidates[0].kind,"OPENAI_API_KEY");
assert.equal(secretResult.secret_candidates[0].value_included,false);
assert.ok(!JSON.stringify(secretResult).includes(sampleSecret));
const normalized = analyzeSource("py/check.py","r = requests.get(url, verify=False)\n");
assert.ok(normalized.findings.some(x=>x.rule_id==="SC-TLS"));
assert.equal(normalized.findings[0].line,1);
const checkHtml = analyzeSource("snippet.html","<script>document.write(x)</script>");
assert.ok(checkHtml.findings.some(x=>x.rule_id==="SC-DOM"));
assert.throws(()=>analyzeSource(".env","secret=value"),/Unsupported/);
assert.throws(()=>analyzeSource("code.js",4),/text source/);
assert.throws(()=>analyzeSource("huge.js","A".repeat(MAX_FILE_BYTES+1)),/limit/);
assert.ok(ACCEPTED.test("test.tsx"));
const joined = summarize([result,secretResult]);
assert.equal(joined.files,2);
assert.equal(joined.unique_api_paths,2);
assert.equal(joined.review_indicators,3);
assert.equal(joined.secret_candidates,1);
const exported = buildReport([result,secretResult]);
assert.equal(exported.static_read_only,true);
assert.equal(exported.files.length,2);
assert.equal(exported.source,"browser_local_only");
assert.ok(!JSON.stringify(exported).includes(sampleSecret));
assert.throws(()=>buildReport(Array.from({length:33},()=>result)),/Too many/);
console.log("Offline source analyzer tests passed");
