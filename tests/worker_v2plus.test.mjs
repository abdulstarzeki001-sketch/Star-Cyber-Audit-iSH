// Standalone offline worker tests (Node 22+).
import assert from "node:assert/strict";
import worker from "../site/worker-v2plus.mjs";
import {analyzeSource,buildReport,summarize,MAX_FILES} from "../site/source-analysis-core.mjs";
async function route(path,method="GET"){
 return worker.fetch(new Request("https://local.example"+path,{method}));
}
for(const path of ["/","/assets/style.css","/assets/app.js",
 "/assets/source-engine.css","/assets/source-engine-ui.mjs","/assets/source-analysis-core.mjs"]) {
 const response=await route(path);
 assert.equal(response.status,200,path);
 assert.equal(response.headers.get("x-content-type-options"),"nosniff");
 const content=await response.text();
 assert.ok(content.length>200,path);
}
const html=await(await route("/")).text();
assert.match(html,/source-engine-ui\.mjs/);
assert.match(html,/source-engine\.css/);
const script=await(await route("/assets/source-engine-ui.mjs")).text();
assert.match(script,/analyzeSource/);
assert.doesNotMatch(script,/\beval\s*\(/);
const csp=(await route("/")).headers.get("content-security-policy");
assert.match(csp,/connect-src 'none'/);
assert.match(csp,/script-src 'self'/);
const details=await(await route("/health")).json();
assert.equal(details.status,"ok");
assert.equal(details.version,"2.1.0-preview");
assert.equal(details.read_only,true);
assert.equal((await route("/","HEAD")).status,200);
assert.equal(await(await route("/","HEAD")).text(),"");
assert.equal((await route("/","POST")).status,405);
assert.equal((await route("/unknown")).status,404);
const file=analyzeSource("sample.ts","el.innerHTML = content;\nconst path='/api/verify/token';\n");
assert.equal(file.classification,"JS_SOURCE");
assert.equal(file.api_paths[0],"/api/verify/token");
assert.ok(file.findings.some(x=>x.rule_id==="SC-HTML"));
assert.equal(analyzeSource("check.py","verify=False").classification,"PY_SOURCE");
assert.equal(analyzeSource("index.html","document.write(x)").classification,"HTML_SOURCE");
const secret="sk-proj-"+"a".repeat(38);
const leaked=analyzeSource("private.js","const key='"+secret+"';");
assert.equal(leaked.secret_candidates.length,1);
assert.ok(!JSON.stringify(leaked).includes(secret));
assert.equal(summarize([file,leaked]).files,2);
assert.equal(buildReport([file]).static_read_only,true);
assert.throws(()=>buildReport(Array.from({length:MAX_FILES+1},()=>file)),/Too many/);
console.log("V2+ full offline route and source scan integration tests passed");
