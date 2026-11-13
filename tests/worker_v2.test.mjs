// Offline smoke checks for the V2 Cloudflare Worker using Node native Request/Response.
import assert from "node:assert/strict";
import worker from "../site/worker-v2.mjs";
const origin = "https://unit.example";
async function get(path, method="GET") {
  return worker.fetch(new Request(origin + path, {method}));
}
const home=await get("/");
assert.equal(home.status,200);
assert.match(home.headers.get("content-type"),/text\/html/);
assert.match(home.headers.get("content-security-policy"),/script-src 'self'/);
assert.doesNotMatch(home.headers.get("content-security-policy"),/unsafe-inline/);
assert.match(await home.text(),/STAR CYBER AUDIT/);
const app=await get("/assets/app.js");
assert.equal(app.status,200);
assert.match(app.headers.get("content-type"),/text\/javascript/);
const clientCode=await app.text();
assert.match(clientCode,/function loadFiles/);
assert.match(clientCode,/function validReport/);
assert.match(clientCode,/document\.createElement/);
assert.doesNotMatch(clientCode,/\.innerHTML\s*=/);
assert.doesNotMatch(clientCode,/\bfetch\s*\(/);
const css=await get("/assets/style.css");
assert.equal(css.status,200);
assert.match(await css.text(),/@media/);
const health=await get("/health");
assert.deepEqual(JSON.parse(await health.text()),{
  status:"ok",service:"star-cyber-audit-v2",version:"2.0.0-preview",read_only:true
});
assert.equal(health.headers.get("cache-control"),"no-store");
const about=await get("/api/about");
assert.equal(JSON.parse(await about.text()).network_uploads,false);
const head=await get("/","HEAD");
assert.equal(await head.text(),"");
const disallowed=await get("/","POST");
assert.equal(disallowed.status,405);
assert.equal(disallowed.headers.get("allow"),"GET, HEAD");
assert.equal((await get("/no-such-route")).status,404);
console.log("Star Cyber Audit V2 Worker smoke checks passed");
